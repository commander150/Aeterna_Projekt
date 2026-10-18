import assert from "node:assert/strict";
import { test } from "node:test";
import type * as vscode from "vscode";

import { createDiffUris, emptyCreateDocument, EMPTY_CREATE_SCHEME } from "../src/create_diff";
import type { CreateSession } from "../src/create_candidate";

test("CREATE diff uses an empty read-only virtual left side and the existing external candidate", () => {
  const candidatePath = "C:\\Aeterna_Local\\document_editor\\create\\candidate.md";
  const session = { candidatePath, input: { artifactId: "AET-DOC-NEW-ITEM" } } as CreateSession;
  const calls: unknown[] = [];
  const host = { Uri: {
    from: (parts: unknown) => { calls.push(parts); return parts; },
    file: (value: string) => { calls.push(value); return { scheme: "file", fsPath: value }; },
  } } as unknown as typeof vscode;
  const diff = createDiffUris(session, host);
  assert.equal(emptyCreateDocument(), "");
  assert.deepEqual(calls[0], { scheme: EMPTY_CREATE_SCHEME, path: "/empty.md" });
  assert.equal((diff.candidate as { fsPath: string }).fsPath, candidatePath);
  assert.match(diff.title, /AET-DOC-NEW-ITEM.*empty.*candidate/);
  assert.equal(calls.length, 2);
});
