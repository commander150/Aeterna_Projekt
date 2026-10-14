import assert from "node:assert/strict";
import { test } from "node:test";
import type * as vscode from "vscode";

import { DocumentManager } from "../src/manager";
import type { ManagedDocument } from "../src/registry";

test("manager opens one separate panel and routes only current selected documents", async () => {
  const documents: ManagedDocument[] = [
    {
      artifact_id: "AET-DOC-PROJECT-PLAN",
      title: "Project Plan",
      path: "project/planning/PROJECT_PLAN.md",
      absolutePath: "C:\\repo\\project\\planning\\PROJECT_PLAN.md",
      kind: "document",
      version: "6.20",
      generated: false,
      scope: "ACTIVE",
    },
    {
      artifact_id: "AET-DOC-EDITOR-SPEC",
      title: "<img src=x onerror=alert(1)>",
      path: "project/requirements/EDITOR_SPEC.md",
      absolutePath: "C:\\repo\\project\\requirements\\EDITOR_SPEC.md",
      kind: "document",
      version: "0.1",
      generated: false,
      scope: "ACTIVE",
    },
  ];
  const posted: unknown[] = [];
  const actions: string[] = [];
  let receiver: ((message: unknown) => void) | undefined;
  let panelCount = 0;
  let revealCount = 0;
  const panel = {
    webview: {
      html: "",
      postMessage: async (message: unknown) => { posted.push(message); return true; },
      onDidReceiveMessage: (listener: (message: unknown) => void) => {
        receiver = listener;
        return { dispose() {} };
      },
    },
    reveal: () => { revealCount += 1; },
    onDidDispose: () => ({ dispose() {} }),
    dispose() {},
  };
  const host = {
    ViewColumn: { One: 1 },
    window: {
      createWebviewPanel: (...args: unknown[]) => {
        panelCount += 1;
        assert.equal(args[0], "aeternaDocumentManager");
        assert.equal(args[1], "AETERNA Document Manager");
        assert.deepEqual(args[3], { enableScripts: true, localResourceRoots: [] });
        return panel;
      },
    },
  } as unknown as typeof vscode;
  const manager = new DocumentManager(
    host,
    () => documents,
    () => "2 managed documents loaded.",
    async (action, document) => {
      actions.push(`${action}:${document?.artifact_id ?? ""}`);
      return { ok: true, message: "Action completed." };
    },
  );

  manager.show();
  manager.show();
  assert.equal(panelCount, 1);
  assert.equal(revealCount, 1);
  assert.doesNotMatch(panel.webview.html, /<img src=x/);
  receiver?.({ type: "ready" });
  assert.equal((posted.at(-1) as { documents: unknown[] }).documents.length, 2);

  receiver?.({ type: "search", query: "PROJECT_PLAN" });
  assert.equal((posted.at(-1) as { documents: unknown[] }).documents.length, 1);
  receiver?.({ type: "action", action: "edit", artifactId: "AET-DOC-PROJECT-PLAN" });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["edit:AET-DOC-PROJECT-PLAN"]);

  receiver?.({ type: "action", action: "apply", artifactId: "AET-DOC-PROJECT-PLAN" });
  receiver?.({ type: "action", action: "compare", artifactId: "AET-DOC-NOT-LISTED" });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["edit:AET-DOC-PROJECT-PLAN"]);
  manager.dispose();
});
