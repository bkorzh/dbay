import { createSyncRuntime, type SyncRuntime } from "lab-link/svelte";
import type { JsonSystemState } from "../state/systemState.svelte";

function backendWsUrl() {
  if (typeof window === "undefined") {
    return "ws://127.0.0.1:8345/sync/ws";
  }

  const isTauri = "__TAURI_INTERNALS__" in window;
  const useBackendBaseUrl = isTauri || import.meta.env.DEV;

  if (useBackendBaseUrl) {
    return "ws://127.0.0.1:8345/sync/ws";
  }

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/sync/ws`;
}

export const syncRuntime: SyncRuntime<JsonSystemState> =
  createSyncRuntime<JsonSystemState>({
    url: backendWsUrl(),
    autoConnect: false,
    commandTimeoutMs: 10_000,
  });
