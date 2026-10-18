import type { ManagedDocument } from "./registry";
import { runWorkflowCommand, type WorkflowCommandExecution } from "./workflow";

const FIELDS = ["artifact_id", "kind", "type", "version", "lifecycle", "integration", "authority", "generated", "depends_on", "supersedes"] as const;
const CONTROLLED = ["kind", "type", "lifecycle", "integration", "authority"] as const;

export interface MetadataAssistance {
  readonly artifactId: string;
  readonly fields: Record<string, string | boolean | readonly string[]>;
  readonly allowed: Record<string, readonly string[]>;
  readonly rules: string;
}

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function parseOutput(result: WorkflowCommandExecution, label: string): Record<string, unknown> {
  if (result.exitCode !== 0) throw new Error(`${label} failed: ${result.stderr.trim()}`);
  let parsed: unknown;
  try { parsed = JSON.parse(result.stdout) as unknown; }
  catch { throw new Error(`${label} returned invalid JSON.`); }
  if (!record(parsed)) throw new Error(`${label} returned no object.`);
  return parsed;
}

export function parseMetadataAssistance(
  document: ManagedDocument, baseline: Record<string, unknown>, schema: Record<string, unknown>,
): MetadataAssistance {
  if (baseline.schema_version !== "aeterna-document-update-baseline/0.1" ||
      baseline.artifact_id !== document.artifact_id || baseline.path !== document.path ||
      !record(baseline.metadata) || !record(schema.controlled_values) ||
      schema.schema_version !== "aeterna-document-create-baseline/0.1") {
    throw new Error("Production metadata identity or schema does not match the selected document.");
  }
  const source = baseline.metadata;
  const fields: Record<string, string | boolean | readonly string[]> = {};
  for (const key of FIELDS) {
    const value = source[key];
    if (key === "generated") {
      if (typeof value !== "boolean") throw new Error(`Invalid canonical metadata: ${key}.`);
    } else if (key === "depends_on" || key === "supersedes") {
      if (!Array.isArray(value) || !value.every((item) => typeof item === "string")) {
        throw new Error(`Invalid canonical metadata: ${key}.`);
      }
    } else if (typeof value !== "string") {
      throw new Error(`Invalid canonical metadata: ${key}.`);
    }
    fields[key] = value as string | boolean | readonly string[];
  }
  if (fields.artifact_id !== document.artifact_id || fields.version !== document.version ||
      fields.kind !== document.kind || fields.generated !== document.generated) {
    throw new Error("Canonical metadata differs from the registry; refresh and inspect the repository.");
  }
  const allowed: Record<string, readonly string[]> = {};
  for (const key of CONTROLLED) {
    const values = schema.controlled_values[key];
    if (!Array.isArray(values) || !values.every((item) => typeof item === "string")) {
      throw new Error(`Production schema did not provide allowed ${key} values.`);
    }
    allowed[key] = values as string[];
  }
  return {
    artifactId: document.artifact_id, fields, allowed,
    rules: "UPDATE protected fields: artifact_id, canonical path, authority, kind, type, generated, supersedes. Other metadata changes require an explicit governed delta; saving a candidate never applies it. See DOCUMENT_UPDATE_WORKFLOW §9.",
  };
}

export async function loadMetadataAssistance(repositoryRoot: string, document: ManagedDocument,
  runner = runWorkflowCommand): Promise<MetadataAssistance> {
  const [baseline, schema] = await Promise.all([
    runner(repositoryRoot, ["inspect-update-baseline", document.artifact_id, "--repo", repositoryRoot]),
    runner(repositoryRoot, ["inspect-create-baseline", "--repo", repositoryRoot]),
  ]);
  return parseMetadataAssistance(document, parseOutput(baseline, "Canonical metadata inspection"),
    parseOutput(schema, "Production metadata schema inspection"));
}
