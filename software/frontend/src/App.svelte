<script lang="ts">
  import "./app.css";
  import TopControls from "./lib/TopControls.svelte";
  import { onMount, onDestroy } from "svelte";
  import { getFullState } from "./api";
  import SubmitButton from "./lib/SubmitButton.svelte";
  import { ui_state } from "./state/uiState.svelte";
  import type {JsonSystemState} from "./state/systemState.svelte"

  // // import all dbay modules
  import * as Modules from "./lib/modules_dbay/index.js";


  import type { SystemState } from "./state/systemState.svelte";
  // import { system_state } from "./state/systemState.svelte";
  import { fallbackState } from "./fallbackState";
  import ModuleAdder from "./lib/modules_ui/ModuleAdder.svelte";
  import BasicContainer from "./lib/BasicContainer.svelte";
  import ReInitSource from "./lib/modules_ui/ReInitSource.svelte";

  import { createSystemStateFromJson } from "./lib/modules_dbay";

  function toggleDarkMode() {
    console.log("toggleDarkMode");
    document.body.classList.toggle("dark-mode");
  }

  // let total_state;

  // let non_initialized_state: SystemState = { data: [], valid: true, dev_mode: true};

  let system_state: SystemState = {data: $state([]), valid: $state(false), dev_mode: $state(false)};

  let serverNotResponding = false;
  // let serverNotInitialized = false;
  let num_modules = 0;
  let module_idx: number[] = [];
  let intervalId: number;

  // $: {
  //   // console.log("running")
  //   module_idx = Array.from(
  //     { length: $voltageStore.data.length },
  //     (_, i) => i + 1,
  //   );
  //   // console.log($voltageStore.data[0].slot)
  // }

  onMount(async () => {
    try {
      const json_state: JsonSystemState = await getFullState();
      // console.log("the response: ", response);
      // if the server responds, but the data field is empty, then the server is not initialized
      if (json_state.data.length === 0) {
        // ui_state.update((state) => {
        //   state.show_module_adder = true;
        //   return state;
        // });
        ui_state.show_module_adder = true; // reactive

        // console.log("serverNotInitialized");
      }
      // voltageStore.set(json_state);
      system_state = createSystemStateFromJson(json_state);

      // Start the interval
      intervalId = setInterval(async () => {
        const json_state = await getFullState();
        system_state = createSystemStateFromJson(json_state); // this seems costly
        // voltageStore.set(total_state);
      }, 1000); // 1000 milliseconds = 1 second

      // if no response, server is not available. Use fallback state for testing
    } catch (error) {
      // Handle the error here
      serverNotResponding = true;
      system_state = fallbackState;
      
    }
    num_modules = fallbackState.data.length;
    module_idx = Array.from({ length: num_modules }, (_, i) => i + 1);

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
      {#each fallbackState.data as module_state, i}
        <Modules.Module module_index={i + 1} />
      {/each}


    {:else if module_idx}
      {#each module_idx as idx}
        <Modules.Module module_index={idx} />
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
