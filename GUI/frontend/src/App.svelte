<script lang="ts">
  import "./app.css";
  import TopControls from "./lib/TopControls.svelte";
  import Channel from "./lib/BareChannel.svelte";
  import { onMount, onDestroy } from "svelte";
  import { getFullState } from "./api";
  import SubmitButton from "./lib/SubmitButton.svelte";
  import { uiStateStore } from "./stores/uiStateStore";
  import Module from "./lib/Module.svelte";
  import { writable } from "svelte/store";
  import type { SystemState, Module4chState } from "./stores/voltageStore";
  import { voltageStore } from "./stores/voltageStore";
  import { fallbackState } from "./fallbackState";
  import ModuleAdder from "./lib/ModuleAdder.svelte";
  import BasicContainer from "./lib/BasicContainer.svelte";
  import ReInitSource from "./lib/ReInitSource.svelte";

  function toggleDarkMode() {
    console.log("toggleDarkMode");
    document.body.classList.toggle("dark-mode");
  }

  let total_state;

  let non_initialized_state: SystemState = { data: [], valid: true };

  let serverNotResponding = false;
  // let serverNotInitialized = false;
  let num_modules = 0;
  let module_idx = [];
  let intervalId;

  $: {
    // console.log("running")
    module_idx = Array.from(
      { length: $voltageStore.data.length },
      (_, i) => i + 1,
    );
    // console.log($voltageStore.data[0].slot)
  }

  onMount(async () => {
    try {
      const response = await getFullState();
      // console.log("the response: ", response);
      total_state = response;

      // console.log("total_state: ", total_state);

      // if the server responds, but the data field is empty, then the server is not initialized
      if (total_state.data.length === 0) {
        uiStateStore.update((state) => {
          state.show_module_adder = true;
          return state;
        });
        // console.log("serverNotInitialized");
        voltageStore.set(non_initialized_state);
      }

      voltageStore.set(total_state);
      num_modules = total_state.data.length;
      module_idx = Array.from({ length: num_modules }, (_, i) => i + 1);

      // Start the interval
      intervalId = setInterval(async () => {
        const response = await getFullState();
        total_state = response;
        voltageStore.set(total_state);
      }, 1000); // 1000 milliseconds = 1 second

      // if no response, server is not available. Use fallback state for testing
    } catch (error) {
      console.log("An error occurred: ", error);
      // Handle the error here
      serverNotResponding = true;
      voltageStore.set(fallbackState);
      num_modules = fallbackState.data.length;
      module_idx = Array.from({ length: num_modules }, (_, i) => i + 1);
    }
  });

  onDestroy(() => {
    // Clear the interval when the component is destroyed
    clearInterval(intervalId);
  });
</script>

<div class="container-main">
  <div class="main-bar">
    <TopControls />

    {#if $uiStateStore.show_module_adder}
      <ModuleAdder />
    {/if}

    {#if $uiStateStore.show_source_reinit}
      <ReInitSource />
    {/if}

    {#if serverNotResponding}
      <BasicContainer>
        <!-- add some padding -->
        <p class="text-red-500 p-3">
          Server not responding. Viewing fallback state
        </p>
      </BasicContainer>
      {#each fallbackState.data as module_state, i}
        <Module module_index={i + 1} />
      {/each}
    {:else if module_idx}
      {#each module_idx as idx}
        <Module module_index={idx} />
      {/each}
    {:else}
      <div class="basic-block">Loading...</div>
    {/if}
  </div>

  <div class="side-area" />
</div>

<style>
  /* .basic-block {
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 0 7px rgba(0, 0, 0, 0.05);
    border: 1.3px solid var(--outer-border-color);
    margin: 0.2rem 0rem;
  } */

  /* input {
    background-color: var(--display-color);
    border-radius: 4px;
    border: 1.5px solid var(--inner-border-color);
    padding: 0rem 0.3rem;
    font-family: "Roboto Flex", sans-serif;
    font-weight: 300;
    font-size: 1.7rem;
    letter-spacing: 0.58rem;
    color: var(--digits-color);
    transition: background-color 0.1s ease-in-out;
    margin: 0.5rem 0rem;
  } */

  .container-main {
    display: flex;
    /* flex-direction: row; */
    /* justify-content: space-between; */
    /* align-items: stretch; */
    /* align-items: center; */
    /* min-height: 100vh;
    min-width: 100vw; */
    /* width: 100%; */
  }

  .main-bar {
    /* justify-content: center; */
    /* align-items: center; */
    /* height: 100%; */
    background-color: var(--bg-color);

    /* flex-grow: 1; */
    /* min-width: 300px; */

    /* display: flex; */
    /* flex-direction: column; */
    /* flex-grow: 1; */
  }

  .side-area {
    background-color: var(--bg-color);
  }

  /* * {
    background-color: var(--bg-color);
  } */

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
