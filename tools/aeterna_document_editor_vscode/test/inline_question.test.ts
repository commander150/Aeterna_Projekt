import assert from "node:assert/strict";
import { test } from "node:test";
import type * as vscode from "vscode";

import { DocumentManager, routeLowRiskQuestion, routeUpdateApplyQuestion, updateApplyQuestion, updateMismatchQuestion } from "../src/manager";
import type { ApplySummary } from "../src/apply_update";
import type { ManagedDocument } from "../src/registry";
import type { InlineQuestion, ManagerAction, ManagerPlanState } from "../src/manager_content";

const document: ManagedDocument = {
  artifact_id: "AET-DOC-PROJECT-PLAN", title: "Project Plan",
  path: "project/planning/PROJECT_PLAN.md", absolutePath: "C:\\repo\\project\\planning\\PROJECT_PLAN.md",
  kind: "document", version: "6.20", generated: false, scope: "ACTIVE",
};

const updateSummary: ApplySummary = {
  artifactId: document.artifact_id, title: document.title, version: "6.20", proposedVersion: "6.21",
  versionIntent: "minor", branch: "main", head: "a".repeat(40), baselineSha256: "b".repeat(64),
  candidateSha256: "c".repeat(64), planSemanticSha256: "d".repeat(64),
  plannedWrites: [document.path, "project/generated/artifacts_registry.json", "project/generated/DOCUMENT_INDEX.md"],
  dependencyImpact: "direct: none; transitive: none", recommendedIntent: "minor", mismatch: false,
};

function harness(deliver = true, reviewGate?: Promise<void>, rejectPost = false,
  scenario: { action?: ManagerAction; cancelConsequence?: string; planState?: ManagerPlanState; completed?: boolean;
    question?: InlineQuestion; secondQuestion?: InlineQuestion; approvedChoice?: string; secondApprovedChoice?: string } = {}) {
  let receiver: ((message: unknown) => void) | undefined;
  let closePanel: (() => void) | undefined;
  let disposeCurrent: (() => void) | undefined;
  let root = "C:\\repo";
  const posted: unknown[] = [];
  const diagnostics: string[] = [];
  const results: (string | undefined)[] = [];
  const actions: string[] = [];
  const host = { ViewColumn: { One: 1 }, window: { createWebviewPanel: () => {
    let disposed = false;
    let onDispose: (() => void) | undefined;
    const dispose = () => { if (!disposed) { disposed = true; onDispose?.(); } };
    closePanel = dispose;
    disposeCurrent = dispose;
    return {
      webview: { html: "", postMessage: (message: unknown) => {
        if (disposed) throw new Error("Webview is disposed");
        if (rejectPost) return Promise.reject(new Error("Webview delivery failed"));
        posted.push(message);
        return Promise.resolve(deliver);
      }, onDidReceiveMessage: (listener: (message: unknown) => void) => { receiver = listener; return { dispose() {} }; } },
      onDidDispose: (listener: () => void) => { onDispose = listener; return { dispose() {} }; },
      reveal() { if (disposed) throw new Error("Webview is disposed"); }, dispose,
    };
  } } } as unknown as typeof vscode;
  let manager: DocumentManager;
  const questionAction = scenario.action ?? "plan";
  manager = new DocumentManager(host, () => [document], () => "Ready", async (action) => {
    actions.push(action);
    if (action === questionAction) {
      const question = manager.ask(scenario.question ?? {
        title: "Terv?", explanation: "Csak read-only terv.", document: document.artifact_id,
        consequence: "Nincs canonical írás.",
        cancelConsequence: scenario.cancelConsequence,
        completed: scenario.completed,
        choices: [{ id: "approve", label: "Terv készítése" }, { id: "review", label: "Diff", review: true }],
      }, {
        review: async () => { actions.push("review"); await reviewGate; },
        "review-diff": async () => { actions.push("review-diff"); await reviewGate; },
        "review-plan": async () => { actions.push("review-plan"); await reviewGate; },
      });
      if (scenario.completed) {
        void question;
        return { ok: true, message: "Completed before review notice" };
      }
      results.push(await question);
      if (scenario.secondQuestion && results.at(-1) === (scenario.approvedChoice ?? "approve")) {
        results.push(await manager.ask(scenario.secondQuestion));
      }
    }
    return { ok: action !== questionAction || results.at(-1) ===
      (scenario.secondQuestion ? scenario.secondApprovedChoice ?? "approve" : scenario.approvedChoice ?? "approve"), message: "Done" };
  }, () => scenario.planState ?? "PLAN_MISSING", undefined, undefined, undefined, undefined, () => root,
  (message) => { diagnostics.push(message); });
  const send = (message: unknown) => receiver?.(message);
  const question = () => (posted.filter((item) => (item as { type?: string }).type === "question")
    .map((item) => (item as { question?: { id: string } }).question).filter(Boolean).at(-1)) as { id: string };
  const settle = () => new Promise<void>((resolve) => setImmediate(resolve));
  manager.show();
  send({ type: "ready" });
  const status = () => posted.filter((item) => (item as { type?: string }).type === "status")
    .at(-1) as { status: string; nextStep: string } | undefined;
  return { manager, send, question, settle, results, actions, posted, diagnostics, status,
    close: () => closePanel?.(), disposeCurrent: () => disposeCurrent?.(),
    changeRoot: (value: string) => { root = value; manager.refresh(); } };
}

