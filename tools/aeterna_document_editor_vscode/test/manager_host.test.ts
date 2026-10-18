import assert from "node:assert/strict";
import { test } from "node:test";
import type * as vscode from "vscode";

import { DocumentManager, notifyPlanReady } from "../src/manager";
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

  receiver?.({ type: "action", action: "planMinor", artifactId: "AET-DOC-PROJECT-PLAN" });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["edit:AET-DOC-PROJECT-PLAN", "planMinor:AET-DOC-PROJECT-PLAN"]);

  receiver?.({ type: "action", action: "newDocument" });
  await new Promise<void>((resolve) => setImmediate(resolve));
  receiver?.({ type: "action", action: "planCreate" });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["edit:AET-DOC-PROJECT-PLAN", "planMinor:AET-DOC-PROJECT-PLAN", "newDocument:", "planCreate:"]);

  receiver?.({ type: "action", action: "apply", artifactId: "AET-DOC-PROJECT-PLAN" });
  receiver?.({ type: "action", action: "compare", artifactId: "AET-DOC-NOT-LISTED" });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["edit:AET-DOC-PROJECT-PLAN", "planMinor:AET-DOC-PROJECT-PLAN", "newDocument:", "planCreate:"]);
  manager.dispose();
});

test("manager permits Apply only for a selected document with a ready plan", async () => {
  const document: ManagedDocument = {
    artifact_id: "AET-DOC-PROJECT-PLAN", title: "Project Plan",
    path: "project/planning/PROJECT_PLAN.md", absolutePath: "C:\\repo\\project\\planning\\PROJECT_PLAN.md",
    kind: "document", version: "6.20", generated: false, scope: "ACTIVE",
  };
  let receiver: ((message: unknown) => void) | undefined;
  const actions: string[] = [];
  const posted: unknown[] = [];
  const panel = {
    webview: {
      html: "",
      postMessage: async (message: unknown) => { posted.push(message); return true; },
      onDidReceiveMessage: (listener: (message: unknown) => void) => {
        receiver = listener; return { dispose() {} };
      },
    },
    onDidDispose: () => ({ dispose() {} }), dispose() {}, reveal() {},
  };
  const host = { ViewColumn: { One: 1 }, window: { createWebviewPanel: () => panel } } as unknown as typeof vscode;
  let state: "PLAN_READY" | "PLAN_STALE" | "APPLY_PASS" = "PLAN_READY";
  const manager = new DocumentManager(host, () => [document], () => "Ready", async (action) => {
    actions.push(action);
    if (action === "apply") state = "APPLY_PASS";
    return { ok: true, message: "Done" };
  }, () => state);
  manager.show();
  receiver?.({ type: "ready" });
  assert.equal((posted.at(-1) as { documents: { planState: string }[] }).documents[0]?.planState, "PLAN_READY");
  receiver?.({ type: "action", action: "apply", artifactId: document.artifact_id });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["apply"]);
  assert.equal((posted.at(-1) as { documents: { planState: string }[] }).documents[0]?.planState, "APPLY_PASS");
  state = "PLAN_STALE";
  receiver?.({ type: "action", action: "apply", artifactId: document.artifact_id });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["apply"]);
  manager.dispose();
});

test("manager gates CREATE Apply on a prepared plan without a selected existing document", async () => {
  let receiver: ((message: unknown) => void) | undefined;
  const actions: string[] = [];
  const posted: unknown[] = [];
  const panel = {
    webview: { html: "", postMessage: async (message: unknown) => { posted.push(message); return true; },
      onDidReceiveMessage: (listener: (message: unknown) => void) => { receiver = listener; return { dispose() {} }; } },
    onDidDispose: () => ({ dispose() {} }), dispose() {}, reveal() {},
  };
  const host = { ViewColumn: { One: 1 }, window: { createWebviewPanel: () => panel } } as unknown as typeof vscode;
  let ready = false;
  const manager = new DocumentManager(host, () => [], () => "Ready", async (action) => {
    actions.push(action);
    return { ok: true, message: "Done" };
  }, undefined, () => "CREATE plan ready", undefined, () => ready);
  manager.show();
  receiver?.({ type: "ready" });
  assert.equal((posted.at(-1) as { createPlanReady: boolean }).createPlanReady, false);
  receiver?.({ type: "action", action: "applyCreate" });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, []);
  ready = true;
  manager.refresh();
  assert.equal((posted.at(-1) as { createPlanReady: boolean }).createPlanReady, true);
  receiver?.({ type: "action", action: "applyCreate" });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["applyCreate"]);
  manager.dispose();
});

test("governance GUI routes only a ready governance plan and excludes ordinary Apply", async () => {
  const document: ManagedDocument = {
    artifact_id: "AET-DOC-GITHUB-WORKFLOW", title: "GitHub Workflow",
    path: "project/governance/workflows/GITHUB_WORKFLOW.md",
    absolutePath: "C:\\repo\\project\\governance\\workflows\\GITHUB_WORKFLOW.md",
    kind: "document", version: "1.1", generated: false, scope: "ACTIVE",
  };
  let receiver: ((message: unknown) => void) | undefined;
  const actions: string[] = [];
  const panel = {
    webview: { html: "", postMessage: async () => true,
      onDidReceiveMessage: (listener: (message: unknown) => void) => { receiver = listener; return { dispose() {} }; } },
    onDidDispose: () => ({ dispose() {} }), dispose() {}, reveal() {},
  };
  const host = { ViewColumn: { One: 1 }, window: { createWebviewPanel: () => panel } } as unknown as typeof vscode;
  let governance = false;
  let ready = false;
  const manager = new DocumentManager(host, () => [document], () => "Ready", async (action) => {
    actions.push(action);
    return { ok: true, message: "Done" };
  }, () => ready ? "PLAN_READY" : "PLAN_STALE", () => "", () => governance);
  manager.show();
  receiver?.({ type: "action", action: "applyGovernance", artifactId: document.artifact_id });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, []);
  governance = true;
  ready = true;
  receiver?.({ type: "action", action: "apply", artifactId: document.artifact_id });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, []);
  receiver?.({ type: "action", action: "applyGovernance", artifactId: document.artifact_id });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["applyGovernance"]);
  manager.dispose();
});

