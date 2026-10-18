import assert from "node:assert/strict";
import { test } from "node:test";

import { loadMetadataAssistance, parseMetadataAssistance } from "../src/metadata_assistance";
import type { ManagedDocument } from "../src/registry";
import type { WorkflowCommandExecution } from "../src/workflow";

const document = {
  artifact_id: "AET-DOC-PROJECT-PLAN", path: "project/planning/PROJECT_PLAN.md",
  version: "6.20", kind: "document", generated: false,
} as ManagedDocument;
const metadata = {
  artifact_id: document.artifact_id, kind: "document", type: "project-plan", version: "6.20",
  lifecycle: "active", integration: "current", authority: "project-direction", generated: false,
  depends_on: ["AET-DOC-DOCUMENT-GOVERNANCE"], supersedes: [],
};
const baseline = { schema_version: "aeterna-document-update-baseline/0.1", artifact_id: document.artifact_id,
  path: document.path, metadata };
const schema = { schema_version: "aeterna-document-create-baseline/0.1", controlled_values: {
  kind: ["document"], type: ["project-plan"], lifecycle: ["active"],
  integration: ["current"], authority: ["project-direction"],
} };

test("metadata assistance uses production canonical metadata and allowed values", () => {
  const result = parseMetadataAssistance(document, baseline, schema);
  assert.deepEqual(result.fields, metadata);
  assert.deepEqual(result.allowed.type, ["project-plan"]);
  assert.match(result.rules, /protected fields/);
});

test("metadata assistance fails closed on missing fields, registry drift or incomplete schema", () => {
  assert.throws(() => parseMetadataAssistance(document, { ...baseline, metadata: { ...metadata, authority: undefined } }, schema));
  assert.throws(() => parseMetadataAssistance(document, { ...baseline, metadata: { ...metadata, version: "6.21" } }, schema));
  assert.throws(() => parseMetadataAssistance(document, baseline,
    { ...schema, controlled_values: { ...schema.controlled_values, type: undefined } }));
});

test("metadata loader invokes only read-only production inspections", async () => {
  const commands: string[][] = [];
  const runner = async (_root: string, args: readonly string[]): Promise<WorkflowCommandExecution> => {
    commands.push([...args]);
    return { exitCode: 0, stdout: JSON.stringify(args[0] === "inspect-update-baseline" ? baseline : schema),
      stderr: "", interpreter: { command: "python", prefixArguments: [], displayName: "test" } };
  };
  const result = await loadMetadataAssistance("C:\\repo", document, runner);
  assert.equal(result.artifactId, document.artifact_id);
  assert.deepEqual(commands, [
    ["inspect-update-baseline", document.artifact_id, "--repo", "C:\\repo"],
    ["inspect-create-baseline", "--repo", "C:\\repo"],
  ]);
});
