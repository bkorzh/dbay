<script lang='ts'>
  import Channel from "../Channel.svelte";
  import { onMount } from "svelte";
  import { ui_state } from "../../state/uiState.svelte";
  // import { voltageStore } from "../../state/systemState.svelte";
  import { system_state } from "../../state/systemState.svelte";
  import { slide } from 'svelte/transition';
  import { blur } from 'svelte/transition';
  import { dac16D } from "./dac16D_data.svelte"

  interface MyProps {
    module_index: number;
  }
  let { module_index }: MyProps = $props();
  let slot = $derived(system_state.data[module_index-1]?.core.slot);


  const this_component_data = system_state.data[module_index-1] as dac16D;


  // let channel_list = [1,2,3,4]
  let toggle_up = $state(false);
  let toggle_down = $state(true);
  let visible = $state(true);

  function togglerRotateState() {
    console.log("togglerRotateState");
    toggle_up = !toggle_up;
    toggle_down = !toggle_down;
    visible = !visible;
  }


  // you would check to see if every one of the 16 channels matches the 'set all' value
</script>

<div class="module-container" >
  <div class="heading" class:closed = {!visible}>
    <div class="closer">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="22"
        height="22"
        fill="currentColor"
        stroke="currentColor"
        class="chevron"
        class:toggle_up
        class:toggle_down
        viewBox="0 0 16 16"
        role="button"
        tabindex="0"
        onclick={togglerRotateState}
        onkeydown={togglerRotateState}
      >
        <path
          fill-rule="evenodd"
          d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
          stroke-width="0.8"
          transform="translate(0, -2)"
        />
        <path
          fill-rule="evenodd"
          d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
          stroke-width="0.8"
          transform="translate(0, 2)"
        />
      </svg>
    </div>
    <div class="identifier">M{slot}:</div>
    <div class="identifier">16 Ch. Voltage Source</div>
  </div>
  <div class="body">
    {#if visible}
      <div class="content">
            <Channel
            ch={this_component_data.shared_voltage}
            module_index={module_index}
            endpoint="/dac16D/voltage/"
          />
          </div>
    {/if}
  </div>
</div>

<style>
  .chevron {
    margin-top: 0.1rem;
    margin-left: 0.2rem;
    color: var(--text-color);
  }

  

  .chevron:focus {
        outline: none;
    }

  .identifier {
    margin-left: 10px;
    color: var(--module-icon-color);
    font-size: large;
  }

  .toggle_up {
    transform: rotate(-90deg);
    transition: transform 0.2s ease-in-out;
  }

  .toggle_down {
    transform: rotate(0);
    transition: transform 0.2s ease-in-out;
  }

  .body {
    background-color: var(--bg-color);
    box-sizing: border-box;
    display: flex;
    flex-direction: row;
  }

  .content {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    width: 100%;
  }


  .heading {
    display: flex;
    
    flex-direction: row;
    /* justify-content: space-between; */
    background-color: var(--module-header-color);
    padding: 0.3rem;
    color: var(--text-color);
    font-size: 1.3rem;
    border: 1.3px solid var(--module-border-color);
    /* border-bottom: none; */
    border-top-left-radius: 0.4rem;
    border-top-right-radius: 0.4rem;
  }

  .closed {
    border-bottom-left-radius: 0.4rem;
    border-bottom-right-radius: 0.4rem;
  }

  .module-container {
    
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin-bottom: 2rem;
    box-shadow: 0 0 9px rgba(0, 0, 0, 0.05);
  }

  @media (min-width: 460px) {
    .module-container {
      margin: 5px 20px 8px 5px;
    }
  }

  @media (max-width: 460px) {
    .module-container {
      margin: 5px 5px 8px 5px;
    }
  }
</style>