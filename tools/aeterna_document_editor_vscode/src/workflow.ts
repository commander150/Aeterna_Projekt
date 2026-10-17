import { spawn } from "node:child_process";
import { stat } from "node:fs/promises";
import path from "node:path";

const MAX_OUTPUT_BYTES = 5 * 1024 * 1024;
const WORKFLOW_MODULE = "tools.aeterna_document_workflow.cli";

export interface PythonInterpreter {
  readonly command: string;
  readonly prefixArguments: readonly string[];
  readonly displayName: string;
}

export interface ResolveResult {
  readonly artifact_id: string;
  readonly path: string;
  readonly [key: string]: unknown;
}

export interface WorkflowResolveResult {
  readonly interpreter: PythonInterpreter;
  readonly result: ResolveResult;
  readonly stderr: string;
}

export class WorkflowIntegrationError extends Error {
  public constructor(
    public readonly code:
      | "INTERPRETER_NOT_FOUND"
      | "WORKFLOW_UNAVAILABLE"
      | "WORKFLOW_ERROR"
      | "INVALID_JSON",
    message: string,
    public readonly stderr = "",
  ) {
    super(message);
    this.name = "WorkflowIntegrationError";
  }
}

interface ProcessResult {
  readonly exitCode: number;
  readonly stdout: string;
  readonly stderr: string;
}

export interface WorkflowCommandExecution extends ProcessResult {
  readonly interpreter: PythonInterpreter;
}

class ProcessLaunchError extends Error {
  public constructor(
    message: string,
    public readonly causeCode: string | undefined,
  ) {
    super(message);
    this.name = "ProcessLaunchError";
  }
}

function executeFile(
  command: string,
  args: readonly string[],
  cwd: string,
): Promise<ProcessResult> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
      shell: false,
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"],
    });
    const stdout: Buffer[] = [];
    const stderr: Buffer[] = [];
    let outputBytes = 0;

    const capture = (target: Buffer[], chunk: Buffer): void => {
      outputBytes += chunk.length;
      if (outputBytes > MAX_OUTPUT_BYTES) {
        child.kill();
        reject(
          new ProcessLaunchError(
            `Child process output exceeded ${MAX_OUTPUT_BYTES} bytes.`,
            undefined,
          ),
        );
        return;
      }
      target.push(chunk);
    };

    child.stdout.on("data", (chunk: Buffer) => capture(stdout, chunk));
    child.stderr.on("data", (chunk: Buffer) => capture(stderr, chunk));
    child.on("error", (error: NodeJS.ErrnoException) => {
      reject(new ProcessLaunchError(error.message, error.code));
    });
    child.on("close", (code) => {
      resolve({
        exitCode: code ?? -1,
        stdout: Buffer.concat(stdout).toString("utf8"),
        stderr: Buffer.concat(stderr).toString("utf8"),
      });
    });
  });
}

function interpreterCandidates(repositoryRoot: string): PythonInterpreter[] {
  const override = process.env.AETERNA_PYTHON?.trim();
  if (override) {
    return [
      {
        command: override,
        prefixArguments: [],
        displayName: override,
      },
    ];
  }
  if (process.platform === "win32") {
    return [
      {
        command: path.join(repositoryRoot, ".venv", "Scripts", "python.exe"),
        prefixArguments: [],
        displayName: "repository .venv Python",
      },
      { command: "py", prefixArguments: ["-3"], displayName: "py -3" },
      { command: "python", prefixArguments: [], displayName: "python" },
    ];
  }
  return [
    {
      command: path.join(repositoryRoot, ".venv", "bin", "python"),
      prefixArguments: [],
      displayName: "repository .venv Python",
    },
    { command: "python3", prefixArguments: [], displayName: "python3" },
    { command: "python", prefixArguments: [], displayName: "python" },
  ];
}

