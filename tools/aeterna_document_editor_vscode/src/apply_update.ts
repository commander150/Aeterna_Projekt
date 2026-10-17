import { isDeepStrictEqual } from "node:util";
import { createHash, randomUUID } from "node:crypto";
import { lstat, mkdir, mkdtemp, readFile, realpath, writeFile } from "node:fs/promises";
import path from "node:path";

import { isPathWithin, loadCandidateSession, pathsEqual, type CandidateSessionRequest } from "./candidate";
import { inspectUpdateBaseline, parseUpdatePlanJson, type PreparedUpdatePreview } from "./update_plan";
import { candidateVersion } from "./version_candidate";
import { runGovernanceGuiCommand, runWorkflowCommand, type GovernanceGuiChallenge, type WorkflowCommandExecution } from "./workflow";

export class ExplicitApplyError extends Error {
  public constructor(public readonly code: string, message: string) {
    super(message);
    this.name = "ExplicitApplyError";
  }
}

export interface MaterializedUpdatePlan {
  readonly repositoryRoot: string;
  readonly planPath: string;
  readonly planSha256: string;
  readonly preview: PreparedUpdatePreview;
}

export interface ApplySummary {
  readonly artifactId: string;
  readonly title: string;
  readonly version: string;
  readonly versionIntent: "git-only" | "minor" | "major";
  readonly proposedVersion: string;
  readonly branch: string;
  readonly head: string;
  readonly baselineSha256: string;
  readonly candidateSha256: string;
  readonly planSemanticSha256: string;
  readonly plannedWrites: readonly string[];
  readonly dependencyImpact: string;
  readonly recommendedIntent: string;
  readonly mismatch: boolean;
}

export interface ApplyOutcome {
  readonly status: "PASS" | "FAIL" | "BLOCKED" | "VERIFY_FAILED" | "CANCELLED";
  readonly message: string;
  readonly reviewPath?: string;
  readonly rollback?: "NOT_RUN" | "PASS" | "FAIL";
}

export interface ApplyOptions {
  readonly candidateIsDirty: () => boolean;
  readonly confirm: (summary: ApplySummary) => Promise<boolean>;
  readonly confirmMismatch: (summary: ApplySummary) => Promise<boolean>;
  readonly onBeforeRun?: () => void;
  readonly runner?: (root: string, args: readonly string[]) => Promise<WorkflowCommandExecution>;
}

export function governanceChallengeMatches(
  challenge: GovernanceGuiChallenge, summary: ApplySummary, repositoryRoot: string,
): boolean {
  const binding = challenge.approval_binding;
  const operation = binding.operation_id;
  return challenge.schema_version === "aeterna-governance-gui-challenge/0.1" &&
    typeof operation === "string" && /^[0-9a-f]{32}$/.test(operation) &&
    challenge.challenge === `APPLY ${operation} ${summary.planSemanticSha256}` &&
    challenge.candidate_sha256 === summary.candidateSha256 &&
    binding.schema_version === "aeterna-local-governance-approval/0.1" &&
    pathsEqual(String(binding.repository_root), repositoryRoot) &&
    binding.artifact_id === summary.artifactId &&
    binding.baseline_branch === summary.branch &&
    binding.baseline_head === summary.head &&
    binding.plan_semantic_sha256 === summary.planSemanticSha256 &&
    binding.change_class === "semantic-governance-change" &&
    binding.version_intent === "major" &&
    isDeepStrictEqual(binding.expected_changed_paths, summary.plannedWrites);
}

function sha256(data: Buffer): string {
  return createHash("sha256").update(data).digest("hex");
}

function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new ExplicitApplyError("PLAN_INVALID", "Prepared UPDATE plan has an invalid structure.");
  }
  return value as Record<string, unknown>;
}

function plannedPaths(plan: Record<string, unknown>): string[] {
  if (!Array.isArray(plan.expected_changes)) {
    throw new ExplicitApplyError("PLAN_INVALID", "Prepared UPDATE plan has no expected changes.");
  }
  const paths = plan.expected_changes.map((entry) => object(entry).path);
  if (!paths.length || paths.some((entry) => typeof entry !== "string" || !entry)) {
    throw new ExplicitApplyError("PLAN_INVALID", "Prepared UPDATE plan has invalid write paths.");
  }
  return paths as string[];
}

