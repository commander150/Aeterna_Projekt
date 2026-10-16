import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { copyFile, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";

import { createOrOpenCandidateSession, type CandidateSession } from "../src/candidate";
import {
  UpdatePreviewError,
  createUpdateManifest,
  currentUpdateIdentity,
  inspectUpdateBaseline,
  isUpdatePlanStale,
  parseUpdateBaselineJson,
  parseUpdatePlanJson,
  prepareUpdatePreview,
  renderUpdatePreview,
  requireSavedCandidate,
} from "../src/update_plan";
import { runWorkflowCommand } from "../src/workflow";
import { writeCandidateVersion } from "../src/version_candidate";

const sourceRoot = path.resolve(__dirname, "../../../..");
const python = path.join(sourceRoot, ".venv", "Scripts", "python.exe");
const priorPython = process.env.AETERNA_PYTHON;
const priorPythonPath = process.env.PYTHONPATH;
process.env.AETERNA_PYTHON = python;
process.env.PYTHONPATH = sourceRoot;

const temporaryDirectories: string[] = [];
const targetRelative = "project/planning/TARGET.md";
const baselineMarkdown = [
  "---",
  "artifact_id: AET-DOC-TARGET",
  "kind: document",
  "type: reference",
  'version: "1.0"',
  "lifecycle: active",
  "integration: current",
  "authority: project-direction",
  "generated: false",
  "depends_on: []",
  "supersedes: []",
  "---",
  "",
  "# Target",
  "",
  "Baseline body.",
  "",
].join("\n");

afterEach(async () => {
  await Promise.all(temporaryDirectories.splice(0).map((directory) =>
    rm(directory, { recursive: true, force: true }),
  ));
});

function run(command: string, args: string[], cwd: string): string {
  const result = spawnSync(command, args, {
    cwd, encoding: "utf8", windowsHide: true,
    env: { ...process.env, PYTHONPATH: sourceRoot },
  });
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed: ${result.error?.message ?? result.stderr}`);
  }
  return result.stdout.trim();
}

function digest(bytes: Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

async function fixture(): Promise<{
  root: string;
  canonical: string;
  session: CandidateSession;
  candidate: string;
}> {
  const top = await mkdtemp(path.join(os.tmpdir(), "aeterna-e2a-test-"));
  temporaryDirectories.push(top);
  const root = path.join(top, "repo");
  const canonical = path.join(root, ...targetRelative.split("/"));
  await mkdir(path.dirname(canonical), { recursive: true });
  await writeFile(path.join(root, ".gitignore"), "TEMP/\n", "utf8");
  await writeFile(canonical, baselineMarkdown, "utf8");
  const workflowCli = path.join(root, "tools", "aeterna_document_workflow", "cli.py");
  await mkdir(path.dirname(workflowCli), { recursive: true });
  await copyFile(path.join(sourceRoot, "tools", "aeterna_document_workflow", "cli.py"), workflowCli);
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
  const session = await createOrOpenCandidateSession({
    repositoryRoot: root,
    storageRoot: path.join(top, "vscode-storage"),
    artifact: {
      artifactId: "AET-DOC-TARGET", canonicalPath: targetRelative,
      version: "1.0", kind: "document", generated: false, scope: "ACTIVE",
    },
  });
  return { root, canonical, session, candidate: session.candidatePath };
}

async function bodyChanged(candidate: string): Promise<void> {
  await writeFile(candidate, baselineMarkdown.replace("Baseline body.", "Candidate body changed."), "utf8");
}

function hasCode(code: string): (error: unknown) => boolean {
  return (error: unknown) => error instanceof UpdatePreviewError && error.code === code;
}

test("production body-only/git-only plan is deterministic, read-only and shows recommendation mismatch", async () => {
  const data = await fixture();
  await bodyChanged(data.candidate);
  const canonicalBefore = await readFile(data.canonical);
  const generatedBefore = await readFile(path.join(data.root, "project/generated/artifacts_registry.json"));
  const preview = await prepareUpdatePreview(data.root, data.session, {
    changeClass: "body-only", versionIntent: "git-only",
  });
  const plan = preview.plan;
  assert.equal(plan.schema_version, "aeterna-document-update-plan/0.1");
  assert.equal(plan.artifact_id, "AET-DOC-TARGET");
  assert.equal(preview.manifest.candidate_sha256, digest(await readFile(data.candidate)));
  assert.deepEqual(preview.manifest.metadata_delta, []);
  assert.deepEqual(preview.manifest.reference_changes, []);
  assert.equal(preview.manifest.proposed_version, null);
  assert.equal((plan.version as Record<string, unknown>).recommended_intent, "minor");
  assert.equal((plan.version as Record<string, unknown>).mismatch, true);
  assert.deepEqual((plan.expected_changes as { path: string }[]).map((item) => item.path), [targetRelative]);
  assert.match(renderUpdatePreview(preview), /Recommendation mismatch: YES/);
  const again = await prepareUpdatePreview(data.root, data.session, {
    changeClass: "body-only", versionIntent: "git-only",
  });
  assert.equal(again.plan.plan_semantic_sha256, plan.plan_semantic_sha256);
  assert.deepEqual(await readFile(data.canonical), canonicalBefore);
  assert.deepEqual(await readFile(path.join(data.root, "project/generated/artifacts_registry.json")), generatedBefore);
  assert.equal(run("git", ["status", "--porcelain"], data.root), "");
});

test("production minor plan binds candidate version, metadata delta and body change without canonical writes", async () => {
  const data = await fixture();
  await bodyChanged(data.candidate);
  const before = await readFile(data.candidate);
  const canonicalBefore = await readFile(data.canonical);
  await writeCandidateVersion(data.candidate, digest(before), "1.0", "1.1");
  assert.deepEqual(await readFile(data.canonical), canonicalBefore);
  const choice = { changeClass: "metadata+body" as const, versionIntent: "minor" as const, proposedVersion: "1.1" };
  const preview = await prepareUpdatePreview(data.root, data.session, choice);
  assert.equal(preview.manifest.change_class, "metadata+body");
  assert.equal(preview.manifest.version_intent, "minor");
  assert.equal(preview.manifest.proposed_version, "1.1");
  assert.deepEqual(preview.manifest.metadata_delta, [{ field: "version", old: "1.0", new: "1.1" }]);
  assert.equal((preview.plan.version as Record<string, unknown>).mismatch, false);
  assert.deepEqual(preview.plan.metadata_delta, preview.manifest.metadata_delta);
  assert.deepEqual((preview.plan.expected_changes as { path: string }[]).map((item) => item.path), [
    targetRelative, "project/generated/artifacts_registry.json", "project/generated/DOCUMENT_INDEX.md",
  ]);
  assert.match(renderUpdatePreview(preview), /Version change: 1\.0 -> 1\.1/);
  assert.match(renderUpdatePreview(preview), /Body changes:/);
  const second = await prepareUpdatePreview(data.root, data.session, choice);
  assert.equal(second.plan.plan_semantic_sha256, preview.plan.plan_semantic_sha256);
  assert.deepEqual(await readFile(data.canonical), canonicalBefore);
  assert.equal(run("git", ["status", "--porcelain"], data.root), "");
});

test("minor plan rejects mismatched candidate version and protected metadata", async () => {
  const data = await fixture();
  await bodyChanged(data.candidate);
  const choice = { changeClass: "metadata+body" as const, versionIntent: "minor" as const, proposedVersion: "1.1" };
  await assert.rejects(prepareUpdatePreview(data.root, data.session, choice), hasCode("CANDIDATE_VERSION_MISMATCH"));
  await writeFile(data.candidate, baselineMarkdown.replace('version: "1.0"', 'version: "1.1"')
    .replace("authority: project-direction", "authority: technical-contract")
    .replace("Baseline body.", "Changed."), "utf8");
  await assert.rejects(prepareUpdatePreview(data.root, data.session, choice), hasCode("PROTECTED_FIELD_CHANGE"));
});

test("unchanged candidate and unsupported choice are rejected", async () => {
  const data = await fixture();
  await assert.rejects(
    prepareUpdatePreview(data.root, data.session, { changeClass: "body-only", versionIntent: "git-only" }),
    hasCode("CHANGE_CLASS_MISMATCH"),
  );
  const { baseline } = await inspectUpdateBaseline(data.root, "AET-DOC-TARGET");
  assert.throws(
    () => createUpdateManifest(data.session, baseline, "0".repeat(64), {
      changeClass: "metadata-only", versionIntent: "git-only",
    } as never),
    hasCode("UNSUPPORTED_CHOICE"),
  );
});

test("front matter and protected metadata changes are rejected by production planner", async () => {
  const data = await fixture();
  await writeFile(data.candidate, baselineMarkdown.replace("authority: project-direction", "authority: technical-contract").replace("Baseline body.", "Changed."), "utf8");
  await assert.rejects(
    prepareUpdatePreview(data.root, data.session, { changeClass: "body-only", versionIntent: "git-only" }),
    hasCode("PROTECTED_FIELD_CHANGE"),
  );
  await writeFile(data.candidate, baselineMarkdown.replace('version: "1.0"', 'version: "1.1"').replace("Baseline body.", "Changed."), "utf8");
  await assert.rejects(
    prepareUpdatePreview(data.root, data.session, { changeClass: "body-only", versionIntent: "git-only" }),
    hasCode("VERSION_INTENT_CONFLICT"),
  );
});

test("stale HEAD, baseline SHA, fingerprint and candidate SHA are rejected", async () => {
  const data = await fixture();
  await bodyChanged(data.candidate);
  const { baseline } = await inspectUpdateBaseline(data.root, "AET-DOC-TARGET");
  const manifest = createUpdateManifest(data.session, baseline, digest(await readFile(data.candidate)), {
    changeClass: "body-only", versionIntent: "git-only",
  });
  const cases: [string, Record<string, unknown>][] = [
    ["EXPECTED_HEAD_MISMATCH", { expected_head: "0".repeat(40) }],
    ["BASELINE_HASH_MISMATCH", { baseline_sha256: "0".repeat(64) }],
    ["METADATA_FINGERPRINT_MISMATCH", { metadata_fingerprint: "0".repeat(64) }],
    ["CANDIDATE_HASH_MISMATCH", { candidate_sha256: "0".repeat(64) }],
  ];
  for (const [code, override] of cases) {
    const manifestPath = path.join(path.dirname(data.candidate), `${code}.json`);
    await writeFile(manifestPath, JSON.stringify({ ...manifest, ...override }), "utf8");
    const result = await runWorkflowCommand(data.root, ["plan-update", "--manifest", manifestPath, "--repo", data.root]);
    assert.notEqual(result.exitCode, 0);
    assert.equal((JSON.parse(result.stderr) as { diagnostics: { code: string }[] }).diagnostics[0]?.code, code);
  }
});

test("dirty worktree and staging are blocked by production preflight", async () => {
  const dirty = await fixture();
  await bodyChanged(dirty.candidate);
  await writeFile(path.join(dirty.root, ".gitignore"), "TEMP/\n# dirty\n", "utf8");
  await assert.rejects(
    prepareUpdatePreview(dirty.root, dirty.session, { changeClass: "body-only", versionIntent: "git-only" }),
    hasCode("WORKTREE_DIRTY"),
  );
  const staged = await fixture();
  await bodyChanged(staged.candidate);
  await writeFile(path.join(staged.root, ".gitignore"), "TEMP/\n# staged\n", "utf8");
  run("git", ["add", ".gitignore"], staged.root);
  await assert.rejects(
    prepareUpdatePreview(staged.root, staged.session, { changeClass: "body-only", versionIntent: "git-only" }),
    hasCode("STAGING_NOT_EMPTY"),
  );
});

test("unsaved buffer, malformed CLI JSON and changed candidate invalidate preview", async () => {
  assert.throws(() => requireSavedCandidate("OPEN_DIRTY"), hasCode("CANDIDATE_UNSAVED"));
  assert.doesNotThrow(() => requireSavedCandidate("CLOSED"));
  assert.throws(() => parseUpdateBaselineJson("not-json"), hasCode("INVALID_JSON"));
  const data = await fixture();
  await bodyChanged(data.candidate);
  const preview = await prepareUpdatePreview(data.root, data.session, {
    changeClass: "body-only", versionIntent: "git-only",
  });
  assert.throws(() => parseUpdatePlanJson("{broken", preview.manifest), hasCode("INVALID_JSON"));
  await writeFile(data.candidate, baselineMarkdown.replace("Baseline body.", "Another edit."), "utf8");
  assert.equal(isUpdatePlanStale(preview.identity, await currentUpdateIdentity(data.root, data.session)), true);
});

test("E1 candidate session remains reusable after E2A preview", async () => {
  const data = await fixture();
  await bodyChanged(data.candidate);
  await prepareUpdatePreview(data.root, data.session, { changeClass: "body-only", versionIntent: "git-only" });
  const reopened = await createOrOpenCandidateSession({
    repositoryRoot: data.root,
    storageRoot: path.join(path.dirname(data.root), "vscode-storage"),
    artifact: { artifactId: "AET-DOC-TARGET", canonicalPath: targetRelative, version: "1.0", kind: "document", generated: false, scope: "ACTIVE" },
  });
  assert.equal(reopened.disposition, "REUSED");
  assert.match((await readFile(reopened.candidatePath, "utf8")), /Candidate body changed/);
});

test.after(() => {
  if (priorPython === undefined) delete process.env.AETERNA_PYTHON;
  else process.env.AETERNA_PYTHON = priorPython;
  if (priorPythonPath === undefined) delete process.env.PYTHONPATH;
  else process.env.PYTHONPATH = priorPythonPath;
});