test("inline approval is accepted once; duplicate and replayed responses cannot approve again", async () => {
  const h = harness();
  h.send({ type: "action", action: "plan", artifactId: document.artifact_id });
  const id = h.question().id;
  h.send({ type: "answer", questionId: id, choice: "invalid" });
  assert.deepEqual(h.results, []);
  h.send({ type: "answer", questionId: id, choice: "approve" });
  h.send({ type: "answer", questionId: id, choice: "approve" });
  await h.settle();
  assert.deepEqual(h.results, ["approve"]);
  h.send({ type: "action", action: "plan", artifactId: document.artifact_id });
  assert.notEqual(h.question().id, id);
  h.send({ type: "answer", questionId: id, choice: "approve" });
  assert.deepEqual(h.results, ["approve"]);
  h.send({ type: "answer", questionId: h.question().id, choice: "cancel" });
  await h.settle();
  assert.deepEqual(h.results, ["approve", undefined]);
  h.manager.dispose();
});

test("Cancel, panel close and repository switch all reject a pending inline question", async () => {
  for (const abort of ["cancel", "close", "root"] as const) {
    const h = harness();
    h.send({ type: "action", action: "plan", artifactId: document.artifact_id });
    const id = h.question().id;
    if (abort === "cancel") h.send({ type: "answer", questionId: id, choice: "cancel" });
    if (abort === "close") h.close();
    if (abort === "root") h.changeRoot("C:\\another-repo");
    await h.settle();
    assert.deepEqual(h.results, [undefined]);
    if (abort !== "close") assert.equal(h.status()?.status, "A művelet megszakítva.");
    h.send({ type: "answer", questionId: id, choice: "approve" });
    assert.deepEqual(h.results, [undefined]);
    h.manager.dispose();
  }
});

test("pending question blocks parallel actions, while Review opens content without approval", async () => {
  const h = harness();
  h.send({ type: "action", action: "plan", artifactId: document.artifact_id });
  h.send({ type: "action", action: "edit", artifactId: document.artifact_id });
  assert.deepEqual(h.actions, ["plan"]);
  h.send({ type: "answer", questionId: h.question().id, choice: "review" });
  await h.settle();
  assert.deepEqual(h.actions, ["plan", "review"]);
  assert.deepEqual(h.results, [undefined]);
  h.manager.dispose();
});

test("commands outside the Manager keep the native fallback even while a Manager action is active", async () => {
  const h = harness();
  h.send({ type: "action", action: "plan", artifactId: document.artifact_id });
  const currentId = h.question().id;
  const fallback = await routeLowRiskQuestion(h.manager, false, {
    title: "Other command", explanation: "Native fallback", document: document.artifact_id,
    consequence: "No writes", choices: [{ id: "approve", label: "Approve" }],
  }, async () => "native");
  assert.equal(fallback, "native");
  assert.equal(h.question().id, currentId);
  h.send({ type: "answer", questionId: currentId, choice: "cancel" });
  await h.settle();
  h.manager.dispose();
});

test("undeliverable Webview question cancels instead of leaving an operation waiting", async () => {
  const h = harness(false);
  h.send({ type: "action", action: "plan", artifactId: document.artifact_id });
  await h.settle();
  assert.deepEqual(h.results, [undefined]);
  h.manager.dispose();
});

