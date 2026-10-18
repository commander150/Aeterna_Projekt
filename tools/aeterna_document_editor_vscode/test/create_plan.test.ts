import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { copyFile, link, mkdir, mkdtemp, readFile, readdir, rm, symlink, unlink, writeFile } from "node:fs/promises";
import path from "node:path";
import { afterEach, test } from "node:test";

import {
  CreateCandidateError, createOrOpenCreateSession, loadCreateSession,
  renderCreateCandidate, type CreateInput,
} from "../src/create_candidate";
import {
  CreatePlanError, inspectCreateBaseline, prepareCreatePreview, renderCreatePreview,
} from "../src/create_plan";
import { CreateApplyCoordinator, CreateApplyError } from "../src/apply_create";

const sourceRoot = path.resolve(__dirname, "../../../..");
const e3aTestRoot = path.join(path.dirname(sourceRoot), "Aeterna_Local", "tests", "e3a-create");
const python = path.join(sourceRoot, ".venv", "Scripts", "python.exe");
process.env.AETERNA_PYTHON = python;
process.env.PYTHONPATH = sourceRoot;
const temporaryDirectories: string[] = [];

const input: CreateInput = {
  artifactId: "AET-DOC-NEW-REVIEW", targetPath: "project/planning/NEW_REVIEW.md",
  type: "specification", authority: "technical-contract", dependencies: ["AET-DOC-TARGET"],
  version: "0.1", integration: "current", title: "New Review", initialContent: "Initial body.",
};

afterEach(async () => {
  await Promise.all(temporaryDirectories.splice(0).map((directory) => {
    const relative = path.relative(e3aTestRoot, path.resolve(directory));
    if (!relative.startsWith("fixture-") || relative.includes(path.sep) || path.isAbsolute(relative)) {
      throw new Error(`Refusing to remove a test directory outside ${e3aTestRoot}`);
    }
    return rm(directory, { recursive: true, force: true });
  }));
});

function run(command: string, args: string[], cwd: string): string {
  const result = spawnSync(command, args, { cwd, encoding: "utf8", windowsHide: true, env: { ...process.env, PYTHONPATH: sourceRoot } });
  if (result.status !== 0) throw new Error(`${command}: ${result.error?.message ?? result.stderr}`);
  return result.stdout.trim();
}

