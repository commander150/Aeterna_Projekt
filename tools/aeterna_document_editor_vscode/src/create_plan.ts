import { randomUUID } from "node:crypto";
import { lstat, readFile, realpath, writeFile } from "node:fs/promises";
import path from "node:path";

import { createMetadata, metadataFingerprint, sha256, validateCreateStorageRoot, type CreateSession } from "./create_candidate";
import { runWorkflowCommand } from "./workflow";

const BASELINE_SCHEMA = "aeterna-document-create-baseline/0.1";
const PLAN_SCHEMA = "aeterna-document-create-plan/0.1";

export class CreatePlanError extends Error {
  public constructor(public readonly code: string, message: string) {
    super(message);
    this.name = "CreatePlanError";
  }
}

export interface CreateBaseline {
  readonly schema_version: typeof BASELINE_SCHEMA;
  readonly repository_root: string;
  readonly branch: string;
  readonly head: string;
  readonly worktree_clean: boolean;
  readonly staging_empty: boolean;
  readonly diagnostics: readonly string[];
  readonly existing_artifact_ids: readonly string[];
  readonly controlled_values: { readonly type: readonly string[]; readonly authority: readonly string[]; readonly integration: readonly string[] };
  readonly create_contract: { readonly kind: "document"; readonly lifecycle: "active"; readonly generated: false; readonly integration: readonly string[] };
}

export interface CreatePreview {
  readonly plan: Record<string, unknown>;
  readonly planPath: string;
  readonly planSha256: string;
  readonly manifestPath: string;
  readonly candidateSha256: string;
}

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function parseJson(text: string, label: string): Record<string, unknown> {
  try {
    const value: unknown = JSON.parse(text);
    if (record(value)) return value;
  } catch { /* fail below */ }
  throw new CreatePlanError("INVALID_JSON", `${label} did not return a JSON object.`);
}

function workflowError(stderr: string, operation: string): CreatePlanError {
  try {
    const result = parseJson(stderr, operation);
    const diagnostics = result.diagnostics;
    if (Array.isArray(diagnostics)) {
      const descriptions = diagnostics.filter(record).map((item) => `${String(item.code)}: ${String(item.message)}`);
      return new CreatePlanError(String((diagnostics[0] as { code?: unknown } | undefined)?.code ?? "WORKFLOW_ERROR"), `${operation}: ${descriptions.join("; ")}`);
    }
  } catch { /* use raw diagnostic */ }
  return new CreatePlanError("WORKFLOW_ERROR", `${operation}: ${stderr.trim() || "no diagnostic output"}`);
}

export function parseCreateBaseline(text: string): CreateBaseline {
  const value = parseJson(text, "CREATE baseline inspection");
  const controlled = value.controlled_values;
  const contract = value.create_contract;
  if (value.schema_version !== BASELINE_SCHEMA || typeof value.repository_root !== "string" ||
      typeof value.branch !== "string" || !/^[0-9a-f]{40}$/.test(String(value.head)) ||
      typeof value.worktree_clean !== "boolean" || typeof value.staging_empty !== "boolean" ||
      !Array.isArray(value.diagnostics) || !Array.isArray(value.existing_artifact_ids) ||
      !record(controlled) || !record(contract) ||
      !Array.isArray(controlled.type) || !Array.isArray(controlled.authority) || !Array.isArray(controlled.integration) ||
      contract.kind !== "document" || contract.lifecycle !== "active" || contract.generated !== false ||
      !Array.isArray(contract.integration)) {
    throw new CreatePlanError("BASELINE_INVALID", "CREATE baseline inspection returned an unsupported contract.");
  }
  return value as unknown as CreateBaseline;
}

export async function inspectCreateBaseline(repositoryRoot: string): Promise<CreateBaseline> {
  const result = await runWorkflowCommand(repositoryRoot, ["inspect-create-baseline", "--repo", repositoryRoot]);
  if (result.exitCode !== 0) throw workflowError(result.stderr, "inspect-create-baseline");
  return parseCreateBaseline(result.stdout);
}

export function requireCreateBaseline(baseline: CreateBaseline, session?: CreateSession): void {
  if (!baseline.worktree_clean || !baseline.staging_empty || baseline.diagnostics.length) {
    throw new CreatePlanError("BASELINE_BLOCKED", "CREATE planning requires a clean worktree, empty staging and diagnostic-free artifact scan.");
  }
  if (session && (baseline.repository_root !== session.repositoryRoot || baseline.branch !== session.branch || baseline.head !== session.head)) {
    throw new CreatePlanError("BASELINE_DRIFT", "Repository identity changed after the CREATE candidate was approved. Existing candidate preserved.");
  }
}

