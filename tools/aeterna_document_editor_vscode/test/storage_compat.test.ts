import assert from "node:assert/strict";
import { test } from "node:test";
import { mkdtemp, mkdir, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

import { updateCandidateStorageRoot } from "../src/storage_compat";

test("installed extension reuses existing E1 globalStorage sessions without moving them", async () => {
  const parent = await mkdtemp(path.join(tmpdir(), "aeterna-storage-compat-"));
  try {
    const current = path.join(parent, "aeterna-local.aeterna-document-editor");
    const legacy = path.join(parent, "undefined_publisher.aeterna-document-editor", "e1-candidates");
    assert.equal(await updateCandidateStorageRoot(current), path.join(current, "e1-candidates"));
    await mkdir(legacy, { recursive: true });
    assert.equal(await updateCandidateStorageRoot(current), legacy);
    assert.equal(await updateCandidateStorageRoot(path.dirname(legacy)), legacy);
  } finally {
    await rm(parent, { recursive: true, force: true });
  }
});
