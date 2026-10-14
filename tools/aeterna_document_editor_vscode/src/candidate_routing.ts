import { createHash } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";

import {
  CandidateSessionError,
  type CandidateSession,
  type CandidateSessionRequest,
  createOrOpenCandidateSession,
  loadCandidateSession,
} from "./candidate";
import { resolveCanonicalMarkdownPath } from "./registry";

export interface RoutedCandidateSession {
  readonly request: CandidateSessionRequest;
  readonly session: CandidateSession;
  readonly newerBaseline: boolean;
}

async function currentBaselineRequest(
  request: CandidateSessionRequest,
): Promise<CandidateSessionRequest> {
  const canonical = await resolveCanonicalMarkdownPath(
    request.repositoryRoot,
    request.artifact.canonicalPath,
  );
  const digest = createHash("sha256")
    .update(await readFile(canonical))
    .digest("hex");
  return {
    ...request,
    storageRoot: path.join(request.storageRoot, "baseline-sessions", digest),
  };
}

function isBaselineDrift(error: unknown): error is CandidateSessionError {
  return error instanceof CandidateSessionError && error.code === "BASELINE_DRIFT";
}

export async function createOrOpenRoutedCandidate(
  request: CandidateSessionRequest,
  confirmNewBaseline: () => Promise<boolean>,
): Promise<RoutedCandidateSession | undefined> {
  try {
    return {
      request,
      session: await createOrOpenCandidateSession(request),
      newerBaseline: false,
    };
  } catch (error) {
    if (!isBaselineDrift(error)) {
      throw error;
    }
    if (!(await confirmNewBaseline())) {
      return undefined;
    }
    const current = await currentBaselineRequest(request);
    return {
      request: current,
      session: await createOrOpenCandidateSession(current),
      newerBaseline: true,
    };
  }
}

export async function loadRoutedCandidate(
  request: CandidateSessionRequest,
): Promise<RoutedCandidateSession> {
  try {
    return {
      request,
      session: await loadCandidateSession(request),
      newerBaseline: false,
    };
  } catch (error) {
    if (!isBaselineDrift(error)) {
      throw error;
    }
    const current = await currentBaselineRequest(request);
    try {
      if (!(await stat(current.storageRoot)).isDirectory()) {
        throw new Error("Current-baseline candidate storage is not a directory.");
      }
    } catch (storageError) {
      if ((storageError as NodeJS.ErrnoException).code !== "ENOENT") {
        throw storageError;
      }
      throw new CandidateSessionError(
        "BASELINE_DRIFT",
        "The earlier-baseline candidate was preserved. Choose Edit Candidate to create a separate candidate for the current baseline.",
      );
    }
    try {
      return {
        request: current,
        session: await loadCandidateSession(current),
        newerBaseline: true,
      };
    } catch (currentError) {
      if (currentError instanceof CandidateSessionError && currentError.code === "SESSION_NOT_FOUND") {
        throw new CandidateSessionError(
          "BASELINE_DRIFT",
          "The earlier-baseline candidate was preserved. Choose Edit Candidate to create a separate candidate for the current baseline.",
        );
      }
      throw currentError;
    }
  }
}
