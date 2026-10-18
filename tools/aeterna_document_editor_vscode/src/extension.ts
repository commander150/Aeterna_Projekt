import * as vscode from "vscode";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { CreateApplyCoordinator, CreateApplyError, type CreateApplySummary } from "./apply_create";
import {
  CreateCandidateError, createOrOpenCreateSession, createStorageRootForRepository, loadCreateSession,
  type CreateInput, type CreateSession,
} from "./create_candidate";
import {
  CreatePlanError, inspectCreateBaseline, prepareCreatePreview, renderCreatePreview,
  type CreateBaseline, type CreatePreview,
} from "./create_plan";
import { createDiffUris, emptyCreateDocument, EMPTY_CREATE_SCHEME } from "./create_diff";
import { loadMetadataAssistance } from "./metadata_assistance";
import { updateCandidateStorageRoot } from "./storage_compat";

import {
  type ManagedDocument,
  loadManagedDocuments,
} from "./registry";
import { resolveRepositoryRoot } from "./repository";
import { resolveArtifact, WorkflowIntegrationError } from "./workflow";
import {
  CandidateSessionError,
  type CandidateSessionRequest,
  candidateDiffDescriptor,
  candidateDocumentState,
  candidateHasUnsavedChanges,
  loadCandidateSession,
  pathsEqual,
} from "./candidate";
import {
  createOrOpenRoutedCandidate,
  loadRoutedCandidate,
} from "./candidate_routing";
import { DocumentManager, notifyPlanReady } from "./manager";
import { isGovernanceDocument, type ManagerAction, type ManagerPlanState } from "./manager_content";
import {
  ExplicitApplyCoordinator,
  ExplicitApplyError,
  materializePreparedUpdate,
  type ApplySummary,
  type MaterializedUpdatePlan,
} from "./apply_update";
import {
  UpdatePreviewError,
  currentUpdateIdentity,
  isUpdatePlanStale,
  prepareUpdatePreview,
  requireSavedCandidate,
  renderUpdatePreview,
  type UpdatePlanIdentity,
} from "./update_plan";
import {
  CandidateVersionError,
  candidateVersion,
  suggestMajorVersion,
  suggestMinorVersion,
  validateProposedVersion,
  writeCandidateVersion,
} from "./version_candidate";

class DocumentTreeItem extends vscode.TreeItem {
  public constructor(public readonly document: ManagedDocument) {
    super(document.artifact_id, vscode.TreeItemCollapsibleState.None);
    this.description = `v${document.version} — ${document.title}`;
    this.tooltip = new vscode.MarkdownString(
      [
        `**${document.artifact_id}**`,
        "",
        `Title: ${document.title}`,
        "",
        `Path: \`${document.path}\``,
        "",
        `Version: ${document.version}`,
      ].join("\n"),
    );
    this.contextValue = "aeternaManagedDocument";
    this.command = {
      command: "aeterna.openDocument",
      title: "Open AETERNA Document",
      arguments: [this],
    };
  }
}

class AeternaDocumentsProvider
  implements vscode.TreeDataProvider<DocumentTreeItem>
{
  private readonly changeEmitter = new vscode.EventEmitter<
    DocumentTreeItem | undefined | void
  >();
  private documents: readonly ManagedDocument[] = [];
  private repositoryRoot: string | undefined;
  private status = "Loading managed documents…";

  public readonly onDidChangeTreeData = this.changeEmitter.event;

  public constructor(private readonly output: vscode.OutputChannel) {}

  public getTreeItem(element: DocumentTreeItem): vscode.TreeItem {
    return element;
  }

  public getChildren(): DocumentTreeItem[] {
    return this.documents.map((document) => new DocumentTreeItem(document));
  }

  public get currentDocuments(): readonly ManagedDocument[] {
    return this.documents;
  }

  public get currentRepositoryRoot(): string | undefined {
    return this.repositoryRoot;
  }

  public get currentStatus(): string {
    return this.status;
  }

  public async refresh(): Promise<void> {
    this.documents = [];
    this.repositoryRoot = undefined;
    const workspaceRoots =
      vscode.workspace.workspaceFolders?.map((folder) => folder.uri.fsPath) ?? [];

    try {
      const root = await resolveRepositoryRoot(workspaceRoots);
      this.output.appendLine(`Resolved repository root: ${root}`);
      const loaded = await loadManagedDocuments(root);
      this.repositoryRoot = root;
      this.documents = loaded.documents;
      this.status = `${loaded.documents.length} managed documents loaded${loaded.diagnostics.length ? `; ${loaded.diagnostics.length} path diagnostic(s) in AETERNA Documents output` : ""}.`;
      this.output.appendLine(
        `Registry load result: PASS (${loaded.documents.length} managed Markdown documents).`,
      );
      for (const diagnostic of loaded.diagnostics) {
        this.output.appendLine(`Registry/path validation problem: ${diagnostic}`);
      }
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
      this.status = `Document list unavailable: ${detail}`;
      this.output.appendLine(`Refresh failed: ${detail}`);
      void vscode.window.showErrorMessage(`AETERNA Documents: ${detail}`);
    } finally {
      this.changeEmitter.fire();
    }
  }

  public dispose(): void {
    this.changeEmitter.dispose();
  }
}

async function chooseDocument(
  provider: AeternaDocumentsProvider,
  item: DocumentTreeItem | undefined,
): Promise<ManagedDocument | undefined> {
  if (item instanceof DocumentTreeItem) {
    return item.document;
  }
  const selected = await vscode.window.showQuickPick(
    provider.currentDocuments.map((document) => ({
      label: document.artifact_id,
      description: `v${document.version} — ${document.title}`,
      detail: document.path,
      document,
    })),
    { placeHolder: "Select an AETERNA managed document", ignoreFocusOut: true },
  );
  return selected?.document;
}

async function prepareCandidateRequest(
  provider: AeternaDocumentsProvider,
  document: ManagedDocument,
  storageRoot: string,
): Promise<CandidateSessionRequest> {
  const repositoryRoot = provider.currentRepositoryRoot;
  if (!repositoryRoot) {
    throw new CandidateSessionError(
      "CANONICAL_UNAVAILABLE",
      "AETERNA repository is unavailable; refresh the document list.",
    );
  }
  const resolved = await resolveArtifact(repositoryRoot, document.artifact_id);
  if (
    resolved.result.artifact_id !== document.artifact_id ||
    resolved.result.path !== document.path ||
    resolved.result.version !== document.version
  ) {
    throw new CandidateSessionError(
      "CANONICAL_UNAVAILABLE",
      "Workflow resolve identity, path or version does not match the selected registry artifact; refresh the document list.",
    );
  }
  return {
    repositoryRoot,
    storageRoot,
    artifact: {
      artifactId: document.artifact_id,
      canonicalPath: document.path,
      version: document.version,
      kind: document.kind,
      generated: document.generated,
      scope: document.scope,
    },
  };
}