async function fixture(): Promise<{ top: string; root: string; storage: string; head: string }> {
  await mkdir(e3aTestRoot, { recursive: true });
  const top = await mkdtemp(path.join(e3aTestRoot, "fixture-"));
  temporaryDirectories.push(top);
  const root = path.join(top, "repo");
  const storage = path.join(top, "Aeterna_Local", "document_editor", "create");
  const canonical = path.join(root, "project", "planning", "TARGET.md");
  await mkdir(path.dirname(canonical), { recursive: true });
  await writeFile(path.join(root, ".gitignore"), "TEMP/\n");
  await writeFile(canonical, [
    "---", "artifact_id: AET-DOC-TARGET", "kind: document", "type: reference", 'version: "1.0"',
    "lifecycle: active", "integration: current", "authority: reference", "generated: false",
    "depends_on: []", "supersedes: []", "---", "", "# Target", "", "Baseline body.", "",
  ].join("\n"));
  const cli = path.join(root, "tools", "aeterna_document_workflow", "cli.py");
  await mkdir(path.dirname(cli), { recursive: true });
  await copyFile(path.join(sourceRoot, "tools", "aeterna_document_workflow", "cli.py"), cli);
  const generator = [
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
  run(python, ["-c", generator], root);
  run("git", ["init", "-b", "main"], root);
  run("git", ["config", "user.email", "fixture@example.invalid"], root);
  run("git", ["config", "user.name", "Fixture"], root);
  run("git", ["add", "."], root);
  run("git", ["commit", "-m", "fixture baseline"], root);
  return { top, root, storage, head: run("git", ["rev-parse", "HEAD"], root) };
}

test("new CREATE candidate is UTF-8/LF, external, reopenable and never overwrites edits", async () => {
  const data = await fixture();
  const created = await createOrOpenCreateSession(data.root, data.storage, "main", data.head, input);
  assert.equal(created.disposition, "CREATED");
  assert.ok(created.session.candidatePath.startsWith(data.storage));
  const bytes = await readFile(created.session.candidatePath);
  assert.deepEqual(bytes, renderCreateCandidate(input));
  assert.equal(bytes.includes(Buffer.from("\r")), false);
  assert.equal(bytes.subarray(0, 3).equals(Buffer.from([0xef, 0xbb, 0xbf])), false);
  assert.match(bytes.toString("utf8"), /depends_on: \["AET-DOC-TARGET"\]/);
  await writeFile(created.session.candidatePath, Buffer.concat([bytes, Buffer.from("Human edit.\n")]));
  const loaded = await loadCreateSession(data.root, data.storage, input.artifactId, "main", data.head);
  assert.equal(loaded?.candidatePath, created.session.candidatePath);
  const reopened = await createOrOpenCreateSession(data.root, data.storage, "main", data.head, input);
  assert.equal(reopened.disposition, "REUSED");
  assert.match((await readFile(reopened.session.candidatePath)).toString("utf8"), /Human edit/);
  await assert.rejects(() => loadCreateSession(data.root, data.storage, input.artifactId, "main", "0".repeat(40)),
    (error: unknown) => error instanceof CreateCandidateError && error.code === "SESSION_DRIFT");
  assert.equal(run("git", ["status", "--short"], data.root), "");
});

test("CREATE storage rejects repository, arbitrary external roots, traversal and junction redirection", async () => {
  const data = await fixture();
  const repositoryStorage = path.join(data.root, "TEMP", "storage");
  await assert.rejects(() => createOrOpenCreateSession(data.root, repositoryStorage, "main", data.head, input),
    (error: unknown) => error instanceof CreateCandidateError && error.code === "STORAGE_INSIDE_REPOSITORY");
  await assert.rejects(() => createOrOpenCreateSession(data.root, path.join(data.top, "other-storage"), "main", data.head, input),
    (error: unknown) => error instanceof CreateCandidateError && error.code === "UNAUTHORIZED_STORAGE");
  await assert.rejects(() => createOrOpenCreateSession(data.root,
    `${data.top}${path.sep}Aeterna_Local${path.sep}..${path.sep}Aeterna_Local${path.sep}document_editor${path.sep}create`, "main", data.head, input),
    (error: unknown) => error instanceof CreateCandidateError && error.code === "UNAUTHORIZED_STORAGE");
  await assert.rejects(() => readdir(repositoryStorage), { code: "ENOENT" });
  const redirected = path.join(data.top, "redirected");
  await mkdir(redirected);
  await symlink(redirected, path.join(data.top, "Aeterna_Local"), "junction");
  await assert.rejects(() => createOrOpenCreateSession(data.root, data.storage, "main", data.head, input),
    (error: unknown) => error instanceof CreateCandidateError && error.code === "UNSAFE_STORAGE");
});

test("existing CREATE candidate hard-linked to canonical content is refused", async () => {
  const data = await fixture();
  const session = (await createOrOpenCreateSession(data.root, data.storage, "main", data.head, input)).session;
  const canonical = path.join(data.root, "project", "planning", "TARGET.md");
  await unlink(session.candidatePath);
  await link(canonical, session.candidatePath);
  await assert.rejects(() => loadCreateSession(data.root, data.storage, input.artifactId, "main", data.head),
    (error: unknown) => error instanceof CreateCandidateError && error.code === "SESSION_UNSAFE");
});

test("unsaved CREATE candidate blocks planning before any plan or manifest is materialized", async () => {
  const data = await fixture();
  const session = (await createOrOpenCreateSession(data.root, data.storage, "main", data.head, input)).session;
  const before = await readdir(path.dirname(session.candidatePath));
  await assert.rejects(() => prepareCreatePreview(data.root, session, () => true),
    (error: unknown) => error instanceof CreatePlanError && error.code === "CANDIDATE_UNSAVED");
  assert.deepEqual(await readdir(path.dirname(session.candidatePath)), before);
  assert.equal(run("git", ["status", "--short"], data.root), "");
});

test("production plan-create accepts external candidate, is deterministic and leaves isolated repository clean", async () => {
  const data = await fixture();
  const baseline = await inspectCreateBaseline(data.root);
  assert.deepEqual(baseline.existing_artifact_ids, ["AET-DOC-TARGET"]);
  assert.ok(baseline.controlled_values.type.includes("specification"));
  assert.ok(baseline.controlled_values.authority.includes("technical-contract"));
  const session = (await createOrOpenCreateSession(data.root, data.storage, "main", data.head, input)).session;
  const canonicalBefore = await readFile(path.join(data.root, "project", "planning", "TARGET.md"));
  const first = await prepareCreatePreview(data.root, session, () => false);
  const second = await prepareCreatePreview(data.root, session, () => false);
  assert.equal(first.plan.plan_semantic_sha256, second.plan.plan_semantic_sha256);
  assert.equal(first.plan.operation, "create");
  assert.equal((first.plan.authority as { risk: string }).risk, "HIGH");
  assert.deepEqual((first.plan.expected_changes as { path: string }[]).map((entry) => entry.path), [
    input.targetPath, "project/generated/artifacts_registry.json", "project/generated/DOCUMENT_INDEX.md",
  ]);
  assert.match(renderCreatePreview(first), /Apply requires separate approval/);
  assert.deepEqual(await readFile(path.join(data.root, "project", "planning", "TARGET.md")), canonicalBefore);
  assert.equal(run("git", ["status", "--short"], data.root), "");
});

test("CREATE plan fails closed on edited metadata and dirty repository", async () => {
  const data = await fixture();
  const session = (await createOrOpenCreateSession(data.root, data.storage, "main", data.head, input)).session;
  const bytes = await readFile(session.candidatePath);
  await writeFile(session.candidatePath, bytes.toString("utf8").replace('version: "0.1"', 'version: "0.2"'));
  await assert.rejects(() => prepareCreatePreview(data.root, session, () => false), (error: unknown) => error instanceof CreatePlanError);
  await writeFile(session.candidatePath, bytes);
  await writeFile(path.join(data.root, "project", "planning", "TARGET.md"), "dirty\n");
  await assert.rejects(() => prepareCreatePreview(data.root, session, () => false),
    (error: unknown) => error instanceof CreatePlanError && error.code === "BASELINE_BLOCKED");
});

test("CREATE plan rejects duplicate identity, missing dependency, target collision and stale HEAD", async () => {
  for (const [name, draft, code] of [
    ["duplicate", { ...input, artifactId: "AET-DOC-TARGET", dependencies: [] }, "CREATE_ARTIFACT_ID_COLLISION"],
    ["missing-dependency", { ...input, dependencies: ["AET-DOC-UNKNOWN"] }, "DOC_DEPENDENCY_MISSING"],
    ["target-collision", { ...input, targetPath: "project/planning/TARGET.md" }, "CREATE_TARGET_NOT_ABSENT"],
  ] as const) {
    const data = await fixture();
    const session = (await createOrOpenCreateSession(data.root, data.storage, "main", data.head, draft)).session;
    await assert.rejects(() => prepareCreatePreview(data.root, session, () => false),
      (error: unknown) => error instanceof CreatePlanError && error.code === code, name);
    assert.equal(run("git", ["status", "--short"], data.root), "");
  }
  const data = await fixture();
  const session = (await createOrOpenCreateSession(data.root, data.storage, "main", data.head, input)).session;
  run("git", ["commit", "--allow-empty", "-m", "advance head"], data.root);
  await assert.rejects(() => prepareCreatePreview(data.root, session, () => false),
    (error: unknown) => error instanceof CreatePlanError && error.code === "BASELINE_DRIFT");
});

test("GUI CREATE Apply uses the immutable external plan, production review and verify-review", async () => {
  const data = await fixture();
  const session = (await createOrOpenCreateSession(data.root, data.storage, "main", data.head, input)).session;
  const preview = await prepareCreatePreview(data.root, session, () => false);
  const candidateBefore = await readFile(session.candidatePath);
  const baselineBefore = await readFile(path.join(data.root, "project", "planning", "TARGET.md"));
  const approvals: string[] = [];
  const coordinator = new CreateApplyCoordinator();
  const result = await coordinator.apply(data.root, session, preview, {
    candidateIsDirty: () => false,
    confirmReview: async (summary) => {
      approvals.push("review");
      assert.equal(summary.artifactId, input.artifactId);
      assert.equal(summary.targetPath, input.targetPath);
      assert.equal(summary.authority, input.authority);
      assert.equal(summary.authorityRisk, "HIGH");
      assert.equal(summary.initialVersion, "0.1");
      assert.equal(summary.candidateSha256, preview.candidateSha256);
      assert.equal(summary.planSemanticSha256, preview.plan.plan_semantic_sha256);
      assert.deepEqual(summary.plannedWrites, [input.targetPath, "project/generated/artifacts_registry.json", "project/generated/DOCUMENT_INDEX.md"]);
      assert.match(summary.dependencyImpact, /AET-DOC-TARGET/);
      return true;
    },
    confirmFinal: async () => { approvals.push("final"); return true; },
  });
  assert.deepEqual(approvals, ["review", "final"]);
  assert.equal(result.status, "PASS", result.message);
  assert.equal(typeof result.reviewPath, "string");
  assert.deepEqual(await readFile(path.join(data.root, input.targetPath)), candidateBefore);
  assert.deepEqual(await readFile(session.candidatePath), candidateBefore);
  assert.deepEqual(await readFile(path.join(data.root, "project", "planning", "TARGET.md")), baselineBefore);
  assert.equal(run("git", ["diff", "--cached", "--name-only"], data.root), "");
  assert.deepEqual(run("git", ["status", "--short"], data.root).split(/\r?\n/).sort(), [
    "M project/generated/DOCUMENT_INDEX.md", " M project/generated/artifacts_registry.json",
    "?? project/planning/NEW_REVIEW.md",
  ].sort());
  await assert.rejects(() => coordinator.apply(data.root, session, preview, {
    candidateIsDirty: () => false, confirmReview: async () => true, confirmFinal: async () => true,
  }), (error: unknown) => error instanceof CreateApplyError && error.code === "APPLY_ALREADY_ATTEMPTED");
});

test("GUI CREATE Apply cancels at either approval without touching canonical files", async () => {
  for (const cancelAt of ["review", "final"]) {
    const data = await fixture();
    const session = (await createOrOpenCreateSession(data.root, data.storage, "main", data.head, input)).session;
    const preview = await prepareCreatePreview(data.root, session, () => false);
    const candidateBefore = await readFile(session.candidatePath);
    let finalCalled = false;
    const result = await new CreateApplyCoordinator().apply(data.root, session, preview, {
      candidateIsDirty: () => false,
      confirmReview: async () => cancelAt !== "review",
      confirmFinal: async () => { finalCalled = true; return cancelAt !== "final"; },
    });
    assert.equal(result.status, "CANCELLED");
    assert.equal(finalCalled, cancelAt === "final");
    assert.equal(run("git", ["status", "--short"], data.root), "");
    assert.deepEqual(await readFile(session.candidatePath), candidateBefore);
    await assert.rejects(() => readFile(path.join(data.root, input.targetPath)), { code: "ENOENT" });
  }
});

test("GUI CREATE Apply blocks unsaved, candidate, immutable plan, HEAD and worktree drift", async () => {
  for (const drift of ["unsaved", "candidate", "plan", "head", "worktree"]) {
    const data = await fixture();
    const session = (await createOrOpenCreateSession(data.root, data.storage, "main", data.head, input)).session;
    const preview = await prepareCreatePreview(data.root, session, () => false);
    if (drift === "candidate") await writeFile(session.candidatePath, Buffer.concat([await readFile(session.candidatePath), Buffer.from("Changed.\n")]));
    if (drift === "plan") await writeFile(preview.planPath, "{}\n");
    if (drift === "head") run("git", ["commit", "--allow-empty", "-m", "advance head"], data.root);
    if (drift === "worktree") await writeFile(path.join(data.root, "project", "planning", "TARGET.md"), "dirty\n");
    let approved = false;
    await assert.rejects(() => new CreateApplyCoordinator().apply(data.root, session, preview, {
      candidateIsDirty: () => drift === "unsaved",
      confirmReview: async () => { approved = true; return true; },
      confirmFinal: async () => true,
    }));
    assert.equal(approved, false, drift);
    await assert.rejects(() => readFile(path.join(data.root, input.targetPath)), { code: "ENOENT" });
  }
});

test("GUI CREATE Apply rechecks candidate after review approval before final approval", async () => {
  const data = await fixture();
  const session = (await createOrOpenCreateSession(data.root, data.storage, "main", data.head, input)).session;
  const preview = await prepareCreatePreview(data.root, session, () => false);
  let finalCalled = false;
  await assert.rejects(() => new CreateApplyCoordinator().apply(data.root, session, preview, {
    candidateIsDirty: () => false,
    confirmReview: async () => {
      await writeFile(session.candidatePath, Buffer.concat([await readFile(session.candidatePath), Buffer.from("Human edit during review.\n")]));
      return true;
    },
    confirmFinal: async () => { finalCalled = true; return true; },
  }), (error: unknown) => error instanceof CreateApplyError && error.code === "CANDIDATE_DRIFT");
  assert.equal(finalCalled, false);
  assert.match((await readFile(session.candidatePath)).toString("utf8"), /Human edit during review/);
  assert.equal(run("git", ["status", "--short"], data.root), "");
  await assert.rejects(() => readFile(path.join(data.root, input.targetPath)), { code: "ENOENT" });
});
