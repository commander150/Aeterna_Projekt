import assert from "node:assert/strict";
import { test } from "node:test";

import {
  filterManagedDocuments,
  parseManagerMessage,
  renderManagerHtml,
} from "../src/manager_content";
import type { ManagedDocument } from "../src/registry";

const documents: ManagedDocument[] = [
  {
    artifact_id: "AET-DOC-PROJECT-PLAN",
    title: "Project Plan",
    kind: "document",
    version: "6.20",
    generated: false,
    scope: "ACTIVE",
    path: "project/planning/PROJECT_PLAN.md",
    absolutePath: "C:\\repo\\project\\planning\\PROJECT_PLAN.md",
  },
  {
    artifact_id: "AET-DOC-DOCUMENT-EDITOR-SPECIFICATION",
    title: "Editor Specification",
    kind: "document",
    version: "0.1",
    generated: false,
    scope: "ACTIVE",
    path: "project/requirements/DOCUMENT_EDITOR_SPECIFICATION.md",
    absolutePath: "C:\\repo\\project\\requirements\\DOCUMENT_EDITOR_SPECIFICATION.md",
  },
];

test("manager search matches artifact ID, title and canonical filename without changing source list", () => {
  assert.deepEqual(filterManagedDocuments(documents, ""), documents);
  assert.deepEqual(filterManagedDocuments(documents, "  PROJECT_PLAN  "), [documents[0]]);
  assert.deepEqual(filterManagedDocuments(documents, "editor specification"), [documents[1]]);
  assert.deepEqual(filterManagedDocuments(documents, "aet-doc-project"), [documents[0]]);
  assert.deepEqual(filterManagedDocuments(documents, "not-found"), []);
  assert.equal(documents.length, 2);
});

test("manager accepts only known actions and well-formed artifact IDs", () => {
  assert.deepEqual(parseManagerMessage({ type: "ready" }), { type: "ready" });
  assert.deepEqual(parseManagerMessage({ type: "search", query: "plan" }), { type: "search", query: "plan" });
  assert.deepEqual(parseManagerMessage({ type: "action", action: "refresh" }), { type: "action", action: "refresh" });
  assert.deepEqual(
    parseManagerMessage({ type: "action", action: "edit", artifactId: "AET-DOC-PROJECT-PLAN" }),
    { type: "action", action: "edit", artifactId: "AET-DOC-PROJECT-PLAN" },
  );
  for (const invalid of [
    null,
    { type: "action", action: "apply", artifactId: "AET-DOC-PROJECT-PLAN" },
    { type: "action", action: "edit", artifactId: "../outside.md" },
    { type: "action", action: "edit", artifactId: "AET-DOC-PROJECT-PLAN", path: "C:\\outside" },
    { type: "action", action: "refresh", artifactId: "AET-DOC-PROJECT-PLAN" },
    { type: "search", query: "x".repeat(257) },
    { type: "ready", extra: true },
  ]) {
    assert.equal(parseManagerMessage(invalid), undefined);
  }
});

test("manager HTML uses CSP and text-only DOM rendering for registry values", () => {
  const html = renderManagerHtml("known-nonce");
  assert.match(html, /default-src 'none'; script-src 'nonce-known-nonce'; style-src 'nonce-known-nonce'/);
  assert.match(html, /row\.append\(title, detail\)/);
  assert.match(html, /title\.textContent = item\.title/);
  assert.match(html, /detail\.textContent = item\.artifactId/);
  assert.doesNotMatch(html, /innerHTML/);
  assert.doesNotMatch(html, /data-action="apply"/);
  assert.doesNotMatch(html, /AET-DOC-PROJECT-PLAN/);
});
