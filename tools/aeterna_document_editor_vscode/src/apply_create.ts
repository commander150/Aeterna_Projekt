import { isDeepStrictEqual } from "node:util";
import { randomUUID } from "node:crypto";
import { lstat, readFile, realpath } from "node:fs/promises";
import path from "node:path";

import { loadCreateSession, sha256, type CreateSession } from "./create_candidate";
import { pathsEqual } from "./candidate";
import { inspectCreateBaseline, requireCreateBaseline, type CreatePreview } from "./create_plan";
import { runWorkflowCommand, type WorkflowCommandExecution } from "./workflow";

const CREATE_PLAN_SCHEMA = "aeterna-document-create-plan/0.1";
const CREATE_REVIEW_SCHEMA = "aeterna-document-create-review/0.1";
const GENERATED_PATHS = new Set(["project/generated/artifacts_registry.json", "project/generated/DOCUMENT_INDEX.md"]);

export class CreateApplyError extends Error {
  public constructor(public readonly code: string, message: string) {
    super(message);
    this.name = "CreateApplyError";
  }
}

export interface CreateApplySummary {
  readonly artifactId: string;
  readonly targetPath: string;
  readonly authority: string;
  readonly authorityRisk: string;
  readonly initialVersion: string;
  readonly branch: string;
  readonly head: string;
  readonly dependencyImpact: string;
  readonly candidateSha256: string;
  readonly planSemanticSha256: string;
  readonly plannedWrites: readonly string[];
}

export interface CreateApplyOutcome {
  readonly status: "PASS" | "FAIL" | "BLOCKED" | "VERIFY_FAILED" | "CANCELLED";
  readonly message: string;
  readonly reviewPath?: string;
}

export interface CreateApplyOptions {
  readonly candidateIsDirty: () => boolean;
  readonly confirmReview: (summary: CreateApplySummary) => Promise<boolean>;
  readonly confirmFinal: (summary: CreateApplySummary) => Promise<boolean>;
  readonly onBeforeRun?: () => void;
  readonly runner?: (root: string, args: readonly string[]) => Promise<WorkflowCommandExecution>;
}

function object(value: unknown, label: string): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new CreateApplyError("PLAN_INVALID", `Prepared CREATE ${label} is invalid.`);
  }
  return value as Record<string, unknown>;
}

function errorDetail(execution: WorkflowCommandExecution): string {
  try {
    const result = object(JSON.parse(execution.stderr) as unknown, "diagnostic");
    const first = Array.isArray(result.diagnostics) ? result.diagnostics[0] : undefined;
    if (first) {
      const item = object(first, "diagnostic entry");
      return `${String(item.code)}: ${String(item.message)}`;
    }
  } catch { /* keep the original error below */ }
  return execution.stderr.trim() || `Production workflow exited ${execution.exitCode}.`;
}

export function summarizePreparedCreate(preview: CreatePreview, session: CreateSession): CreateApplySummary {
  const plan = preview.plan;
  const repository = object(plan.repository, "repository");
  const baseline = object(plan.baseline, "baseline");
  const target = object(plan.target, "target");
  const candidate = object(plan.candidate, "candidate");
  const authority = object(plan.authority, "authority");
  const version = object(plan.version, "version");
  const expected = plan.expected_changes;
  if (plan.schema_version !== CREATE_PLAN_SCHEMA || plan.operation !== "create" ||
      plan.artifact_id !== session.input.artifactId ||
      !pathsEqual(String(repository.root), session.repositoryRoot) ||
      baseline.branch !== session.branch || baseline.head !== session.head ||
      target.declared_path !== session.input.targetPath || target.absent !== true ||
      candidate.sha256 !== preview.candidateSha256 || !pathsEqual(String(candidate.resolved_path), session.candidatePath) ||
      authority.declared_authority !== session.input.authority || !["HIGH", "NORMAL"].includes(String(authority.risk)) ||
      version.initial_version !== session.input.version ||
      !/^[0-9a-f]{64}$/.test(String(plan.plan_semantic_sha256)) ||
      !Array.isArray(plan.preconditions) || plan.preconditions.some((item) => object(item, "precondition").result !== "PASS") ||
      !Array.isArray(expected) || expected.length < 1 || expected.length > 3) {
    throw new CreateApplyError("PLAN_INVALID", "Prepared CREATE plan does not match this candidate and repository.");
  }
  const writes = expected.map((entry) => object(entry, "write").path);
  if (writes.some((item) => typeof item !== "string") ||
      writes[0] !== session.input.targetPath || new Set(writes).size !== writes.length ||
      writes.slice(1).some((item) => !GENERATED_PATHS.has(String(item)))) {
    throw new CreateApplyError("PLAN_SCOPE_INVALID", "Prepared CREATE plan has an unexpected write target.");
  }
  return {
    artifactId: session.input.artifactId,
    targetPath: session.input.targetPath,
    authority: session.input.authority,
    authorityRisk: String(authority.risk),
    initialVersion: session.input.version,
    branch: session.branch,
    head: session.head,
    dependencyImpact: JSON.stringify(object(plan.impact, "dependency impact")),
    candidateSha256: preview.candidateSha256,
    planSemanticSha256: String(plan.plan_semantic_sha256),
    plannedWrites: writes as string[],
  };
}

