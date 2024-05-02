<script>
  import Channel from "../Channel.svelte";
  import { onMount } from "svelte";
  import { uiStateStore } from "../../stores/uiStateStore";
  import { voltageStore } from "../../stores/voltageStore";
  import { slide } from 'svelte/transition';
  import { blur } from 'svelte/transition';

  export let module_index;
  let slot = 0;


  $: slot = $voltageStore.data[module_index-1]?.slot

  // const intervalId = setInterval(async () => {
  //       console.log($voltageStore.data[module_index-1]?.slot)
  //     }, 1000); // 1000 milliseconds = 1 second


  // onMount(() => {
  //   console.log("module_state: ", module_state);
  // });]

  let channel_list = [1,2,3,4]

  let toggle_up = false;
  let toggle_down = true;
  let visible = true;

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
        on:click={togglerRotateState}
        on:keydown={togglerRotateState}
      >
        <path
          fill-rule="evenodd"
          d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
          stroke-width="0.8"
        />
      </svg>
    </div>
    <div class="identifier">M{slot}</div>
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
    <!-- <div class="left-space"></div>
    <div class="right-content">
      {#each module_state as channel_state, i}
        <Channel
          index={i + 1}
          bias_voltage={channel_state.bias_voltage}
          activated={channel_state.activated}
          heading_text={channel_state.heading_text}
        />
      {/each}
    </div> -->
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

  /* .body {
    display: flex;
    flex-direction: row;
    
  } */

  .heading {
    display: flex;
    
    flex-direction: row;
    /* justify-content: space-between; */
    background-color: var(--module-header-color);
    padding: 0.3rem;
    color: var(--text-color);
    font-size: 1.3rem;
    /* margin-right: auto;
    margin-top: auto;
    margin-bottom: auto; */
    /* padding-right: 0.8rem; */
    /* opacity: 0.5; */
    border: 1.3px solid var(--module-border-color);
    border-radius: 0.4rem;
  }

  .module-container {
    /* font-size: 0.5rem; */
    
    display: flex;
    flex-direction: column;
    justify-content: center;
    /* box-shadow: 0 0 7px rgba(0, 0, 0, 0.05); */
    /* border: 1.3px solid var(--outer-border-color); */
    /* background-color: var(--module-header-color); */
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