test("Review remains exclusive even if the outer Manager action finishes first", async () => {
  let finishReview: (() => void) | undefined;
  const reviewGate = new Promise<void>((resolve) => { finishReview = resolve; });
  const h = harness(true, reviewGate);
  h.send({ type: "action", action: "plan", artifactId: document.artifact_id });
  h.send({ type: "answer", questionId: h.question().id, choice: "review" });
  await h.settle();
  h.send({ type: "action", action: "edit", artifactId: document.artifact_id });
  assert.deepEqual(h.actions, ["plan", "review"]);
  finishReview?.();
  await h.settle();
  h.send({ type: "action", action: "edit", artifactId: document.artifact_id });
  await h.settle();
  assert.deepEqual(h.actions, ["plan", "review", "edit"]);
  h.manager.dispose();
});

test("closing a panel with a pending question cancels without posting to the disposed Webview", async () => {
  const h = harness();
  h.send({ type: "action", action: "plan", artifactId: document.artifact_id });
  const id = h.question().id;
  assert.match(h.status()?.status ?? "", /Jóváhagyásra vár/);
  h.close();
  h.manager.show();
  h.send({ type: "ready" });
  await h.settle();
  assert.deepEqual(h.results, [undefined]);
  assert.equal(h.manager.actionActive, false);
  assert.equal(h.diagnostics.some((item) => item.includes("Webview is disposed")), false);
  assert.equal((h.posted.at(-1) as { status?: string }).status, "A művelet megszakítva.");
  h.send({ type: "answer", questionId: id, choice: "approve" });
  h.send({ type: "action", action: "plan", artifactId: document.artifact_id });
  assert.notEqual(h.question().id, id);
  h.send({ type: "answer", questionId: h.question().id, choice: "approve" });
  assert.match(h.status()?.status ?? "", /végrehajtása folyamatban/);
  await h.settle();
  assert.deepEqual(h.results, [undefined, "approve"]);
  assert.equal((h.posted.at(-2) as { status?: string }).status, "A terv elkészült. A canonical dokumentum nem módosult.");
  h.manager.dispose();
});

test("status refresh racing panel disposal and late metadata cannot address a closed or reopened panel", async () => {
  let finishMetadata: ((value: { artifactId: string; fields: {}; allowed: {}; rules: string }) => void) | undefined;
  const metadata = new Promise<{ artifactId: string; fields: {}; allowed: {}; rules: string }>((resolve) => { finishMetadata = resolve; });
  let receiver: ((message: unknown) => void) | undefined;
  let disposePanel: (() => void) | undefined;
  let disposed = false;
  const posts: unknown[][] = [];
  const host = { ViewColumn: { One: 1 }, window: { createWebviewPanel: () => {
    disposed = false;
    const ownPosts: unknown[] = [];
    posts.push(ownPosts);
    return { webview: { html: "", postMessage: (message: unknown) => {
      if (disposed) throw new Error("Webview is disposed");
      ownPosts.push(message); return Promise.resolve(true);
    }, onDidReceiveMessage: (listener: (message: unknown) => void) => { receiver = listener; return { dispose() {} }; } },
    onDidDispose: (listener: () => void) => { disposePanel = () => { disposed = true; listener(); }; return { dispose() {} }; },
    reveal() {}, dispose() { disposePanel?.(); } };
  } } } as unknown as typeof vscode;
  const manager = new DocumentManager(host, () => [document], () => "Ready", async () => ({ ok: true, message: "Done" }),
    undefined, undefined, undefined, undefined, () => metadata);
  manager.show();
  receiver?.({ type: "select", artifactId: document.artifact_id });
  const oldReceiver = receiver;
  disposePanel?.();
  manager.refresh();
  manager.show();
  receiver?.({ type: "ready" });
  finishMetadata?.({ artifactId: document.artifact_id, fields: {}, allowed: {}, rules: "read only" });
  await new Promise<void>((resolve) => setImmediate(resolve));
  oldReceiver?.({ type: "action", action: "plan", artifactId: document.artifact_id });
  assert.equal(posts[0]?.some((item) => (item as { type?: string }).type === "metadata"), false);
  assert.equal(posts[1]?.some((item) => (item as { type?: string }).type === "metadata"), false);
  manager.dispose();
});

test("rejected Webview delivery ends pending question and records a diagnostic without unhandled rejection", async () => {
  const h = harness(true, undefined, true);
  h.send({ type: "action", action: "plan", artifactId: document.artifact_id });
  await h.settle();
  assert.deepEqual(h.results, [undefined]);
  assert.equal(h.manager.actionActive, false);
  assert.ok(h.diagnostics.some((item) => item.includes("Webview delivery failed")));
  h.manager.dispose();
});