async function validatePreparedState(
  repositoryRoot: string, session: CreateSession, preview: CreatePreview, candidateIsDirty: () => boolean,
): Promise<CreateApplySummary> {
  if (candidateIsDirty()) throw new CreateApplyError("CANDIDATE_UNSAVED", "Save the CREATE candidate before Apply.");
  const root = await realpath(repositoryRoot);
  if (!pathsEqual(root, session.repositoryRoot)) {
    throw new CreateApplyError("REPOSITORY_MISMATCH", "CREATE candidate belongs to a different repository.");
  }
  const loaded = await loadCreateSession(root, session.storageRoot, session.input.artifactId, session.branch, session.head);
  if (!loaded || !pathsEqual(loaded.candidatePath, session.candidatePath) ||
      !pathsEqual(loaded.manifestPath, session.manifestPath) ||
      JSON.stringify(loaded.input) !== JSON.stringify(session.input)) {
    throw new CreateApplyError("SESSION_DRIFT", "CREATE session changed after planning; candidate was preserved.");
  }
  const planInfo = await lstat(preview.planPath).catch(() => undefined);
  if (!planInfo?.isFile() || planInfo.isSymbolicLink() || planInfo.nlink !== 1 ||
      !pathsEqual(path.dirname(preview.planPath), path.dirname(session.candidatePath)) ||
      !pathsEqual(await realpath(preview.planPath), preview.planPath)) {
    throw new CreateApplyError("PLAN_MISSING", "Immutable CREATE plan file is missing or unsafe.");
  }
  const planBytes = await readFile(preview.planPath);
  if (sha256(planBytes) !== preview.planSha256) {
    throw new CreateApplyError("PLAN_STALE", "Immutable CREATE plan file changed; prepare a new plan.");
  }
  let plan: unknown;
  try { plan = JSON.parse(planBytes.toString("utf8")); }
  catch { throw new CreateApplyError("PLAN_INVALID", "Immutable CREATE plan is not valid JSON."); }
  if (!isDeepStrictEqual(plan, preview.plan)) {
    throw new CreateApplyError("PLAN_STALE", "Immutable CREATE plan differs from the reviewed plan.");
  }
  const summary = summarizePreparedCreate(preview, session);
  const candidateInfo = await lstat(session.candidatePath);
  if (!candidateInfo.isFile() || candidateInfo.isSymbolicLink() || candidateInfo.nlink !== 1 ||
      sha256(await readFile(session.candidatePath)) !== summary.candidateSha256) {
    throw new CreateApplyError("CANDIDATE_DRIFT", "CREATE candidate changed after planning; prepare a new plan.");
  }
  const baseline = await inspectCreateBaseline(root);
  requireCreateBaseline(baseline, session);
  if (candidateIsDirty()) throw new CreateApplyError("CANDIDATE_UNSAVED", "CREATE candidate became unsaved during approval.");
  return summary;
}

export class CreateApplyCoordinator {
  private running = false;
  private readonly attempted = new Set<string>();

