import { createHash } from "node:crypto";
import { lstat, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

import type { CandidateSession } from "./candidate";
import type { CandidateDocumentState } from "./candidate";
import { runWorkflowCommand, type WorkflowCommandExecution } from "./workflow";

const BASELINE_SCHEMA = "aeterna-document-update-baseline/0.1";
const PLAN_SCHEMA = "aeterna-document-update-plan/0.1";
const MANIFEST_SCHEMA = "aeterna-document-update-manifest/0.1";
const SHA256_PATTERN = /^[0-9a-f]{64}$/;

export interface WorkflowDiagnostic {
  readonly code: string;
  readonly severity: string;
  readonly message: string;
  readonly field: string | null;
}

export class UpdatePreviewError extends Error {
  public constructor(
    public readonly code: string,
    message: string,
    public readonly diagnostics: readonly WorkflowDiagnostic[] = [],
  ) {
    super(message);
    this.name = "UpdatePreviewError";
  }
}

export interface UpdateBaseline {
  readonly schema_version: typeof BASELINE_SCHEMA;
  readonly artifact_id: string;
  readonly path: string;
  readonly repository_root: string;
  readonly branch: string;
  readonly head: string;
  readonly worktree_clean: boolean;
  readonly staging_empty: boolean;
  readonly sha256: string;
  readonly metadata_fingerprint: string;
  readonly metadata: Record<string, unknown>;
  readonly byte_convention: Record<string, unknown>;
}

export interface UpdateChoice {
  readonly changeClass: "body-only";
  readonly versionIntent: "git-only";
}

export interface UpdateManifestPayload {
  readonly schema_version: typeof MANIFEST_SCHEMA;
  readonly artifact_id: string;
  readonly expected_branch: string;
  readonly expected_head: string;
  readonly expected_path: string;
  readonly baseline_sha256: string;
  readonly metadata_fingerprint: string;
  readonly change_class: "body-only";
  readonly version_intent: "git-only";
  readonly candidate_path: string;
  readonly candidate_sha256: string;
  readonly metadata_delta: readonly [];
  readonly reference_changes: readonly [];
  readonly proposed_version: null;
}

export interface UpdatePlanIdentity {
  readonly repositoryRoot: string;
  readonly branch: string;
  readonly head: string;
  readonly baselineSha256: string;
  readonly metadataFingerprint: string;
  readonly candidateSha256: string;
}

export interface PreparedUpdatePreview {
  readonly plan: Record<string, unknown>;
  readonly planJson: string;
  readonly identity: UpdatePlanIdentity;
  readonly manifest: UpdateManifestPayload;
  readonly interpreter: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function sha256(bytes: Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

function parseJsonObject(output: string, description: string): Record<string, unknown> {
  let value: unknown;
  try {
    value = JSON.parse(output) as unknown;
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new UpdatePreviewError("INVALID_JSON", `${description} returned invalid JSON: ${detail}`);
  }
  if (!isRecord(value)) {
    throw new UpdatePreviewError("INVALID_JSON", `${description} must return a JSON object.`);
  }
  return value;
}

function requireString(value: Record<string, unknown>, key: string): string {
  const field = value[key];
  if (typeof field !== "string" || !field) {
    throw new UpdatePreviewError("INVALID_JSON", `Workflow JSON field must be a non-empty string: ${key}.`);
  }
  return field;
}

export function parseUpdateBaselineJson(output: string): UpdateBaseline {
  const value = parseJsonObject(output, "UPDATE baseline inspection");
  if (
    value.schema_version !== BASELINE_SCHEMA ||
    typeof value.worktree_clean !== "boolean" ||
    typeof value.staging_empty !== "boolean" ||
    !isRecord(value.metadata) ||
    !isRecord(value.byte_convention)
  ) {
    throw new UpdatePreviewError("INVALID_JSON", "UPDATE baseline inspection has an invalid schema or fields.");
  }
  const sha = requireString(value, "sha256");
  const fingerprint = requireString(value, "metadata_fingerprint");
  if (!SHA256_PATTERN.test(sha) || !SHA256_PATTERN.test(fingerprint)) {
    throw new UpdatePreviewError("INVALID_JSON", "UPDATE baseline hash or fingerprint is invalid.");
  }
  return {
    schema_version: BASELINE_SCHEMA,
    artifact_id: requireString(value, "artifact_id"),
    path: requireString(value, "path"),
    repository_root: requireString(value, "repository_root"),
    branch: requireString(value, "branch"),
    head: requireString(value, "head"),
    worktree_clean: value.worktree_clean,
    staging_empty: value.staging_empty,
    sha256: sha,
    metadata_fingerprint: fingerprint,
    metadata: value.metadata,
    byte_convention: value.byte_convention,
  };
}

function workflowFailure(execution: WorkflowCommandExecution, operation: string): UpdatePreviewError {
  try {
    const error = parseJsonObject(execution.stderr, `${operation} error`);
    if (Array.isArray(error.diagnostics)) {
      const diagnostics = error.diagnostics.filter(isRecord).map((item) => ({
        code: String(item.code ?? "WORKFLOW_ERROR"),
        severity: String(item.severity ?? "ERROR"),
        message: String(item.message ?? "Workflow rejected the request."),
        field: typeof item.field === "string" ? item.field : null,
      }));
      return new UpdatePreviewError(
        diagnostics[0]?.code ?? "WORKFLOW_ERROR",
        `${operation} rejected the request (exit ${execution.exitCode}): ${diagnostics.map((item) => `${item.code}: ${item.message}`).join("; ")}`,
        diagnostics,
      );
    }
  } catch (error) {
    if (!(error instanceof UpdatePreviewError) || error.code !== "INVALID_JSON") {
      throw error;
    }
  }
  return new UpdatePreviewError(
    "WORKFLOW_ERROR",
    `${operation} failed with exit code ${execution.exitCode}: ${execution.stderr.trim() || "no diagnostic output"}`,
  );
}

export async function inspectUpdateBaseline(
  repositoryRoot: string,
  artifactId: string,
): Promise<{ baseline: UpdateBaseline; interpreter: string }> {
  const result = await runWorkflowCommand(repositoryRoot, [
    "inspect-update-baseline", artifactId, "--repo", repositoryRoot,
  ]);
  if (result.exitCode !== 0) {
    throw workflowFailure(result, "UPDATE baseline inspection");
  }
  return {
    baseline: parseUpdateBaselineJson(result.stdout),
    interpreter: result.interpreter.displayName,
  };
}

export function createUpdateManifest(
  session: CandidateSession,
  baseline: UpdateBaseline,
  candidateSha256: string,
  choice: UpdateChoice,
): UpdateManifestPayload {
  if (choice.changeClass !== "body-only" || choice.versionIntent !== "git-only") {
    throw new UpdatePreviewError("UNSUPPORTED_CHOICE", "E2A supports only an explicit body-only / git-only UPDATE choice.");
  }
  if (
    baseline.artifact_id !== session.manifest.artifactId ||
    baseline.path !== session.manifest.canonicalPath ||
    baseline.sha256 !== session.manifest.baseline.canonicalSha256 ||
    baseline.metadata.version !== session.manifest.baseline.version ||
    baseline.repository_root !== session.manifest.repositoryRoot
  ) {
    throw new UpdatePreviewError("BASELINE_DRIFT", "Current Python workflow baseline does not match the E1 candidate session.");
  }
  return {
    schema_version: MANIFEST_SCHEMA,
    artifact_id: baseline.artifact_id,
    expected_branch: baseline.branch,
    expected_head: baseline.head,
    expected_path: baseline.path,
    baseline_sha256: baseline.sha256,
    metadata_fingerprint: baseline.metadata_fingerprint,
    change_class: choice.changeClass,
    version_intent: choice.versionIntent,
    candidate_path: session.candidatePath,
    candidate_sha256: candidateSha256,
    metadata_delta: [],
    reference_changes: [],
    proposed_version: null,
  };
}

export function isUpdatePlanStale(
  planned: UpdatePlanIdentity,
  current: UpdatePlanIdentity,
): boolean {
  return (
    planned.repositoryRoot !== current.repositoryRoot ||
    planned.branch !== current.branch ||
    planned.head !== current.head ||
    planned.baselineSha256 !== current.baselineSha256 ||
    planned.metadataFingerprint !== current.metadataFingerprint ||
    planned.candidateSha256 !== current.candidateSha256
  );
}

export function requireSavedCandidate(state: CandidateDocumentState): void {
  if (state === "OPEN_DIRTY") {
    throw new UpdatePreviewError(
      "CANDIDATE_UNSAVED",
      "Save the candidate in VS Code or ManulDown before preparing a plan. No unsaved buffer is used for planning.",
    );
  }
}

export function parseUpdatePlanJson(
  output: string,
  manifest: UpdateManifestPayload,
): Record<string, unknown> {
  const plan = parseJsonObject(output, "plan-update");
  const baseline = plan.baseline;
  const candidate = plan.candidate;
  if (
    plan.schema_version !== PLAN_SCHEMA ||
    plan.operation !== "update" ||
    plan.artifact_id !== manifest.artifact_id ||
    !isRecord(baseline) ||
    !isRecord(candidate) ||
    !SHA256_PATTERN.test(requireString(plan, "plan_semantic_sha256")) ||
    baseline.head !== manifest.expected_head ||
    baseline.sha256 !== manifest.baseline_sha256 ||
    baseline.metadata_fingerprint !== manifest.metadata_fingerprint ||
    candidate.sha256 !== manifest.candidate_sha256
  ) {
    throw new UpdatePreviewError("INVALID_JSON", "plan-update returned a mismatched plan identity.");
  }
  return plan;
}

async function candidateBytes(candidatePath: string): Promise<Buffer> {
  const information = await lstat(candidatePath);
  if (!information.isFile() || information.isSymbolicLink()) {
    throw new UpdatePreviewError("CANDIDATE_UNSAFE", "Candidate must remain a regular file without a symlink.");
  }
  return readFile(candidatePath);
}

export async function currentUpdateIdentity(
  repositoryRoot: string,
  session: CandidateSession,
): Promise<UpdatePlanIdentity> {
  const [{ baseline }, bytes] = await Promise.all([
    inspectUpdateBaseline(repositoryRoot, session.manifest.artifactId),
    candidateBytes(session.candidatePath),
  ]);
  return {
    repositoryRoot: baseline.repository_root,
    branch: baseline.branch,
    head: baseline.head,
    baselineSha256: baseline.sha256,
    metadataFingerprint: baseline.metadata_fingerprint,
    candidateSha256: sha256(bytes),
  };
}

export async function prepareUpdatePreview(
  repositoryRoot: string,
  session: CandidateSession,
  choice: UpdateChoice,
): Promise<PreparedUpdatePreview> {
  const [{ baseline, interpreter }, bytes] = await Promise.all([
    inspectUpdateBaseline(repositoryRoot, session.manifest.artifactId),
    candidateBytes(session.candidatePath),
  ]);
  const candidateSha256 = sha256(bytes);
  const manifest = createUpdateManifest(session, baseline, candidateSha256, choice);
  const operationDirectory = await mkdtemp(path.join(os.tmpdir(), "aeterna-e2a-plan-"));
  try {
    const manifestPath = path.join(operationDirectory, "update-manifest.json");
    await writeFile(manifestPath, `${JSON.stringify(manifest, undefined, 2)}\n`, {
      encoding: "utf8", flag: "wx", mode: 0o600,
    });
    const execution = await runWorkflowCommand(repositoryRoot, [
      "plan-update", "--manifest", manifestPath, "--repo", repositoryRoot,
    ]);
    if (execution.exitCode !== 0) {
      throw workflowFailure(execution, "plan-update");
    }
    const plan = parseUpdatePlanJson(execution.stdout, manifest);
    const currentBytes = await candidateBytes(session.candidatePath);
    if (sha256(currentBytes) !== candidateSha256) {
      throw new UpdatePreviewError("PLAN_STALE", "Candidate changed while plan-update was running; discard this plan.");
    }
    return {
      plan,
      planJson: execution.stdout,
      manifest,
      interpreter,
      identity: {
        repositoryRoot: baseline.repository_root,
        branch: baseline.branch,
        head: baseline.head,
        baselineSha256: baseline.sha256,
        metadataFingerprint: baseline.metadata_fingerprint,
        candidateSha256,
      },
    };
  } finally {
    await rm(operationDirectory, { recursive: true, force: true });
  }
}

export function renderUpdatePreview(preview: PreparedUpdatePreview): string {
  const plan = preview.plan;
  const version = isRecord(plan.version) ? plan.version : {};
  const changes = Array.isArray(plan.expected_changes) ? plan.expected_changes : [];
  const impact = isRecord(plan.impact) ? plan.impact : {};
  const direct = Array.isArray(impact.direct_reverse_dependencies) ? impact.direct_reverse_dependencies : [];
  const transitive = Array.isArray(impact.transitive_reverse_dependents) ? impact.transitive_reverse_dependents : [];
  const diagnostics = Array.isArray(plan.preconditions) ? plan.preconditions.filter(
    (entry) => isRecord(entry) && entry.result !== "PASS",
  ) : [];
  const paths = changes.map((item) => isRecord(item) ? String(item.path ?? "<missing path>") : "<invalid item>");
  const describeDependencies = (items: unknown[]): string => items.length
    ? items.map((item) => isRecord(item)
      ? `${String(item.artifact_id ?? "<missing ID>")} (${String(item.impact ?? "unknown impact")})`
      : "<invalid dependency>").join(", ")
    : "none";
  return [
    "AETERNA read-only UPDATE plan preview",
    `Artifact: ${preview.manifest.artifact_id}`,
    "Explicit choice: change_class=body-only, version_intent=git-only",
    `HEAD: ${preview.identity.head}`,
    `Baseline SHA-256: ${preview.identity.baselineSha256}`,
    `Candidate SHA-256: ${preview.identity.candidateSha256}`,
    `Plan semantic SHA-256: ${String(plan.plan_semantic_sha256)}`,
    `Expected changed paths: ${paths.length ? paths.join(", ") : "none"}`,
    `Direct reverse dependencies (${direct.length}): ${describeDependencies(direct)}`,
    `Transitive reverse dependencies (${transitive.length}): ${describeDependencies(transitive)}`,
    `Version recommendation: ${String(version.recommended_intent ?? "unknown")}`,
    `Declared intent: ${String(version.declared_intent ?? "unknown")}`,
    `Recommendation mismatch: ${version.mismatch === true ? "YES" : "NO"}`,
    `Failed preconditions: ${diagnostics.length}`,
    "Candidate save and plan preview do not apply canonical changes.",
    "Full production plan JSON:",
    JSON.stringify(plan, undefined, 2),
  ].join("\n");
}
