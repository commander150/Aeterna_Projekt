import assert from "node:assert/strict";
import { mkdir, mkdtemp, readFile, readdir, rm, stat, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, test } from "node:test";

import {
  CandidateSessionError,
  type CandidateSessionRequest,
  createOrOpenCandidateSession,
} from "../src/candidate";
import {
  createOrOpenRoutedCandidate,
  loadRoutedCandidate,
} from "../src/candidate_routing";

const temporaryDirectories: string[] = [];

afterEach(async () => {
  await Promise.all(temporaryDirectories.splice(0).map((directory) =>
    rm(directory, { recursive: true, force: true })));
});

async function fixture(): Promise<{ request: CandidateSessionRequest; canonical: string }> {
  const temporary = await mkdtemp(path.join(os.tmpdir(), "aeterna-manager-routing-"));
  temporaryDirectories.push(temporary);
  const repositoryRoot = path.join(temporary, "repository");
  const canonical = path.join(repositoryRoot, "project", "planning", "PROJECT_PLAN.md");
  await mkdir(path.dirname(canonical), { recursive: true });
  await writeFile(canonical, "---\r\nversion: \"6.19\"\r\n---\r\n# Plan\r\n", "utf8");
  return {
    canonical,
    request: {
      repositoryRoot,
      storageRoot: path.join(temporary, "globalStorage", "e1-candidates"),
      artifact: {
        artifactId: "AET-DOC-PROJECT-PLAN",
        canonicalPath: "project/planning/PROJECT_PLAN.md",
        version: "6.19",
        kind: "document",
        generated: false,
        scope: "ACTIVE",
      },
    },
  };
}

test("current-baseline E1 session still reopens without a new-session prompt", async () => {
  const { request } = await fixture();
  const created = await createOrOpenCandidateSession(request);
  const routed = await createOrOpenRoutedCandidate(request, async () => {
    throw new Error("Prompt was not expected.");
  });
  assert.equal(routed?.session.disposition, "REUSED");
  assert.equal(routed?.session.candidatePath, created.candidatePath);
  assert.equal(routed?.newerBaseline, false);
});

test("loading an existing candidate for preview never creates a missing session", async () => {
  const { request } = await fixture();
  await assert.rejects(loadRoutedCandidate(request), (error: unknown) =>
    error instanceof CandidateSessionError && error.code === "SESSION_NOT_FOUND");
  assert.equal((await readdir(request.storageRoot, { recursive: true, withFileTypes: true }))
    .filter((entry) => entry.isFile()).length, 0);
});

test("version drift preserves old candidate on cancellation and blocks compare/plan", async () => {
  const { request, canonical } = await fixture();
  const old = await createOrOpenCandidateSession(request);
  await writeFile(old.candidatePath, "valuable v6.19 edits\n", "utf8");
  await writeFile(canonical, "---\r\nversion: \"6.20\"\r\n---\r\n# Plan\r\n", "utf8");
  const currentRequest = { ...request, artifact: { ...request.artifact, version: "6.20" } };

  assert.equal(await createOrOpenRoutedCandidate(currentRequest, async () => false), undefined);
  await assert.rejects(loadRoutedCandidate(currentRequest), (error: unknown) =>
    error instanceof CandidateSessionError && error.code === "BASELINE_DRIFT");
  await assert.rejects(stat(path.join(request.storageRoot, "baseline-sessions")), { code: "ENOENT" });
  assert.equal((await readFile(old.candidatePath, "utf8")), "valuable v6.19 edits\n");
});

test("explicit new baseline creates separate byte-faithful candidate and preserves both sessions", async () => {
  const { request, canonical } = await fixture();
  const old = await createOrOpenCandidateSession(request);
  await writeFile(old.candidatePath, "valuable v6.19 edits\n", "utf8");
  await writeFile(canonical, "---\r\nversion: \"6.20\"\r\n---\r\n# Plan v6.20\r\n", "utf8");
  const currentRequest = { ...request, artifact: { ...request.artifact, version: "6.20" } };
  const current = await createOrOpenRoutedCandidate(currentRequest, async () => true);
  assert.ok(current);
  assert.equal(current.newerBaseline, true);
  assert.notEqual(current.session.candidatePath, old.candidatePath);
  assert.deepEqual(await readFile(current.session.candidatePath), await readFile(canonical));
  assert.equal((await readFile(old.candidatePath, "utf8")), "valuable v6.19 edits\n");

  await writeFile(current.session.candidatePath, "edited current candidate\n", "utf8");
  const reopened = await loadRoutedCandidate(currentRequest);
  assert.equal(reopened.session.candidatePath, current.session.candidatePath);
  assert.equal((await readFile(reopened.session.candidatePath, "utf8")), "edited current candidate\n");
  assert.equal((await readFile(old.candidatePath, "utf8")), "valuable v6.19 edits\n");
});
