<script lang="ts">
  import TopControls from "./lib/TopControls.svelte";
  import { onMount, onDestroy } from "svelte";
  import { ui_state } from "./state/uiState.svelte";
  import ModuleAdder from "./lib/modules_ui/ModuleAdder.svelte";
  import BasicContainer from "./lib/BasicContainer.svelte";
  import ReInitSource from "./lib/modules_ui/ReInitSource.svelte";
  import RemoteAccess from "./lib/modules_ui/RemoteAccess.svelte";

  import {
    createSystemStatefromJson,
    updateSystemStatefromJson,
    updateSystemStatetoFallback,
  } from "./lib/modules_dbay/index.svelte";

  import { system_state } from "./state/systemState.svelte";
  import { manager } from "./lib/modules_dbay/index.svelte";
  import { syncRuntime } from "./sync/runtime.svelte";
  import { syncErrors } from "./sync/errors.svelte";
  // import { Command } from "../node_modules_old/@tauri-apps/plugin-shell/dist-js";

  // import { Command } from "@tauri-apps/api/shell";

  function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
  }

  let serverNotResponding = $state(false);
  let show_loading = $state(true);
  let show_loading_longer = $state(false);

  let didCreateState = false;
  let failedSetup = false;
  let unsubSnapshot: (() => void) | undefined;
  let unsubStatus: (() => void) | undefined;
  let unsubErrors: (() => void) | undefined;
  let longLoadingTimer: ReturnType<typeof setTimeout>;
  let fallbackTimer: ReturnType<typeof setTimeout>;

  const inBrowser = !("__TAURI_INTERNALS__" in window);
  console.log(inBrowser ? "running in browser" : "running in tauri");

  function failSetup(error: unknown) {
    if (failedSetup) return;
    failedSetup = true;
    console.log("error!", error);
    show_loading = false;
    show_loading_longer = false;
    serverNotResponding = true;
    updateSystemStatetoFallback();
  }

  onMount(() => {
    unsubSnapshot = syncRuntime.onSnapshot(({ data }) => {
      if (data.data.every((module) => module.core.type === "empty")) {
        ui_state.show_module_adder = true;
      }

      if (!didCreateState) {
        createSystemStatefromJson(data);
        didCreateState = true;
      } else {
        updateSystemStatefromJson(data);
      }

      show_loading = false;
      show_loading_longer = false;
      serverNotResponding = false;
      clearTimeout(longLoadingTimer);
      clearTimeout(fallbackTimer);
    });

    unsubStatus = syncRuntime.onStatus((status) => {
      if (status === "error" && !didCreateState) {
        show_loading_longer = true;
      }
    });

    unsubErrors = syncRuntime.onCommandError((error) => {
      syncErrors.add(error);
    });

    longLoadingTimer = setTimeout(() => {
      if (!didCreateState) show_loading_longer = true;
    }, 3500);

    fallbackTimer = setTimeout(
      () => {
        if (!didCreateState) {
          failSetup(new Error("Sync server did not provide an initial snapshot."));
          syncRuntime.disconnect();
        }
      },
      inBrowser ? 10000 : 15000,
    );

    syncRuntime.connect();
  });

  onDestroy(() => {
    clearTimeout(longLoadingTimer);
    clearTimeout(fallbackTimer);
    unsubSnapshot?.();
    unsubStatus?.();
    unsubErrors?.();
    syncRuntime.disconnect();
  });
</script>

<div class="container-main">
  <div class="main-bar">
    <TopControls />

    {#if ui_state.show_module_adder}
      <ModuleAdder />
    {/if}

    {#if ui_state.show_source_reinit}
      <ReInitSource />
    {/if}

    {#if ui_state.show_remote_access}
      <RemoteAccess />
    {/if}

    {#if syncErrors.banner}
      <BasicContainer>
        <div class="sync-error sync-error-banner">
          <div>
            <p>{syncErrors.banner.message}</p>
            {#if syncErrors.banner.detail}
              <small>{syncErrors.banner.detail}</small>
            {/if}
          </div>
          <button type="button" onclick={() => syncErrors.clearBanner()}>
            Dismiss
          </button>
        </div>
      </BasicContainer>
    {/if}

    {#if show_loading && !show_loading_longer}
      <BasicContainer>
        <p class="text-red-500 p-3">Loading...</p>
      </BasicContainer>
    {/if}

    {#if show_loading_longer}
      <BasicContainer>
        <p class="text-red-500 p-3">
          Loading may take more than several seconds during first startup
        </p>
      </BasicContainer>
    {/if}

    {#if system_state.dev_mode}
      <BasicContainer>
        <p class="text-red-500 p-3">
          Dev mode is enabled. No UDP commands will be sent to the hardware.
        </p>
      </BasicContainer>
    {/if}

    {#if serverNotResponding}
      <BasicContainer>
        <p class="text-red-500 p-3">
          Server not responding. Viewing fallback state
        </p>
      </BasicContainer>
    {/if}

    {#if manager}
      {#each manager.component_array as component_holder}
        <component_holder.component
          module_index={component_holder.module_index}
        />
      {/each}
    {:else}
      <div class="basic-block">Loading...</div>
    {/if}
  </div>

  {#if syncErrors.toasts.length > 0}
    <div class="sync-toasts">
      {#each syncErrors.toasts as error (error.id)}
        <div class={`sync-toast sync-toast-${error.severity}`}>
          <p>{error.message}</p>
          <button type="button" onclick={() => syncErrors.clearToast(error.id)}>
            Dismiss
          </button>
        </div>
      {/each}
    </div>
  {/if}

  <div class="side-area"></div>
</div>

<style>
  .container-main {
    display: flex;
  }

  .main-bar {
    background-color: var(--bg-color);
  }

  .side-area {
    background-color: var(--bg-color);
  }

  .sync-error,
  .sync-toast {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem;
    color: #7f1d1d;
  }

  .sync-error p,
  .sync-toast p {
    margin: 0;
  }

  .sync-error small {
    display: block;
    margin-top: 0.25rem;
  }

  .sync-error button,
  .sync-toast button {
    border: 1px solid currentColor;
    border-radius: 4px;
    padding: 0.25rem 0.5rem;
    background: transparent;
    color: inherit;
    cursor: pointer;
  }

  .sync-toasts {
    position: fixed;
    right: 1rem;
    bottom: 1rem;
    z-index: 20;
    display: grid;
    gap: 0.5rem;
    max-width: min(22rem, calc(100vw - 2rem));
  }

  .sync-toast {
    border: 1px solid #fecaca;
    border-radius: 6px;
    background: #fef2f2;
    box-shadow: 0 8px 20px rgb(0 0 0 / 0.14);
  }

  .sync-toast-warning {
    color: #78350f;
    border-color: #fde68a;
    background: #fffbeb;
  }

  @media (min-width: 460px) {
    .main-bar {
      flex-grow: 0;
      min-width: 420px;
      max-width: 420px;
    }
    .side-area {
      display: flex;
      flex-grow: 4;
      min-height: 100vh;
      width: 100%;
      justify-content: center;
      align-items: center;
    }
  }

  @media (max-width: 460px) {
    .side-area {
      display: none;
    }
    .main-bar {
      width: 100%;
    }
  }
</style>
