import { realpath, stat } from "node:fs/promises";
import path from "node:path";

export const REPOSITORY_SENTINELS = [
  "project/generated/artifacts_registry.json",
  "tools/aeterna_document_workflow/cli.py",
] as const;

export class RepositoryDiscoveryError extends Error {
  public constructor(
    public readonly code: "NO_CANDIDATE" | "MULTIPLE_CANDIDATES",
    message: string,
    public readonly candidates: readonly string[] = [],
  ) {
    super(message);
    this.name = "RepositoryDiscoveryError";
  }
}

async function isFile(filePath: string): Promise<boolean> {
  try {
    return (await stat(filePath)).isFile();
  } catch {
    return false;
  }
}

export async function findRepositoryCandidates(
  workspaceRoots: readonly string[],
): Promise<string[]> {
  const candidates = new Set<string>();

  for (const workspaceRoot of workspaceRoots) {
    const normalizedRoot = path.resolve(workspaceRoot);
    const sentinelResults = await Promise.all(
      REPOSITORY_SENTINELS.map((sentinel) =>
        isFile(path.join(normalizedRoot, ...sentinel.split("/"))),
      ),
    );
    if (sentinelResults.every(Boolean)) {
      candidates.add(await realpath(normalizedRoot));
    }
  }

  return [...candidates].sort((left, right) => left.localeCompare(right));
}

export async function resolveRepositoryRoot(
  workspaceRoots: readonly string[],
): Promise<string> {
  const candidates = await findRepositoryCandidates(workspaceRoots);
  if (candidates.length === 0) {
    throw new RepositoryDiscoveryError(
      "NO_CANDIDATE",
      "No AETERNA repository was found in the open workspace folders.",
    );
  }
  if (candidates.length > 1) {
    throw new RepositoryDiscoveryError(
      "MULTIPLE_CANDIDATES",
      `Multiple AETERNA repositories were found; refusing to guess: ${candidates.join(", ")}`,
      candidates,
    );
  }
  return candidates[0]!;
}
