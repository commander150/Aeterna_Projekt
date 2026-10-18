import type { ManagedDocument } from "./registry";

export type ManagerAction = "edit" | "preview" | "compare" | "plan" | "planMinor" | "planGovernance" | "apply" | "applyGovernance" | "refresh" | "newDocument" | "compareCreate" | "planCreate" | "applyCreate";

export function isGovernanceDocument(path: string): boolean {
  return path.startsWith("project/governance/") && path.endsWith(".md") &&
    !path.includes("\\") && path.split("/").every((part) => part !== "" && part !== "." && part !== "..");
}

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
  | { readonly type: "select"; readonly artifactId: string }
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
  if (value.type === "select" && typeof value.artifactId === "string" &&
      /^AET-DOC-[A-Z0-9]+(?:-[A-Z0-9]+)*$/.test(value.artifactId) && Object.keys(value).length === 2) {
    return { type: "select", artifactId: value.artifactId };
  }
  if (value.type !== "action" || typeof value.action !== "string") {
    return undefined;
  }
  const actions: readonly string[] = ["edit", "preview", "compare", "plan", "planMinor", "planGovernance", "apply", "applyGovernance", "refresh", "newDocument", "compareCreate", "planCreate", "applyCreate"];
  if (!actions.includes(value.action)) {
    return undefined;
  }
  if (["refresh", "newDocument", "compareCreate", "planCreate", "applyCreate"].includes(value.action) && Object.keys(value).length === 2) {
    return { type: "action", action: value.action as "refresh" | "newDocument" | "compareCreate" | "planCreate" | "applyCreate" };
  }
  if (!["refresh", "newDocument", "compareCreate", "planCreate", "applyCreate"].includes(value.action) && typeof value.artifactId === "string"
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
<html lang="hu">
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
    .layout { display: grid; grid-template-columns: minmax(220px, 0.8fr) minmax(280px, 1.2fr); gap: 16px; margin-top: 16px; }
    .layout > * { min-width: 0; }
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
    .operation { margin-top: 16px; padding: 10px; border: 1px solid var(--vscode-panel-border); border-left: 3px solid var(--vscode-focusBorder); overflow-wrap: anywhere; }
    .operation h2 { margin: 0 0 8px; font-size: 1.05rem; }
    .operation p { margin: 5px 0; }
    @media (max-width: 720px) { .layout { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <h1>AETERNA Document Manager</h1>
  <p>Válasszon kezelt dokumentumot, vagy indítson új dokumentumot. A candidate mentése és a tervkészítés nem módosítja a canonical fájlokat. Az Apply külön jóváhagyást igényel.</p>
  <div class="actions" aria-label="New document actions">
    <button class="action" type="button" data-action="newDocument">New Document</button>
    <button class="action" type="button" data-action="compareCreate">Compare CREATE Candidate</button>
    <button class="action" type="button" data-action="planCreate">Prepare CREATE Plan (read only)</button>
    <button class="action" type="button" data-action="applyCreate" disabled>Apply Prepared CREATE</button>
  </div>
  <p id="create-state" role="status">No CREATE candidate open.</p>
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
      <p id="metadata-state" role="status">Select a document to inspect its canonical metadata.</p>
      <p id="metadata-rules" hidden></p>
      <p id="plan-state" role="status">Plan missing.</p>
      <div class="actions">
        <button class="action" type="button" data-action="edit" disabled>Candidate szerkesztése</button>
        <button class="action" type="button" data-action="preview" disabled>Markdown előnézet</button>
        <button class="action" type="button" data-action="compare" disabled>Compare Candidate</button>
        <button class="action" type="button" data-action="planMinor" disabled>Versioned UPDATE Plan (minor)</button>
        <button class="action" type="button" data-action="plan" disabled>Unchanged Version Plan (git-only)</button>
        <button class="action" type="button" data-action="planGovernance" disabled>Governance UPDATE Plan (major)</button>
        <button class="action" type="button" data-action="apply" disabled>Apply Prepared UPDATE</button>
        <button class="action" type="button" data-action="applyGovernance" disabled>Approve Governance Apply</button>
        <button class="action" type="button" data-action="refresh">Refresh List</button>
      </div>
    </section>
  </div>
  <section class="operation" aria-label="Művelet és visszajelzés">
    <h2>Művelet és visszajelzés</h2>
    <p id="status" role="status" aria-live="polite">Betöltés…</p>
    <p id="next-step"></p>
  </section>
  <script nonce="${nonce}">
    (() => {
      const vscode = acquireVsCodeApi();
      const search = document.getElementById("search");
      const list = document.getElementById("documents");
      const count = document.getElementById("count");
      const empty = document.getElementById("empty");
      const fields = document.getElementById("fields");
      const metadataState = document.getElementById("metadata-state");
      const metadataRules = document.getElementById("metadata-rules");
      const planState = document.getElementById("plan-state");
      const status = document.getElementById("status");
      const nextStep = document.getElementById("next-step");
      const createState = document.getElementById("create-state");
      const buttons = [...document.querySelectorAll("button[data-action]")];
      let documents = [];
      let selectedId;
      let selectedDocument;
      let createPlanReady = false;
      let metadata;

      function showDetails() {
        const selected = documents.find((item) => item.artifactId === selectedId) || selectedDocument;
        fields.replaceChildren();
        empty.hidden = Boolean(selected);
        fields.hidden = !selected;
        metadataState.textContent = selected ? (metadata?.artifactId === selectedId ? "Canonical metadata (read only):" : "Loading canonical metadata…") : "Select a document to inspect its canonical metadata.";
        metadataRules.hidden = !selected || metadata?.artifactId !== selectedId;
        metadataRules.textContent = metadata?.artifactId === selectedId ? metadata.rules : "";
        for (const button of buttons) {
          if (button.dataset.action === "applyCreate") button.disabled = !createPlanReady;
          else if (button.dataset.action === "apply") button.disabled = !selected || selected.governancePlan || !["PLAN_READY", "PLAN_READY_MISMATCH"].includes(selected.planState);
          else if (button.dataset.action === "applyGovernance") button.disabled = !selected || !selected.governancePlan || !["PLAN_READY", "PLAN_READY_MISMATCH"].includes(selected.planState);
          else if (button.dataset.action === "planGovernance") button.disabled = !selected || !selected.governance;
          else if (!["refresh", "newDocument", "planCreate", "applyCreate"].includes(button.dataset.action)) button.disabled = !selected;
        }
        planState.textContent = selected ? selected.planStateLabel : "Plan missing.";
        if (!selected) return;
        for (const [label, value] of [
          ["Artifact ID", selected.artifactId], ["Title", selected.title],
          ["Canonical path", selected.path],
        ]) {
          const term = document.createElement("dt");
          const detail = document.createElement("dd");
          term.textContent = label;
          detail.textContent = value;
          fields.append(term, detail);
        }
        if (metadata?.artifactId === selectedId) {
          for (const [label, value] of Object.entries(metadata.fields)) {
            const term = document.createElement("dt");
            const detail = document.createElement("dd");
            term.textContent = label;
            detail.textContent = Array.isArray(value) ? (value.join(", ") || "[]") : String(value);
            fields.append(term, detail);
          }
          for (const [label, values] of Object.entries(metadata.allowed)) {
            const term = document.createElement("dt");
            const detail = document.createElement("dd");
            term.textContent = label + " allowed";
            detail.textContent = values.join(", ");
            fields.append(term, detail);
          }
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
            selectedDocument = item;
            metadata = undefined;
            vscode.postMessage({ type: "select", artifactId: selectedId });
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
          if (["refresh", "newDocument", "compareCreate", "planCreate", "applyCreate"].includes(action)) vscode.postMessage({ type: "action", action });
          else if (selectedId) vscode.postMessage({ type: "action", action, artifactId: selectedId });
        });
      }
      window.addEventListener("message", (event) => {
        const message = event.data;
        if (message?.type === "documents" && Array.isArray(message.documents)) {
          documents = message.documents;
          createPlanReady = message.createPlanReady === true;
          const previousId = selectedId;
          selectedId = typeof message.selectedId === "string" ? message.selectedId : undefined;
          selectedDocument = message.selectedDocument?.artifactId === selectedId ? message.selectedDocument : undefined;
          if (previousId !== selectedId) metadata = undefined;
          if (typeof message.query === "string" && search.value !== message.query) search.value = message.query;
          renderList();
          if (selectedId && (previousId !== selectedId || !metadata)) vscode.postMessage({ type: "select", artifactId: selectedId });
          status.textContent = message.status;
          nextStep.textContent = typeof message.nextStep === "string" ? message.nextStep : "";
          createState.textContent = typeof message.createState === "string" ? message.createState : "CREATE state unavailable.";
        } else if (message?.type === "metadata" && message.artifactId === selectedId) {
          metadata = message.data;
          showDetails();
        } else if (message?.type === "metadataError" && message.artifactId === selectedId) {
          metadataState.textContent = message.error;
        } else if (message?.type === "status" && typeof message.status === "string") {
          status.textContent = message.status;
          nextStep.textContent = typeof message.nextStep === "string" ? message.nextStep : "";
        }
      });
      vscode.postMessage({ type: "ready" });
    })();
  </script>
</body>
</html>`;
}

