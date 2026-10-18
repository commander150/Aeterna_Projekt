import type * as vscode from "vscode";

import type { CreateSession } from "./create_candidate";

export const EMPTY_CREATE_SCHEME = "aeterna-empty-create";

export function createDiffUris(session: CreateSession, host: typeof vscode): {
  readonly empty: vscode.Uri;
  readonly candidate: vscode.Uri;
  readonly title: string;
} {
  return {
    empty: host.Uri.from({ scheme: EMPTY_CREATE_SCHEME, path: "/empty.md" }),
    candidate: host.Uri.file(session.candidatePath),
    title: `${session.input.artifactId}: new document (empty → candidate)`,
  };
}

export function emptyCreateDocument(): string {
  return "";
}
