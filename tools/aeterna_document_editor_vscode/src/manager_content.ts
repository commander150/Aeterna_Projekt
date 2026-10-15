import type { ManagedDocument } from "./registry";

export type ManagerAction = "edit" | "compare" | "plan" | "apply" | "refresh";

export type ManagerPlanState =
  | "PLAN_MISSING" | "CANDIDATE_SAVED" | "PLAN_READY" | "PLAN_READY_MISMATCH" | "PLAN_STALE"
  | "APPLY_RUNNING" | "APPLY_PASS" | "APPLY_FAIL" | "APPLY_BLOCKED";

export function managerPlanStateLabel(state: ManagerPlanState): string {
  return ({
    PLAN_MISSING: "Plan missing. Save a candidate, then prepare an UPDATE plan.",
    CANDIDATE_SAVED: "Candidate saved. Prepare a read-only UPDATE plan.",
    PLAN_READY: "Plan ready. Review the diff and plan before explicit Apply.",
    PLAN_READY_MISMATCH: "Plan ready — VERSION RECOMMENDATION MISMATCH. Planner recommends a different intent; Apply requires a second explicit confirmation. Version will not increase.",
    PLAN_STALE: "Plan stale. Prepare a new plan before Apply.",
    APPLY_RUNNING: "Governed Apply in progress. Do not close or repeat it.",
    APPLY_PASS: "Apply passed. Review Git changes in GitHub Desktop; commit and push are manual.",
    APPLY_FAIL: "Apply failed. Inspect production review and rollback evidence.",
    APPLY_BLOCKED: "Apply blocked. Inspect the reason and prepare a new plan.",
  } satisfies Record<ManagerPlanState, string>)[state];
}

export type ManagerMessage =
  | { readonly type: "ready" }
  | { readonly type: "search"; readonly query: string }
  | { readonly type: "action"; readonly action: ManagerAction; readonly artifactId?: string };

