import { createHash } from "node:crypto";
import {
  lstat,
  mkdir,
  open,
  readFile,
  realpath,
} from "node:fs/promises";
import path from "node:path";

import {
  RegistryValidationError,
  resolveCanonicalMarkdownPath,
} from "./registry";

export const CANDIDATE_SESSION_SCHEMA =
  "aeterna-document-editor-candidate-session/0.1";

const ARTIFACT_ID_PATTERN = /^AET-DOC-[A-Z0-9]+(?:-[A-Z0-9]+)*$/;

export interface CandidateArtifactIdentity {
  readonly artifactId: string;
  readonly canonicalPath: string;
  readonly version: string;
  readonly kind: string;
  readonly generated: boolean;
  readonly scope: string;
}

export interface CandidateSessionRequest {
  readonly repositoryRoot: string;
  readonly storageRoot: string;
  readonly artifact: CandidateArtifactIdentity;
}

export interface CandidateBaseline {
  readonly version: string;
  readonly canonicalSha256: string;
  readonly byteLength: number;
}

export interface CandidateSessionManifest {
  readonly schemaVersion: typeof CANDIDATE_SESSION_SCHEMA;
  readonly artifactId: string;
  readonly repositoryRoot: string;
  readonly canonicalPath: string;
  readonly canonicalRealPath: string;
  readonly candidatePath: string;
  readonly baseline: CandidateBaseline;
  readonly createdAt: string;
}

export interface CandidateSession {
  readonly disposition: "CREATED" | "REUSED";
  readonly manifestPath: string;
  readonly candidatePath: string;
  readonly canonicalPath: string;
  readonly manifest: CandidateSessionManifest;
}

export interface CandidateDiffDescriptor {
  readonly leftCanonicalPath: string;
  readonly rightCandidatePath: string;
  readonly title: string;
}

export interface OpenDocumentState {
  readonly fsPath: string;
  readonly isDirty: boolean;
}

export type CandidateDocumentState = "CLOSED" | "OPEN_CLEAN" | "OPEN_DIRTY";

export class CandidateSessionError extends Error {
  public constructor(
    public readonly code:
      | "INVALID_ARTIFACT_ID"
      | "UNSUPPORTED_ARTIFACT"
      | "CANONICAL_UNAVAILABLE"
      | "STORAGE_INSIDE_REPOSITORY"
      | "UNSAFE_STORAGE"
      | "SESSION_NOT_FOUND"
      | "SESSION_CORRUPT"
      | "BASELINE_DRIFT"
      | "CANONICAL_CHANGED_DURING_COPY",
    message: string,
  ) {
    super(message);
    this.name = "CandidateSessionError";
  }
}

function sha256(bytes: Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

function normalizePathIdentity(value: string): string {
  const resolved = path.resolve(value);
  return process.platform === "win32"
    ? resolved.toLocaleLowerCase("en-US")
    : resolved;
}

export function pathsEqual(left: string, right: string): boolean {
  return normalizePathIdentity(left) === normalizePathIdentity(right);
}

export function isPathWithin(root: string, candidate: string): boolean {
  const relative = path.relative(root, candidate);
  return (
    relative === "" ||
    (relative !== ".." &&
      !relative.startsWith(`..${path.sep}`) &&
      !path.isAbsolute(relative))
  );
}

export function candidateDocumentState(
  candidatePath: string,
  documents: readonly OpenDocumentState[],
): CandidateDocumentState {
  const open = documents.find((document) =>
    pathsEqual(document.fsPath, candidatePath),
  );
  if (!open) {
    return "CLOSED";
  }
  return open.isDirty ? "OPEN_DIRTY" : "OPEN_CLEAN";
}

export function candidateDiffDescriptor(
  session: CandidateSession,
): CandidateDiffDescriptor {
  return {
    leftCanonicalPath: session.canonicalPath,
    rightCandidatePath: session.candidatePath,
    title: `${session.manifest.artifactId}: Canonical ↔ Candidate`,
  };
}

function validateArtifact(artifact: CandidateArtifactIdentity): void {
  if (!ARTIFACT_ID_PATTERN.test(artifact.artifactId)) {
    throw new CandidateSessionError(
      "INVALID_ARTIFACT_ID",
      `Invalid managed document artifact ID: ${artifact.artifactId}`,
    );
  }
  if (
    artifact.kind !== "document" ||
    artifact.generated ||
    artifact.scope !== "ACTIVE" ||
    !artifact.canonicalPath.toLocaleLowerCase("en-US").endsWith(".md")
  ) {
    throw new CandidateSessionError(
      "UNSUPPORTED_ARTIFACT",
      `Edit Candidate supports active, non-generated managed Markdown documents only: ${artifact.artifactId}`,
    );
  }
}

async function exists(target: string): Promise<boolean> {
  try {
    await lstat(target);
    return true;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") {
      return false;
    }
    throw error;
  }
}

