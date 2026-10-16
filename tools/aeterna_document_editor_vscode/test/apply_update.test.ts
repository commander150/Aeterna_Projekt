import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { copyFile, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";

import { createOrOpenCandidateSession, type CandidateSession } from "../src/candidate";
import {
  ExplicitApplyCoordinator, ExplicitApplyError, materializePreparedUpdate,
  type ApplyOptions, type MaterializedUpdatePlan,
} from "../src/apply_update";
import { prepareUpdatePreview } from "../src/update_plan";
import type { WorkflowCommandExecution } from "../src/workflow";
import { writeCandidateVersion } from "../src/version_candidate";

const sourceRoot = path.resolve(__dirname, "../../../..");
const python = path.join(sourceRoot, ".venv", "Scripts", "python.exe");
const priorPython = process.env.AETERNA_PYTHON;
const priorPythonPath = process.env.PYTHONPATH;
process.env.AETERNA_PYTHON = python;
process.env.PYTHONPATH = sourceRoot;
const temporary: string[] = [];
const target = "project/planning/TARGET.md";
const baseline = [
  "---", "artifact_id: AET-DOC-TARGET", "kind: document", "type: reference",
  'version: "1.0"', "lifecycle: active", "integration: current",
  "authority: project-direction", "generated: false", "depends_on: []", "supersedes: []",
  "---", "", "# Target", "", "Baseline body.", "",
].join("\n");

afterEach(async () => {
  await Promise.all(temporary.splice(0).map((directory) => rm(directory, { recursive: true, force: true })));
});

function run(command: string, args: string[], cwd: string): string {
  const result = spawnSync(command, args, {
    cwd, encoding: "utf8", windowsHide: true,
    env: { ...process.env, PYTHONPATH: sourceRoot },
  });
  if (result.status !== 0) throw new Error(`${command} ${args.join(" ")} failed: ${result.stderr}`);
  return result.stdout.trim();
}

async function fixture(mode: "git-only" | "minor" = "git-only"): Promise<{
  readonly root: string;
  readonly canonical: string;
  readonly session: CandidateSession;
  readonly request: Parameters<ExplicitApplyCoordinator["apply"]>[1];
  readonly saved: MaterializedUpdatePlan;
}> {
  const top = await mkdtemp(path.join(os.tmpdir(), "aeterna-e2b-test-"));
  temporary.push(top);
  const root = path.join(top, "repo");
  const canonical = path.join(root, ...target.split("/"));
  await mkdir(path.dirname(canonical), { recursive: true });
  await writeFile(path.join(root, ".gitignore"), "TEMP/\n", "utf8");
  await writeFile(canonical, baseline, "utf8");
  const cli = path.join(root, "tools", "aeterna_document_workflow", "cli.py");
  await mkdir(path.dirname(cli), { recursive: true });
  await copyFile(path.join(sourceRoot, "tools", "aeterna_document_workflow", "cli.py"), cli);
  const generation = [
    "from pathlib import Path",
    "from tools.aeterna_artifacts.scanner import scan_repository",
    "from tools.aeterna_artifacts.generation import build_generated_content, REGISTRY_PATH, DOCUMENT_INDEX_PATH",
    "root = Path.cwd()",
    "generated = build_generated_content(scan_repository(root).artifacts)",
    "for relative, text in ((REGISTRY_PATH, generated.registry), (DOCUMENT_INDEX_PATH, generated.document_index)):",
    "    target = root / relative",
    "    target.parent.mkdir(parents=True, exist_ok=True)",
    "    target.write_bytes(text.encode('utf-8'))",
  ].join("\n");
  run(python, ["-c", generation], root);
  run("git", ["init", "-b", "main"], root);
  run("git", ["config", "user.email", "fixture@example.invalid"], root);
  run("git", ["config", "user.name", "Fixture"], root);
  run("git", ["add", "."], root);
  run("git", ["commit", "-m", "fixture baseline"], root);
  const request = {
    repositoryRoot: root,
    storageRoot: path.join(top, "vscode-storage", "e1-candidates"),
    artifact: {
      artifactId: "AET-DOC-TARGET", canonicalPath: target,
      version: "1.0", kind: "document", generated: false, scope: "ACTIVE",
    },
  };
  const session = await createOrOpenCandidateSession(request);
  await writeFile(session.candidatePath, baseline.replace("Baseline body.", "Candidate body changed."), "utf8");
  if (mode === "minor") {
    const bytes = await readFile(session.candidatePath);
    await writeCandidateVersion(session.candidatePath, createHash("sha256").update(bytes).digest("hex"), "1.0", "1.1");
  }
  const preview = await prepareUpdatePreview(root, session, mode === "minor"
    ? { changeClass: "metadata+body", versionIntent: "minor", proposedVersion: "1.1" }
    : { changeClass: "body-only", versionIntent: "git-only" });
  const saved = await materializePreparedUpdate(preview, root, path.join(top, "vscode-storage", "e2b-plans"));
  return { root, canonical, session, request, saved };
}

function options(overrides: Partial<ApplyOptions> = {}): ApplyOptions {
  return {
    candidateIsDirty: () => false,
    confirm: async () => true,
    confirmMismatch: async () => true,
    ...overrides,
  };
}

function hasCode(code: string): (error: unknown) => boolean {
  return (error) => error instanceof ExplicitApplyError && error.code === code;
}

test("immutable reviewed plan executes one real production Apply only in an isolated repository", async () => {
  const data = await fixture();
  assert.equal(await readFile(data.saved.planPath, "utf8"), data.saved.preview.planJson);
  const coordinator = new ExplicitApplyCoordinator();
  let summarySeen = false;
  let mismatchSeen = false;
  const outcome = await coordinator.apply(data.saved, data.request, "Target", "1.0", options({
    confirm: async (summary) => {
      summarySeen = true;
      assert.equal(summary.artifactId, "AET-DOC-TARGET");
      assert.deepEqual(summary.plannedWrites, [target]);
      assert.equal(summary.version, "1.0");
      assert.equal(summary.mismatch, true);
      return true;
    },
    confirmMismatch: async () => { mismatchSeen = true; return true; },
  }));
  assert.equal(summarySeen, true);
  assert.equal(mismatchSeen, true);
  assert.equal(outcome.status, "PASS");
  assert.equal(outcome.rollback, "NOT_RUN");
  assert.match(outcome.message, /Git-visible changed paths: project\/planning\/TARGET\.md/);
  assert.ok(outcome.reviewPath?.includes(`${path.sep}TEMP${path.sep}`));
  assert.deepEqual(await readFile(data.canonical), await readFile(data.session.candidatePath));
  assert.match(run("git", ["diff", "--name-only"], data.root), /TARGET\.md/);
  assert.equal(run("git", ["diff", "--cached", "--name-only"], data.root), "");
  await assert.rejects(
    coordinator.apply(data.saved, data.request, "Target", "1.0", options()),
    hasCode("APPLY_ALREADY_ATTEMPTED"),
  );
});

test("versioned minor plan needs confirmation and production review in an isolated repository", async () => {
  const data = await fixture("minor");
  const canonicalBefore = await readFile(data.canonical);
  let mismatchConfirmations = 0;
  const coordinator = new ExplicitApplyCoordinator();
  const cancelled = await coordinator.apply(data.saved, data.request, "Target", "1.0", options({
    confirm: async (summary) => {
      assert.equal(summary.versionIntent, "minor");
      assert.equal(summary.version, "1.0");
      assert.equal(summary.proposedVersion, "1.1");
      assert.equal(summary.mismatch, false);
      assert.deepEqual(summary.plannedWrites, [target, "project/generated/artifacts_registry.json", "project/generated/DOCUMENT_INDEX.md"]);
      return false;
    },
  }));
  assert.equal(cancelled.status, "CANCELLED");
  assert.deepEqual(await readFile(data.canonical), canonicalBefore);
  assert.equal(run("git", ["status", "--porcelain"], data.root), "");
  const outcome = await coordinator.apply(data.saved, data.request, "Target", "1.0", options({
    confirmMismatch: async () => { mismatchConfirmations += 1; return true; },
  }));
  assert.equal(outcome.status, "PASS");
  assert.equal(mismatchConfirmations, 0);
  assert.equal(outcome.rollback, "NOT_RUN");
  assert.deepEqual(await readFile(data.canonical), await readFile(data.session.candidatePath));
  assert.match((await readFile(data.canonical, "utf8")), /version: "1\.1"/);
  assert.deepEqual(run("git", ["diff", "--name-only"], data.root).split(/\r?\n/).sort(), [
    target, "project/generated/artifacts_registry.json", "project/generated/DOCUMENT_INDEX.md",
  ].sort());
  const review = JSON.parse(await readFile(outcome.reviewPath!, "utf8")) as Record<string, unknown>;
  assert.equal(review.final_status, "PASS");
  assert.equal((review.transaction as Record<string, unknown>).state, "COMMITTED_TO_WORKTREE");
  assert.equal(run("git", ["diff", "--cached", "--name-only"], data.root), "");
});

test("Cancel and mismatch rejection never invoke production Apply", async () => {
  const data = await fixture();
  const before = await readFile(data.canonical);
  let calls = 0;
  const runner = async (): Promise<WorkflowCommandExecution> => {
    calls += 1; throw new Error("Apply must not run");
  };
  const coordinator = new ExplicitApplyCoordinator();
  assert.equal((await coordinator.apply(data.saved, data.request, "Target", "1.0", options({
    confirm: async () => false, runner,
  }))).status, "CANCELLED");
  assert.equal((await coordinator.apply(data.saved, data.request, "Target", "1.0", options({
    confirmMismatch: async () => false, runner,
  }))).status, "CANCELLED");
  assert.equal(calls, 0);
  assert.deepEqual(await readFile(data.canonical), before);
  assert.equal(run("git", ["status", "--porcelain"], data.root), "");
});

test("missing/tampered plan, unsaved and externally modified candidate block Apply", async () => {
  const data = await fixture();
  const coordinator = new ExplicitApplyCoordinator();
  await assert.rejects(coordinator.apply(data.saved, data.request, "Target", "1.0", options({ candidateIsDirty: () => true })), hasCode("CANDIDATE_UNSAVED"));
  await writeFile(data.session.candidatePath, baseline.replace("Baseline body.", "External change."), "utf8");
  await assert.rejects(coordinator.apply(data.saved, data.request, "Target", "1.0", options()), hasCode("PLAN_STALE"));
  await writeFile(data.session.candidatePath, baseline.replace("Baseline body.", "Candidate body changed."), "utf8");
  await writeFile(data.saved.planPath, "tampered", "utf8");
  await assert.rejects(coordinator.apply(data.saved, data.request, "Target", "1.0", options()), hasCode("PLAN_STALE"));
  await rm(data.saved.planPath);
  await assert.rejects(coordinator.apply(data.saved, data.request, "Target", "1.0", options()), hasCode("PLAN_MISSING"));
  assert.equal(run("git", ["status", "--porcelain"], data.root), "");
});

test("HEAD, canonical baseline, dirty worktree and different repository block Apply", async () => {
  const dirty = await fixture();
  await writeFile(path.join(dirty.root, ".gitignore"), "TEMP/\n# dirty\n", "utf8");
  await assert.rejects(new ExplicitApplyCoordinator().apply(dirty.saved, dirty.request, "Target", "1.0", options()), hasCode("WORKTREE_DIRTY"));
  const staged = await fixture();
  await writeFile(path.join(staged.root, ".gitignore"), "TEMP/\n# staged\n", "utf8");
  run("git", ["add", ".gitignore"], staged.root);
  await assert.rejects(new ExplicitApplyCoordinator().apply(staged.saved, staged.request, "Target", "1.0", options()), hasCode("WORKTREE_DIRTY"));
  const branch = await fixture();
  run("git", ["checkout", "-b", "different-branch"], branch.root);
  await assert.rejects(new ExplicitApplyCoordinator().apply(branch.saved, branch.request, "Target", "1.0", options()), hasCode("PLAN_STALE"));
  const changed = await fixture();
  await writeFile(changed.canonical, baseline.replace("Baseline body.", "Another baseline."), "utf8");
  run("git", ["add", target], changed.root);
  run("git", ["commit", "-m", "new canonical baseline"], changed.root);
  await assert.rejects(new ExplicitApplyCoordinator().apply(changed.saved, changed.request, "Target", "1.0", options()));
  const wrongRoot = await fixture();
  await assert.rejects(new ExplicitApplyCoordinator().apply(wrongRoot.saved, changed.request, "Target", "1.0", options()), hasCode("REPOSITORY_MISMATCH"));
});

test("parallel Apply request is rejected while first confirmation is open", async () => {
  const data = await fixture();
  const coordinator = new ExplicitApplyCoordinator();
  let release!: (answer: boolean) => void;
  const pending = new Promise<boolean>((resolve) => { release = resolve; });
  const first = coordinator.apply(data.saved, data.request, "Target", "1.0", options({ confirm: () => pending }));
  await assert.rejects(coordinator.apply(data.saved, data.request, "Target", "1.0", options()), hasCode("APPLY_ALREADY_ATTEMPTED"));
  release(false);
  assert.equal((await first).status, "CANCELLED");
});

test("production FAIL reports verified and unverified rollback without retry", async () => {
  for (const rollbackVerified of [true, false]) {
    const data = await fixture();
    let applyCalls = 0;
    const reviewDigest = "a".repeat(64);
    const runner = async (_root: string, args: readonly string[]): Promise<WorkflowCommandExecution> => {
      if (args[0] === "apply") {
        applyCalls += 1;
        const reviewDir = args[5];
        assert.ok(reviewDir);
        await mkdir(reviewDir, { recursive: true });
        await writeFile(path.join(reviewDir, "review.json"), JSON.stringify({
          operation: "update",
          artifact: { artifact_id: "AET-DOC-TARGET" },
          plan_semantic_sha256: data.saved.preview.plan.plan_semantic_sha256,
          review_semantic_sha256: reviewDigest,
          final_status: "FAIL",
          transaction: { state: "ROLLED_BACK" },
          rollback: { performed: true, verified: rollbackVerified, original_hashes_restored: rollbackVerified },
        }), "utf8");
        return {
          exitCode: rollbackVerified ? 4 : 5, stdout: "",
          stderr: JSON.stringify({ diagnostics: [{ code: rollbackVerified ? "TRANSACTION_FAILED_ROLLED_BACK" : "ROLLBACK_VERIFICATION_FAILED", message: "Injected failure" }] }),
          interpreter: { command: python, prefixArguments: [], displayName: "test" },
        };
      }
      return {
        exitCode: 0, stdout: JSON.stringify({ status: "PASS", review_semantic_sha256: reviewDigest }), stderr: "",
        interpreter: { command: python, prefixArguments: [], displayName: "test" },
      };
    };
    const outcome = await new ExplicitApplyCoordinator().apply(data.saved, data.request, "Target", "1.0", options({ runner }));
    assert.equal(outcome.status, "FAIL");
    assert.equal(outcome.rollback, rollbackVerified ? "PASS" : "FAIL");
    assert.equal(applyCalls, 1);
    assert.deepEqual(await readFile(data.canonical, "utf8"), baseline);
  }
});

test("missing production review and verify-review failure never appear as success", async () => {
  for (const mode of ["missing-review", "verify-fails"]) {
    const data = await fixture();
    const runner = async (_root: string, args: readonly string[]): Promise<WorkflowCommandExecution> => {
      if (args[0] === "apply") {
        if (mode === "verify-fails") {
          const reviewDir = args[5];
          assert.ok(reviewDir);
          await mkdir(reviewDir, { recursive: true });
          await writeFile(path.join(reviewDir, "review.json"), JSON.stringify({
            operation: "update", artifact: { artifact_id: "AET-DOC-TARGET" },
            plan_semantic_sha256: data.saved.preview.plan.plan_semantic_sha256,
            review_semantic_sha256: "b".repeat(64), final_status: "PASS",
            transaction: { state: "COMMITTED_TO_WORKTREE" }, rollback: { performed: false },
          }), "utf8");
        }
        return {
          exitCode: 0, stdout: JSON.stringify({ status: "PASS" }), stderr: "",
          interpreter: { command: python, prefixArguments: [], displayName: "test" },
        };
      }
      return {
        exitCode: 3, stdout: "", stderr: "Review integrity mismatch",
        interpreter: { command: python, prefixArguments: [], displayName: "test" },
      };
    };
    const outcome = await new ExplicitApplyCoordinator().apply(data.saved, data.request, "Target", "1.0", options({ runner }));
    assert.equal(outcome.status, "VERIFY_FAILED");
    assert.ok(outcome.reviewPath);
    assert.deepEqual(await readFile(data.canonical, "utf8"), baseline);
  }
});

test("plan storage inside repository is refused", async () => {
  const data = await fixture();
  await assert.rejects(
    materializePreparedUpdate(data.saved.preview, data.root, path.join(data.root, "TEMP", "unsafe-plans")),
    hasCode("PLAN_STORAGE_UNSAFE"),
  );
});

test.after(() => {
  if (priorPython === undefined) delete process.env.AETERNA_PYTHON;
  else process.env.AETERNA_PYTHON = priorPython;
  if (priorPythonPath === undefined) delete process.env.PYTHONPATH;
  else process.env.PYTHONPATH = priorPythonPath;
});
