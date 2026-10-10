import * as vscode from "vscode";

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
  createOrOpenCandidateSession,
  loadCandidateSession,
  pathsEqual,
} from "./candidate";

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
      this.output.appendLine(
        `Registry load result: PASS (${loaded.documents.length} managed Markdown documents).`,
      );
      for (const diagnostic of loaded.diagnostics) {
        this.output.appendLine(`Registry/path validation problem: ${diagnostic}`);
      }
    } catch (error) {
      const detail = error instanceof Error ? error.message : String(error);
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
    { placeHolder: "Select an AETERNA managed document" },
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
    resolved.result.path !== document.path
  ) {
    throw new CandidateSessionError(
      "CANONICAL_UNAVAILABLE",
      "Workflow resolve result does not match the selected registry artifact.",
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

function reportCandidateError(
  output: vscode.OutputChannel,
  action: string,
  error: unknown,
): void {
  const detail = error instanceof Error ? error.message : String(error);
  const code = error instanceof CandidateSessionError ? ` [${error.code}]` : "";
  output.appendLine(`${action} failed${code}: ${detail}`);
  void vscode.window.showErrorMessage(`AETERNA Documents: ${detail}`);
}

export async function activate(context: vscode.ExtensionContext): Promise<void> {
  const output = vscode.window.createOutputChannel("AETERNA Documents");
  const provider = new AeternaDocumentsProvider(output);
  const candidateStorageRoot = vscode.Uri.joinPath(
    context.globalStorageUri,
    "e1-candidates",
  ).fsPath;
  context.subscriptions.push(
    output,
    provider,
    vscode.window.registerTreeDataProvider("aeternaDocuments", provider),
    vscode.commands.registerCommand("aeterna.refreshDocuments", async () => {
      await provider.refresh();
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
      async (item: DocumentTreeItem | undefined) => {
        const document = await chooseDocument(provider, item);
        if (!document) {
          return;
        }
        try {
          const request = await prepareCandidateRequest(
            provider,
            document,
            candidateStorageRoot,
          );
          const session = await createOrOpenCandidateSession(request);
          const alreadyOpen = openCandidateDocument(session.candidatePath);
          if (alreadyOpen) {
            await vscode.window.showTextDocument(alreadyOpen, { preview: false });
          } else {
            await vscode.window.showTextDocument(
              vscode.Uri.file(session.candidatePath),
              { preview: false },
            );
          }
          output.appendLine(
            `Candidate ${session.disposition.toLocaleLowerCase("en-US")}: ${session.manifest.artifactId} -> ${session.candidatePath}`,
          );
          output.appendLine(
            `Candidate baseline SHA-256: ${session.manifest.baseline.canonicalSha256}`,
          );
          void vscode.window.showInformationMessage(
            "AETERNA candidate opened outside the repository. Saving updates only the candidate; governed Apply is a separate explicit action and is not available in E1. Use Open With manually to select ManulDown when desired.",
          );
        } catch (error) {
          reportCandidateError(output, "Edit Candidate", error);
        }
      },
    ),
    vscode.commands.registerCommand(
      "aeterna.compareCandidate",
      async (item: DocumentTreeItem | undefined) => {
        const document = await chooseDocument(provider, item);
        if (!document) {
          return;
        }
        try {
          const request = await prepareCandidateRequest(
            provider,
            document,
            candidateStorageRoot,
          );
          const session = await loadCandidateSession(request);
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
              return;
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
        } catch (error) {
          reportCandidateError(output, "Compare Candidate", error);
        }
      },
    ),
    vscode.commands.registerCommand("aeterna.showDiagnostics", () => {
      output.show(true);
    }),
  );

  output.appendLine(
    "AETERNA document extension activated (E1 candidate editing foundation).",
  );
  output.appendLine(`Candidate storage root: ${candidateStorageRoot}`);
  await provider.refresh();
}

export function deactivate(): void {
  // VS Code disposes registered resources through the extension context.
}