export function summarizePreparedUpdate(materialized: MaterializedUpdatePlan, title: string, version: string): ApplySummary {
  const { preview } = materialized;
  const plan = preview.plan;
  const impact = object(plan.impact);
  const recommendation = object(plan.version);
  const describeDependencies = (items: unknown): string => Array.isArray(items) && items.length
    ? items.map((item) => String(object(item).artifact_id ?? "unknown")).join(", ")
    : "none";
  return {
    artifactId: preview.manifest.artifact_id,
    title,
    version,
    versionIntent: preview.manifest.version_intent,
    proposedVersion: preview.manifest.proposed_version ?? version,
    branch: preview.identity.branch,
    head: preview.identity.head,
    baselineSha256: preview.identity.baselineSha256,
    candidateSha256: preview.identity.candidateSha256,
    planSemanticSha256: String(plan.plan_semantic_sha256),
    plannedWrites: plannedPaths(plan),
    dependencyImpact: `direct: ${describeDependencies(impact.direct_reverse_dependencies)}; transitive: ${describeDependencies(impact.transitive_reverse_dependents)}`,
    recommendedIntent: String(recommendation.recommended_intent ?? "unknown"),
    mismatch: recommendation.mismatch === true,
  };
}

export async function materializePreparedUpdate(
  preview: PreparedUpdatePreview,
  repositoryRoot: string,
  planStorageRoot: string,
): Promise<MaterializedUpdatePlan> {
  if (preview.identity.repositoryRoot !== repositoryRoot || preview.manifest.artifact_id !== preview.plan.artifact_id) {
    throw new ExplicitApplyError("PLAN_IDENTITY_MISMATCH", "Plan belongs to a different repository or artifact.");
  }
  const parsed = parseUpdatePlanJson(preview.planJson, preview.manifest);
  if (!isDeepStrictEqual(parsed, preview.plan)) {
    throw new ExplicitApplyError("PLAN_IDENTITY_MISMATCH", "Materialized plan differs from the reviewed production plan.");
  }
  await mkdir(planStorageRoot, { recursive: true });
  const information = await lstat(planStorageRoot);
  const realStorage = await realpath(planStorageRoot);
  const realRepository = await realpath(repositoryRoot);
  if (!information.isDirectory() || information.isSymbolicLink() || isPathWithin(realRepository, realStorage)) {
    throw new ExplicitApplyError("PLAN_STORAGE_UNSAFE", "Plan storage must be a real directory outside the repository.");
  }
  const operation = await mkdtemp(path.join(realStorage, "update-"));
  const planPath = path.join(operation, "plan.json");
  const bytes = Buffer.from(preview.planJson, "utf8");
  await writeFile(planPath, bytes, { flag: "wx", mode: 0o600 });
  if (sha256(await readFile(planPath)) !== sha256(bytes)) {
    throw new ExplicitApplyError("PLAN_STORAGE_FAILURE", "Stored plan bytes changed during materialization.");
  }
  return { repositoryRoot: realRepository, planPath, planSha256: sha256(bytes), preview };
}

