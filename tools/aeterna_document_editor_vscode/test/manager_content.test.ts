import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";

import {
  filterManagedDocuments,
  isGovernanceDocument,
  managerPlanStateLabel,
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

test("AETERNA Activity Bar container contains the existing documents view and a packaged SVG icon", () => {
  const root = path.resolve(__dirname, "../..");
  const manifest = JSON.parse(readFileSync(path.join(root, "package.json"), "utf8")) as {
    contributes: { viewsContainers: { activitybar: { id: string; icon: string }[] };
      views: Record<string, { id: string }[]> };
  };
  const container = manifest.contributes.viewsContainers.activitybar.find((item) => item.id === "aeternaDocumentsContainer");
  assert.ok(container);
  const views = manifest.contributes.views.aeternaDocumentsContainer;
  assert.ok(views);
  assert.deepEqual(views.map((item) => item.id), ["aeternaDocuments"]);
  assert.match(readFileSync(path.join(root, container.icon), "utf8"), /<svg[^>]+viewBox="0 0 24 24"/);
});

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
  assert.deepEqual(parseManagerMessage({ type: "action", action: "newDocument" }), { type: "action", action: "newDocument" });
  assert.deepEqual(parseManagerMessage({ type: "action", action: "compareCreate" }), { type: "action", action: "compareCreate" });
  assert.deepEqual(parseManagerMessage({ type: "select", artifactId: "AET-DOC-PROJECT-PLAN" }),
    { type: "select", artifactId: "AET-DOC-PROJECT-PLAN" });
  assert.deepEqual(parseManagerMessage({ type: "action", action: "planCreate" }), { type: "action", action: "planCreate" });
  assert.deepEqual(parseManagerMessage({ type: "action", action: "applyCreate" }), { type: "action", action: "applyCreate" });
  assert.deepEqual(parseManagerMessage({ type: "answer", questionId: "a".repeat(32), choice: "approve" }),
    { type: "answer", questionId: "a".repeat(32), choice: "approve" });
  assert.deepEqual(
    parseManagerMessage({ type: "action", action: "edit", artifactId: "AET-DOC-PROJECT-PLAN" }),
    { type: "action", action: "edit", artifactId: "AET-DOC-PROJECT-PLAN" },
  );
  assert.deepEqual(
    parseManagerMessage({ type: "action", action: "preview", artifactId: "AET-DOC-PROJECT-PLAN" }),
    { type: "action", action: "preview", artifactId: "AET-DOC-PROJECT-PLAN" },
  );
  assert.deepEqual(
    parseManagerMessage({ type: "action", action: "apply", artifactId: "AET-DOC-PROJECT-PLAN" }),
    { type: "action", action: "apply", artifactId: "AET-DOC-PROJECT-PLAN" },
  );
  assert.deepEqual(
    parseManagerMessage({ type: "action", action: "planMinor", artifactId: "AET-DOC-PROJECT-PLAN" }),
    { type: "action", action: "planMinor", artifactId: "AET-DOC-PROJECT-PLAN" },
  );
  assert.deepEqual(parseManagerMessage({ type: "action", action: "planGovernance", artifactId: "AET-DOC-GITHUB-WORKFLOW" }),
    { type: "action", action: "planGovernance", artifactId: "AET-DOC-GITHUB-WORKFLOW" });
  assert.deepEqual(parseManagerMessage({ type: "action", action: "applyGovernance", artifactId: "AET-DOC-GITHUB-WORKFLOW" }),
    { type: "action", action: "applyGovernance", artifactId: "AET-DOC-GITHUB-WORKFLOW" });
  for (const invalid of [
    null,
    { type: "action", action: "create", artifactId: "AET-DOC-PROJECT-PLAN" },
    { type: "answer", questionId: "bad", choice: "approve" },
    { type: "answer", questionId: "a".repeat(32), choice: "approve", approved: true },
    { type: "select", artifactId: "../outside.md" },
    { type: "action", action: "edit", artifactId: "../outside.md" },
    { type: "action", action: "edit", artifactId: "AET-DOC-PROJECT-PLAN", path: "C:\\outside" },
    { type: "action", action: "refresh", artifactId: "AET-DOC-PROJECT-PLAN" },
    { type: "action", action: "newDocument", artifactId: "AET-DOC-PROJECT-PLAN" },
    { type: "action", action: "planCreate", extra: true },
    { type: "action", action: "applyCreate", artifactId: "AET-DOC-PROJECT-PLAN" },
    { type: "search", query: "x".repeat(257) },
    { type: "ready", extra: true },
  ]) {
    assert.equal(parseManagerMessage(invalid), undefined);
  }
});

test("governance actions are limited to the canonical governance directory", () => {
  assert.equal(isGovernanceDocument("project/governance/workflows/GITHUB_WORKFLOW.md"), true);
  assert.equal(isGovernanceDocument("project/planning/PROJECT_PLAN.md"), false);
  assert.equal(isGovernanceDocument("project/governance/../planning/PROJECT_PLAN.md"), false);
});

test("manager HTML uses CSP and text-only DOM rendering for registry values", () => {
  const html = renderManagerHtml("known-nonce");
  assert.match(html, /default-src 'none'; script-src 'nonce-known-nonce'; style-src 'nonce-known-nonce'/);
  assert.match(html, /row\.append\(title, detail\)/);
  assert.match(html, /title\.textContent = item\.title/);
  assert.match(html, /detail\.textContent = item\.artifactId/);
  assert.doesNotMatch(html, /innerHTML/);
  assert.match(html, /data-action="apply" disabled/);
  assert.match(html, /data-action="planMinor" disabled/);
  assert.match(html, /data-action="planGovernance" disabled/);
  assert.match(html, /data-action="applyGovernance" disabled/);
  assert.match(html, /data-action="plan" disabled/);
  assert.match(html, /data-action="newDocument"/);
  assert.match(html, /data-action="compareCreate"/);
  assert.match(html, /metadataState\.textContent/);
  assert.match(html, /metadataRules\.textContent/);
  assert.match(html, /data-action="planCreate"/);
  assert.match(html, /data-action="applyCreate" disabled/);
  assert.match(html, /data-action="edit" disabled>Candidate szerkesztése/);
  assert.match(html, /data-action="preview" disabled>Markdown előnézet/);
  assert.match(html, /class="operation"/);
  assert.match(html, /message\.selectedId/);
  assert.match(html, /message\.selectedDocument/);
  assert.match(html, /message\.query/);
  assert.match(html, /createState\.textContent/);
  assert.match(html, /questionArea\.replaceChildren\(\)/);
  assert.match(html, /content\.textContent = question\.details/);
  assert.match(html, /choice: option\.id/);
  assert.match(html, /"PLAN_READY_MISMATCH"/);
  assert.doesNotMatch(html, /AET-DOC-PROJECT-PLAN/);
});

test("version recommendation mismatch is visible before Apply", () => {
  assert.match(managerPlanStateLabel("PLAN_READY_MISMATCH"), /VERSION RECOMMENDATION MISMATCH/);
  assert.match(managerPlanStateLabel("PLAN_READY_MISMATCH"), /second explicit confirmation/);
});
