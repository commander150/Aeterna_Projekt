import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { mkdir, mkdtemp, readFile, rm, symlink, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";

import {
  CandidateVersionError, candidateVersion, replaceCandidateVersion,
  suggestMajorVersion, suggestMinorVersion, writeCandidateVersion,
} from "../src/version_candidate";

function digest(bytes: Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

function hasCode(code: string): (error: unknown) => boolean {
  return (error) => error instanceof CandidateVersionError && error.code === code;
}

test("minor suggestion applies only to a known two-component numeric form", () => {
  assert.equal(suggestMinorVersion("1.1"), "1.2");
  assert.equal(suggestMinorVersion("6.20"), "6.21");
  assert.equal(suggestMinorVersion("release-1.1"), undefined);
  assert.equal(suggestMinorVersion("1.2.3"), undefined);
  assert.equal(suggestMajorVersion("1.1"), "2.0");
  assert.equal(suggestMajorVersion("6.20"), "7.0");
  assert.equal(suggestMajorVersion("release-1.1"), undefined);
});

test("candidate version edit preserves BOM, CRLF and every other byte", () => {
  const source = Buffer.from('\uFEFF---\r\nartifact_id: AET-DOC-TARGET\r\nversion: "1.1"\r\nauthority: project-direction\r\n---\r\n# Café\r\nUser edit.\r\n');
  const changed = replaceCandidateVersion(source, "1.1", "1.2");
  assert.equal(candidateVersion(changed), "1.2");
  assert.deepEqual(changed, Buffer.from(source.toString("utf8").replace('version: "1.1"', 'version: "1.2"')));
  assert.equal(changed.subarray(0, 3).toString("hex"), "efbbbf");
});

test("unsafe or ambiguous version front matter blocks without a write", () => {
  for (const text of [
    '---\nversion: 1.1\n---\n# Body\n',
    '---\nversion: "1.1"\nversion: "1.2"\n---\n# Body\n',
    '---\nversion: "1.1" # comment\n---\n# Body\n',
    '---\nversion: "1.1"\n# Body\n',
  ]) {
    assert.throws(() => replaceCandidateVersion(Buffer.from(text), "1.1", "1.2"), hasCode("CANDIDATE_FORMAT_UNSAFE"));
  }
  assert.throws(() => replaceCandidateVersion(Buffer.from('---\nversion: "1.1"\n---\n'), "1.0", "1.2"), hasCode("CANDIDATE_VERSION_DRIFT"));
});

test("approved candidate-only write preserves canonical and refuses stale bytes", async () => {
  const directory = await mkdtemp(path.join(os.tmpdir(), "aeterna-e2c-version-"));
  try {
    const canonical = path.join(directory, "canonical.md");
    const candidate = path.join(directory, "candidate.md");
    const original = Buffer.from('---\nversion: "1.1"\n---\n# Body\nUser edit.\n');
    await writeFile(canonical, original);
    await writeFile(candidate, original);
    const changedHash = await writeCandidateVersion(candidate, digest(original), "1.1", "1.2");
    assert.equal(changedHash, digest(await readFile(candidate)));
    assert.deepEqual(await readFile(canonical), original);
    assert.match((await readFile(candidate)).toString("utf8"), /User edit\./);
    await assert.rejects(writeCandidateVersion(candidate, digest(original), "1.2", "1.3"), hasCode("CANDIDATE_VERSION_DRIFT"));
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});

test("candidate version writer refuses a symlinked parent when supported", async (context) => {
  const directory = await mkdtemp(path.join(os.tmpdir(), "aeterna-e2c-parent-"));
  try {
    const real = path.join(directory, "real");
    const link = path.join(directory, "linked");
    await mkdir(real);
    const bytes = Buffer.from('---\nversion: "1.1"\n---\n# Body\n');
    await writeFile(path.join(real, "candidate.md"), bytes);
    try { await symlink(real, link, "dir"); }
    catch { context.skip("Directory symlinks are unavailable in this environment."); return; }
    await assert.rejects(
      writeCandidateVersion(path.join(link, "candidate.md"), digest(bytes), "1.1", "1.2"),
      hasCode("CANDIDATE_UNSAFE"),
    );
    assert.deepEqual(await readFile(path.join(real, "candidate.md")), bytes);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