test("each UX-2A cancellation keeps its specific consequence after selection and refresh", async () => {
  const cases: readonly { action: ManagerAction; consequence: string }[] = [
    { action: "planMinor", consequence: "A candidate verziója nem módosult, új terv nem készült; a meglévő candidate és terv megmaradt." },
    { action: "plan", consequence: "Nem készült új terv, a candidate nem módosult; a korábbi terv megmaradt." },
    { action: "newDocument", consequence: "Nem jött létre új CREATE candidate; a megadott adatok nem kerültek alkalmazásra." },
    { action: "edit", consequence: "Nem készült új baseline-candidate; a korábbi candidate és tartalma megmaradt." },
    { action: "compare", consequence: "Nem történt automatikus mentés vagy összehasonlítás; a szerkesztő mentetlen változásai megmaradtak." },
  ];
  for (const { action, consequence } of cases) {
    const h = harness(true, undefined, false, { action, cancelConsequence: consequence, planState: "CANDIDATE_SAVED" });
    h.send({ type: "select", artifactId: document.artifact_id });
    h.send({ type: "action", action, ...(action === "newDocument" ? {} : { artifactId: document.artifact_id }) });
    h.send({ type: "answer", questionId: h.question().id, choice: "cancel" });
    await h.settle();
    const lastDocuments = h.posted.filter((item) => (item as { type?: string }).type === "documents")
      .at(-1) as { status: string; nextStep: string };
    assert.equal(lastDocuments.status, "A művelet megszakítva.", action);
    assert.equal(lastDocuments.nextStep, consequence, action);
    h.manager.refresh();
    const refreshed = h.posted.at(-1) as { status: string; nextStep: string };
    assert.equal(refreshed.status, "A művelet megszakítva.", action);
    assert.equal(refreshed.nextStep, consequence, action);
    assert.deepEqual(h.results, [undefined]);
    h.manager.dispose();
  }
});

test("dismissing a completed plan or Apply review notice does not label the completed operation cancelled", async () => {
  for (const { action, planState, consequence, expected } of [
    { action: "plan" as const, planState: "PLAN_MISSING" as const,
      consequence: "A read-only terv már elkészült; a canonical dokumentum nem módosult.",
      expected: "A terv elkészült. A canonical dokumentum nem módosult." },
    { action: "planCreate" as const, planState: "PLAN_MISSING" as const,
      consequence: "A read-only CREATE-terv már elkészült; canonical dokumentum nem jött létre.",
      expected: "A terv elkészült. A canonical dokumentum nem módosult." },
    { action: "apply" as const, planState: "PLAN_READY" as const,
      consequence: "A sikeres Apply eredménye és production review-ja megmaradt.",
      expected: "Az Apply és a production ellenőrzés sikeres." },
  ]) {
    const h = harness(true, undefined, false, { action, planState, cancelConsequence: consequence, completed: true });
    if (action !== "planCreate") h.send({ type: "select", artifactId: document.artifact_id });
    h.send({ type: "action", action, ...(action === "planCreate" ? {} : { artifactId: document.artifact_id }) });
    await h.settle();
    assert.equal(h.status()?.status, expected);
    h.send({ type: "answer", questionId: h.question().id, choice: "cancel" });
    assert.equal(h.status()?.status, "A tájékoztatás bezárva.");
    assert.equal(h.status()?.nextStep, consequence);
    h.manager.dispose();
  }
});

test("UPDATE Apply question shows document, version and writes; Review never approves", async () => {
  const question = updateApplyQuestion(updateSummary, `Plan SHA-256: ${updateSummary.planSemanticSha256}`);
  assert.match(question.explanation, /6\.20 → 6\.21/);
  assert.match(question.explanation, /artifacts_registry\.json/);
  assert.equal(question.document, `${document.artifact_id} — ${document.title}`);
  assert.match(question.details ?? "", /Plan SHA-256/);
  const h = harness(true, undefined, false, { action: "apply", planState: "PLAN_READY", question, approvedChoice: "apply-update" });
  h.send({ type: "action", action: "apply", artifactId: document.artifact_id });
  const reviewedId = h.question().id;
  h.send({ type: "answer", questionId: reviewedId, choice: "review-diff" });
  await h.settle();
  assert.deepEqual(h.results, [undefined]);
  assert.deepEqual(h.actions, ["apply", "review-diff"]);
  assert.equal(h.status()?.status, "A művelet megszakítva.");
  h.send({ type: "action", action: "apply", artifactId: document.artifact_id });
  const newId = h.question().id;
  assert.notEqual(newId, reviewedId);
  h.send({ type: "answer", questionId: reviewedId, choice: "apply-update" });
  assert.deepEqual(h.results, [undefined]);
  h.send({ type: "answer", questionId: newId, choice: "review-plan" });
  await h.settle();
  assert.deepEqual(h.results, [undefined, undefined]);
  assert.ok(h.actions.includes("review-plan"));
  h.manager.dispose();
});

