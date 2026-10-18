import { randomBytes } from "node:crypto";
import type * as vscode from "vscode";

import type { ManagedDocument } from "./registry";
import type { MetadataAssistance } from "./metadata_assistance";
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
  private selectedId: string | undefined;
  private repositoryIdentity: string | undefined;
  private feedback = "Válasszon dokumentumot vagy hozzon létre újat.";
  private nextStep = "A candidate szerkesztése és a tervkészítés nem módosítja a canonical fájlokat.";
  private busy = false;

  public constructor(
    private readonly host: typeof vscode,
    private readonly documents: () => readonly ManagedDocument[],
    private readonly status: () => string,
    private readonly act: (action: ManagerAction, document?: ManagedDocument) => Promise<ManagerActionResult>,
    private readonly planState: (artifactId: string) => ManagerPlanState = () => "PLAN_MISSING",
    private readonly createState: () => string = () => "No CREATE candidate open.",
    private readonly governancePlan: (artifactId: string) => boolean = () => false,
    private readonly createPlanReady: () => boolean = () => false,
    private readonly loadMetadata: (document: ManagedDocument) => Promise<MetadataAssistance> = async () => { throw new Error("Canonical metadata inspection is unavailable."); },
    private readonly repositoryRoot: () => string | undefined = () => undefined,
    private readonly diagnostic: (message: string) => void = () => undefined,
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
    const root = this.repositoryRoot();
    if (this.repositoryIdentity !== root) {
      this.repositoryIdentity = root;
      this.selectedId = undefined;
      this.query = "";
    }
    const all = this.documents();
    if (this.selectedId && !all.some((item) => item.artifact_id === this.selectedId)) {
      this.selectedId = undefined;
      this.feedback = "A korábban kijelölt dokumentum már nem érhető el.";
      this.nextStep = "Válasszon másik dokumentumot a listából.";
    }
    const selected = all.find((item) => item.artifact_id === this.selectedId);
    if (selected) {
      const state = this.planState(selected.artifact_id);
      if (state === "PLAN_STALE") {
        this.feedback = "A korábbi UPDATE-terv érvénytelen vagy elavult.";
        this.nextStep = "Mentse a candidate-et, majd készítsen és ellenőrizzen új tervet.";
      } else if (state === "CANDIDATE_SAVED") {
        this.feedback = "A candidate mentve van.";
        this.nextStep = "Készítsen read-only UPDATE-tervet a változtatás áttekintéséhez.";
      } else if (state === "APPLY_BLOCKED" || state === "APPLY_FAIL") {
        this.feedback = state === "APPLY_BLOCKED" ? "Az Apply blokkolva lett." : "Az Apply hibával zárult.";
        this.nextStep = "Ellenőrizze az Output panelt és a production review-t; ne ismételje automatikusan.";
      }
    }
    const visible = filterManagedDocuments(all, this.query);
    const view = (document: ManagedDocument) => ({
      artifactId: document.artifact_id,
      title: document.title,
      path: document.path,
      version: document.version,
      governance: isGovernanceDocument(document.path),
      governancePlan: this.governancePlan(document.artifact_id),
      planState: this.planState(document.artifact_id),
      planStateLabel: managerPlanStateLabel(this.planState(document.artifact_id)),
    });
    void this.panel.webview.postMessage({
      type: "documents",
      documents: visible.map(view),
      selectedId: this.selectedId,
      selectedDocument: selected ? view(selected) : undefined,
      query: this.query,
      status: this.feedback,
      nextStep: this.nextStep,
      repositoryStatus: this.status(),
      createState: this.createState(),
      createPlanReady: this.createPlanReady(),
    });
  }

  private publishStatus(message: string, nextStep = ""): void {
    this.feedback = message;
    this.nextStep = nextStep;
    void this.panel?.webview.postMessage({ type: "status", status: message, nextStep });
  }

  private async receive(raw: unknown): Promise<void> {
    const message = parseManagerMessage(raw);
    if (!message) {
      this.publishStatus("Ismeretlen Document Manager kérés elutasítva.");
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
    if (message.type === "select") {
      const document = this.documents().find((item) => item.artifact_id === message.artifactId);
      if (!document) {
        this.publishStatus("A kijelölt dokumentum már nem érhető el.", "Frissítse a listát, majd válasszon dokumentumot.");
        return;
      }
      this.selectedId = document.artifact_id;
      try {
        const data = await this.loadMetadata(document);
        void this.panel?.webview.postMessage({ type: "metadata", artifactId: document.artifact_id, data });
      } catch (error) {
        void this.panel?.webview.postMessage({ type: "metadataError", artifactId: document.artifact_id,
          error: `Canonical metadata unavailable: ${error instanceof Error ? error.message : String(error)}` });
      }
      return;
    }
    if (this.busy) {
      this.publishStatus("Egy másik művelet még folyamatban van.", "Várja meg a művelet végét.");
      return;
    }
    const document = message.artifactId
      ? this.documents().find((item) => item.artifact_id === message.artifactId)
      : undefined;
    if (!["refresh", "newDocument", "compareCreate", "planCreate", "applyCreate"].includes(message.action) && !document) {
      this.publishStatus("A kijelölt dokumentum már nem érhető el.", "Frissítse a listát.");
      return;
    }
    if ((message.action === "planGovernance" || message.action === "applyGovernance") && document && !isGovernanceDocument(document.path)) {
      this.publishStatus("Governance művelet blokkolva: ez nem governance dokumentum.");
      return;
    }
    if ((message.action === "apply" || message.action === "applyGovernance") && document &&
        (!["PLAN_READY", "PLAN_READY_MISMATCH"].includes(this.planState(document.artifact_id)) ||
         this.governancePlan(document.artifact_id) !== (message.action === "applyGovernance"))) {
      this.publishStatus("Apply blokkolva: nincs aktuális előkészített terv.", "Készítsen új tervet, és ellenőrizze a diffet.");
      return;
    }
    if (message.action === "applyCreate" && !this.createPlanReady()) {
      this.publishStatus("CREATE Apply blokkolva: nincs aktuális előkészített terv.", "Mentse a candidate-et, majd készítsen új tervet.");
      return;
    }
    this.busy = true;
    this.publishStatus("Művelet folyamatban…", "Várja meg a művelet végét.");
    try {
      const result = await this.act(message.action, document);
      this.diagnostic(`Document Manager ${message.action}: ${result.message}`);
      const apply = ["apply", "applyGovernance", "applyCreate"].includes(message.action);
      const plan = ["plan", "planMinor", "planGovernance", "planCreate"].includes(message.action);
      if (!result.ok) {
        const applyState = document ? this.planState(document.artifact_id) : undefined;
        const createApplyState = message.action === "applyCreate" ? this.createState() : "";
        const failed = applyState === "APPLY_FAIL" || /CREATE Apply FAIL/i.test(createApplyState);
        const blocked = applyState === "APPLY_BLOCKED" || /CREATE Apply BLOCKED/i.test(createApplyState);
        this.publishStatus(apply ? failed ? "Az Apply hibával zárult." : blocked ? "Az Apply blokkolva lett." : "Az Apply megszakadt vagy nem igazolt." : "A művelet megszakadt vagy blokkolva lett.",
          apply ? "Ellenőrizze az Output panelt és a production review-t; ne ismételje automatikusan." : "A részleteket az AETERNA Documents Output panel mutatja.");
      } else if (apply) {
        this.publishStatus("Az Apply és a production ellenőrzés sikeres.", "Tekintse át a Git-változásokat; a commit és push külön emberi művelet.");
      } else if (plan) {
        this.publishStatus("A read-only terv elkészült; canonical fájl nem módosult.", "Tekintse át a candidate-et, a diffet és a tervet az Apply előtt.");
      } else if (message.action === "edit" || message.action === "newDocument") {
        this.publishStatus("A candidate megnyílt szerkesztésre.", "Mentés után készítsen vagy frissítsen tervet.");
      } else if (message.action === "preview") {
        this.publishStatus("A meglévő candidate Markdown előnézete megnyílt.");
      } else if (message.action === "refresh") {
        this.publishStatus("A dokumentumlista frissült.");
      } else {
        this.publishStatus("A művelet befejeződött.", "A részleteket az AETERNA Documents Output panel mutatja.");
      }
      this.publishDocuments();
    } catch (error) {
      this.diagnostic(`Document Manager ${message.action} error: ${error instanceof Error ? error.stack ?? error.message : String(error)}`);
      this.publishStatus("A művelet hibával vagy ellenőrizhetetlen eredménnyel zárult.",
        "Ellenőrizze az Output panelt és az esetleges production review-t; ne ismételje automatikusan.");
    } finally {
      this.busy = false;
    }
  }

  public dispose(): void {
    this.panel?.dispose();
  }
}
