import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import {
  mkdir,
  mkdtemp,
  readFile,
  rm,
  symlink,
  unlink,
  writeFile,
} from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";

import {
  CandidateSessionError,
  type CandidateSessionRequest,
  candidateDiffDescriptor,
  candidateDocumentState,
  createOrOpenCandidateSession,
  loadCandidateSession,
} from "../src/candidate";

const temporaryDirectories: string[] = [];
const canonicalRelativePath = "project/planning/PROJECT_PLAN.md";
const canonicalBytes = Buffer.from(
  "\uFEFF---\r\nartifact_id: AET-DOC-PROJECT-PLAN\r\nversion: \"6.19\"\r\n---\r\n# Árvíztűrő tükörfúrógép\r\n",
  "utf8",
);

afterEach(async () => {
  await Promise.all(
    temporaryDirectories.splice(0).map((directory) =>
      rm(directory, { recursive: true, force: true }),
    ),
  );
});

async function temporaryDirectory(prefix = "aeterna-e1-"): Promise<string> {
  const directory = await mkdtemp(path.join(os.tmpdir(), prefix));
  temporaryDirectories.push(directory);
  return directory;
}

async function candidateFixture(): Promise<{
  readonly request: CandidateSessionRequest;
  readonly canonicalPath: string;
}> {
  const root = await temporaryDirectory();
  const repositoryRoot = path.join(root, "repository");
  const storageRoot = path.join(root, "vscode-global-storage");
  const canonicalPath = path.join(
    repositoryRoot,
    ...canonicalRelativePath.split("/"),
  );
  await mkdir(path.dirname(canonicalPath), { recursive: true });
  await writeFile(canonicalPath, canonicalBytes);
  return {
    request: {
      repositoryRoot,
      storageRoot,
      artifact: {
        artifactId: "AET-DOC-PROJECT-PLAN",
        canonicalPath: canonicalRelativePath,
        version: "6.19",
        kind: "document",
        generated: false,
        scope: "ACTIVE",
      },
    },
    canonicalPath,
  };
}

function hasErrorCode(code: CandidateSessionError["code"]): (error: unknown) => boolean {
  return (error: unknown) =>
    error instanceof CandidateSessionError && error.code === code;
}

test("candidate creation is byte-faithful and leaves canonical bytes unchanged", async () => {
  const { request, canonicalPath } = await candidateFixture();
  const before = await readFile(canonicalPath);

  const session = await createOrOpenCandidateSession(request);

  assert.equal(session.disposition, "CREATED");
  assert.deepEqual(await readFile(session.candidatePath), before);
  assert.deepEqual(await readFile(canonicalPath), before);
  assert.equal(session.manifest.baseline.byteLength, before.length);
  assert.equal(
    session.manifest.baseline.canonicalSha256,
    createHash("sha256").update(before).digest("hex"),
  );
  assert.equal(session.manifest.artifactId, request.artifact.artifactId);
  assert.equal(session.manifest.canonicalPath, canonicalRelativePath);
  assert.equal(session.manifest.canonicalRealPath, canonicalPath);
  assert.equal(session.manifest.candidatePath, session.candidatePath);
});

test("reopening a candidate preserves edited content instead of overwriting it", async () => {
  const { request, canonicalPath } = await candidateFixture();
  const created = await createOrOpenCandidateSession(request);
  const edited = Buffer.from("candidate-only edit\n", "utf8");
  await writeFile(created.candidatePath, edited);

  const reopened = await createOrOpenCandidateSession(request);

  assert.equal(reopened.disposition, "REUSED");
  assert.deepEqual(await readFile(reopened.candidatePath), edited);
  assert.deepEqual(await readFile(canonicalPath), canonicalBytes);
  assert.deepEqual(candidateDiffDescriptor(reopened), {
    leftCanonicalPath: reopened.canonicalPath,
    rightCandidatePath: reopened.candidatePath,
    title: "AET-DOC-PROJECT-PLAN: Canonical ↔ Candidate",
  });
});

test("open dirty candidate state is detected for unsaved-change protection", () => {
  const candidatePath = path.resolve("candidate.md");
  assert.equal(candidateDocumentState(candidatePath, []), "CLOSED");
  assert.equal(
    candidateDocumentState(candidatePath, [
      { fsPath: candidatePath, isDirty: false },
    ]),
    "OPEN_CLEAN",
  );
  assert.equal(
    candidateDocumentState(candidatePath, [
      { fsPath: candidatePath, isDirty: true },
    ]),
    "OPEN_DIRTY",
  );
});

test("invalid artifact ID is rejected before candidate creation", async () => {
  const { request } = await candidateFixture();
  await assert.rejects(
    createOrOpenCandidateSession({
      ...request,
      artifact: { ...request.artifact, artifactId: "bad-id" },
    }),
    hasErrorCode("INVALID_ARTIFACT_ID"),
  );
});

test("missing canonical file is rejected", async () => {
  const { request, canonicalPath } = await candidateFixture();
  await unlink(canonicalPath);
  await assert.rejects(
    createOrOpenCandidateSession(request),
    hasErrorCode("CANONICAL_UNAVAILABLE"),
  );
});

