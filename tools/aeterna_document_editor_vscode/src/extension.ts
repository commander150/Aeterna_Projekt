import * as vscode from "vscode";

import {
  type ManagedDocument,
  loadManagedDocuments,
} from "./registry";
import { resolveRepositoryRoot } from "./repository";
import { resolveArtifact, WorkflowIntegrationError } from "./workflow";

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

export async function activate(context: vscode.ExtensionContext): Promise<void> {
  const output = vscode.window.createOutputChannel("AETERNA Documents");
  const provider = new AeternaDocumentsProvider(output);
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
    vscode.commands.registerCommand("aeterna.showDiagnostics", () => {
      output.show(true);
    }),
  );

  output.appendLine("AETERNA read-only document extension activated.");
  await provider.refresh();
}

export function deactivate(): void {
  // VS Code disposes registered resources through the extension context.
}
