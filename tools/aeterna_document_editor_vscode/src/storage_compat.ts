import { lstat } from "node:fs/promises";
import path from "node:path";

const LEGACY_EXTENSION_ID = "undefined_publisher.aeterna-document-editor";

export async function updateCandidateStorageRoot(currentGlobalStorage: string): Promise<string> {
  const current = path.join(currentGlobalStorage, "e1-candidates");
  const legacy = path.join(path.dirname(currentGlobalStorage), LEGACY_EXTENSION_ID, "e1-candidates");
  if (path.basename(currentGlobalStorage).toLowerCase() === LEGACY_EXTENSION_ID) return current;
  try {
    const entry = await lstat(legacy);
    if (!entry.isDirectory() || entry.isSymbolicLink()) {
      throw new Error("Legacy UPDATE candidate storage is not a real directory; existing sessions were preserved.");
    }
    return legacy;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return current;
    throw error;
  }
}
