import path from "node:path";

import { loadManagedDocuments } from "../src/registry";
import { resolveRepositoryRoot } from "../src/repository";
import { resolveArtifact, WorkflowIntegrationError } from "../src/workflow";

const PROJECT_PLAN_ID = "AET-DOC-PROJECT-PLAN";
const PROJECT_PLAN_PATH = "project/planning/PROJECT_PLAN.md";

async function main(): Promise<void> {
  const requestedRoot = process.argv[2];
  if (!requestedRoot) {
    throw new Error("Usage: proof-smoke <aeterna-repository-root>");
  }

  const expectedRoot = path.resolve(requestedRoot);
  const repositoryRoot = await resolveRepositoryRoot([expectedRoot]);
  console.log("REPOSITORY_DETECTION = PASS");
  console.log(`REPOSITORY_ROOT = ${repositoryRoot}`);

  const loaded = await loadManagedDocuments(repositoryRoot);
  if (loaded.diagnostics.length > 0) {
    throw new Error(
      `Registry/path diagnostics were reported: ${loaded.diagnostics.join(" | ")}`,
    );
  }
  if (loaded.documents.length === 0) {
    throw new Error("Managed Markdown document list is empty.");
  }
  console.log("REGISTRY_LOAD = PASS");
  console.log(`MANAGED_MARKDOWN_DOCUMENT_COUNT = ${loaded.documents.length}`);

  const projectPlan = loaded.documents.find(
    (document) => document.artifact_id === PROJECT_PLAN_ID,
  );
  if (!projectPlan) {
    throw new Error(`${PROJECT_PLAN_ID} is not present in the managed list.`);
  }
  if (projectPlan.path !== PROJECT_PLAN_PATH) {
    throw new Error(
      `${PROJECT_PLAN_ID} path mismatch: expected ${PROJECT_PLAN_PATH}, got ${projectPlan.path}.`,
    );
  }
  console.log("PROJECT_PLAN_LISTED = YES");
  console.log("PROJECT_PLAN_SAFE_PATH = PASS");

  const resolved = await resolveArtifact(repositoryRoot, PROJECT_PLAN_ID);
  if (resolved.result.artifact_id !== PROJECT_PLAN_ID) {
    throw new Error(
      `Resolve artifact_id mismatch: ${resolved.result.artifact_id}`,
    );
  }
  if (resolved.result.path !== PROJECT_PLAN_PATH) {
    throw new Error(`Resolve path mismatch: ${resolved.result.path}`);
  }
  console.log("WORKFLOW_RESOLVE = PASS");
  console.log(`PYTHON_INTERPRETER = ${resolved.interpreter.displayName}`);
  console.log(`WORKFLOW_RESOLVE_ARTIFACT_ID = ${resolved.result.artifact_id}`);
  console.log(`WORKFLOW_RESOLVE_PATH = ${resolved.result.path}`);
  if (resolved.stderr.trim()) {
    console.log(`WORKFLOW_STDERR = ${resolved.stderr.trim()}`);
  }
  console.log("PROOF_SMOKE = PASS");
}

main().catch((error: unknown) => {
  const detail = error instanceof Error ? error.stack ?? error.message : String(error);
  console.error(`PROOF_SMOKE = FAIL\n${detail}`);
  if (error instanceof WorkflowIntegrationError && error.stderr.trim()) {
    console.error(`WORKFLOW_STDERR = ${error.stderr.trim()}`);
  }
  process.exitCode = 1;
});