async function validatePreparedState(
  saved: MaterializedUpdatePlan,
  request: CandidateSessionRequest,
  candidateIsDirty: () => boolean,
): Promise<void> {
  if (candidateIsDirty()) {
    throw new ExplicitApplyError("CANDIDATE_UNSAVED", "Save the candidate before Apply; unsaved VS Code edits cannot be applied.");
  }
  const realRoot = await realpath(request.repositoryRoot);
  if (!pathsEqual(saved.repositoryRoot, realRoot) || !pathsEqual(saved.preview.identity.repositoryRoot, realRoot)) {
    throw new ExplicitApplyError("REPOSITORY_MISMATCH", "Prepared plan belongs to a different repository.");
  }
  const planInfo = await lstat(saved.planPath).catch(() => undefined);
  if (!planInfo || !planInfo.isFile() || planInfo.isSymbolicLink()) {
    throw new ExplicitApplyError("PLAN_MISSING", "Prepared plan file is missing or unsafe; prepare a new plan.");
  }
  const bytes = await readFile(saved.planPath);
  if (sha256(bytes) !== saved.planSha256) {
    throw new ExplicitApplyError("PLAN_STALE", "Prepared plan file changed; prepare a new plan.");
  }
  let parsed: Record<string, unknown>;
  try {
    parsed = parseUpdatePlanJson(bytes.toString("utf8"), saved.preview.manifest);
  } catch {
    throw new ExplicitApplyError("PLAN_INVALID", "Prepared plan file is malformed; prepare a new plan.");
  }
  const manifest = saved.preview.manifest;
  const expectedMode = manifest.change_class === "body-only" && manifest.version_intent === "git-only"
    ? manifest.metadata_delta.length === 0 && manifest.proposed_version === null
    : ((manifest.change_class === "metadata+body" && manifest.version_intent === "minor") ||
       (manifest.change_class === "semantic-governance-change" && manifest.version_intent === "major"))
      && manifest.metadata_delta.length === 1
      && manifest.metadata_delta[0]?.field === "version"
      && manifest.metadata_delta[0]?.old === request.artifact.version
      && manifest.metadata_delta[0]?.new === manifest.proposed_version;
  if (!expectedMode || !isDeepStrictEqual(parsed, saved.preview.plan) ||
      !plannedPaths(parsed).includes(request.artifact.canonicalPath)) {
    throw new ExplicitApplyError("PLAN_INVALID", "Prepared plan no longer matches the approved UPDATE operation.");
  }
  const session = await loadCandidateSession(request);
  if (!pathsEqual(session.candidatePath, String(object(parsed.candidate).resolved_path)) ||
      session.manifest.artifactId !== saved.preview.manifest.artifact_id) {
    throw new ExplicitApplyError("CANDIDATE_MISMATCH", "Candidate session differs from the prepared plan.");
  }
  const candidateInfo = await lstat(session.candidatePath);
  const candidateBytes = await readFile(session.candidatePath);
  if (!candidateInfo.isFile() || candidateInfo.isSymbolicLink() ||
      sha256(candidateBytes) !== saved.preview.identity.candidateSha256) {
    throw new ExplicitApplyError("PLAN_STALE", "Candidate changed after planning; prepare a new plan.");
  }
  if (manifest.version_intent !== "git-only" && candidateVersion(candidateBytes) !== manifest.proposed_version) {
    throw new ExplicitApplyError("PLAN_STALE", "Candidate version no longer matches the approved minor plan.");
  }
  const { baseline } = await inspectUpdateBaseline(realRoot, session.manifest.artifactId);
  const identity = saved.preview.identity;
  if (!baseline.worktree_clean || !baseline.staging_empty) {
    throw new ExplicitApplyError("WORKTREE_DIRTY", "Apply requires a clean worktree and empty staging area.");
  }
  if (!pathsEqual(baseline.repository_root, realRoot) || baseline.branch !== identity.branch ||
      baseline.head !== identity.head || baseline.sha256 !== identity.baselineSha256 ||
      baseline.metadata_fingerprint !== identity.metadataFingerprint ||
      baseline.metadata.version !== request.artifact.version) {
    throw new ExplicitApplyError("PLAN_STALE", "Repository branch, HEAD, canonical baseline or metadata changed; prepare a new plan.");
  }
}

function diagnostic(execution: WorkflowCommandExecution): string {
  try {
    const payload = object(JSON.parse(execution.stderr) as unknown);
    const first = Array.isArray(payload.diagnostics) ? payload.diagnostics[0] : undefined;
    if (first) {
      const item = object(first);
      return `${String(item.code)}: ${String(item.message)}`;
    }
  } catch { /* preserve raw workflow error below */ }
  return execution.stderr.trim() || `Production workflow exited ${execution.exitCode}.`;
}

export class ExplicitApplyCoordinator {
  private running = false;
  private readonly attempted = new Set<string>();