test("minor and git-only plan notifications do not hold Manager actions busy", async () => {
  const document: ManagedDocument = {
    artifact_id: "AET-DOC-PROJECT-PLAN", title: "Project Plan",
    path: "project/planning/PROJECT_PLAN.md", absolutePath: "C:\\repo\\project\\planning\\PROJECT_PLAN.md",
    kind: "document", version: "6.20", generated: false, scope: "ACTIVE",
  };
  for (const planAction of ["planMinor", "plan"] as const) {
    let receiver: ((message: unknown) => void) | undefined;
    let dismissNotice: ((choice: string | undefined) => void) | undefined;
    let comparedFromNotice = 0;
    const errors: unknown[] = [];
    const actions: string[] = [];
    const notice = new Promise<string | undefined>((resolve) => { dismissNotice = resolve; });
    const panel = {
      webview: {
        html: "",
        postMessage: async () => true,
        onDidReceiveMessage: (listener: (message: unknown) => void) => {
          receiver = listener; return { dispose() {} };
        },
      },
      onDidDispose: () => ({ dispose() {} }), dispose() {}, reveal() {},
    };
    const host = { ViewColumn: { One: 1 }, window: { createWebviewPanel: () => panel } } as unknown as typeof vscode;
    const manager = new DocumentManager(host, () => [document], () => "Ready", async (action) => {
      actions.push(action);
      if (action === planAction) {
        notifyPlanReady(
          () => notice,
          async () => { comparedFromNotice += 1; },
          (error) => { errors.push(error); },
        );
      }
      return { ok: true, message: "Done" };
    });
    manager.show();
    receiver?.({ type: "action", action: planAction, artifactId: document.artifact_id });
    await new Promise<void>((resolve) => setImmediate(resolve));
    receiver?.({ type: "action", action: "edit", artifactId: document.artifact_id });
    await new Promise<void>((resolve) => setImmediate(resolve));
    receiver?.({ type: "action", action: "compare", artifactId: document.artifact_id });
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.deepEqual(actions, [planAction, "edit", "compare"]);
    dismissNotice?.(planAction === "planMinor" ? undefined : "Compare Candidate");
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.equal(comparedFromNotice, planAction === "planMinor" ? 0 : 1);
    receiver?.({ type: "action", action: "edit", artifactId: document.artifact_id });
    await new Promise<void>((resolve) => setImmediate(resolve));
    assert.deepEqual(actions, [planAction, "edit", "compare", "edit"]);
    assert.deepEqual(errors, []);
    manager.dispose();
  }
});

test("Manager remains busy during Apply and unlocks after cancellation", async () => {
  const document: ManagedDocument = {
    artifact_id: "AET-DOC-PROJECT-PLAN", title: "Project Plan",
    path: "project/planning/PROJECT_PLAN.md", absolutePath: "C:\\repo\\project\\planning\\PROJECT_PLAN.md",
    kind: "document", version: "6.20", generated: false, scope: "ACTIVE",
  };
  let receiver: ((message: unknown) => void) | undefined;
  let cancelApply: ((result: { ok: boolean; message: string }) => void) | undefined;
  const apply = new Promise<{ ok: boolean; message: string }>((resolve) => { cancelApply = resolve; });
  const actions: string[] = [];
  const posted: unknown[] = [];
  const panel = {
    webview: {
      html: "",
      postMessage: async (message: unknown) => { posted.push(message); return true; },
      onDidReceiveMessage: (listener: (message: unknown) => void) => {
        receiver = listener; return { dispose() {} };
      },
    },
    onDidDispose: () => ({ dispose() {} }), dispose() {}, reveal() {},
  };
  const host = { ViewColumn: { One: 1 }, window: { createWebviewPanel: () => panel } } as unknown as typeof vscode;
  const manager = new DocumentManager(host, () => [document], () => "Ready", async (action) => {
    actions.push(action);
    return action === "apply" ? apply : { ok: true, message: "Done" };
  }, () => "PLAN_READY");
  manager.show();
  receiver?.({ type: "action", action: "apply", artifactId: document.artifact_id });
  await new Promise<void>((resolve) => setImmediate(resolve));
  receiver?.({ type: "action", action: "edit", artifactId: document.artifact_id });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["apply"]);
  assert.ok(posted.some((message) => (message as { status?: string }).status === "Another Document Manager action is still running."));
  cancelApply?.({ ok: false, message: "Cancelled" });
  await new Promise<void>((resolve) => setImmediate(resolve));
  receiver?.({ type: "action", action: "edit", artifactId: document.artifact_id });
  await new Promise<void>((resolve) => setImmediate(resolve));
  assert.deepEqual(actions, ["apply", "edit"]);
  manager.dispose();
});