  public async apply(
    repositoryRoot: string, session: CreateSession, preview: CreatePreview, options: CreateApplyOptions,
  ): Promise<CreateApplyOutcome> {
    if (this.running || this.attempted.has(preview.planPath)) {
      throw new CreateApplyError("APPLY_ALREADY_ATTEMPTED", "CREATE Apply is running or this plan was already attempted. Prepare a new plan.");
    }
    this.running = true;
    try {
      const summary = await validatePreparedState(repositoryRoot, session, preview, options.candidateIsDirty);
      if (!(await options.confirmReview(summary))) {
        return { status: "CANCELLED", message: "CREATE review cancelled; no Apply ran and the candidate was preserved." };
      }
      await validatePreparedState(repositoryRoot, session, preview, options.candidateIsDirty);
      if (!(await options.confirmFinal(summary))) {
        return { status: "CANCELLED", message: "Final CREATE approval cancelled; no Apply ran and the candidate was preserved." };
      }
      await validatePreparedState(repositoryRoot, session, preview, options.candidateIsDirty);
      const run = options.runner ?? runWorkflowCommand;
      const reviewDir = path.join(repositoryRoot, "TEMP", "aeterna_document_editor_vscode", "create_reviews", randomUUID());
      const reviewPath = path.join(reviewDir, "review.json");
      this.attempted.add(preview.planPath);
      options.onBeforeRun?.();
      let execution: WorkflowCommandExecution;
      try {
        execution = await run(repositoryRoot, ["apply", preview.planPath, "--repo", repositoryRoot, "--review-dir", reviewDir]);
      } catch (error) {
        return { status: "BLOCKED", message: `Production CREATE Apply could not complete: ${error instanceof Error ? error.message : String(error)}. Do not retry this plan automatically.`, reviewPath };
      }
      let review: Record<string, unknown>;
      try { review = object(JSON.parse(await readFile(reviewPath, "utf8")) as unknown, "review"); }
      catch {
        return { status: execution.exitCode === 0 ? "VERIFY_FAILED" : "BLOCKED", message: `Production CREATE review is missing or invalid. ${errorDetail(execution)} Inspect the repository before another Apply.`, reviewPath };
      }
      let verified: WorkflowCommandExecution;
      try { verified = await run(repositoryRoot, ["verify-review", reviewPath]); }
      catch (error) {
        return { status: "VERIFY_FAILED", message: `Production verify-review failed to run: ${error instanceof Error ? error.message : String(error)}`, reviewPath };
      }
      let verification: Record<string, unknown> | undefined;
      try { verification = object(JSON.parse(verified.stdout) as unknown, "verification"); } catch { /* fail below */ }
      if (verified.exitCode !== 0 || verification?.status !== "PASS" ||
          verification.schema_version !== CREATE_REVIEW_SCHEMA ||
          verification.review_semantic_sha256 !== review.review_semantic_sha256 ||
          review.schema_version !== CREATE_REVIEW_SCHEMA || review.operation !== "create" ||
          review.plan_semantic_sha256 !== summary.planSemanticSha256 ||
          object(review.artifact, "review artifact").artifact_id !== summary.artifactId ||
          object(review.target, "review target").declared_path !== summary.targetPath ||
          object(review.candidate, "review candidate").sha256 !== summary.candidateSha256) {
        return { status: "VERIFY_FAILED", message: "Production CREATE review does not match the approved plan or verify-review failed.", reviewPath };
      }
      const rollback = object(review.rollback, "rollback");
      if (execution.exitCode !== 0 || review.final_status !== "PASS") {
        const status = review.final_status === "FAIL" ? "FAIL" : "BLOCKED";
        return { status, message: `Production CREATE Apply ${status}: ${errorDetail(execution)}. Rollback verified: ${String(rollback.verified)}. No automatic retry.`, reviewPath };
      }
      let result: Record<string, unknown>;
      try { result = object(JSON.parse(execution.stdout) as unknown, "result"); }
      catch { return { status: "VERIFY_FAILED", message: "Production CREATE result JSON is invalid after a successful review.", reviewPath }; }
      const scope = object(review.scope, "scope");
      const git = object(review.git, "Git checks");
      const transaction = object(review.transaction, "transaction");
      const hashes = object(review.hashes, "hashes");
      const validation = object(review.validation, "validation");
      if (result.status !== "PASS" || result.artifact_id !== summary.artifactId ||
          !pathsEqual(String(result.review_json), reviewPath) ||
          !isDeepStrictEqual(scope.expected_paths, summary.plannedWrites) ||
          !isDeepStrictEqual(scope.actual_paths, result.changed_paths) ||
          !Array.isArray(scope.actual_paths) || scope.actual_paths.some((item) => typeof item !== "string") ||
          !isDeepStrictEqual([...scope.actual_paths].sort(), [...summary.plannedWrites].sort()) ||
          transaction.state !== "COMMITTED_TO_WORKTREE" || rollback.performed !== false ||
          validation.recomputed_create_plan_match !== "PASS" || validation.post_write !== "PASS" ||
          hashes.final_target_sha256 !== summary.candidateSha256 ||
          git.staging_empty !== true || git.diff_check !== true || git.target_direct_text_check !== "PASS" ||
          !Array.isArray(review.deviations) || review.deviations.length !== 0) {
        return { status: "VERIFY_FAILED", message: "Production CREATE result, scope, transaction or Git checks conflict with the approved plan.", reviewPath };
      }
      return { status: "PASS", message: `CREATE Apply and production review verified. Changed paths: ${summary.plannedWrites.join(", ")}. Inspect GitHub Desktop before manual commit/push.`, reviewPath };
    } finally {
      this.running = false;
    }
  }
}
