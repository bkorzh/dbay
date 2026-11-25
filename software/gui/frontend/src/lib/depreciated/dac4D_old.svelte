<script lang='ts'>
  import Channel from "../Channel_old.svelte";
  import { onMount } from "svelte";
  import { ui_state } from "../../state/uiState.svelte";
  // import { voltageStore } from "../../state/systemState.svelte";
  import { system_state } from "../../state/systemState.svelte";
  import { slide } from 'svelte/transition';
  import { blur } from 'svelte/transition';

  interface MyProps {
    module_index: number;
  }

  let { module_index }: MyProps = $props();
  // let slot = 0;


  let slot = $derived(system_state.data[module_index-1]?.core.slot);

  // let slot = system_state.data[module_index-1]?.core.slot

  let channel_list = [1,2,3,4]

  let toggle_up = $state(false);
  let toggle_down = $state(true);
  let visible = $state(true);

  function togglerRotateState() {
    console.log("togglerRotateState");
    toggle_up = !toggle_up;
    toggle_down = !toggle_down;
    // alter = !alter;
    visible = !visible;
  }
</script>

<div class="module-container">
  <div class="heading">
    <div class="closer">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="23"
        height="23"
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
        />
      </svg>
    </div>
    <div class="identifier">(old) M{slot}</div>
  </div>
  <div class="body">
    {#if visible}
      <div class="left-space"></div>
      <div class="right-content">
        {#each channel_list as _, i}
          <div transition:slide|global class="channel">
            <Channel
            index={i + 1}
            module_index={module_index}
          />
          </div>
          
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .chevron {
    margin-top: 0.1rem;
    margin-left: 0.2rem;
    /* padding-top: 1px; */
    color: var(--module-icon-color);
  }

  .chevron:focus {
        outline: none;
    }

  .identifier {
    margin-left: 10px;
    color: var(--module-icon-color);
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

  .left-space {
    width: 7%;
    background-color: var(--module-header-color);
    background-color: var(--bg-color);
  }

  .right-content {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    width: 93%;
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
    border-radius: 0.4rem;
  }

  .module-container {
    
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin-bottom: 2rem;
  }

  @media (min-width: 460px) {
    .module-container {
      margin: 5px 20px 15px 5px;
    }
  }

  @media (max-width: 460px) {
    .module-container {
      margin: 5px 5px 15px 5px;
    }
  }
</style>