  public async apply(
    saved: MaterializedUpdatePlan,
    request: CandidateSessionRequest,
    title: string,
    version: string,
    options: ApplyOptions,
  ): Promise<ApplyOutcome> {
    return this.applyInternal(saved, request, title, version, options);
  }

  public async applyGovernance(
    saved: MaterializedUpdatePlan,
    request: CandidateSessionRequest,
    title: string,
    version: string,
    options: ApplyOptions,
    confirmChallenge: (summary: ApplySummary, challenge: GovernanceGuiChallenge) => Promise<boolean>,
  ): Promise<ApplyOutcome> {
    return this.applyInternal(saved, request, title, version, options, confirmChallenge);
  }

  private async applyInternal(
    saved: MaterializedUpdatePlan,
    request: CandidateSessionRequest,
    title: string,
    version: string,
    options: ApplyOptions,
    confirmChallenge?: (summary: ApplySummary, challenge: GovernanceGuiChallenge) => Promise<boolean>,
  ): Promise<ApplyOutcome> {
    const key = saved.planPath;
    if (this.running || this.attempted.has(key)) {
      throw new ExplicitApplyError("APPLY_ALREADY_ATTEMPTED", "An Apply is already running or this plan was already attempted. Prepare a new plan.");
    }
    this.running = true;
    try {
      await validatePreparedState(saved, request, options.candidateIsDirty);
      const governance = saved.preview.manifest.change_class === "semantic-governance-change";
      if (governance !== Boolean(confirmChallenge)) {
        throw new ExplicitApplyError("GOVERNANCE_ENTRYPOINT_REQUIRED", "High-risk governance plans require the separate GUI governance approval action.");
      }
      const summary = summarizePreparedUpdate(saved, title, version);
      if (!(await options.confirm(summary))) {
        return { status: "CANCELLED", message: "Apply cancelled; canonical files were not changed." };
      }
      if (summary.mismatch && !(await options.confirmMismatch(summary))) {
        return { status: "CANCELLED", message: "Version recommendation mismatch was not approved; no Apply ran." };
      }
      await validatePreparedState(saved, request, options.candidateIsDirty);
      const run = options.runner ?? runWorkflowCommand;
      const reviewDir = path.join(saved.repositoryRoot, "TEMP", "aeterna_document_editor_vscode", "e2b_reviews", randomUUID());
      this.attempted.add(key);
      options.onBeforeRun?.();
      const reviewPath = path.join(reviewDir, "review.json");
      let execution: WorkflowCommandExecution;
      try {
        const args = [governance ? "apply-governance-gui" : "apply", saved.planPath,
          "--repo", saved.repositoryRoot, "--review-dir", reviewDir];
        execution = governance
          ? await runGovernanceGuiCommand(saved.repositoryRoot, args, async (challenge) => {
            if (!governanceChallengeMatches(challenge, summary, saved.repositoryRoot)) {
              throw new ExplicitApplyError("GOVERNANCE_CHALLENGE_MISMATCH", "Production governance challenge does not match the reviewed plan.");
            }
            const approved = await confirmChallenge!(summary, challenge);
            if (!approved) return false;
            await validatePreparedState(saved, request, options.candidateIsDirty);
            return true;
          })
          : await run(saved.repositoryRoot, args);
      } catch (error) {
        return { status: "BLOCKED", message: `Production Apply could not start or complete: ${error instanceof Error ? error.message : String(error)}. No automatic retry.`, reviewPath };
      }
      let review: Record<string, unknown> | undefined;
      try {
        review = object(JSON.parse(await readFile(reviewPath, "utf8")) as unknown);
      } catch {
        if (execution.exitCode === 0) {
          return { status: "VERIFY_FAILED", message: "Apply returned success but production review is missing or invalid. Inspect the repository before any further action.", reviewPath };
        }
        return { status: "BLOCKED", message: `Production Apply rejected: ${diagnostic(execution)}. No automatic retry.`, reviewPath };
      }
      let verified: WorkflowCommandExecution;
      try {
        verified = await run(saved.repositoryRoot, ["verify-review", reviewPath]);
      } catch (error) {
        return { status: "VERIFY_FAILED", message: `Production verify-review could not run: ${error instanceof Error ? error.message : String(error)}. Inspect review evidence.`, reviewPath };
      }
      let verification: Record<string, unknown> | undefined;
      try { verification = object(JSON.parse(verified.stdout) as unknown); } catch { /* handled below */ }
      if (verified.exitCode !== 0 || verification?.status !== "PASS" ||
          verification.review_semantic_sha256 !== review.review_semantic_sha256 ||
          review.operation !== "update" ||
          object(review.artifact).artifact_id !== summary.artifactId ||
          review.plan_semantic_sha256 !== summary.planSemanticSha256) {
        return { status: "VERIFY_FAILED", message: `Production review verification failed: ${diagnostic(verified)}. Inspect the repository and review evidence.`, reviewPath };
      }
      if (governance && execution.exitCode === 0) {
        const approval = object(review.governance_approval);
        const binding = object(approval.binding);
        if (approval.method !== "interactive-gui" || approval.decision !== "CONFIRMED" ||
            approval.consumed !== true || !governanceChallengeMatches({
              schema_version: "aeterna-governance-gui-challenge/0.1",
              approval_binding: binding,
              challenge: `APPLY ${String(binding.operation_id)} ${summary.planSemanticSha256}`,
              candidate_sha256: summary.candidateSha256,
            }, summary, saved.repositoryRoot) || binding.operation_id !== review.operation_id) {
          return { status: "VERIFY_FAILED", message: "Governance approval evidence does not match the reviewed operation.", reviewPath };
        }
      }
      const rollback = object(review.rollback);
      const rollbackStatus: ApplyOutcome["rollback"] = rollback.performed
        ? rollback.verified === true && rollback.original_hashes_restored === true ? "PASS" : "FAIL"
        : "NOT_RUN";
      if (execution.exitCode === 0 && review.final_status === "PASS" &&
          object(review.transaction).state === "COMMITTED_TO_WORKTREE" && rollbackStatus === "NOT_RUN") {
        let payload: Record<string, unknown>;
        try { payload = object(JSON.parse(execution.stdout) as unknown); }
        catch {
          return { status: "VERIFY_FAILED", message: "Apply result JSON is invalid despite a verified review; inspect repository state.", reviewPath };
        }
        if (payload.status !== "PASS" || payload.artifact_id !== summary.artifactId ||
            !pathsEqual(String(payload.review_json), reviewPath)) {
          return { status: "VERIFY_FAILED", message: "Apply result does not match production review; inspect repository state.", reviewPath };
        }
        const scope = object(review.scope);
        const git = object(review.git);
        const actual = scope.actual_git_changed_paths;
        const planned = scope.planned_write_paths;
        if (!Array.isArray(actual) || actual.some((item) => typeof item !== "string") ||
            !Array.isArray(planned) || !isDeepStrictEqual(planned, summary.plannedWrites) ||
            !isDeepStrictEqual(actual, payload.changed_paths) ||
            !actual.includes(request.artifact.canonicalPath) ||
            actual.some((item) => !summary.plannedWrites.includes(item)) ||
            git.staging_empty !== true || git.diff_check !== true ||
            !Array.isArray(review.deviations) || review.deviations.length !== 0) {
          return { status: "VERIFY_FAILED", message: "Production review scope or Git checks conflict with Apply result; inspect repository state.", reviewPath };
        }
        const normalized = Array.isArray(scope.git_normalized_unchanged_generated_paths)
          ? scope.git_normalized_unchanged_generated_paths.join(", ") : "unknown";
        return {
          status: "PASS",
          message: `Governed Apply and production review verified. Git-visible changed paths: ${actual.join(", ")}. Git-normalized unchanged generated paths: ${normalized || "none"}. Inspect GitHub Desktop before manual commit/push.`,
          reviewPath,
          rollback: rollbackStatus,
        };
      }
      const status = review.final_status === "FAIL" ? "FAIL" : "BLOCKED";
      return { status, message: `Production Apply ${status}: ${diagnostic(execution)}. Rollback: ${rollbackStatus}. No automatic retry.`, reviewPath, rollback: rollbackStatus };
    } finally {
      this.running = false;
    }
  }
}