export async function discoverPythonInterpreter(
  repositoryRoot: string,
): Promise<PythonInterpreter> {
  const attempts: string[] = [];
  for (const candidate of interpreterCandidates(repositoryRoot)) {
    try {
      const probe = await executeFile(
        candidate.command,
        [...candidate.prefixArguments, "--version"],
        repositoryRoot,
      );
      if (probe.exitCode === 0) {
        return candidate;
      }
      attempts.push(`${candidate.displayName}: exit ${probe.exitCode}`);
    } catch (error) {
      if (error instanceof ProcessLaunchError && error.causeCode === "ENOENT") {
        attempts.push(`${candidate.displayName}: not found`);
        continue;
      }
      const detail = error instanceof Error ? error.message : String(error);
      attempts.push(`${candidate.displayName}: ${detail}`);
    }
  }
  throw new WorkflowIntegrationError(
    "INTERPRETER_NOT_FOUND",
    `No usable Python interpreter was found (${attempts.join("; ")}).`,
  );
}

export function buildResolveArguments(
  interpreter: PythonInterpreter,
  artifactId: string,
  repositoryRoot: string,
): string[] {
  return [
    ...interpreter.prefixArguments,
    "-m",
    WORKFLOW_MODULE,
    "resolve",
    artifactId,
    "--repo",
    repositoryRoot,
    "--json",
  ];
}

export function parseResolveJson(output: string): ResolveResult {
  let value: unknown;
  try {
    value = JSON.parse(output) as unknown;
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new WorkflowIntegrationError(
      "INVALID_JSON",
      `Workflow resolve returned invalid UTF-8 JSON: ${detail}`,
    );
  }
  if (
    typeof value !== "object" ||
    value === null ||
    Array.isArray(value) ||
    typeof (value as Record<string, unknown>).artifact_id !== "string" ||
    typeof (value as Record<string, unknown>).path !== "string"
  ) {
    throw new WorkflowIntegrationError(
      "INVALID_JSON",
      "Workflow resolve JSON is missing string artifact_id or path fields.",
    );
  }
  return value as ResolveResult;
}

async function workflowIsAvailable(repositoryRoot: string): Promise<boolean> {
  const cliPath = path.join(
    repositoryRoot,
    "tools",
    "aeterna_document_workflow",
    "cli.py",
  );
  try {
    return (await stat(cliPath)).isFile();
  } catch {
    return false;
  }
}

export async function runWorkflowCommand(
  repositoryRoot: string,
  arguments_: readonly string[],
): Promise<WorkflowCommandExecution> {
  if (!(await workflowIsAvailable(repositoryRoot))) {
    throw new WorkflowIntegrationError(
      "WORKFLOW_UNAVAILABLE",
      "The AETERNA document workflow CLI is unavailable in the repository.",
    );
  }
  const interpreter = await discoverPythonInterpreter(repositoryRoot);
  try {
    const execution = await executeFile(
      interpreter.command,
      [...interpreter.prefixArguments, "-m", WORKFLOW_MODULE, ...arguments_],
      repositoryRoot,
    );
    return { ...execution, interpreter };
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new WorkflowIntegrationError(
      "WORKFLOW_ERROR",
      `Unable to execute workflow with ${interpreter.displayName}: ${detail}`,
    );
  }
}

export interface GovernanceGuiChallenge {
  readonly schema_version: "aeterna-governance-gui-challenge/0.1";
  readonly approval_binding: Record<string, unknown>;
  readonly challenge: string;
  readonly candidate_sha256: string;
}

