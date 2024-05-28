<script lang="ts">
  import "./app.css";
  import TopControls from "./lib/TopControls.svelte";
  import { onMount, onDestroy } from "svelte";
  import { getFullState } from "./api";
  import SubmitButton from "./lib/SubmitButton.svelte";
  import { ui_state } from "./state/uiState.svelte";
  import type {IModule, JsonSystemState} from "./state/systemState.svelte"
  import Dac4D from "./lib/modules_dbay/dac4D.svelte";
  import type { SystemState } from "./state/systemState.svelte";
  import ModuleAdder from "./lib/modules_ui/ModuleAdder.svelte";
  import BasicContainer from "./lib/BasicContainer.svelte";
  import ReInitSource from "./lib/modules_ui/ReInitSource.svelte";

  import { createComponentArray } from "./lib/modules_dbay/index.svelte";

  import { updateSystemStatefromJson, updateSystemStatetoFallback } from "./lib/modules_dbay/index.svelte";

  import { system_state } from "./state/systemState.svelte";

  function toggleDarkMode() {
    console.log("toggleDarkMode");
    document.body.classList.toggle("dark-mode");
  }


  let serverNotResponding = $state(false);
  // let serverNotInitialized = false;
  let num_modules = 0;
  let module_idx: number[] = $state([]);
  let intervalId: number;

  let component_array = $derived(createComponentArray(system_state.data))

  onMount(async () => {
    try {
      const json_state: JsonSystemState = await getFullState();
      // if the server responds, but the data field is empty, then the server is not initialized
      if (json_state.data.length === 0) {
        ui_state.show_module_adder = true; // reactive

      }
      updateSystemStatefromJson(json_state);

      // Start the interval
      intervalId = setInterval(async () => {
        const json_state = await getFullState();
        updateSystemStatefromJson(json_state); // this seems costly
      }, 1000); // 1000 milliseconds = 1 second

      // if no response, server is not available. Use fallback state for testing
    } catch (error) {
      serverNotResponding = true;
      updateSystemStatetoFallback();
    }
    num_modules = system_state.data.length;
    module_idx = Array.from({ length: num_modules }, (_, i) => i + 1);
    // console.log("module_idx: ", module_idx);
    // console.log("component_array: ", component_array);

  });

  onDestroy(() => {
    // Clear the interval when the component is destroyed
    clearInterval(intervalId);
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

    {#if module_idx}
      {#each module_idx as idx}
        <svelte:component this={component_array[idx-1]} module_index={idx}/>
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
