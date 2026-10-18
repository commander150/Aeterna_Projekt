import { randomBytes } from "node:crypto";
import type * as vscode from "vscode";

import type { ManagedDocument } from "./registry";
import type { MetadataAssistance } from "./metadata_assistance";
import { filterManagedDocuments, isGovernanceDocument, managerPlanStateLabel, parseManagerMessage, renderManagerHtml, type InlineQuestion, type ManagerAction, type ManagerActionResult, type ManagerPlanState } from "./manager_content";

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

export function routeLowRiskQuestion(
  manager: Pick<DocumentManager, "actionActive" | "ask">,
  fromManager: boolean,
  question: InlineQuestion,
  native: () => PromiseLike<string | undefined>,
  review: Readonly<Record<string, () => PromiseLike<unknown>>> = {},
): Promise<string | undefined> {
  return fromManager && manager.actionActive ? manager.ask(question, review) : Promise.resolve(native());
}

export class DocumentManager implements vscode.Disposable {
  private panel: vscode.WebviewPanel | undefined;
  private query = "";
  private selectedId: string | undefined;
  private repositoryIdentity: string | undefined;
  private observedSelectionState: string | undefined;
  private feedback = "Válasszon dokumentumot vagy hozzon létre újat.";
  private nextStep = "A candidate szerkesztése és a tervkészítés nem módosítja a canonical fájlokat.";
  private busy = false;
  private reviewInProgress = false;
  private questionCancelled = false;
  private cancelledQuestionConsequence: string | undefined;
  private pendingQuestion: {
    readonly id: string;
    readonly root: string | undefined;
    readonly choices: InlineQuestion["choices"];
    readonly completed: boolean;
    readonly cancelConsequence: string | undefined;
    readonly resolve: (choice: string | undefined) => void;
    readonly review: Readonly<Record<string, () => PromiseLike<unknown>>>;
  } | undefined;

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
    panel.onDidDispose(() => {
      if (this.panel !== panel) return;
      this.panel = undefined;
      this.cancelQuestion();
    });
    panel.webview.onDidReceiveMessage((raw: unknown) => {
      if (this.panel !== panel) return;
      void this.receive(raw, panel).catch((error) => {
        this.diagnostic(`Document Manager message failed: ${error instanceof Error ? error.message : String(error)}`);
      });
    });
  }

  public refresh(): void {
    this.publishDocuments();
  }

  public get actionActive(): boolean {
    return this.busy || this.reviewInProgress;
  }

  private post(panel: vscode.WebviewPanel, message: unknown, onUndelivered?: () => void): void {
    if (this.panel !== panel) return;
    try {
      void Promise.resolve(panel.webview.postMessage(message)).then((delivered) => {
        if (this.panel === panel && !delivered) {
          this.diagnostic("Document Manager Webview message was not delivered.");
          onUndelivered?.();
        }
      }, (error) => {
        if (this.panel === panel) {
          this.diagnostic(`Document Manager Webview message failed: ${error instanceof Error ? error.message : String(error)}`);
          onUndelivered?.();
        }
      });
    } catch (error) {
      if (this.panel === panel) {
        this.diagnostic(`Document Manager Webview message failed: ${error instanceof Error ? error.message : String(error)}`);
        onUndelivered?.();
      }
    }
  }

  public ask(question: InlineQuestion, review: Readonly<Record<string, () => PromiseLike<unknown>>> = {}): Promise<string | undefined> {
    const panel = this.panel;
    if (!this.actionActive || !panel || this.pendingQuestion) return Promise.resolve(undefined);
    const id = randomBytes(16).toString("hex");
    return new Promise<string | undefined>((resolve) => {
      this.pendingQuestion = { id, root: this.repositoryRoot(), choices: question.choices,
        completed: question.completed === true, cancelConsequence: question.cancelConsequence, resolve, review };
      if (!question.completed) this.publishStatus("Jóváhagyásra vár. Válaszd ki a kívánt műveletet, vagy kattints a Mégse gombra.");
      try {
        panel.reveal();
        this.post(panel, { type: "question", question: { ...question, id } }, () => {
          if (this.pendingQuestion?.id === id) this.cancelQuestion();
        });
      } catch {
        this.cancelQuestion();
      }
    });
  }

  private cancelQuestion(): void {
    const pending = this.pendingQuestion;
    if (!pending) return;
    this.pendingQuestion = undefined;
    if (this.panel) this.post(this.panel, { type: "question", question: undefined });
    if (!pending.completed) {
      this.questionCancelled = true;
      this.cancelledQuestionConsequence = pending.cancelConsequence;
      this.publishStatus("A művelet megszakítva.",
        pending.cancelConsequence ?? "A jóváhagyás utáni lépés nem indult el; a korábbi candidate és terv megmaradt.");
    } else if (pending.cancelConsequence) {
      this.publishStatus("A tájékoztatás bezárva.", pending.cancelConsequence);
    }
    pending.resolve(undefined);
  }

  private publishDocuments(): void {
    if (!this.panel) return;
    const root = this.repositoryRoot();
    if (this.repositoryIdentity !== root) {
      this.cancelQuestion();
      this.repositoryIdentity = root;
      this.selectedId = undefined;
      this.query = "";
      this.observedSelectionState = undefined;
    }
    const all = this.documents();
    if (this.selectedId && !all.some((item) => item.artifact_id === this.selectedId)) {
      this.selectedId = undefined;
      this.observedSelectionState = undefined;
      this.feedback = "A korábban kijelölt dokumentum már nem érhető el.";
      this.nextStep = "Válasszon másik dokumentumot a listából.";
    }
    const selected = all.find((item) => item.artifact_id === this.selectedId);
    const state = selected ? this.planState(selected.artifact_id) : undefined;
    const selectionState = selected ? `${selected.artifact_id}:${state}` : undefined;
    if (selectionState !== this.observedSelectionState) {
      this.observedSelectionState = selectionState;
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
    this.post(this.panel, {
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
    if (this.panel) this.post(this.panel, { type: "status", status: message, nextStep });
  }

  private async receive(raw: unknown, sourcePanel: vscode.WebviewPanel): Promise<void> {
    if (this.panel !== sourcePanel) return;
    const message = parseManagerMessage(raw);
    if (!message) {
      this.publishStatus("Ismeretlen Document Manager kérés elutasítva.");
      return;
    }
    if (message.type === "ready") {
      this.publishDocuments();
      return;
    }
    if (message.type === "answer") {
      const pending = this.pendingQuestion;
      if (!pending || pending.id !== message.questionId) return;
      if (pending.root !== this.repositoryRoot()) {
        this.cancelQuestion();
        return;
      }
      if (message.choice === "cancel") {
        this.cancelQuestion();
        return;
      }
      const choice = pending.choices.find((item) => item.id === message.choice);
      if (!choice) return;
      if (choice.review) {
        const open = pending.review[choice.id];
        if (!open) return;
        this.cancelQuestion();
        this.reviewInProgress = true;
        try { await open(); }
        catch (error) { this.diagnostic(`Inline review failed: ${error instanceof Error ? error.message : String(error)}`); }
        finally { this.reviewInProgress = false; }
        return;
      }
      this.pendingQuestion = undefined;
      this.post(sourcePanel, { type: "question", question: undefined });
      if (!pending.completed) this.publishStatus("A művelet végrehajtása folyamatban. Kérlek, várj.");
      pending.resolve(choice.id);
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
      this.observedSelectionState = `${document.artifact_id}:${this.planState(document.artifact_id)}`;
      try {
        const data = await this.loadMetadata(document);
        this.post(sourcePanel, { type: "metadata", artifactId: document.artifact_id, data });
      } catch (error) {
        this.post(sourcePanel, { type: "metadataError", artifactId: document.artifact_id,
          error: `Canonical metadata unavailable: ${error instanceof Error ? error.message : String(error)}` });
      }
      return;
    }
    if (this.busy || this.reviewInProgress) {
      this.publishStatus("Egy másik művelet még folyamatban van.", "Várja meg a művelet végét.");
      return;
    }
    this.cancelQuestion();
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
    this.questionCancelled = false;
    this.cancelledQuestionConsequence = undefined;
    this.publishStatus("A művelet végrehajtása folyamatban. Kérlek, várj.");
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
        if (!apply && this.questionCancelled) {
          this.publishStatus("A művelet megszakítva.",
            this.cancelledQuestionConsequence ?? "A jóváhagyás utáni lépés nem indult el; a korábbi candidate és terv megmaradt.");
        } else {
          this.publishStatus(apply ? failed ? "Az Apply hibával zárult." : blocked ? "Az Apply blokkolva lett." : "Az Apply megszakadt vagy nem igazolt." : "A művelet megszakadt vagy blokkolva lett.",
            apply ? "Ellenőrizze az Output panelt és a production review-t; ne ismételje automatikusan." : "A részleteket az AETERNA Documents Output panel mutatja.");
        }
      } else if (apply) {
        this.publishStatus("Az Apply és a production ellenőrzés sikeres.", "Tekintse át a Git-változásokat; a commit és push külön emberi művelet.");
      } else if (plan) {
        this.publishStatus("A terv elkészült. A canonical dokumentum nem módosult.", "Tekintse át a candidate-et, a diffet és a tervet az Apply előtt.");
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
    const panel = this.panel;
    this.panel = undefined;
    this.cancelQuestion();
    panel?.dispose();
  }
}
