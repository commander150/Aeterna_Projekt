import { createHash, randomUUID } from "node:crypto";
import { lstat, open, readFile, realpath, rename, rm } from "node:fs/promises";
import path from "node:path";

import { pathsEqual } from "./candidate";

export class CandidateVersionError extends Error {
  public constructor(public readonly code: string, message: string) {
    super(message);
    this.name = "CandidateVersionError";
  }
}

function sha256(bytes: Buffer): string {
  return createHash("sha256").update(bytes).digest("hex");
}

export function suggestMinorVersion(current: string): string | undefined {
  const match = /^(\d+)\.(\d+)$/.exec(current);
  if (!match) return undefined;
  return `${match[1]}.${BigInt(match[2]!) + 1n}`;
}

export function validateProposedVersion(current: string, proposed: string): void {
  if (!proposed || proposed !== proposed.trim() || proposed === current ||
      /["\\\u0000-\u001f\u007f]/.test(proposed)) {
    throw new CandidateVersionError("VERSION_INVALID", "Choose a new, non-empty version without quotes, backslashes or control characters.");
  }
}

function versionLine(bytes: Buffer): { lines: string[]; index: number; version: string } {
  let text: string;
  try {
    text = new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(bytes);
  } catch {
    throw new CandidateVersionError("CANDIDATE_FORMAT_UNSAFE", "Candidate is not valid UTF-8.");
  }
  const lines = text.match(/[^\n]*\n|[^\n]+$/g) ?? [];
  if (lines.length < 3 || lines[0]!.replace(/\r?\n$/, "").replace(/^\uFEFF/, "") !== "---") {
    throw new CandidateVersionError("CANDIDATE_FORMAT_UNSAFE", "Candidate needs a simple Markdown YAML front matter block.");
  }
  const closing = lines.findIndex((line, index) => index > 0 && line.replace(/\r?\n$/, "") === "---");
  if (closing < 2) {
    throw new CandidateVersionError("CANDIDATE_FORMAT_UNSAFE", "Candidate front matter has no valid closing delimiter.");
  }
  const indices: number[] = [];
  for (let index = 1; index < closing; index += 1) {
    if (/^version(?:\s*:|\s*$)/.test(lines[index]!)) indices.push(index);
  }
  if (indices.length !== 1) {
    throw new CandidateVersionError("CANDIDATE_FORMAT_UNSAFE", "Candidate must have exactly one top-level version field.");
  }
  const index = indices[0]!;
  const match = /^version: "([^"\\\r\n]+)"(?:\r?\n)?$/.exec(lines[index]!);
  if (!match) {
    throw new CandidateVersionError("CANDIDATE_FORMAT_UNSAFE", "Candidate version must be a simple, double-quoted YAML scalar.");
  }
  return { lines, index, version: match[1]! };
}

export function candidateVersion(bytes: Buffer): string {
  return versionLine(bytes).version;
}

export function replaceCandidateVersion(bytes: Buffer, current: string, proposed: string): Buffer {
  validateProposedVersion(current, proposed);
  const parsed = versionLine(bytes);
  if (parsed.version !== current) {
    throw new CandidateVersionError("CANDIDATE_VERSION_DRIFT", "Candidate version changed since it was inspected.");
  }
  const line = parsed.lines[parsed.index]!;
  const ending = line.endsWith("\r\n") ? "\r\n" : line.endsWith("\n") ? "\n" : "";
  parsed.lines[parsed.index] = `version: "${proposed}"${ending}`;
  return Buffer.from(parsed.lines.join(""), "utf8");
}

export async function writeCandidateVersion(
  candidatePath: string,
  expectedSha256: string,
  current: string,
  proposed: string,
): Promise<string> {
  const parent = path.dirname(candidatePath);
  if (!pathsEqual(await realpath(parent), parent)) {
    throw new CandidateVersionError("CANDIDATE_UNSAFE", "Candidate parent must not be a symlink or junction.");
  }
  const info = await lstat(candidatePath);
  if (!info.isFile() || info.isSymbolicLink()) {
    throw new CandidateVersionError("CANDIDATE_UNSAFE", "Candidate must remain a regular file.");
  }
  const original = await readFile(candidatePath);
  if (sha256(original) !== expectedSha256) {
    throw new CandidateVersionError("CANDIDATE_VERSION_DRIFT", "Candidate changed before version approval could be applied.");
  }
  const updated = replaceCandidateVersion(original, current, proposed);
  const temporary = path.join(parent, `.${path.basename(candidatePath)}.e2c-${randomUUID()}.tmp`);
  try {
    const handle = await open(temporary, "wx", 0o600);
    try {
      await handle.writeFile(updated);
      await handle.sync();
    } finally {
      await handle.close();
    }
    if (!pathsEqual(await realpath(parent), parent)) {
      throw new CandidateVersionError("CANDIDATE_UNSAFE", "Candidate parent changed before the version write.");
    }
    const latest = await lstat(candidatePath);
    if (!latest.isFile() || latest.isSymbolicLink() ||
        sha256(await readFile(candidatePath)) !== expectedSha256) {
      throw new CandidateVersionError("CANDIDATE_VERSION_DRIFT", "Candidate changed while the approved version edit was prepared.");
    }
    await rename(temporary, candidatePath);
    if (sha256(await readFile(candidatePath)) !== sha256(updated)) {
      throw new CandidateVersionError("CANDIDATE_WRITE_FAILED", "Candidate version write could not be verified.");
    }
    return sha256(updated);
  } finally {
    await rm(temporary, { force: true });
  }
}