export async function prepareCreatePreview(
  repositoryRoot: string, session: CreateSession, candidateIsDirty: () => boolean,
): Promise<CreatePreview> {
  if (candidateIsDirty()) throw new CreatePlanError("CANDIDATE_UNSAVED", "Save every CREATE candidate editor before planning.");
  const realStorage = await validateCreateStorageRoot(repositoryRoot, session.storageRoot);
  const candidateDirectory = path.dirname(session.candidatePath);
  const relativeDirectory = path.relative(realStorage, candidateDirectory);
  if (!relativeDirectory || relativeDirectory === ".." || relativeDirectory.startsWith(`..${path.sep}`) ||
      path.isAbsolute(relativeDirectory) || path.basename(session.candidatePath) !== "candidate.md" ||
      path.dirname(session.manifestPath) !== candidateDirectory) {
    throw new CreatePlanError("CANDIDATE_PATH_BLOCKED", "CREATE candidate is outside its authorized session directory.");
  }
  if (await realpath(candidateDirectory) !== candidateDirectory) {
    throw new CreatePlanError("CANDIDATE_PATH_BLOCKED", "CREATE candidate session uses a redirected directory.");
  }
  const candidateEntry = await lstat(session.candidatePath);
  if (!candidateEntry.isFile() || candidateEntry.nlink !== 1) {
    throw new CreatePlanError("CANDIDATE_PATH_BLOCKED", "CREATE candidate must be a real, single-linked file.");
  }
  const baseline = await inspectCreateBaseline(repositoryRoot);
  requireCreateBaseline(baseline, session);
  const candidateBytes = await readFile(session.candidatePath);
  const candidateSha256 = sha256(candidateBytes);
  if (candidateIsDirty()) throw new CreatePlanError("CANDIDATE_UNSAVED", "CREATE candidate became unsaved during planning.");
  const metadata = createMetadata(session.input);
  const manifest = {
    schema_version: "aeterna-document-create-manifest/0.1",
    artifact_id: session.input.artifactId,
    target_path: session.input.targetPath,
    candidate_path: "candidate.md",
    expected_branch: session.branch,
    expected_head: session.head,
    candidate_sha256: candidateSha256,
    candidate_metadata_fingerprint: metadataFingerprint(metadata),
    candidate_metadata: metadata,
    candidate_byte_convention: { encoding: "UTF-8", bom: false, newline: "LF" },
    declared_authority: session.input.authority,
    initial_version: session.input.version,
  };
  const manifestPath = path.join(path.dirname(session.candidatePath), `plan-manifest-${randomUUID()}.json`);
  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, { encoding: "utf8", flag: "wx", mode: 0o600 });
  const result = await runWorkflowCommand(repositoryRoot, [
    "plan-create", "--manifest", manifestPath, "--repo", repositoryRoot,
    "--external-candidate-root", session.storageRoot,
  ]);
  if (result.exitCode !== 0) throw workflowError(result.stderr, "plan-create");
  const plan = parseJson(result.stdout, "plan-create");
  const planBaseline = plan.baseline;
  const planCandidate = plan.candidate;
  const target = plan.target;
  const authority = plan.authority;
  const version = plan.version;
  if (plan.schema_version !== PLAN_SCHEMA || plan.operation !== "create" || plan.artifact_id !== session.input.artifactId ||
      !record(planBaseline) || planBaseline.head !== session.head || planBaseline.branch !== session.branch ||
      !record(planCandidate) || planCandidate.sha256 !== candidateSha256 || planCandidate.metadata_fingerprint !== manifest.candidate_metadata_fingerprint ||
      !record(target) || target.declared_path !== session.input.targetPath || target.absent !== true ||
      !record(authority) || authority.declared_authority !== session.input.authority ||
      !record(version) || version.initial_version !== session.input.version ||
      !Array.isArray(plan.preconditions) || plan.preconditions.some((entry) => !record(entry) || entry.result !== "PASS") ||
      !Array.isArray(plan.expected_changes) || !/^[0-9a-f]{64}$/.test(String(plan.plan_semantic_sha256))) {
    throw new CreatePlanError("PLAN_INVALID", "Production CREATE plan identity, scope or preconditions do not match the approved candidate.");
  }
  if (sha256(await readFile(session.candidatePath)) !== candidateSha256) {
    throw new CreatePlanError("PLAN_STALE", "CREATE candidate changed while plan-create was running.");
  }
  if (candidateIsDirty()) throw new CreatePlanError("CANDIDATE_UNSAVED", "CREATE candidate became unsaved during planning.");
  const after = await inspectCreateBaseline(repositoryRoot);
  requireCreateBaseline(after, session);
  const planPath = path.join(path.dirname(session.candidatePath), `create-plan-${randomUUID()}.json`);
  const planBytes = Buffer.from(`${JSON.stringify(plan, null, 2)}\n`, "utf8");
  await writeFile(planPath, planBytes, { flag: "wx", mode: 0o600 });
  return { plan, planPath, planSha256: sha256(planBytes), manifestPath, candidateSha256 };
}

export function renderCreatePreview(preview: CreatePreview): string {
  const plan = preview.plan;
  const target = record(plan.target) ? plan.target : {};
  const authority = record(plan.authority) ? plan.authority : {};
  const impact = record(plan.impact) ? plan.impact : {};
  const expected = Array.isArray(plan.expected_changes) ? plan.expected_changes : [];
  const generated = record(plan.generated) && Array.isArray(plan.generated.outputs) ? plan.generated.outputs : [];
  return [
    "AETERNA read-only CREATE plan review — Apply requires separate approval",
    `Artifact ID: ${String(plan.artifact_id)}`,
    `Canonical target: ${String(target.declared_path)}`,
    `Authority: ${String(authority.declared_authority)}; review risk: ${String(authority.risk)}`,
    `Initial version: ${String(record(plan.version) ? plan.version.initial_version : "unknown")}`,
    `Forward dependencies: ${JSON.stringify(impact.forward_dependencies ?? [])}`,
    `Dependency impact: ${JSON.stringify(impact)}`,
    `Generated output preview: ${JSON.stringify(generated)}`,
    `Planned writes: ${JSON.stringify(expected)}`,
    `Preconditions: ${JSON.stringify(plan.preconditions)}`,
    `Candidate SHA-256: ${preview.candidateSha256}`,
    `Plan semantic SHA-256: ${String(plan.plan_semantic_sha256)}`,
    `Full production plan: ${preview.planPath}`,
    "Saving the candidate and preparing this plan do not create the canonical document.",
  ].join("\n");
}