test("UPDATE Apply Cancel, close and repository switch fail closed; a reopened Manager needs a new answer", async () => {
  for (const abort of ["cancel", "close", "root"] as const) {
    const h = harness(true, undefined, false, {
      action: "apply", planState: "PLAN_READY", question: updateApplyQuestion(updateSummary, "plan details"),
      approvedChoice: "apply-update",
    });
    h.send({ type: "action", action: "apply", artifactId: document.artifact_id });
    const oldId = h.question().id;
    if (abort === "cancel") h.send({ type: "answer", questionId: oldId, choice: "cancel" });
    if (abort === "close") { h.close(); h.manager.show(); }
    if (abort === "root") h.changeRoot("C:\\different-repo");
    await h.settle();
    h.send({ type: "answer", questionId: oldId, choice: "apply-update" });
    assert.deepEqual(h.results, [undefined]);
    assert.equal(h.status()?.status, "A művelet megszakítva.");
    h.manager.dispose();
  }
});

test("UPDATE version mismatch is a second explicit question and its Cancel prevents completion", async () => {
  const summary = { ...updateSummary, versionIntent: "git-only" as const,
    proposedVersion: "6.20", recommendedIntent: "minor", mismatch: true };
  const first = updateApplyQuestion(summary, "reviewed plan");
  const second = updateMismatchQuestion(summary, "reviewed plan");
  assert.match(second.explanation, /minor/);
  assert.match(second.explanation, /git-only/);
  assert.equal(second.choices.length, 1);
  const h = harness(true, undefined, false, { action: "apply", planState: "PLAN_READY_MISMATCH",
    question: first, secondQuestion: second, approvedChoice: "apply-update", secondApprovedChoice: "approve-mismatch" });
  h.send({ type: "action", action: "apply", artifactId: document.artifact_id });
  const firstId = h.question().id;
  h.send({ type: "answer", questionId: firstId, choice: "apply-update" });
  await h.settle();
  const secondId = h.question().id;
  assert.notEqual(secondId, firstId);
  h.send({ type: "answer", questionId: firstId, choice: "approve-mismatch" });
  assert.deepEqual(h.results, ["apply-update"]);
  h.send({ type: "answer", questionId: secondId, choice: "cancel" });
  await h.settle();
  assert.deepEqual(h.results, ["apply-update", undefined]);
  assert.equal(h.status()?.status, "A művelet megszakítva.");
  h.manager.dispose();

  const accepted = harness(true, undefined, false, { action: "apply", planState: "PLAN_READY_MISMATCH",
    question: first, secondQuestion: second, approvedChoice: "apply-update", secondApprovedChoice: "approve-mismatch" });
  accepted.send({ type: "action", action: "apply", artifactId: document.artifact_id });
  accepted.send({ type: "answer", questionId: accepted.question().id, choice: "apply-update" });
  await accepted.settle();
  accepted.send({ type: "answer", questionId: accepted.question().id, choice: "approve-mismatch" });
  await accepted.settle();
  assert.deepEqual(accepted.results, ["apply-update", "approve-mismatch"]);
  assert.equal(accepted.status()?.status, "Az Apply és a production ellenőrzés sikeres.");
  accepted.manager.dispose();
});

test("UPDATE commands outside the Manager retain native approval; Manager origin never falls back when unavailable", async () => {
  const h = harness();
  const question = updateApplyQuestion(updateSummary, "details");
  const native = await routeUpdateApplyQuestion(h.manager, false, question, async () => "apply-update");
  assert.equal(native, "apply-update");
  h.manager.dispose();
  let fallbackCalled = false;
  const closed = await routeUpdateApplyQuestion(h.manager, true, question, async () => {
    fallbackCalled = true; return "apply-update";
  });
  assert.equal(closed, undefined);
  assert.equal(fallbackCalled, false);
});