export interface ManagerActionResult {
  readonly ok: boolean;
  readonly message: string;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function parseManagerMessage(value: unknown): ManagerMessage | undefined {
  if (!isRecord(value)) {
    return undefined;
  }
  if (value.type === "ready" && Object.keys(value).length === 1) {
    return { type: "ready" };
  }
  if (value.type === "search" && typeof value.query === "string" && value.query.length <= 256
    && Object.keys(value).length === 2) {
    return { type: "search", query: value.query };
  }
  if (value.type !== "action" || typeof value.action !== "string") {
    return undefined;
  }
  const actions: readonly string[] = ["edit", "compare", "plan", "apply", "refresh"];
  if (!actions.includes(value.action)) {
    return undefined;
  }
  if (value.action === "refresh" && Object.keys(value).length === 2) {
    return { type: "action", action: "refresh" };
  }
  if (value.action !== "refresh" && typeof value.artifactId === "string"
    && /^AET-DOC-[A-Z0-9]+(?:-[A-Z0-9]+)*$/.test(value.artifactId)
    && Object.keys(value).length === 3) {
    return { type: "action", action: value.action as ManagerAction, artifactId: value.artifactId };
  }
  return undefined;
}

export function filterManagedDocuments(
  documents: readonly ManagedDocument[],
  query: string,
): readonly ManagedDocument[] {
  const needle = query.trim().toLocaleLowerCase();
  if (!needle) {
    return documents;
  }
  return documents.filter((document) => [
    document.artifact_id,
    document.title,
    document.path,
  ].some((value) => value.toLocaleLowerCase().includes(needle)));
}

export function renderManagerHtml(nonce: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-${nonce}'; style-src 'nonce-${nonce}';">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AETERNA Document Manager</title>
  <style nonce="${nonce}">
    body { font-family: var(--vscode-font-family); color: var(--vscode-foreground); padding: 16px; }
    h1 { font-size: 1.3rem; margin: 0 0 8px; }
    p { line-height: 1.45; }
    input { box-sizing: border-box; width: 100%; padding: 7px; color: var(--vscode-input-foreground); background: var(--vscode-input-background); border: 1px solid var(--vscode-input-border); }
    .layout { display: grid; grid-template-columns: minmax(240px, 1fr) minmax(260px, 1fr); gap: 16px; margin-top: 16px; }
    .list { max-height: 60vh; overflow: auto; border: 1px solid var(--vscode-panel-border); }
    .row { width: 100%; display: block; text-align: left; padding: 9px; color: var(--vscode-foreground); background: transparent; border: 0; border-bottom: 1px solid var(--vscode-panel-border); cursor: pointer; }
    .row:hover, .row:focus { background: var(--vscode-list-hoverBackground); }
    .row[aria-selected="true"] { background: var(--vscode-list-activeSelectionBackground); color: var(--vscode-list-activeSelectionForeground); }
    .row-title { display: block; font-weight: 600; }
    .row-detail { display: block; font-size: 0.85em; overflow-wrap: anywhere; }
    .details { border: 1px solid var(--vscode-panel-border); padding: 12px; min-height: 180px; }
    .details dl { display: grid; grid-template-columns: max-content 1fr; gap: 6px 10px; }
    .details dd { margin: 0; overflow-wrap: anywhere; }
    .actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
    button.action { padding: 7px 10px; border: 1px solid var(--vscode-button-border); color: var(--vscode-button-foreground); background: var(--vscode-button-background); cursor: pointer; }
    button.action:hover:not(:disabled) { background: var(--vscode-button-hoverBackground); }
    button.action:disabled { opacity: 0.5; cursor: default; }
    #status { margin-top: 16px; padding: 8px; border-left: 3px solid var(--vscode-focusBorder); overflow-wrap: anywhere; }
    @media (max-width: 720px) { .layout { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <h1>AETERNA Document Manager</h1>
  <p>Choose a managed document. Saving a candidate does not change its canonical document. Apply requires a reviewed plan and separate confirmation; version stays unchanged.</p>
  <label for="search">Search by name, title, path or artifact ID</label>
  <input id="search" type="search" autocomplete="off" placeholder="Search managed documents">
  <div class="layout">
    <section aria-label="Managed documents">
      <p id="count">Loading documents…</p>
      <div id="documents" class="list" role="listbox" aria-label="Managed documents"></div>
    </section>
    <section class="details" aria-label="Selected document">
      <h2>Selected document</h2>
      <p id="empty">Select a document from the list.</p>
      <dl id="fields" hidden></dl>
      <p id="plan-state" role="status">Plan missing.</p>
      <div class="actions">
        <button class="action" type="button" data-action="edit" disabled>Edit Candidate + Preview</button>
        <button class="action" type="button" data-action="compare" disabled>Compare Candidate</button>
        <button class="action" type="button" data-action="plan" disabled>Read-only UPDATE Plan</button>
        <button class="action" type="button" data-action="apply" disabled>Apply Prepared UPDATE</button>
        <button class="action" type="button" data-action="refresh">Refresh List</button>
      </div>
    </section>
  </div>
  <p id="status" role="status" aria-live="polite">Loading…</p>
  <script nonce="${nonce}">
    (() => {
      const vscode = acquireVsCodeApi();
      const search = document.getElementById("search");
      const list = document.getElementById("documents");
      const count = document.getElementById("count");
      const empty = document.getElementById("empty");
      const fields = document.getElementById("fields");
      const planState = document.getElementById("plan-state");
      const status = document.getElementById("status");
      const buttons = [...document.querySelectorAll("button[data-action]")];
      let documents = [];
      let selectedId;

      function showDetails() {
        const selected = documents.find((item) => item.artifactId === selectedId);
        fields.replaceChildren();
        empty.hidden = Boolean(selected);
        fields.hidden = !selected;
        for (const button of buttons) {
          if (button.dataset.action === "apply") button.disabled = !selected || !["PLAN_READY", "PLAN_READY_MISMATCH"].includes(selected.planState);
          else if (button.dataset.action !== "refresh") button.disabled = !selected;
        }
        planState.textContent = selected ? selected.planStateLabel : "Plan missing.";
        if (!selected) return;
        for (const [label, value] of [
          ["Artifact ID", selected.artifactId], ["Title", selected.title],
          ["Canonical path", selected.path], ["Version", selected.version],
        ]) {
          const term = document.createElement("dt");
          const detail = document.createElement("dd");
          term.textContent = label;
          detail.textContent = value;
          fields.append(term, detail);
        }
      }

      function renderList() {
        list.replaceChildren();
        count.textContent = documents.length + " managed document(s) shown";
        for (const item of documents) {
          const row = document.createElement("button");
          row.type = "button";
          row.className = "row";
          row.setAttribute("role", "option");
          row.setAttribute("aria-selected", String(item.artifactId === selectedId));
          const title = document.createElement("span");
          title.className = "row-title";
          title.textContent = item.title;
          const detail = document.createElement("span");
          detail.className = "row-detail";
          detail.textContent = item.artifactId + " · v" + item.version + " · " + item.path;
          row.append(title, detail);
          row.addEventListener("click", () => {
            selectedId = item.artifactId;
            renderList();
            showDetails();
          });
          list.append(row);
        }
        showDetails();
      }

      search.addEventListener("input", () => vscode.postMessage({ type: "search", query: search.value }));
      for (const button of buttons) {
        button.addEventListener("click", () => {
          const action = button.dataset.action;
          if (action === "refresh") vscode.postMessage({ type: "action", action });
          else if (selectedId) vscode.postMessage({ type: "action", action, artifactId: selectedId });
        });
      }
      window.addEventListener("message", (event) => {
        const message = event.data;
        if (message?.type === "documents" && Array.isArray(message.documents)) {
          documents = message.documents;
          if (!documents.some((item) => item.artifactId === selectedId)) selectedId = undefined;
          renderList();
          status.textContent = message.status;
        } else if (message?.type === "status" && typeof message.status === "string") {
          status.textContent = message.status;
        }
      });
      vscode.postMessage({ type: "ready" });
    })();
  </script>
</body>
</html>`;
}