function openCandidateDocument(
  candidatePath: string,
): vscode.TextDocument | undefined {
  return vscode.workspace.textDocuments.find((document) =>
    pathsEqual(document.uri.fsPath, candidatePath),
  );
}

function isCandidateUnsaved(candidatePath: string): boolean {
  return candidateHasUnsavedChanges(
    candidatePath,
    vscode.workspace.textDocuments.map((document) => ({
      fsPath: document.uri.fsPath,
      isDirty: document.isDirty,
    })),
    vscode.window.tabGroups.all.flatMap((group) => group.tabs.map((tab) => {
      const input = tab.input;
      const fsPaths = input instanceof vscode.TabInputText || input instanceof vscode.TabInputCustom
        ? [input.uri.fsPath]
        : input instanceof vscode.TabInputTextDiff ? [input.original.fsPath, input.modified.fsPath] : [];
      return { fsPaths, isDirty: tab.isDirty };
    })),
  );
}

function reportCandidateError(
  output: vscode.OutputChannel,
  action: string,
  error: unknown,
): void {
  const detail = error instanceof Error ? error.message : String(error);
  const code = error instanceof CandidateSessionError || error instanceof UpdatePreviewError || error instanceof ExplicitApplyError || error instanceof CandidateVersionError || error instanceof CreateCandidateError || error instanceof CreatePlanError
    ? ` [${error.code}]` : "";
  output.appendLine(`${action} failed${code}: ${detail}`);
  if (error instanceof UpdatePreviewError) {
    for (const diagnostic of error.diagnostics) {
      output.appendLine(
        `Workflow diagnostic: ${diagnostic.code} (${diagnostic.severity}) ${diagnostic.message}`,
      );
    }
    output.show(true);
  }
  void vscode.window.showErrorMessage(`AETERNA Documents: ${detail}`);
}

function applyConfirmationDetail(summary: ApplySummary): string {
  return [
    `Document: ${summary.artifactId} — ${summary.title}`,
    `Current version: ${summary.version}; mode: ${summary.versionIntent === "major" ? "semantic-governance-change / major" : summary.versionIntent === "minor" ? "metadata+body / minor" : "body-only / git-only"}; proposed version: ${summary.proposedVersion}.`,
    `Branch/HEAD: ${summary.branch} / ${summary.head}`,
    `Canonical baseline SHA-256: ${summary.baselineSha256}`,
    `Candidate SHA-256: ${summary.candidateSha256}`,
    `Reviewed plan SHA-256: ${summary.planSemanticSha256}`,
    `Planned writes: ${summary.plannedWrites.join(", ")}`,
    "Actual Git changes may omit generated outputs that normalize to HEAD; the production review records both sets.",
    `Dependency impact: ${summary.dependencyImpact}`,
    `Planner version recommendation: ${summary.recommendedIntent}; mismatch: ${summary.mismatch ? "YES" : "NO"}.`,
    "Apply CAN modify canonical and generated repository files. Candidate save alone does not Apply.",
    "Review the plan in AETERNA Documents output and the native candidate diff first.",
  ].join("\n");
}

function createApplyConfirmationDetail(summary: CreateApplySummary): string {
  return [
    `Artifact ID: ${summary.artifactId}`,
    `Canonical target: ${summary.targetPath}`,
    `Authority: ${summary.authority}; risk: ${summary.authorityRisk}${summary.authorityRisk === "HIGH" ? " — HIGH-RISK AUTHORITY: review carefully" : ""}`,
    `Initial version: ${summary.initialVersion}`,
    `Branch/HEAD: ${summary.branch} / ${summary.head}`,
    `Dependency impact: ${summary.dependencyImpact}`,
    `Candidate SHA-256: ${summary.candidateSha256}`,
    `Immutable plan semantic SHA-256: ${summary.planSemanticSha256}`,
    `All planned writes: ${summary.plannedWrites.join(", ")}`,
    "Only explicit Apply can create the canonical document. Saving or planning cannot Apply.",
    "After PASS, inspect GitHub Desktop; commit and push remain manual.",
  ].join("\n");
}

function offerProductionReview(reviewPath: string | undefined, message: string, error: boolean): void {
  const notification = error
    ? vscode.window.showErrorMessage(message, ...(reviewPath ? ["Open Production Review"] : []))
    : vscode.window.showInformationMessage(message, ...(reviewPath ? ["Open Production Review"] : []));
  void notification.then(async (choice) => {
    if (choice === "Open Production Review" && reviewPath) {
      await vscode.window.showTextDocument(vscode.Uri.file(reviewPath), { preview: false });
    }
  });
}

async function promptCreateInput(baseline: CreateBaseline, artifactId: string): Promise<CreateInput | undefined> {
  const targetPath = await vscode.window.showInputBox({
    ignoreFocusOut: true,
    title: "New Document — canonical target path",
    prompt: "Repository-relative .md path in an existing project/, data/, design/ or src/engine/docs/ directory.",
    validateInput: (value) => value && !value.includes("\\") && !value.includes("..") && value.endsWith(".md")
      ? undefined : "Enter a safe repository-relative .md path. The production planner checks collisions and scope.",
  });
  if (targetPath === undefined) return undefined;
  const type = await vscode.window.showQuickPick(
    baseline.controlled_values.type.map((value) => ({ label: value })),
    { title: "New Document — document type", placeHolder: "Select a type from the production metadata schema", ignoreFocusOut: true },
  );
  if (!type) return undefined;
  const authority = await vscode.window.showQuickPick(
    baseline.controlled_values.authority.map((value) => ({ label: value })),
    { title: "New Document — authority", placeHolder: "Select the document's authority explicitly", ignoreFocusOut: true },
  );
  if (!authority) return undefined;
  const integration = await vscode.window.showQuickPick(
    baseline.create_contract.integration.map((value) => ({ label: value })),
    { title: "New Document — integration state", placeHolder: "Choose current or pending_integration", ignoreFocusOut: true },
  );
  if (!integration || !["current", "pending_integration"].includes(integration.label)) return undefined;
  const dependencies = await vscode.window.showQuickPick(
    baseline.existing_artifact_ids.filter((id) => id !== artifactId).map((id) => ({ label: id })),
    { title: "New Document — dependencies", placeHolder: "Select zero or more existing artifact IDs", canPickMany: true, ignoreFocusOut: true },
  );
  if (!dependencies) return undefined;
  const version = await vscode.window.showInputBox({
    ignoreFocusOut: true,
    title: "New Document — initial version",
    prompt: "Enter and approve the initial version. No default or automatic increment is applied.",
    validateInput: (value) => value.trim() && !/[\r\n]/.test(value) ? undefined : "Enter a non-empty, single-line version.",
  });
  if (version === undefined) return undefined;
  const title = await vscode.window.showInputBox({
    ignoreFocusOut: true,
    title: "New Document — H1 title",
    prompt: "Enter the initial Markdown H1 title.",
    validateInput: (value) => value.trim() && !/[\r\n]/.test(value) ? undefined : "Enter a non-empty, single-line title.",
  });
  if (title === undefined) return undefined;
  const initialContent = await vscode.window.showInputBox({
    ignoreFocusOut: true,
    title: "New Document — initial body",
    prompt: "Optional first paragraph. You can edit the external candidate in the native Markdown editor.",
  });
  if (initialContent === undefined) return undefined;
  return {
    artifactId, targetPath, type: type.label, authority: authority.label,
    dependencies: dependencies.map((item) => item.label), version, integration: integration.label as CreateInput["integration"],
    title, initialContent,
  };
}