test("non-active, generated, and non-document artifacts are unsupported", async () => {
  const { request } = await candidateFixture();
  for (const artifact of [
    { ...request.artifact, scope: "ARCHIVE" },
    { ...request.artifact, generated: true },
    { ...request.artifact, kind: "dataset" },
  ]) {
    await assert.rejects(
      createOrOpenCandidateSession({ ...request, artifact }),
      hasErrorCode("UNSUPPORTED_ARTIFACT"),
    );
  }
});

test("canonical path traversal is rejected", async () => {
  const { request } = await candidateFixture();
  await assert.rejects(
    createOrOpenCandidateSession({
      ...request,
      artifact: {
        ...request.artifact,
        canonicalPath: "../outside.md",
      },
    }),
    hasErrorCode("CANONICAL_UNAVAILABLE"),
  );
});

test("candidate storage inside the repository is rejected", async () => {
  const { request } = await candidateFixture();
  await assert.rejects(
    createOrOpenCandidateSession({
      ...request,
      storageRoot: path.join(request.repositoryRoot, ".candidate-storage"),
    }),
    hasErrorCode("STORAGE_INSIDE_REPOSITORY"),
  );
});

test("symlinked candidate storage root is rejected when symlinks are available", async (context) => {
  const { request } = await candidateFixture();
  const actualStorage = path.join(
    path.dirname(request.repositoryRoot),
    "actual-storage",
  );
  const linkedStorage = path.join(
    path.dirname(request.repositoryRoot),
    "linked-storage",
  );
  await mkdir(actualStorage, { recursive: true });
  try {
    await symlink(
      actualStorage,
      linkedStorage,
      process.platform === "win32" ? "junction" : "dir",
    );
  } catch (error) {
    const code = (error as NodeJS.ErrnoException).code;
    if (code === "EPERM" || code === "EACCES") {
      context.skip(`symlink creation is unavailable: ${code}`);
      return;
    }
    throw error;
  }
  await assert.rejects(
    createOrOpenCandidateSession({ ...request, storageRoot: linkedStorage }),
    hasErrorCode("UNSAFE_STORAGE"),
  );
});

test("canonical symlink escape is rejected when symlinks are available", async (context) => {
  const { request, canonicalPath } = await candidateFixture();
  const outsideDirectory = path.join(
    path.dirname(request.repositoryRoot),
    "outside-documents",
  );
  const outside = path.join(outsideDirectory, "PROJECT_PLAN.md");
  await mkdir(outsideDirectory, { recursive: true });
  await writeFile(outside, "outside\n", "utf8");
  const canonicalDirectory = path.dirname(canonicalPath);
  await rm(canonicalDirectory, { recursive: true, force: true });
  try {
    await symlink(
      outsideDirectory,
      canonicalDirectory,
      process.platform === "win32" ? "junction" : "dir",
    );
  } catch (error) {
    const code = (error as NodeJS.ErrnoException).code;
    if (code === "EPERM" || code === "EACCES") {
      context.skip(`symlink creation is unavailable: ${code}`);
      return;
    }
    throw error;
  }
  await assert.rejects(
    createOrOpenCandidateSession(request),
    hasErrorCode("CANONICAL_UNAVAILABLE"),
  );
});

test("baseline drift blocks reopen and preserves candidate edits", async () => {
  const { request, canonicalPath } = await candidateFixture();
  const created = await createOrOpenCandidateSession(request);
  const edited = Buffer.from("valuable candidate work\n", "utf8");
  await writeFile(created.candidatePath, edited);
  await writeFile(canonicalPath, "changed canonical baseline\n", "utf8");

  await assert.rejects(
    createOrOpenCandidateSession(request),
    hasErrorCode("BASELINE_DRIFT"),
  );
  assert.deepEqual(await readFile(created.candidatePath), edited);
});

test("registry version drift blocks reopen and preserves candidate edits", async () => {
  const { request } = await candidateFixture();
  const created = await createOrOpenCandidateSession(request);
  const edited = Buffer.from("candidate survives version drift\n", "utf8");
  await writeFile(created.candidatePath, edited);

  await assert.rejects(
    createOrOpenCandidateSession({
      ...request,
      artifact: { ...request.artifact, version: "6.20" },
    }),
    hasErrorCode("BASELINE_DRIFT"),
  );
  assert.deepEqual(await readFile(created.candidatePath), edited);
});

test("incomplete session fails closed without deleting candidate content", async () => {
  const { request } = await candidateFixture();
  const created = await createOrOpenCandidateSession(request);
  const edited = Buffer.from("recoverable candidate work\n", "utf8");
  await writeFile(created.candidatePath, edited);
  await unlink(created.manifestPath);

  await assert.rejects(
    loadCandidateSession(request),
    hasErrorCode("SESSION_CORRUPT"),
  );
  assert.deepEqual(await readFile(created.candidatePath), edited);
});
