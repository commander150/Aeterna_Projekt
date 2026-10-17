import { createHash } from "node:crypto";
import { lstat, mkdir, open, readFile, realpath } from "node:fs/promises";
import path from "node:path";

export const CREATE_SESSION_SCHEMA = "aeterna-editor-create-session/0.1";
export const CREATE_MANIFEST_SCHEMA = "aeterna-document-create-manifest/0.1";

export interface CreateInput {
  readonly artifactId: string;
  readonly targetPath: string;
  readonly type: string;
  readonly authority: string;
  readonly dependencies: readonly string[];
  readonly version: string;
  readonly integration: "current" | "pending_integration";
  readonly title: string;
  readonly initialContent: string;
}

export interface CreateSession {
  readonly schemaVersion: typeof CREATE_SESSION_SCHEMA;
  readonly repositoryRoot: string;
  readonly storageRoot: string;
  readonly candidatePath: string;
  readonly manifestPath: string;
  readonly branch: string;
  readonly head: string;
  readonly input: CreateInput;
}

export class CreateCandidateError extends Error {
  public constructor(public readonly code: string, message: string) {
    super(message);
    this.name = "CreateCandidateError";
  }
}

export function sha256(bytes: Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

export function createStorageRootForRepository(repositoryRoot: string): string {
  const aeternaRoot = path.dirname(path.resolve(repositoryRoot));
  return path.join(aeternaRoot, "Aeterna_Local", "document_editor", "create");
}

function samePath(left: string, right: string): boolean {
  const a = path.resolve(left);
  const b = path.resolve(right);
  return process.platform === "win32" ? a.toLowerCase() === b.toLowerCase() : a === b;
}

function within(root: string, candidate: string): boolean {
  const relative = path.relative(root, candidate);
  return relative === "" || (relative !== ".." && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative));
}

async function realDirectoryWithoutLinks(directory: string, label: string): Promise<string> {
  const resolved = path.resolve(directory);
  const parsed = path.parse(resolved);
  let current = parsed.root;
  for (const segment of resolved.slice(parsed.root.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, segment);
    const entry = await lstat(current);
    if (entry.isSymbolicLink() || !entry.isDirectory()) {
      throw new CreateCandidateError("UNSAFE_STORAGE", `${label} contains a link or non-directory component: ${current}`);
    }
  }
  return realpath(resolved);
}

async function mkdirWithoutLinks(directory: string): Promise<void> {
  const resolved = path.resolve(directory);
  const parsed = path.parse(resolved);
  let current = parsed.root;
  for (const segment of resolved.slice(parsed.root.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, segment);
    try { await mkdir(current); }
    catch (error) { if ((error as NodeJS.ErrnoException).code !== "EEXIST") throw error; }
    const entry = await lstat(current);
    if (entry.isSymbolicLink() || !entry.isDirectory()) {
      throw new CreateCandidateError("UNSAFE_STORAGE", `CREATE storage contains a link or non-directory: ${current}`);
    }
  }
}

export async function validateCreateStorageRoot(repositoryRoot: string, storageRoot: string): Promise<string> {
  const realRepository = await realpath(repositoryRoot);
  if (!path.isAbsolute(storageRoot) || storageRoot.split(/[\\/]/).some((part) => part === "." || part === "..")) {
    throw new CreateCandidateError("UNAUTHORIZED_STORAGE", "CREATE storage must be an absolute path without traversal components.");
  }
  if (within(realRepository, path.resolve(storageRoot))) {
    throw new CreateCandidateError("STORAGE_INSIDE_REPOSITORY", "CREATE candidate storage must be outside the repository.");
  }
  if (!samePath(storageRoot, createStorageRootForRepository(realRepository))) {
    throw new CreateCandidateError("UNAUTHORIZED_STORAGE", "CREATE storage must be the Aeterna_Local/document_editor/create directory beside the repository.");
  }
  await mkdirWithoutLinks(storageRoot);
  const realStorage = await realDirectoryWithoutLinks(storageRoot, "CREATE storage");
  if (!samePath(realStorage, createStorageRootForRepository(realRepository))) {
    throw new CreateCandidateError("UNSAFE_STORAGE", "CREATE storage resolved outside the authorized Aeterna_Local directory.");
  }
  return realStorage;
}