export async function activate(context: vscode.ExtensionContext): Promise<void> {
  const output = vscode.window.createOutputChannel("AETERNA Documents");
  const provider = new AeternaDocumentsProvider(output);
  const candidateStorageRoot = await updateCandidateStorageRoot(context.globalStorageUri.fsPath);
  let createSession: CreateSession | undefined;
  let createPreview: CreatePreview | undefined;
  let createState = "No CREATE candidate open.";
  const planStates = new Map<string, ManagerPlanState>();
  const candidatePaths = new Map<string, string>();
  const applyCoordinator = new ExplicitApplyCoordinator();
  const createApplyCoordinator = new CreateApplyCoordinator();
  const setPlanState = (artifactId: string, state: ManagerPlanState): void => {
    planStates.set(artifactId, state);
    manager.refresh();
  };
  const manager = new DocumentManager(
    vscode,
    () => provider.currentDocuments,
    () => provider.currentStatus,
    async (action: ManagerAction, document: ManagedDocument | undefined) => {
      if (action === "refresh") {
        await provider.refresh();
        return {
          ok: Boolean(provider.currentRepositoryRoot),
          message: provider.currentStatus,
        };
      }
      if (action === "newDocument" || action === "compareCreate" || action === "planCreate" || action === "applyCreate") {
        const succeeded = await vscode.commands.executeCommand<boolean>(
          action === "newDocument" ? "aeterna.newDocument"
            : action === "compareCreate" ? "aeterna.compareCreateCandidate"
              : action === "planCreate" ? "aeterna.prepareCreatePlan" : "aeterna.applyPreparedCreate",
        );
        return succeeded
          ? { ok: true, message: action === "newDocument" ? "CREATE candidate opened outside the repository. Save it before planning."
            : action === "compareCreate" ? "CREATE candidate diff opened against an empty read-only document."
              : action === "planCreate" ? "Read-only CREATE plan ready. Review candidate, diff, plan and AETERNA Documents output."
              : "CREATE Apply PASS. Inspect the production review and GitHub Desktop before manual commit/push." }
          : { ok: false, message: action === "applyCreate" ? createState
            : "CREATE candidate or plan cancelled or blocked. See the VS Code notification and AETERNA Documents output." };
      }
      if (!document) {
        return { ok: false, message: "Selected document is unavailable. Refresh the list." };
      }
      const command = {
        edit: "aeterna.editCandidate",
        preview: "aeterna.previewCandidate",
        compare: "aeterna.compareCandidate",
        plan: "aeterna.prepareUpdatePlan",
        planMinor: "aeterna.prepareMinorUpdatePlan",
        planGovernance: "aeterna.prepareGovernanceUpdatePlan",
        apply: "aeterna.applyPreparedUpdate",
        applyGovernance: "aeterna.applyGovernanceUpdate",
      }[action];
      const succeeded = await vscode.commands.executeCommand<boolean>(
        command,
        new DocumentTreeItem(document),
        false,
      );
      return succeeded
        ? { ok: true, message: `${document.artifact_id}: ${action} completed. Check AETERNA Documents output for details.` }
        : { ok: false, message: `${document.artifact_id}: ${action} cancelled or blocked. See the VS Code notification and AETERNA Documents output.` };
    },
    (artifactId) => planStates.get(artifactId) ?? "PLAN_MISSING",
    () => createState,
    (artifactId) => preparedPlans.get(artifactId)?.materialized.preview.manifest.change_class === "semantic-governance-change",
    () => createPreview !== undefined,
    async (document) => {
      const root = provider.currentRepositoryRoot;
      if (!root) throw new Error("Repository unavailable; refresh the document list.");
      return loadMetadataAssistance(root, document);
    },
    () => provider.currentRepositoryRoot,
    (message) => output.appendLine(message),
  );
  const preparedPlans = new Map<string, {
    readonly request: CandidateSessionRequest;
    readonly candidatePath: string;
    readonly canonicalPath: string;
    readonly artifactId: string;
    readonly identity: UpdatePlanIdentity;
    readonly materialized: MaterializedUpdatePlan;
  }>();
  const invalidateChangedDocument = (documentPath: string): void => {
    for (const [key, saved] of preparedPlans) {
      if (pathsEqual(saved.candidatePath, documentPath) || pathsEqual(saved.canonicalPath, documentPath)) {
        preparedPlans.delete(key);
        setPlanState(saved.artifactId, "PLAN_STALE");
        output.appendLine(`UPDATE plan STALE after document edit: ${saved.artifactId}. Prepare a new plan.`);
      }
    }
  };
  const preparePlanForMode = async (
    item: DocumentTreeItem | undefined,
    mode: "git-only" | "minor" | "major",
  ): Promise<boolean> => {
    const document = await chooseDocument(provider, item);
    if (!document) return false;
    if (mode === "major" && !isGovernanceDocument(document.path)) {
      void vscode.window.showErrorMessage("Governance UPDATE planning is limited to project/governance/ documents.");
      return false;
    }
    try {
      const originalRequest = await prepareCandidateRequest(provider, document, candidateStorageRoot);
      const { request, session } = await loadRoutedCandidate(originalRequest);
      if (isCandidateUnsaved(session.candidatePath)) {
        throw new UpdatePreviewError("CANDIDATE_UNSAVED", "Save every candidate editor before preparing a plan.");
      }
      let proposedVersion: string | undefined;
      if (mode === "minor" || mode === "major") {
        const before = await readFile(session.candidatePath);
        const existingVersion = candidateVersion(before);
        const baselineVersion = session.manifest.baseline.version;
        proposedVersion = await vscode.window.showInputBox({
          ignoreFocusOut: true,
          title: mode === "major" ? "Governance UPDATE (major)" : "Versioned UPDATE (minor)",
          prompt: `Current canonical version: ${baselineVersion}. Approve the new candidate version. Only the candidate will be edited.`,
          value: existingVersion !== baselineVersion ? existingVersion : (mode === "major" ? suggestMajorVersion(baselineVersion) : suggestMinorVersion(baselineVersion)) ?? "",
          validateInput: (value) => {
            try { validateProposedVersion(baselineVersion, value); return undefined; }
            catch (error) { return error instanceof Error ? error.message : String(error); }
          },
        });
        if (proposedVersion === undefined) return false;
        validateProposedVersion(baselineVersion, proposedVersion);
        const approval = await vscode.window.showWarningMessage(
          `Approve candidate version ${baselineVersion} -> ${proposedVersion} for ${document.artifact_id}?`,
          { modal: true, detail: "The version field changes only in the external candidate. The canonical document remains untouched; plan-update is read-only and Apply requires separate approval." },
          "Approve Candidate Version and Plan",
        );
        if (approval !== "Approve Candidate Version and Plan") return false;
        if (isCandidateUnsaved(session.candidatePath)) {
          throw new UpdatePreviewError("CANDIDATE_UNSAVED", "Candidate has unsaved edits; version change was cancelled.");
        }
        const current = await readFile(session.candidatePath);
        const currentHash = createHash("sha256").update(current).digest("hex");
        if (currentHash !== createHash("sha256").update(before).digest("hex")) {
          throw new CandidateVersionError("CANDIDATE_VERSION_DRIFT", "Candidate changed while version approval was open.");
        }
        if (existingVersion !== proposedVersion) {
          preparedPlans.delete(document.artifact_id);
          setPlanState(document.artifact_id, "PLAN_STALE");
          await writeCandidateVersion(session.candidatePath, currentHash, existingVersion, proposedVersion);
          output.appendLine(`Approved candidate-only version edit: ${existingVersion} -> ${proposedVersion}.`);
        }
      } else {
        const confirmation = await vscode.window.showWarningMessage(
          "Confirm all candidate edits are saved, including ManulDown. Prepare a read-only UPDATE plan with change_class=body-only and version_intent=git-only? No canonical changes or Apply will occur.",
          { modal: true },
          "Prepare body-only / git-only plan",
        );
        if (confirmation !== "Prepare body-only / git-only plan") return false;
      }
      if (isCandidateUnsaved(session.candidatePath)) {
        throw new UpdatePreviewError("CANDIDATE_UNSAVED", "Save the candidate before planning.");
      }
      const previous = preparedPlans.get(document.artifact_id);
      if (previous) {
        const current = await currentUpdateIdentity(request.repositoryRoot, session);
        if (isUpdatePlanStale(previous.identity, current)) {
          preparedPlans.delete(document.artifact_id);
          setPlanState(document.artifact_id, "PLAN_STALE");
          output.appendLine(`Previous UPDATE plan STALE: ${document.artifact_id}.`);
        }
      }
      const choice = mode === "major"
        ? { changeClass: "semantic-governance-change" as const, versionIntent: "major" as const, proposedVersion: proposedVersion! }
        : mode === "minor"
        ? { changeClass: "metadata+body" as const, versionIntent: "minor" as const, proposedVersion: proposedVersion! }
        : { changeClass: "body-only" as const, versionIntent: "git-only" as const };
      const preview = await prepareUpdatePreview(request.repositoryRoot, session, choice);
      const current = await currentUpdateIdentity(request.repositoryRoot, session);
      if (isCandidateUnsaved(session.candidatePath) || isUpdatePlanStale(preview.identity, current)) {
        throw new UpdatePreviewError("PLAN_STALE", "Candidate, baseline or HEAD changed after planning; prepare a new plan.");
      }
      if (mode === "major" && ((preview.plan.change as { risk?: unknown } | undefined)?.risk !== "HIGH" ||
          (preview.plan.version as { declared_intent?: unknown } | undefined)?.declared_intent !== "major")) {
        throw new UpdatePreviewError("GOVERNANCE_PLAN_INVALID", "Production plan did not classify this UPDATE as high-risk governance / major.");
      }
      const materialized = await materializePreparedUpdate(
        preview, request.repositoryRoot, vscode.Uri.joinPath(context.globalStorageUri, "e2b-plans").fsPath,
      );
      preparedPlans.set(document.artifact_id, {
        request, candidatePath: session.candidatePath, canonicalPath: session.canonicalPath,
        artifactId: document.artifact_id, identity: preview.identity, materialized,
      });
      candidatePaths.set(document.artifact_id, session.candidatePath);
      const recommendationMismatch = (preview.plan.version as { mismatch?: unknown } | undefined)?.mismatch === true;
      setPlanState(document.artifact_id, recommendationMismatch ? "PLAN_READY_MISMATCH" : "PLAN_READY");
      output.appendLine(renderUpdatePreview(preview));
      output.appendLine(`Immutable production plan stored: ${materialized.planPath} (SHA-256 ${materialized.planSha256}).`);
      output.show(true);
      notifyPlanReady(
        () => vscode.window.showInformationMessage(
          `Read-only ${mode === "major" ? "governance major" : mode === "minor" ? "versioned minor" : "git-only"} UPDATE plan ready for ${document.artifact_id}. See AETERNA Documents output for impact, paths and version.`,
          "Compare Candidate",
        ),
        () => vscode.commands.executeCommand("aeterna.compareCandidate", item),
        (error) => reportCandidateError(output, "Compare Candidate", error),
      );
      return true;
    } catch (error) {
      reportCandidateError(output, "Prepare UPDATE plan", error);
      return false;
    }
  };
  context.subscriptions.push(
    output,
    provider,
    manager,
    vscode.workspace.registerTextDocumentContentProvider(EMPTY_CREATE_SCHEME, {
      provideTextDocumentContent: emptyCreateDocument,
    }),
    provider.onDidChangeTreeData(() => manager.refresh()),
    vscode.workspace.onDidChangeWorkspaceFolders(() => { void provider.refresh(); }),
    vscode.workspace.onDidChangeTextDocument((event) => {
      if (event.contentChanges.length > 0) {
        invalidateChangedDocument(event.document.uri.fsPath);
        if (createSession && pathsEqual(createSession.candidatePath, event.document.uri.fsPath)) {
          createPreview = undefined;
          createState = "CREATE candidate changed. Save it and prepare a new read-only plan.";
          manager.refresh();
        }
      }
    }),
    vscode.workspace.onDidSaveTextDocument((document) => {
      invalidateChangedDocument(document.uri.fsPath);
      if (createSession && pathsEqual(createSession.candidatePath, document.uri.fsPath)) {
        createPreview = undefined;
        createState = "CREATE candidate saved. Prepare a new read-only plan.";
        manager.refresh();
      }
      for (const [artifactId, candidatePath] of candidatePaths) {
        if (pathsEqual(candidatePath, document.uri.fsPath) && (planStates.get(artifactId) ?? "PLAN_MISSING") === "PLAN_MISSING") {
          setPlanState(artifactId, "CANDIDATE_SAVED");
        }
      }
    }),
    vscode.window.onDidChangeWindowState((state) => {
      if (!state.focused) {
        return;
      }
      if (createSession && createPreview) {
        const session = createSession;
        const preview = createPreview;
        void (async () => {
          try {
            const [bytes, baseline] = await Promise.all([readFile(session.candidatePath), inspectCreateBaseline(session.repositoryRoot)]);
            if (createPreview === preview && (createHash("sha256").update(bytes).digest("hex") !== preview.candidateSha256 ||
                baseline.head !== session.head || baseline.branch !== session.branch || !baseline.worktree_clean || !baseline.staging_empty)) {
              createPreview = undefined;
              createState = "CREATE plan STALE after candidate or repository change. Prepare a new plan.";
              manager.refresh();
            }
          } catch {
            if (createPreview === preview) {
              createPreview = undefined;
              createState = "CREATE plan STALE because its baseline could not be verified.";
              manager.refresh();
            }
          }
        })();
      }
      for (const [key, saved] of preparedPlans) {
        void (async () => {
          try {
            const session = await loadCandidateSession(saved.request);
            const current = await currentUpdateIdentity(saved.request.repositoryRoot, session);
            if (preparedPlans.get(key) === saved && isUpdatePlanStale(saved.identity, current)) {
              preparedPlans.delete(key);
              setPlanState(saved.artifactId, "PLAN_STALE");
              output.appendLine(`UPDATE plan STALE after candidate/baseline change: ${saved.artifactId}.`);
            }
          } catch {
            if (preparedPlans.get(key) === saved) {
              preparedPlans.delete(key);
              setPlanState(saved.artifactId, "PLAN_STALE");
              output.appendLine(`UPDATE plan STALE because its candidate/baseline could not be verified: ${saved.artifactId}.`);
            }
          }
        })();
      }
    }),
    vscode.window.registerTreeDataProvider("aeternaDocuments", provider),
    vscode.commands.registerCommand("aeterna.openManager", () => manager.show()),
    vscode.commands.registerCommand("aeterna.refreshDocuments", async () => {
      await provider.refresh();
    }),
    vscode.commands.registerCommand("aeterna.newDocument", async (): Promise<boolean> => {
      const root = provider.currentRepositoryRoot;
      if (!root) {
        void vscode.window.showErrorMessage("AETERNA Documents: repository is unavailable; refresh the list.");
        return false;
      }
      try {
        const baseline = await inspectCreateBaseline(root);
        const artifactId = await vscode.window.showInputBox({
          ignoreFocusOut: true,
          title: "New Document — artifact ID",
          prompt: "Enter a stable AET-DOC-... ID. Existing sessions reopen without overwriting edits.",
          validateInput: (value) => /^AET-DOC-[A-Z0-9]+(?:-[A-Z0-9]+)*$/.test(value)
            ? undefined : "Use AET-DOC- followed by uppercase alphanumeric tokens separated by single hyphens.",
        });
        if (artifactId === undefined) return false;
        if (baseline.existing_artifact_ids.some((id) => id.toLowerCase() === artifactId.toLowerCase())) {
          throw new CreateCandidateError("ARTIFACT_ID_COLLISION", "Artifact ID already exists in the current repository scan.");
        }
        const createStorageRoot = createStorageRootForRepository(root);
        const existing = await loadCreateSession(root, createStorageRoot, artifactId, baseline.branch, baseline.head);
        if (existing) {
          createSession = existing;
          createPreview = undefined;
          createState = `CREATE candidate reopened: ${artifactId}. Save and prepare a new plan.`;
          output.appendLine(`Existing CREATE candidate reopened without overwrite: ${existing.candidatePath}`);
        } else {
          const input = await promptCreateInput(baseline, artifactId);
          if (!input) return false;
          const approval = await vscode.window.showWarningMessage(
            `Approve new document identity and metadata for ${artifactId}?`,
            { modal: true, detail: [
              `Canonical target: ${input.targetPath}`, `Type: ${input.type}`, `Authority: ${input.authority}`,
              `Dependencies: ${input.dependencies.join(", ") || "none"}`, `Initial version: ${input.version}`,
              `Integration: ${input.integration}`, `H1 title: ${input.title}`,
              "Only a candidate outside the repository will be created. Apply requires a separate plan review and approval.",
            ].join("\n") },
            "Create External Candidate",
          );
          if (approval !== "Create External Candidate") return false;
          const created = await createOrOpenCreateSession(root, createStorageRoot, baseline.branch, baseline.head, input);
          createSession = created.session;
          createPreview = undefined;
          createState = `CREATE candidate ready: ${artifactId}. Save and prepare a read-only plan.`;
          output.appendLine(`CREATE candidate ${created.disposition}: ${created.session.candidatePath}`);
        }
        const session = createSession;
        manager.refresh();
        await vscode.window.showTextDocument(vscode.Uri.file(session.candidatePath), { preview: false, viewColumn: vscode.ViewColumn.Beside });
        await vscode.commands.executeCommand("markdown.showPreviewToSide");
        output.appendLine(`CREATE target (not created): ${session.input.targetPath}; baseline ${session.head}.`);
        return true;
      } catch (error) {
        reportCandidateError(output, "New Document", error);
        return false;
      }
    }),
    vscode.commands.registerCommand("aeterna.compareCreateCandidate", async (): Promise<boolean> => {
      const session = createSession;
      if (!session || !provider.currentRepositoryRoot || !pathsEqual(session.repositoryRoot, provider.currentRepositoryRoot)) {
        void vscode.window.showWarningMessage("Open a CREATE candidate in this repository before comparing it.");
        return false;
      }
      try {
        const verified = await loadCreateSession(session.repositoryRoot, session.storageRoot,
          session.input.artifactId, session.branch, session.head);
        if (!verified || !pathsEqual(verified.candidatePath, session.candidatePath)) {
          throw new CreateCandidateError("SESSION_DRIFT", "CREATE candidate session changed; reopen it before comparing.");
        }
        const diff = createDiffUris(session, vscode);
        await vscode.commands.executeCommand("vscode.diff", diff.empty, diff.candidate, diff.title, { preview: false });
        return true;
      } catch (error) {
        reportCandidateError(output, "Compare CREATE Candidate", error);
        return false;
      }
    }),
    vscode.commands.registerCommand("aeterna.prepareCreatePlan", async (): Promise<boolean> => {
      const session = createSession;
      const root = provider.currentRepositoryRoot;
      if (!session || !root) {
        void vscode.window.showWarningMessage("Open a New Document candidate in this VS Code window before preparing a CREATE plan.");
        return false;
      }
      try {
        if (isCandidateUnsaved(session.candidatePath)) {
          throw new CreatePlanError("CANDIDATE_UNSAVED", "Save every CREATE candidate editor before planning.");
        }
        createPreview = undefined;
        createState = `Preparing read-only CREATE plan for ${session.input.artifactId}…`;
        manager.refresh();
        const preview = await prepareCreatePreview(root, session, () => isCandidateUnsaved(session.candidatePath));
        if (isCandidateUnsaved(session.candidatePath)) {
          throw new CreatePlanError("CANDIDATE_UNSAVED", "CREATE candidate became unsaved during planning; plan discarded.");
        }
        createPreview = preview;
        createState = `CREATE plan ready for ${session.input.artifactId}. Review candidate, diff and plan before explicit Apply.`;
        manager.refresh();
        output.appendLine(renderCreatePreview(preview));
        output.show(true);
        await vscode.window.showTextDocument(vscode.Uri.file(preview.planPath), { preview: false, viewColumn: vscode.ViewColumn.Beside });
        void vscode.window.showInformationMessage("Read-only CREATE plan ready. Review the external candidate, Compare CREATE Candidate diff, full plan and AETERNA Documents output. Apply requires separate approval.");
        return true;
      } catch (error) {
        createPreview = undefined;
        createState = `CREATE plan blocked: ${error instanceof Error ? error.message : String(error)}`;
        manager.refresh();
        reportCandidateError(output, "Prepare CREATE plan", error);
        return false;
      }
    }),
    vscode.commands.registerCommand("aeterna.applyPreparedCreate", async (): Promise<boolean> => {
      const session = createSession;
      const preview = createPreview;
      const root = provider.currentRepositoryRoot;
      if (!session || !preview || !root) {
        void vscode.window.showWarningMessage("No current prepared CREATE plan exists. Save the external candidate and prepare a new plan.");
        return false;
      }
      try {
        const result = await createApplyCoordinator.apply(root, session, preview, {
          candidateIsDirty: () => isCandidateUnsaved(session.candidatePath),
          confirmReview: async (summary) => {
            output.appendLine(renderCreatePreview(preview));
            output.show(true);
            const choice = await vscode.window.showWarningMessage(
              `Review prepared CREATE for ${summary.artifactId}?`,
              { modal: true, detail: createApplyConfirmationDetail(summary) },
              "Review Candidate", "Review CREATE Diff", "Review Full Plan", "Continue to Final Approval",
            );
            if (choice === "Review Candidate") {
              await vscode.window.showTextDocument(vscode.Uri.file(session.candidatePath), { preview: false });
            } else if (choice === "Review CREATE Diff") {
              await vscode.commands.executeCommand("aeterna.compareCreateCandidate");
            } else if (choice === "Review Full Plan") {
              await vscode.window.showTextDocument(vscode.Uri.file(preview.planPath), { preview: false });
            }
            return choice === "Continue to Final Approval";
          },
          confirmFinal: async (summary) => (await vscode.window.showWarningMessage(
            `Final approval: create ${summary.artifactId} at ${summary.targetPath}?`,
            { modal: true, detail: createApplyConfirmationDetail(summary) },
            "Apply Prepared CREATE",
          )) === "Apply Prepared CREATE",
          onBeforeRun: () => {
            createState = `Production CREATE Apply running for ${session.input.artifactId}…`;
            manager.refresh();
            output.appendLine(`Production CREATE Apply started for ${session.input.artifactId}.`);
          },
        });
        output.appendLine(`CREATE Apply ${result.status}: ${result.message}`);
        if (result.reviewPath) output.appendLine(`Production CREATE review: ${result.reviewPath}`);
        if (result.status === "CANCELLED") {
          createState = createPreview === preview ? `CREATE plan ready for ${session.input.artifactId}; Apply cancelled without writes.`
            : "CREATE plan stale after candidate change. Prepare a new plan.";
          manager.refresh();
          return false;
        }
        if (createPreview === preview) createPreview = undefined;
        createState = `CREATE Apply ${result.status}: ${result.message}`;
        manager.refresh();
        if (result.status === "PASS") {
          await provider.refresh();
          offerProductionReview(result.reviewPath, `AETERNA ${session.input.artifactId}: CREATE Apply PASS, review verified. Inspect GitHub Desktop before manual commit/push.`, false);
          return true;
        }
        output.show(true);
        offerProductionReview(result.reviewPath, `AETERNA ${session.input.artifactId}: ${result.message}`, true);
        return false;
      } catch (error) {
        if (!(error instanceof CreateApplyError && error.code === "APPLY_ALREADY_ATTEMPTED")) {
          if (createPreview === preview) createPreview = undefined;
          createState = `CREATE Apply BLOCKED: ${error instanceof Error ? error.message : String(error)} Candidate preserved.`;
          manager.refresh();
        }
        reportCandidateError(output, "Apply Prepared CREATE", error);
        return false;
      }
    }),
    vscode.commands.registerCommand(
      "aeterna.openDocument",
      async (item: DocumentTreeItem | undefined) => {
        const document = await chooseDocument(provider, item);
        if (!document) {
          return;
        }
        await vscode.window.showTextDocument(vscode.Uri.file(document.absolutePath), {
          preview: false,
        });
      },
    ),
    vscode.commands.registerCommand(
      "aeterna.resolveDocument",
      async (item: DocumentTreeItem | undefined) => {
        const document = await chooseDocument(provider, item);
        const root = provider.currentRepositoryRoot;
        if (!document || !root) {
          void vscode.window.showErrorMessage(
            "AETERNA Documents: repository or document is unavailable.",
          );
          return;
        }
        try {
          const resolved = await resolveArtifact(root, document.artifact_id);
          output.appendLine(
            `Python interpreter used for resolve: ${resolved.interpreter.displayName}`,
          );
          output.appendLine(
            `Resolve success: ${resolved.result.artifact_id} -> ${resolved.result.path}`,
          );
          if (resolved.stderr.trim()) {
            output.appendLine(`Workflow stderr: ${resolved.stderr.trim()}`);
          }
          void vscode.window.showInformationMessage(
            `Resolved ${resolved.result.artifact_id}: ${resolved.result.path}`,
          );
        } catch (error) {
          const detail = error instanceof Error ? error.message : String(error);
          output.appendLine(`Resolve failure: ${detail}`);
          if (error instanceof WorkflowIntegrationError && error.stderr.trim()) {
            output.appendLine(`Workflow stderr: ${error.stderr.trim()}`);
          }
          void vscode.window.showErrorMessage(`AETERNA Documents: ${detail}`);
        }
      },
    ),
    vscode.commands.registerCommand(
      "aeterna.editCandidate",
      async (item: DocumentTreeItem | undefined, openPreview = false): Promise<boolean> => {
        const document = await chooseDocument(provider, item);
        if (!document) {
          return false;
        }
        try {
          const request = await prepareCandidateRequest(
            provider,
            document,
            candidateStorageRoot,
          );
          const routed = await createOrOpenRoutedCandidate(request, async () => {
            const decision = await vscode.window.showWarningMessage(
              "An earlier-baseline candidate exists and will be preserved. Create a separate candidate for the current canonical baseline? This does not Apply or overwrite the old candidate.",
              { modal: true },
              "Create Current-Baseline Candidate",
            );
            return decision === "Create Current-Baseline Candidate";
          });
          if (!routed) {
            output.appendLine(`Current-baseline candidate creation cancelled: ${document.artifact_id}.`);
            return false;
          }
          const session = routed.session;
          candidatePaths.set(document.artifact_id, session.candidatePath);
          if (!preparedPlans.has(document.artifact_id)) {
            setPlanState(document.artifact_id, "CANDIDATE_SAVED");
          }
          const alreadyOpen = openCandidateDocument(session.candidatePath);
          const editorOptions: vscode.TextDocumentShowOptions = openPreview
            ? { preview: false, viewColumn: vscode.ViewColumn.Beside }
            : { preview: false };
          if (alreadyOpen) {
            await vscode.window.showTextDocument(alreadyOpen, editorOptions);
          } else {
            await vscode.window.showTextDocument(
              vscode.Uri.file(session.candidatePath),
              editorOptions,
            );
          }
          if (openPreview) {
            await vscode.commands.executeCommand("markdown.showPreviewToSide");
            output.appendLine(`Native Markdown preview opened beside candidate: ${session.candidatePath}.`);
          }
          output.appendLine(
            `Candidate ${session.disposition.toLocaleLowerCase("en-US")}: ${session.manifest.artifactId} -> ${session.candidatePath}`,
          );
          if (routed.newerBaseline) {
            output.appendLine("Earlier-baseline candidate was preserved in its original E1 session.");
          }
          output.appendLine(
            `Candidate baseline SHA-256: ${session.manifest.baseline.canonicalSha256}`,
          );
          void vscode.window.showInformationMessage(
            "AETERNA candidate opened outside the repository. Saving updates only the candidate; Apply requires a separate reviewed plan and explicit confirmation. Use Open With manually to select ManulDown when desired.",
          );
          return true;
        } catch (error) {
          reportCandidateError(output, "Edit Candidate", error);
          return false;
        }
      },
    ),
    vscode.commands.registerCommand(
      "aeterna.previewCandidate",
      async (item: DocumentTreeItem | undefined): Promise<boolean> => {
        const document = await chooseDocument(provider, item);
        if (!document) return false;
        try {
          const request = await prepareCandidateRequest(provider, document, candidateStorageRoot);
          const { session } = await loadRoutedCandidate(request);
          const openDocument = openCandidateDocument(session.candidatePath);
          if (openDocument?.isDirty) {
            void vscode.window.showWarningMessage("Mentse a candidate-et az előnézet megnyitása előtt. A mentetlen módosításokat az előnézet nem mutatja biztosan.");
            return false;
          }
          if (openDocument) {
            await vscode.window.showTextDocument(openDocument, { preview: false });
          } else {
            await vscode.window.showTextDocument(vscode.Uri.file(session.candidatePath), { preview: false });
          }
          await vscode.commands.executeCommand("markdown.showPreviewToSide");
          output.appendLine(`Native Markdown preview opened for existing candidate: ${session.candidatePath}.`);
          return true;
        } catch (error) {
          reportCandidateError(output, "Preview Candidate", error);
          return false;
        }
      },
    ),
    vscode.commands.registerCommand(
      "aeterna.compareCandidate",
      async (item: DocumentTreeItem | undefined): Promise<boolean> => {
        const document = await chooseDocument(provider, item);
        if (!document) {
          return false;
        }
        try {
          const request = await prepareCandidateRequest(
            provider,
            document,
            candidateStorageRoot,
          );
          const { session } = await loadRoutedCandidate(request);
          const openDocument = openCandidateDocument(session.candidatePath);
          const documentState = candidateDocumentState(
            session.candidatePath,
            vscode.workspace.textDocuments.map((candidateDocument) => ({
              fsPath: candidateDocument.uri.fsPath,
              isDirty: candidateDocument.isDirty,
            })),
          );
          if (documentState === "OPEN_DIRTY") {
            if (!openDocument) {
              throw new Error("Dirty candidate document could not be located.");
            }
            const decision = await vscode.window.showWarningMessage(
              "The candidate has unsaved changes. Save the candidate before opening the native diff? This does not apply changes to the canonical document.",
              { modal: true },
              "Save and Compare",
            );
            if (decision !== "Save and Compare") {
              output.appendLine(
                `Candidate comparison cancelled with unsaved changes preserved: ${session.candidatePath}`,
              );
              return false;
            }
            if (!(await openDocument.save())) {
              throw new Error("VS Code did not save the candidate; comparison cancelled.");
            }
          }
          const diff = candidateDiffDescriptor(session);
          await vscode.commands.executeCommand(
            "vscode.diff",
            vscode.Uri.file(diff.leftCanonicalPath),
            vscode.Uri.file(diff.rightCandidatePath),
            diff.title,
            { preview: false },
          );
          output.appendLine(
            `Native diff opened: ${session.manifest.artifactId} (canonical -> candidate).`,
          );
          return true;
        } catch (error) {
          reportCandidateError(output, "Compare Candidate", error);
          return false;
        }
      },
    ),
    vscode.commands.registerCommand(
      "aeterna.prepareUpdatePlan",
      (item: DocumentTreeItem | undefined) => preparePlanForMode(item, "git-only"),
    ),
    vscode.commands.registerCommand(
      "aeterna.prepareMinorUpdatePlan",
      (item: DocumentTreeItem | undefined) => preparePlanForMode(item, "minor"),
    ),
    vscode.commands.registerCommand(
      "aeterna.prepareGovernanceUpdatePlan",
      (item: DocumentTreeItem | undefined) => preparePlanForMode(item, "major"),
    ),
    vscode.commands.registerCommand(
      "aeterna.applyPreparedUpdate",
      async (item: DocumentTreeItem | undefined): Promise<boolean> => {
        const document = await chooseDocument(provider, item);
        if (!document) return false;
        const saved = preparedPlans.get(document.artifact_id);
        if (!saved || !["PLAN_READY", "PLAN_READY_MISMATCH"].includes(planStates.get(document.artifact_id) ?? "PLAN_MISSING")) {
          void vscode.window.showWarningMessage("No current prepared UPDATE plan exists for this document. Save the candidate and prepare a new plan.");
          return false;
        }
        try {
          const result = await applyCoordinator.apply(
            saved.materialized,
            saved.request,
            document.title,
            document.version,
            {
              candidateIsDirty: () => isCandidateUnsaved(saved.candidatePath),
              confirm: async (summary) => {
                const choice = await vscode.window.showWarningMessage(
                  `Apply prepared UPDATE to ${summary.artifactId}?`,
                  { modal: true, detail: applyConfirmationDetail(summary) },
                  "Review Diff", "Apply Prepared UPDATE",
                );
                if (choice === "Review Diff") {
                  await vscode.commands.executeCommand("aeterna.compareCandidate", item);
                }
                return choice === "Apply Prepared UPDATE";
              },
              confirmMismatch: async (summary) => {
                const choice = await vscode.window.showWarningMessage(
          `Version recommendation mismatch for ${summary.artifactId}: planner recommends ${summary.recommendedIntent}, but this plan uses ${summary.versionIntent} and proposes ${summary.proposedVersion}. Apply anyway?`,
                  { modal: true, detail: "This is a separate, explicit approval. Canonical files may change without a version increase. Cancel to leave the repository unchanged." },
                  "Apply Despite Version Mismatch",
                );
                return choice === "Apply Despite Version Mismatch";
              },
              onBeforeRun: () => {
                setPlanState(document.artifact_id, "APPLY_RUNNING");
                output.appendLine(`Production governed Apply started for ${document.artifact_id}.`);
              },
            },
          );
          output.appendLine(`Governed Apply ${result.status}: ${result.message}`);
          if (result.reviewPath) output.appendLine(`Production review: ${result.reviewPath}`);
          if (result.status === "CANCELLED") {
            setPlanState(document.artifact_id, preparedPlans.get(document.artifact_id) === saved
              ? ((saved.materialized.preview.plan.version as { mismatch?: unknown } | undefined)?.mismatch === true ? "PLAN_READY_MISMATCH" : "PLAN_READY")
              : "PLAN_STALE");
            return false;
          }
          preparedPlans.delete(document.artifact_id);
          if (result.status === "PASS") {
            await provider.refresh();
            setPlanState(document.artifact_id, "APPLY_PASS");
            offerProductionReview(result.reviewPath, `AETERNA ${document.artifact_id}: Apply PASS, review verified. Inspect GitHub Desktop changes before manual commit/push.`, false);
            return true;
          }
          setPlanState(document.artifact_id, result.status === "BLOCKED" ? "APPLY_BLOCKED" : "APPLY_FAIL");
          output.show(true);
          offerProductionReview(result.reviewPath, `AETERNA ${document.artifact_id}: ${result.message} Review: ${result.reviewPath ?? "not available"}`, true);
          return false;
        } catch (error) {
          if (!(error instanceof ExplicitApplyError && error.code === "APPLY_ALREADY_ATTEMPTED")) {
            preparedPlans.delete(document.artifact_id);
            setPlanState(document.artifact_id, "APPLY_BLOCKED");
          }
          reportCandidateError(output, "Apply Prepared UPDATE", error);
          return false;
        }
      },
    ),
    vscode.commands.registerCommand(
      "aeterna.applyGovernanceUpdate",
      async (item: DocumentTreeItem | undefined): Promise<boolean> => {
        const document = await chooseDocument(provider, item);
        if (!document || !isGovernanceDocument(document.path)) return false;
        const saved = preparedPlans.get(document.artifact_id);
        if (!saved || saved.materialized.preview.manifest.change_class !== "semantic-governance-change" ||
            !["PLAN_READY", "PLAN_READY_MISMATCH"].includes(planStates.get(document.artifact_id) ?? "PLAN_MISSING")) {
          void vscode.window.showWarningMessage("No current high-risk governance plan exists for this document. Prepare a new governance plan.");
          return false;
        }
        try {
          const result = await applyCoordinator.applyGovernance(
            saved.materialized, saved.request, document.title, document.version,
            {
              candidateIsDirty: () => isCandidateUnsaved(saved.candidatePath),
              confirm: async (summary) => {
                const choice = await vscode.window.showWarningMessage(
                  `Review high-risk governance UPDATE for ${summary.artifactId}?`,
                  { modal: true, detail: applyConfirmationDetail(summary) },
                  "Review Diff", "Continue to Separate Approval",
                );
                if (choice === "Review Diff") await vscode.commands.executeCommand("aeterna.compareCandidate", item);
                return choice === "Continue to Separate Approval";
              },
              confirmMismatch: async (summary) => (await vscode.window.showWarningMessage(
                `Planner recommends ${summary.recommendedIntent}, but the selected governance plan declares ${summary.versionIntent}. Continue?`,
                { modal: true, detail: applyConfirmationDetail(summary) },
                "Continue Despite Mismatch",
              )) === "Continue Despite Mismatch",
              onBeforeRun: () => {
                setPlanState(document.artifact_id, "APPLY_RUNNING");
                output.appendLine(`Production governance Apply preconditions started for ${document.artifact_id}.`);
              },
            },
            async (summary, challenge) => {
              const approved = await vscode.window.showWarningMessage(
                `Approve this one governance Apply: ${summary.artifactId} — ${summary.title}?`,
                { modal: true, detail: [
                  `Version ${summary.version} → ${summary.proposedVersion}; semantic-governance-change / major.`,
                  `Repository HEAD: ${summary.head}`,
                  `Candidate SHA-256: ${summary.candidateSha256}`,
                  `Immutable plan semantic SHA-256: ${summary.planSemanticSha256}`,
                  `One-time operation: ${String(challenge.approval_binding.operation_id)}`,
                  `Exact planned writes: ${summary.plannedWrites.join(", ")}`,
                  `Dependency impact: ${summary.dependencyImpact}`,
                  "Production has rechecked the plan under the repository lock. This confirmation authorizes one current operation only.",
                ].join("\n") },
                "Approve This Governance Apply",
              );
              return approved === "Approve This Governance Apply";
            },
          );
          output.appendLine(`Governance Apply ${result.status}: ${result.message}`);
          if (result.reviewPath) output.appendLine(`Production review: ${result.reviewPath}`);
          if (result.status === "CANCELLED") {
            setPlanState(document.artifact_id, preparedPlans.get(document.artifact_id) === saved ? "PLAN_READY" : "PLAN_STALE");
            return false;
          }
          preparedPlans.delete(document.artifact_id);
          if (result.status === "PASS") {
            await provider.refresh();
            setPlanState(document.artifact_id, "APPLY_PASS");
            offerProductionReview(result.reviewPath, `AETERNA governance Apply PASS for ${document.artifact_id}; production review verified. Inspect GitHub Desktop before manual commit/push.`, false);
            return true;
          }
          setPlanState(document.artifact_id, result.status === "BLOCKED" ? "APPLY_BLOCKED" : "APPLY_FAIL");
          output.show(true);
          offerProductionReview(result.reviewPath, `AETERNA governance Apply ${result.status}: ${result.message}`, true);
          return false;
        } catch (error) {
          if (!(error instanceof ExplicitApplyError && error.code === "APPLY_ALREADY_ATTEMPTED")) {
            preparedPlans.delete(document.artifact_id);
            setPlanState(document.artifact_id, "APPLY_BLOCKED");
          }
          reportCandidateError(output, "Governance Apply", error);
          return false;
        }
      },
    ),
    vscode.commands.registerCommand("aeterna.showDiagnostics", () => {
      output.show(true);
    }),
  );

  output.appendLine(
    "AETERNA document extension activated (Document Manager, candidate editing, UPDATE and CREATE planning, explicit governed Apply).",
  );
  output.appendLine(`Candidate storage root: ${candidateStorageRoot}`);
  await provider.refresh();
}

export function deactivate(): void {
  // VS Code disposes registered resources through the extension context.
}