export async function runGovernanceGuiCommand(
  repositoryRoot: string,
  arguments_: readonly string[],
  confirm: (challenge: GovernanceGuiChallenge) => Promise<boolean>,
): Promise<WorkflowCommandExecution> {
  if (!(await workflowIsAvailable(repositoryRoot))) {
    throw new WorkflowIntegrationError("WORKFLOW_UNAVAILABLE", "The AETERNA document workflow CLI is unavailable in the repository.");
  }
  const interpreter = await discoverPythonInterpreter(repositoryRoot);
  return new Promise((resolve, reject) => {
    const child = spawn(interpreter.command,
      [...interpreter.prefixArguments, "-m", WORKFLOW_MODULE, ...arguments_],
      { cwd: repositoryRoot, shell: false, windowsHide: true, stdio: ["pipe", "pipe", "pipe"] });
    const stdout: Buffer[] = [];
    const stderr: Buffer[] = [];
    let size = 0;
    let pending = Buffer.alloc(0);
    let challenged = false;
    let prefixLength = 0;
    let failed = false;
    let protocolError: Error | undefined;
    const abort = (error: Error): void => {
      if (failed) return;
      failed = true;
      child.stdin.end();
      child.kill();
      reject(error);
    };
    const capture = (target: Buffer[], chunk: Buffer): void => {
      size += chunk.length;
      if (size > MAX_OUTPUT_BYTES) {
        abort(new Error("Governance workflow output exceeded the allowed size."));
        return;
      }
      target.push(chunk);
    };
    child.stdout.on("data", (chunk: Buffer) => {
      capture(stdout, chunk);
      if (challenged || failed) return;
      pending = Buffer.concat([pending, chunk]);
      const end = pending.indexOf(10);
      if (end < 0) return;
      challenged = true;
      prefixLength = end + 1;
      let challenge: GovernanceGuiChallenge;
      try {
        challenge = JSON.parse(pending.subarray(0, end).toString("utf8")) as GovernanceGuiChallenge;
        if (challenge.schema_version !== "aeterna-governance-gui-challenge/0.1" ||
            !challenge.approval_binding || typeof challenge.challenge !== "string" ||
            typeof challenge.candidate_sha256 !== "string") throw new Error("Invalid governance challenge.");
      } catch {
        protocolError = new Error("Production governance challenge was malformed.");
        child.stdin.end("\n");
        return;
      }
      void Promise.resolve().then(() => confirm(challenge)).then((approved) => {
        if (!failed && child.exitCode === null && !child.stdin.destroyed) child.stdin.end(`${approved ? challenge.challenge : ""}\n`);
      }).catch((error: unknown) => {
        protocolError = error instanceof Error ? error : new Error(String(error));
        if (child.exitCode === null && !child.stdin.destroyed) child.stdin.end("\n");
      });
    });
    child.stderr.on("data", (chunk: Buffer) => capture(stderr, chunk));
    child.on("error", (error: Error) => abort(error));
    child.on("close", (code) => {
      if (failed) return;
      if (protocolError) {
        reject(protocolError);
        return;
      }
      const output = Buffer.concat(stdout);
      if (code === 0 && !challenged) {
        reject(new Error("Governance workflow completed without an interactive challenge."));
        return;
      }
      resolve({ exitCode: code ?? -1, stdout: challenged ? output.subarray(prefixLength).toString("utf8") : output.toString("utf8"),
        stderr: Buffer.concat(stderr).toString("utf8"), interpreter });
    });
  });
}

export async function resolveArtifact(
  repositoryRoot: string,
  artifactId: string,
): Promise<WorkflowResolveResult> {
  if (!(await workflowIsAvailable(repositoryRoot))) {
    throw new WorkflowIntegrationError(
      "WORKFLOW_UNAVAILABLE",
      "The AETERNA document workflow CLI is unavailable in the repository.",
    );
  }
  const interpreter = await discoverPythonInterpreter(repositoryRoot);
  let execution: ProcessResult;
  try {
    execution = await executeFile(
      interpreter.command,
      buildResolveArguments(interpreter, artifactId, repositoryRoot),
      repositoryRoot,
    );
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new WorkflowIntegrationError(
      "WORKFLOW_ERROR",
      `Unable to execute workflow resolve with ${interpreter.displayName}: ${detail}`,
    );
  }
  if (execution.exitCode !== 0) {
    throw new WorkflowIntegrationError(
      "WORKFLOW_ERROR",
      `Workflow resolve failed with exit code ${execution.exitCode}.`,
      execution.stderr,
    );
  }
  return {
    interpreter,
    result: parseResolveJson(execution.stdout),
    stderr: execution.stderr,
  };
}
