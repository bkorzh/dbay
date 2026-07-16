import type { SyncCommandError } from "lab-link/core";

export interface DisplayError {
  id: string;
  message: string;
  detail?: string;
  code: string;
  severity: "info" | "warning" | "error";
  display: "toast" | "banner" | "inline";
  path?: string;
  recoverable: boolean;
  createdAt: number;
}

export const syncErrors = $state({
  banner: null as DisplayError | null,
  toasts: [] as DisplayError[],
  byPath: new Map<string, DisplayError>(),

  add(error: SyncCommandError) {
    const item: DisplayError = {
      id: `${error.code}-${Date.now()}-${Math.random()}`,
      message: error.message,
      detail: error.detail,
      code: error.code,
      severity: error.severity,
      display: error.display,
      path: error.path,
      recoverable: error.recoverable,
      createdAt: Date.now(),
    };

    if (item.display === "banner") {
      this.banner = item;
      return;
    }

    if (item.display === "inline" && item.path) {
      this.byPath.set(item.path, item);
      return;
    }

    this.toasts.push(item);
  },

  clearBanner() {
    this.banner = null;
  },

  clearToast(id: string) {
    this.toasts = this.toasts.filter((toast) => toast.id !== id);
  },

  clearPath(path: string) {
    this.byPath.delete(path);
  },
});