function quote(value: string): string { return JSON.stringify(value); }

export function createMetadata(input: CreateInput): Record<string, unknown> {
  return {
    artifact_id: input.artifactId,
    kind: "document",
    type: input.type,
    version: input.version,
    lifecycle: "active",
    integration: input.integration,
    authority: input.authority,
    generated: false,
    depends_on: [...input.dependencies],
    supersedes: [],
  };
}

export function metadataFingerprint(metadata: Record<string, unknown>): string {
  const sorted = Object.fromEntries(Object.keys(metadata).sort().map((key) => [key, metadata[key]]));
  return sha256(Buffer.from(JSON.stringify(sorted), "utf8"));
}

export function renderCreateCandidate(input: CreateInput): Buffer {
  if (!/^AET-DOC-[A-Z0-9]+(?:-[A-Z0-9]+)*$/.test(input.artifactId)) {
    throw new CreateCandidateError("ARTIFACT_ID_INVALID", "New managed document needs a valid AET-DOC artifact ID.");
  }
  if (!input.version.trim() || /[\r\n]/.test(input.version) || !input.title.trim() || /[\r\n]/.test(input.title)) {
    throw new CreateCandidateError("CREATE_INPUT_INVALID", "Version and H1 title must be non-empty single-line values.");
  }
  if (input.dependencies.some((id) => !/^AET-(?:DOC|DATA|SOURCE|GEN|PKG|BP)-[A-Z0-9]+(?:-[A-Z0-9]+)*$/.test(id)) ||
      new Set(input.dependencies).size !== input.dependencies.length || input.dependencies.includes(input.artifactId)) {
    throw new CreateCandidateError("DEPENDENCIES_INVALID", "Dependencies must be unique, valid IDs and cannot refer to the new document.");
  }
  const body = input.initialContent.replace(/\r\n?/g, "\n").trim();
  const lines = [
    "---", `artifact_id: ${quote(input.artifactId)}`, "kind: document", `type: ${quote(input.type)}`,
    `version: ${quote(input.version)}`, "lifecycle: active", `integration: ${quote(input.integration)}`,
    `authority: ${quote(input.authority)}`, "generated: false",
    `depends_on: ${JSON.stringify(input.dependencies)}`, "supersedes: []", "---", `# ${input.title.trim()}`, "",
  ];
  if (body) lines.push(body, "");
  return Buffer.from(`${lines.join("\n")}\n`, "utf8");
}

