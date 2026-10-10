import { readFile, realpath, stat } from "node:fs/promises";
import path from "node:path";

export const REGISTRY_RELATIVE_PATH =
  "project/generated/artifacts_registry.json";

export interface RegistryArtifact {
  readonly artifact_id: string;
  readonly title: string;
  readonly kind: string;
  readonly version: string;
  readonly generated: boolean;
  readonly scope: string;
  readonly path: string;
}

export interface ArtifactRegistry {
  readonly registry_schema_version: string;
  readonly artifacts: readonly RegistryArtifact[];
}

export interface ManagedDocument extends RegistryArtifact {
  readonly absolutePath: string;
}

export interface RegistryLoadResult {
  readonly documents: readonly ManagedDocument[];
  readonly diagnostics: readonly string[];
}

export class RegistryValidationError extends Error {
  public constructor(message: string) {
    super(message);
    this.name = "RegistryValidationError";
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function requireString(
  record: Record<string, unknown>,
  field: string,
  context: string,
): string {
  const value = record[field];
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new RegistryValidationError(
      `${context}.${field} must be a non-empty string.`,
    );
  }
  return value;
}

function parseArtifact(value: unknown, index: number): RegistryArtifact {
  const context = `artifacts[${index}]`;
  if (!isRecord(value)) {
    throw new RegistryValidationError(`${context} must be an object.`);
  }
  if (typeof value.generated !== "boolean") {
    throw new RegistryValidationError(`${context}.generated must be boolean.`);
  }
  return {
    artifact_id: requireString(value, "artifact_id", context),
    title: requireString(value, "title", context),
    kind: requireString(value, "kind", context),
    version: requireString(value, "version", context),
    generated: value.generated,
    scope: requireString(value, "scope", context),
    path: requireString(value, "path", context),
  };
}

export function parseRegistryText(text: string): ArtifactRegistry {
  let value: unknown;
  try {
    value = JSON.parse(text) as unknown;
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new RegistryValidationError(`Registry JSON is invalid: ${detail}`);
  }
  if (!isRecord(value)) {
    throw new RegistryValidationError("Registry root must be an object.");
  }
  const schemaVersion = requireString(
    value,
    "registry_schema_version",
    "registry",
  );
  if (schemaVersion !== "0.1") {
    throw new RegistryValidationError(
      `Unsupported registry_schema_version: ${schemaVersion}`,
    );
  }
  if (!Array.isArray(value.artifacts)) {
    throw new RegistryValidationError("registry.artifacts must be an array.");
  }
  return {
    registry_schema_version: schemaVersion,
    artifacts: value.artifacts.map(parseArtifact),
  };
}

export function selectManagedMarkdownArtifacts(
  registry: ArtifactRegistry,
): RegistryArtifact[] {
  return registry.artifacts.filter(
    (artifact) =>
      artifact.kind === "document" &&
      artifact.generated === false &&
      artifact.scope === "ACTIVE" &&
      artifact.path.toLocaleLowerCase("en-US").endsWith(".md"),
  );
}

function isWithinRoot(root: string, candidate: string): boolean {
  const relative = path.relative(root, candidate);
  return (
    relative === "" ||
    (relative !== ".." &&
      !relative.startsWith(`..${path.sep}`) &&
      !path.isAbsolute(relative))
  );
}

export async function resolveCanonicalMarkdownPath(
  repositoryRoot: string,
  canonicalPath: string,
): Promise<string> {
  if (
    canonicalPath.includes("\\") ||
    path.posix.isAbsolute(canonicalPath) ||
    path.win32.isAbsolute(canonicalPath)
  ) {
    throw new RegistryValidationError(
      `Canonical path must be a repository-relative POSIX path: ${canonicalPath}`,
    );
  }
  const segments = canonicalPath.split("/");
  if (
    segments.length === 0 ||
    segments.some((segment) =>
      segment === "" || segment === "." || segment === ".." || segment.includes("\0")
    )
  ) {
    throw new RegistryValidationError(
      `Canonical path contains an unsafe segment: ${canonicalPath}`,
    );
  }
  if (!canonicalPath.toLocaleLowerCase("en-US").endsWith(".md")) {
    throw new RegistryValidationError(
      `Canonical managed document path must end in .md: ${canonicalPath}`,
    );
  }

  const realRoot = await realpath(repositoryRoot);
  const candidate = path.resolve(realRoot, ...segments);
  if (!isWithinRoot(realRoot, candidate)) {
    throw new RegistryValidationError(
      `Canonical path escapes the repository root: ${canonicalPath}`,
    );
  }

  let candidateStat;
  try {
    candidateStat = await stat(candidate);
  } catch {
    throw new RegistryValidationError(
      `Canonical document is missing: ${canonicalPath}`,
    );
  }
  if (!candidateStat.isFile()) {
    throw new RegistryValidationError(
      `Canonical document is not a file: ${canonicalPath}`,
    );
  }

  const realCandidate = await realpath(candidate);
  if (!isWithinRoot(realRoot, realCandidate)) {
    throw new RegistryValidationError(
      `Canonical document resolves outside the repository root: ${canonicalPath}`,
    );
  }
  return realCandidate;
}

export async function loadManagedDocuments(
  repositoryRoot: string,
): Promise<RegistryLoadResult> {
  const registryPath = path.join(
    repositoryRoot,
    ...REGISTRY_RELATIVE_PATH.split("/"),
  );
  let registryText: string;
  try {
    registryText = await readFile(registryPath, "utf8");
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new RegistryValidationError(
      `Unable to read ${REGISTRY_RELATIVE_PATH}: ${detail}`,
    );
  }

  const registry = parseRegistryText(registryText);
  const candidates = selectManagedMarkdownArtifacts(registry);
  const documents: ManagedDocument[] = [];
  const diagnostics: string[] = [];

  for (const artifact of candidates) {
    try {
      const absolutePath = await resolveCanonicalMarkdownPath(
        repositoryRoot,
        artifact.path,
      );
      documents.push({ ...artifact, absolutePath });
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      diagnostics.push(`${artifact.artifact_id}: ${detail}`);
    }
  }

  documents.sort((left, right) =>
    left.artifact_id.localeCompare(right.artifact_id),
  );
  return { documents, diagnostics };
}
