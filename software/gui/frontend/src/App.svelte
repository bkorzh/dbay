<script lang="ts">
  import "./app.css";
  import TopControls from "./lib/TopControls.svelte";
  import { onMount, onDestroy } from "svelte";
  import { getFullState } from "./api";
  import SubmitButton from "./lib/buttons/SubmitButton.svelte";
  import { ui_state } from "./state/uiState.svelte";
  import type { IModule, JsonSystemState } from "./state/systemState.svelte";
  import Dac4D from "./lib/modules_dbay/dac4D.svelte";
  import type { SystemState } from "./state/systemState.svelte";
  import ModuleAdder from "./lib/modules_ui/ModuleAdder.svelte";
  import BasicContainer from "./lib/BasicContainer.svelte";
  import ReInitSource from "./lib/modules_ui/ReInitSource.svelte";
  import RemoteAccess from "./lib/modules_ui/RemoteAccess.svelte";

  import { ComponentManager } from "./lib/modules_dbay/index.svelte";

  import {
    createSystemStatefromJson,
    updateSystemStatefromJson,
    updateSystemStatetoFallback,
  } from "./lib/modules_dbay/index.svelte";

  import { system_state } from "./state/systemState.svelte";
  import { manager } from "./lib/modules_dbay/index.svelte";
  import QrCode from "./lib/modules_ui/RemoteAccess.svelte";
  // import { Command } from "../node_modules_old/@tauri-apps/plugin-shell/dist-js";

  // import { Command } from "@tauri-apps/api/shell";

  function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
  }

  let serverNotResponding = $state(false);
  // let serverNotInitialized = false;
  let num_modules = 0;

  let intervalId: Timer;
  let checkIntervalId: Timer;
  let json_state: JsonSystemState;
  let show_loading = $state(true);
  let show_loading_longer = $state(false);
  let in_browser = false;

  if ("__TAURI_INTERNALS__" in window) {
    console.log("running in tauri");
    in_browser = false;
  } else {
    console.log("running in browser");
    in_browser = true;
  }

  async function attemptSetup() {
    try {
      json_state = await getFullState();
      if (json_state.data.every((module) => module.core.type === "empty")) {
        ui_state.show_module_adder = true; // reactive
      }
      show_loading = false;
      show_loading_longer = false;
      createSystemStatefromJson(json_state);

      // Start the interval to update the system state every second
      intervalId = setInterval(async () => {
        try {
          json_state = await getFullState();

          // console.log("full state: ", json_state);

          updateSystemStatefromJson(json_state); // this seems costly
        } catch (error) {
          console.error("Failed to update system state:", error);
        }
      }, 1000);
    } catch (error) {
      throw error;
    }
  }

  async function failSetup(error) {
    console.log("error!", error);
    show_loading = false;
    show_loading_longer = false;
    serverNotResponding = true;
    updateSystemStatetoFallback();
  }

  onMount(async () => {
    if (in_browser) {
      try {
        await attemptSetup();
      } catch (error) {
        failSetup(error);
        updateSystemStatetoFallback();
      }
    } else {
      let attempts = 0;
      const maxAttempts = 20; // 10 seconds / 50 milliseconds
      const mediumAttempts = 7; // 5 seconds / 50 milliseconds
      // check if the server is available several times before giving up
      // the tauri sidecar (backend) can take a second or two to start
      checkIntervalId = setInterval(async () => {
        attempts++;
        try {
          await attemptSetup();
          clearInterval(checkIntervalId); // Stop checking once the backend responds
        } catch (error) {
          if (attempts >= mediumAttempts) {
            show_loading_longer = true;
          }

          if (attempts >= maxAttempts) {
            failSetup(error);
            clearInterval(checkIntervalId); // Stop checking after 5 seconds
          }
        }
        num_modules = system_state.data.length;
      }, 500);
    }
  });

  onDestroy(() => {
    clearInterval(intervalId);
    clearInterval(checkIntervalId);
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