export async function createOrOpenCreateSession(
  repositoryRoot: string, storageRoot: string, branch: string, head: string, input: CreateInput,
): Promise<{ session: CreateSession; disposition: "CREATED" | "REUSED" }> {
  const realRepository = await realpath(repositoryRoot);
  const realStorage = await validateCreateStorageRoot(realRepository, storageRoot);
  const repositoryKey = sha256(Buffer.from(process.platform === "win32" ? realRepository.toLowerCase() : realRepository));
  const artifactKey = sha256(Buffer.from(input.artifactId));
  const sessionDirectory = path.join(realStorage, repositoryKey, artifactKey);
  await mkdirWithoutLinks(sessionDirectory);
  await realDirectoryWithoutLinks(sessionDirectory, "CREATE session");
  const candidatePath = path.join(sessionDirectory, "candidate.md");
  const manifestPath = path.join(sessionDirectory, "session.json");
  const session: CreateSession = {
    schemaVersion: CREATE_SESSION_SCHEMA, repositoryRoot: realRepository, storageRoot: realStorage,
    candidatePath, manifestPath, branch, head, input,
  };
  let candidateExists = false;
  let manifestExists = false;
  try { await lstat(candidatePath); candidateExists = true; } catch (error) { if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error; }
  try { await lstat(manifestPath); manifestExists = true; } catch (error) { if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error; }
  if (candidateExists || manifestExists) {
    if (!candidateExists || !manifestExists) throw new CreateCandidateError("SESSION_INCOMPLETE", "Existing CREATE session is incomplete; its files were preserved.");
    const candidateEntry = await lstat(candidatePath);
    const manifestEntry = await lstat(manifestPath);
    if (!candidateEntry.isFile() || candidateEntry.nlink !== 1 || !manifestEntry.isFile() || manifestEntry.nlink !== 1) {
      throw new CreateCandidateError("SESSION_UNSAFE", "Existing CREATE session contains a link or non-file.");
    }
    let existing: CreateSession;
    try { existing = JSON.parse(await readFile(manifestPath, "utf8")) as CreateSession; }
    catch { throw new CreateCandidateError("SESSION_CORRUPT", "Existing CREATE session manifest is invalid; candidate preserved."); }
    if (existing.schemaVersion !== CREATE_SESSION_SCHEMA || existing.repositoryRoot !== realRepository ||
        existing.candidatePath !== candidatePath || existing.storageRoot !== realStorage ||
        existing.branch !== branch || existing.head !== head ||
        JSON.stringify(existing.input) !== JSON.stringify(input)) {
      throw new CreateCandidateError("SESSION_DRIFT", "Existing CREATE session identity or baseline differs; candidate preserved.");
    }
    return { session, disposition: "REUSED" };
  }
  const candidate = renderCreateCandidate(input);
  const handle = await open(candidatePath, "wx", 0o600);
  try { await handle.writeFile(candidate); } finally { await handle.close(); }
  const manifestHandle = await open(manifestPath, "wx", 0o600);
  try { await manifestHandle.writeFile(`${JSON.stringify(session, null, 2)}\n`, "utf8"); }
  finally { await manifestHandle.close(); }
  return { session, disposition: "CREATED" };
}

export async function loadCreateSession(
  repositoryRoot: string, storageRoot: string, artifactId: string, branch: string, head: string,
): Promise<CreateSession | undefined> {
  const realRepository = await realpath(repositoryRoot);
  const realStorage = await validateCreateStorageRoot(realRepository, storageRoot);
  const repositoryKey = sha256(Buffer.from(process.platform === "win32" ? realRepository.toLowerCase() : realRepository));
  const artifactKey = sha256(Buffer.from(artifactId));
  const sessionDirectory = path.join(realStorage, repositoryKey, artifactKey);
  let entry;
  try { entry = await lstat(sessionDirectory); }
  catch (error) { if ((error as NodeJS.ErrnoException).code === "ENOENT") return undefined; throw error; }
  if (!entry.isDirectory()) throw new CreateCandidateError("SESSION_UNSAFE", "CREATE session directory is not a real directory.");
  await realDirectoryWithoutLinks(sessionDirectory, "CREATE session");
  const candidatePath = path.join(sessionDirectory, "candidate.md");
  const manifestPath = path.join(sessionDirectory, "session.json");
  const candidateEntry = await lstat(candidatePath);
  const manifestEntry = await lstat(manifestPath);
  if (!candidateEntry.isFile() || candidateEntry.nlink !== 1 || !manifestEntry.isFile() || manifestEntry.nlink !== 1) {
    throw new CreateCandidateError("SESSION_UNSAFE", "CREATE session file is a link or non-file.");
  }
  let existing: CreateSession;
  try { existing = JSON.parse(await readFile(manifestPath, "utf8")) as CreateSession; }
  catch { throw new CreateCandidateError("SESSION_CORRUPT", "Existing CREATE session manifest is invalid."); }
  if (existing.schemaVersion !== CREATE_SESSION_SCHEMA || existing.repositoryRoot !== realRepository ||
      existing.storageRoot !== realStorage || existing.candidatePath !== candidatePath || existing.manifestPath !== manifestPath ||
      existing.input?.artifactId !== artifactId || existing.branch !== branch || existing.head !== head) {
    throw new CreateCandidateError("SESSION_DRIFT", "CREATE session baseline or identity changed; existing candidate preserved.");
  }
  return existing;
}