async function assertDirectoryWithoutSymlink(
  directory: string,
  label: string,
): Promise<void> {
  const information = await lstat(directory);
  if (!information.isDirectory() || information.isSymbolicLink()) {
    throw new CandidateSessionError(
      "UNSAFE_STORAGE",
      `${label} must be a real directory without a symlink: ${directory}`,
    );
  }
}

async function assertRegularFileWithoutSymlink(
  filePath: string,
  label: string,
): Promise<void> {
  const information = await lstat(filePath);
  if (!information.isFile() || information.isSymbolicLink()) {
    throw new CandidateSessionError(
      "SESSION_CORRUPT",
      `${label} must be a regular file without a symlink: ${filePath}`,
    );
  }
}

async function prepareSessionPaths(
  request: CandidateSessionRequest,
): Promise<{
  readonly realRepositoryRoot: string;
  readonly realStorageRoot: string;
  readonly sessionDirectory: string;
  readonly manifestPath: string;
  readonly candidatePath: string;
}> {
  validateArtifact(request.artifact);
  const realRepositoryRoot = await realpath(request.repositoryRoot);
  await mkdir(request.storageRoot, { recursive: true });
  await assertDirectoryWithoutSymlink(request.storageRoot, "Candidate storage root");
  const realStorageRoot = await realpath(request.storageRoot);
  if (isPathWithin(realRepositoryRoot, realStorageRoot)) {
    throw new CandidateSessionError(
      "STORAGE_INSIDE_REPOSITORY",
      "Candidate storage must be outside the AETERNA repository.",
    );
  }

  const repositoryKey = sha256(
    Buffer.from(normalizePathIdentity(realRepositoryRoot), "utf8"),
  );
  const artifactKey = sha256(
    Buffer.from(
      `${request.artifact.artifactId}\0${request.artifact.canonicalPath}`,
      "utf8",
    ),
  );
  const relativeSegments = ["candidate-sessions", repositoryKey, artifactKey];
  const sessionDirectory = path.join(realStorageRoot, ...relativeSegments);
  await mkdir(sessionDirectory, { recursive: true });

  let current = realStorageRoot;
  for (const segment of relativeSegments) {
    current = path.join(current, segment);
    await assertDirectoryWithoutSymlink(current, "Candidate session directory");
  }
  const realSessionDirectory = await realpath(sessionDirectory);
  if (!isPathWithin(realStorageRoot, realSessionDirectory)) {
    throw new CandidateSessionError(
      "UNSAFE_STORAGE",
      "Candidate session directory resolves outside the configured storage root.",
    );
  }

  return {
    realRepositoryRoot,
    realStorageRoot,
    sessionDirectory: realSessionDirectory,
    manifestPath: path.join(realSessionDirectory, "session.json"),
    candidatePath: path.join(
      realSessionDirectory,
      `${request.artifact.artifactId}.candidate.md`,
    ),
  };
}

function requireString(
  record: Record<string, unknown>,
  field: string,
): string {
  const value = record[field];
  if (typeof value !== "string" || value.length === 0) {
    throw new CandidateSessionError(
      "SESSION_CORRUPT",
      `Candidate session field must be a non-empty string: ${field}`,
    );
  }
  return value;
}

