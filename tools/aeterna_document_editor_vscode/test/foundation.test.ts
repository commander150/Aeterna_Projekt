import assert from "node:assert/strict";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";

import {
  parseRegistryText,
  RegistryValidationError,
  resolveCanonicalMarkdownPath,
  selectManagedMarkdownArtifacts,
} from "../src/registry";
import {
  findRepositoryCandidates,
  RepositoryDiscoveryError,
  resolveRepositoryRoot,
} from "../src/repository";
import {
  buildResolveArguments,
  parseResolveJson,
  WorkflowIntegrationError,
} from "../src/workflow";

const temporaryDirectories: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporaryDirectories.splice(0).map((directory) =>
      rm(directory, { recursive: true, force: true }),
    ),
  );
});

async function temporaryDirectory(): Promise<string> {
  const directory = await mkdtemp(path.join(os.tmpdir(), "aeterna-vscode-"));
  temporaryDirectories.push(directory);
  return directory;
}

async function createRepository(root: string): Promise<void> {
  await mkdir(path.join(root, "project", "generated"), { recursive: true });
  await mkdir(path.join(root, "tools", "aeterna_document_workflow"), {
    recursive: true,
  });
  await writeFile(
    path.join(root, "project", "generated", "artifacts_registry.json"),
    '{"registry_schema_version":"0.1","artifacts":[]}',
    "utf8",
  );
  await writeFile(
    path.join(root, "tools", "aeterna_document_workflow", "cli.py"),
    "# sentinel\n",
    "utf8",
  );
}

function validRegistryText(): string {
  return JSON.stringify({
    registry_schema_version: "0.1",
    artifacts: [
      {
        artifact_id: "AET-DOC-PROJECT-PLAN",
        title: "Project Plan",
        kind: "document",
        version: "6.18",
        generated: false,
        scope: "ACTIVE",
        path: "project/planning/PROJECT_PLAN.md",
      },
      {
        artifact_id: "AET-DOC-GENERATED",
        title: "Generated",
        kind: "document",
        version: "1.0",
        generated: true,
        scope: "ACTIVE",
        path: "project/generated/GENERATED.md",
      },
      {
        artifact_id: "AET-DATA-NOT-DOCUMENT",
        title: "Data",
        kind: "dataset",
        version: "1.0",
        generated: false,
        scope: "ACTIVE",
        path: "data/example.md",
      },
    ],
  });
}

test("valid registry parsing and managed Markdown filtering", () => {
  const registry = parseRegistryText(validRegistryText());
  assert.equal(registry.registry_schema_version, "0.1");
  assert.equal(registry.artifacts.length, 3);
  assert.deepEqual(
    selectManagedMarkdownArtifacts(registry).map(
      (artifact) => artifact.artifact_id,
    ),
    ["AET-DOC-PROJECT-PLAN"],
  );
});

test("malformed registry is rejected", () => {
  assert.throws(
    () => parseRegistryText('{"registry_schema_version":"0.1"}'),
    (error: unknown) =>
      error instanceof RegistryValidationError &&
      error.message.includes("artifacts"),
  );
  assert.throws(
    () =>
      parseRegistryText(
        '{"registry_schema_version":"0.1","artifacts":[{"artifact_id":7}]}',
      ),
    RegistryValidationError,
  );
  assert.throws(
    () =>
      parseRegistryText(
        '{"registry_schema_version":"9.9","artifacts":[]}',
      ),
    (error: unknown) =>
      error instanceof RegistryValidationError &&
      error.message.includes("registry_schema_version"),
  );
});

test("absolute and traversal canonical paths are rejected", async () => {
  await assert.rejects(
    resolveCanonicalMarkdownPath(".", "C:\\outside\\file.md"),
    RegistryValidationError,
  );
  await assert.rejects(
    resolveCanonicalMarkdownPath(".", "../outside.md"),
    RegistryValidationError,
  );
  await assert.rejects(
    resolveCanonicalMarkdownPath(".", "/outside.md"),
    RegistryValidationError,
  );
});

test("safe canonical path resolves to an existing repository file", async () => {
  const root = await temporaryDirectory();
  const relative = "project/planning/PROJECT_PLAN.md";
  const target = path.join(root, ...relative.split("/"));
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(target, "# Project Plan\n", "utf8");
  assert.equal(await resolveCanonicalMarkdownPath(root, relative), target);
});

test("repository candidate detection finds one valid workspace root", async () => {
  const root = await temporaryDirectory();
  const unrelated = await temporaryDirectory();
  await createRepository(root);
  assert.deepEqual(await findRepositoryCandidates([unrelated, root]), [root]);
  assert.equal(await resolveRepositoryRoot([root]), root);
});

test("zero repository candidates produces a clear error", async () => {
  const root = await temporaryDirectory();
  await assert.rejects(
    resolveRepositoryRoot([root]),
    (error: unknown) =>
      error instanceof RepositoryDiscoveryError &&
      error.code === "NO_CANDIDATE",
  );
});

test("multiple repository candidates are rejected without guessing", async () => {
  const first = await temporaryDirectory();
  const second = await temporaryDirectory();
  await createRepository(first);
  await createRepository(second);
  await assert.rejects(
    resolveRepositoryRoot([first, second]),
    (error: unknown) =>
      error instanceof RepositoryDiscoveryError &&
      error.code === "MULTIPLE_CANDIDATES" &&
      error.candidates.length === 2,
  );
});

test("resolve command construction uses an argument array", () => {
  const args = buildResolveArguments(
    { command: "py", prefixArguments: ["-3"], displayName: "py -3" },
    "AET-DOC-PROJECT-PLAN",
    "C:\\repo with spaces",
  );
  assert.deepEqual(args, [
    "-3",
    "-m",
    "tools.aeterna_document_workflow.cli",
    "resolve",
    "AET-DOC-PROJECT-PLAN",
    "--repo",
    "C:\\repo with spaces",
    "--json",
  ]);
});

test("resolve JSON parsing validates required fields", () => {
  assert.deepEqual(
    parseResolveJson(
      '{"artifact_id":"AET-DOC-PROJECT-PLAN","path":"project/planning/PROJECT_PLAN.md"}',
    ),
    {
      artifact_id: "AET-DOC-PROJECT-PLAN",
      path: "project/planning/PROJECT_PLAN.md",
    },
  );
  assert.throws(
    () => parseResolveJson("not-json"),
    (error: unknown) =>
      error instanceof WorkflowIntegrationError && error.code === "INVALID_JSON",
  );
});
