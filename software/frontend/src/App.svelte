<script lang="ts">
  import "./app.css";
  import TopControls from "./lib/TopControls.svelte";
  import { onMount, onDestroy } from "svelte";
  import { getFullState } from "./api";
  import SubmitButton from "./lib/buttons/SubmitButton.svelte";
  import { ui_state } from "./state/uiState.svelte";
  import type {IModule, JsonSystemState} from "./state/systemState.svelte"
  import Dac4D from "./lib/modules_dbay/dac4D.svelte";
  import type { SystemState } from "./state/systemState.svelte";
  import ModuleAdder from "./lib/modules_ui/ModuleAdder.svelte";
  import BasicContainer from "./lib/BasicContainer.svelte";
  import ReInitSource from "./lib/modules_ui/ReInitSource.svelte";

  import { ComponentManager } from "./lib/modules_dbay/index.svelte";

  import { createSystemStatefromJson, updateSystemStatefromJson, updateSystemStatetoFallback } from "./lib/modules_dbay/index.svelte";

  import { system_state } from "./state/systemState.svelte";
  import { manager } from "./lib/modules_dbay/index.svelte";

  function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
  }

  let serverNotResponding = $state(false);
  // let serverNotInitialized = false;
  let num_modules = 0;
  
  let intervalId: number;
  let json_state: JsonSystemState

  // let component_array = $derived(createComponentArray(system_state.data))
  


  onMount(async () => {
    try {
      json_state = await getFullState();
      console.log("initial json state: ", json_state)
      // if the server responds, but the data field is empty, then the server is not initialized
      if (json_state.data.every(module => module.core.type === "empty")) {
        ui_state.show_module_adder = true; // reactive
      }

      createSystemStatefromJson(json_state);

      // Start the interval
      intervalId = setInterval(async () => {
        
        json_state = await getFullState();
        updateSystemStatefromJson(json_state); // this seems costly
      }, 1000); // 1000 milliseconds = 1 second

      // if no response, server is not available. Use fallback state for testing
    } catch (error) {
      console.log("error!", error);
      serverNotResponding = true;
      updateSystemStatetoFallback();
    }
    num_modules = system_state.data.length;

    

  });

  onDestroy(() => {
    // Clear the interval when the component is destroyed
    clearInterval(intervalId);
  });

  $effect(() => {
    console.log("system_state inside effect: ", system_state.data)
    // if (scrollY > 0) {
    //   console.log("scrollY: ", scrollY);
    // }
  });

  $effect(() => {
    console.log("manager.module_idx inside effect: ", manager.module_idx)
  });


  // let scrollable = $state(true);

  // wheel = (node, options) => {
  //   let { scrollable } = options;
  //   console.log("scrollable: ", scrollable);

  //   const handler = e => {
  //     // console.log("inside handler")
  //     // console.log(e)

  //     // if the event comes from an input: then prevent default

  //     if (e.target.tagName === "INPUT") {
  //       e.preventDefault();
  //       console.log("input")
  //       return;
  //     }
  //     // if (!scrollable) e.preventDefault();
  //   };

  //   node.addEventListener('wheel', handler, { passive: false });

  //   return {
  //     update(options) {
  //       scrollable = options.scrollable;
  //     },
  //     destroy() {
  //       node.removeEventListener('wheel', handler, { passive: false });
  //     }
  //   };
  // };
</script>

<!-- <svelte:window use:wheel={{scrollable}}/> -->

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

    {#if manager.module_idx}
      {#each manager.module_idx as idx, i (idx)}
      <!-- module_idx has numbers for filled slots. e.g [0, 3, 5] -->
      <!-- i counts from 0 to (one minus number of filled slots). e.g. [0, 1, 2] -->
        <svelte:component this={manager.component_array[i]} module_index={idx}/>
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