function parseManifest(text: string): CandidateSessionManifest {
  let value: unknown;
  try {
    value = JSON.parse(text) as unknown;
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    throw new CandidateSessionError(
      "SESSION_CORRUPT",
      `Candidate session JSON is invalid: ${detail}`,
    );
  }
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new CandidateSessionError(
      "SESSION_CORRUPT",
      "Candidate session root must be an object.",
    );
  }
  const record = value as Record<string, unknown>;
  if (record.schemaVersion !== CANDIDATE_SESSION_SCHEMA) {
    throw new CandidateSessionError(
      "SESSION_CORRUPT",
      `Unsupported candidate session schema: ${String(record.schemaVersion)}`,
    );
  }
  const baselineValue = record.baseline;
  if (
    typeof baselineValue !== "object" ||
    baselineValue === null ||
    Array.isArray(baselineValue)
  ) {
    throw new CandidateSessionError(
      "SESSION_CORRUPT",
      "Candidate session baseline must be an object.",
    );
  }
  const baseline = baselineValue as Record<string, unknown>;
  const byteLength = baseline.byteLength;
  if (
    typeof byteLength !== "number" ||
    !Number.isSafeInteger(byteLength) ||
    byteLength < 0
  ) {
    throw new CandidateSessionError(
      "SESSION_CORRUPT",
      "Candidate session baseline.byteLength must be a non-negative integer.",
    );
  }
  const canonicalSha256 = requireString(baseline, "canonicalSha256");
  if (!/^[0-9a-f]{64}$/.test(canonicalSha256)) {
    throw new CandidateSessionError(
      "SESSION_CORRUPT",
      "Candidate session baseline SHA-256 is invalid.",
    );
  }
  return {
    schemaVersion: CANDIDATE_SESSION_SCHEMA,
    artifactId: requireString(record, "artifactId"),
    repositoryRoot: requireString(record, "repositoryRoot"),
    canonicalPath: requireString(record, "canonicalPath"),
    canonicalRealPath: requireString(record, "canonicalRealPath"),
    candidatePath: requireString(record, "candidatePath"),
    baseline: {
      version: requireString(baseline, "version"),
      canonicalSha256,
      byteLength,
    },
    createdAt: requireString(record, "createdAt"),
  };
}

async function resolveCanonical(
  request: CandidateSessionRequest,
): Promise<string> {
  try {
    return await resolveCanonicalMarkdownPath(
      request.repositoryRoot,
      request.artifact.canonicalPath,
    );
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    const prefix =
      error instanceof RegistryValidationError ? "Canonical path rejected" : "Canonical path unavailable";
    throw new CandidateSessionError(
      "CANONICAL_UNAVAILABLE",
      `${prefix}: ${detail}`,
    );
  }
}

async function loadExisting(
  request: CandidateSessionRequest,
  paths: Awaited<ReturnType<typeof prepareSessionPaths>>,
  canonicalRealPath: string,
): Promise<CandidateSession> {
  const manifestExists = await exists(paths.manifestPath);
  const candidateExists = await exists(paths.candidatePath);
  if (!manifestExists && !candidateExists) {
    throw new CandidateSessionError(
      "SESSION_NOT_FOUND",
      `No candidate session exists for ${request.artifact.artifactId}.`,
    );
  }
  if (!manifestExists || !candidateExists) {
    throw new CandidateSessionError(
      "SESSION_CORRUPT",
      "Candidate session is incomplete; existing content was preserved.",
    );
  }
  await assertRegularFileWithoutSymlink(paths.manifestPath, "Candidate manifest");
  await assertRegularFileWithoutSymlink(paths.candidatePath, "Candidate file");
  const manifest = parseManifest(await readFile(paths.manifestPath, "utf8"));
  if (
    manifest.artifactId !== request.artifact.artifactId ||
    manifest.canonicalPath !== request.artifact.canonicalPath ||
    !pathsEqual(manifest.repositoryRoot, paths.realRepositoryRoot) ||
    !pathsEqual(manifest.canonicalRealPath, canonicalRealPath) ||
    !pathsEqual(manifest.candidatePath, paths.candidatePath)
  ) {
    throw new CandidateSessionError(
      "SESSION_CORRUPT",
      "Candidate session identity does not match the selected managed artifact.",
    );
  }
  if (manifest.baseline.version !== request.artifact.version) {
    throw new CandidateSessionError(
      "BASELINE_DRIFT",
      `Canonical version changed for ${request.artifact.artifactId}; the existing candidate was preserved and must not be overwritten.`,
    );
  }
  const canonicalBytes = await readFile(canonicalRealPath);
  const currentSha256 = sha256(canonicalBytes);
  if (
    currentSha256 !== manifest.baseline.canonicalSha256 ||
    canonicalBytes.length !== manifest.baseline.byteLength
  ) {
    throw new CandidateSessionError(
      "BASELINE_DRIFT",
      `Canonical baseline changed for ${request.artifact.artifactId}; the existing candidate was preserved and must not be overwritten.`,
    );
  }
  return {
    disposition: "REUSED",
    manifestPath: paths.manifestPath,
    candidatePath: paths.candidatePath,
    canonicalPath: canonicalRealPath,
    manifest,
  };
}

