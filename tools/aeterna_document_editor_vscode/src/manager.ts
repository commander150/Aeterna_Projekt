import { randomBytes } from "node:crypto";
import type * as vscode from "vscode";

import type { ManagedDocument } from "./registry";
import { filterManagedDocuments, isGovernanceDocument, managerPlanStateLabel, parseManagerMessage, renderManagerHtml, type ManagerAction, type ManagerActionResult, type ManagerPlanState } from "./manager_content";

export function notifyPlanReady(
  show: () => PromiseLike<string | undefined>,
  compare: () => PromiseLike<unknown>,
  reportError: (error: unknown) => void,
): void {
  void Promise.resolve()
    .then(show)
    .then((action) => action === "Compare Candidate" ? compare() : undefined)
    .catch(reportError);
}

export class DocumentManager implements vscode.Disposable {
  private panel: vscode.WebviewPanel | undefined;
  private query = "";
  private busy = false;

  public constructor(
    private readonly host: typeof vscode,
    private readonly documents: () => readonly ManagedDocument[],
    private readonly status: () => string,
    private readonly act: (action: ManagerAction, document?: ManagedDocument) => Promise<ManagerActionResult>,
    private readonly planState: (artifactId: string) => ManagerPlanState = () => "PLAN_MISSING",
    private readonly createState: () => string = () => "No CREATE candidate open.",
    private readonly governancePlan: (artifactId: string) => boolean = () => false,
  ) {}

  public show(): void {
    if (this.panel) {
      this.panel.reveal();
      this.publishDocuments();
      return;
    }
    const panel = this.host.window.createWebviewPanel(
      "aeternaDocumentManager",
      "AETERNA Document Manager",
      this.host.ViewColumn.One,
      { enableScripts: true, localResourceRoots: [] },
    );
    this.panel = panel;
    panel.webview.html = renderManagerHtml(randomBytes(16).toString("base64"));
    panel.onDidDispose(() => { this.panel = undefined; });
    panel.webview.onDidReceiveMessage((raw: unknown) => { void this.receive(raw); });
  }

  public refresh(): void {
    this.publishDocuments();
  }

  private publishDocuments(): void {
    if (!this.panel) return;
    const visible = filterManagedDocuments(this.documents(), this.query);
    void this.panel.webview.postMessage({
      type: "documents",
      documents: visible.map((document) => ({
        artifactId: document.artifact_id,
        title: document.title,
        path: document.path,
        version: document.version,
        governance: isGovernanceDocument(document.path),
        governancePlan: this.governancePlan(document.artifact_id),
        planState: this.planState(document.artifact_id),
        planStateLabel: managerPlanStateLabel(this.planState(document.artifact_id)),
      })),
      status: this.status(),
      createState: this.createState(),
    });
  }

  private publishStatus(message: string): void {
    void this.panel?.webview.postMessage({ type: "status", status: message });
  }

  private async receive(raw: unknown): Promise<void> {
    const message = parseManagerMessage(raw);
    if (!message) {
      this.publishStatus("Unsupported Document Manager request was ignored.");
      return;
    }
    if (message.type === "ready") {
      this.publishDocuments();
      return;
    }
    if (message.type === "search") {
      this.query = message.query;
      this.publishDocuments();
      return;
    }
    if (this.busy) {
      this.publishStatus("Another Document Manager action is still running.");
      return;
    }
    const document = message.artifactId
      ? this.documents().find((item) => item.artifact_id === message.artifactId)
      : undefined;
    if (!["refresh", "newDocument", "planCreate"].includes(message.action) && !document) {
      this.publishStatus("Selected document is no longer available. Refresh the list.");
      return;
    }
    if ((message.action === "planGovernance" || message.action === "applyGovernance") && document && !isGovernanceDocument(document.path)) {
      this.publishStatus("Governance action blocked: selected document is outside project/governance/.");
      return;
    }
    if ((message.action === "apply" || message.action === "applyGovernance") && document &&
        (!["PLAN_READY", "PLAN_READY_MISMATCH"].includes(this.planState(document.artifact_id)) ||
         this.governancePlan(document.artifact_id) !== (message.action === "applyGovernance"))) {
      this.publishStatus("Apply blocked: selected document has no current prepared plan.");
      return;
    }
    this.busy = true;
    this.publishStatus("Working…");
    try {
      const result = await this.act(message.action, document);
      this.publishStatus(result.message);
      this.publishDocuments();
    } catch (error) {
      this.publishStatus(error instanceof Error ? error.message : String(error));
    } finally {
      this.busy = false;
    }
  }

  public dispose(): void {
    this.panel?.dispose();
  }
}