async function prepareRequest(
  request: CandidateSessionRequest,
): Promise<{
  readonly paths: Awaited<ReturnType<typeof prepareSessionPaths>>;
  readonly canonicalRealPath: string;
}> {
  const paths = await prepareSessionPaths(request);
  const canonicalRealPath = await resolveCanonical(request);
  if (!isPathWithin(paths.realRepositoryRoot, canonicalRealPath)) {
    throw new CandidateSessionError(
      "CANONICAL_UNAVAILABLE",
      "Canonical document resolves outside the repository.",
    );
  }
  return { paths, canonicalRealPath };
}

export async function loadCandidateSession(
  request: CandidateSessionRequest,
): Promise<CandidateSession> {
  const { paths, canonicalRealPath } = await prepareRequest(request);
  return loadExisting(request, paths, canonicalRealPath);
}

export async function createOrOpenCandidateSession(
  request: CandidateSessionRequest,
): Promise<CandidateSession> {
  const { paths, canonicalRealPath } = await prepareRequest(request);
  if ((await exists(paths.manifestPath)) || (await exists(paths.candidatePath))) {
    return loadExisting(request, paths, canonicalRealPath);
  }

  const canonicalBytes = await readFile(canonicalRealPath);
  const baselineSha256 = sha256(canonicalBytes);
  const candidateHandle = await open(paths.candidatePath, "wx", 0o600);
  try {
    await candidateHandle.writeFile(canonicalBytes);
  } finally {
    await candidateHandle.close();
  }

  const canonicalAfterCopy = await readFile(canonicalRealPath);
  if (
    canonicalAfterCopy.length !== canonicalBytes.length ||
    sha256(canonicalAfterCopy) !== baselineSha256
  ) {
    throw new CandidateSessionError(
      "CANONICAL_CHANGED_DURING_COPY",
      "Canonical document changed while the candidate was being created; candidate content was preserved for recovery.",
    );
  }

  const manifest: CandidateSessionManifest = {
    schemaVersion: CANDIDATE_SESSION_SCHEMA,
    artifactId: request.artifact.artifactId,
    repositoryRoot: paths.realRepositoryRoot,
    canonicalPath: request.artifact.canonicalPath,
    canonicalRealPath,
    candidatePath: paths.candidatePath,
    baseline: {
      version: request.artifact.version,
      canonicalSha256: baselineSha256,
      byteLength: canonicalBytes.length,
    },
    createdAt: new Date().toISOString(),
  };
  const manifestHandle = await open(paths.manifestPath, "wx", 0o600);
  try {
    await manifestHandle.writeFile(
      `${JSON.stringify(manifest, undefined, 2)}\n`,
      "utf8",
    );
  } finally {
    await manifestHandle.close();
  }
  return {
    disposition: "CREATED",
    manifestPath: paths.manifestPath,
    candidatePath: paths.candidatePath,
    canonicalPath: canonicalRealPath,
    manifest,
  };
}
