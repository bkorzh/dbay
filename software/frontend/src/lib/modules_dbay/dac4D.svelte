<script lang='ts'>
  import Channel from "../Channel.svelte";
  import { onMount } from "svelte";
  import { ui_state } from "../../state/uiState.svelte";
  // import { voltageStore } from "../../state/systemState.svelte";
  import { system_state } from "../../state/systemState.svelte";
  import { slide } from 'svelte/transition';
  import { blur } from 'svelte/transition';
  import { dac4D } from "./dac4D_data.svelte"
  import type { VsourceChange } from "../addons/vsource/interface";
  import { requestChannelUpdate } from "../../api";
    import ModuleChevron from "../buttons/ModuleChevron.svelte";
  

  interface MyProps {
    module_index: number;
  }
  let { module_index }: MyProps = $props();

  const this_component_data = system_state.data[module_index-1] as dac4D;


  let slot = $derived(system_state.data[module_index-1]?.core.slot);
  let channel_list = [1,2,3,4]
  let visible = $state(true);

  async function onChannelChange(data: VsourceChange) {
    let returnData;
    if (system_state.valid) {
          returnData = await requestChannelUpdate(data, "/dac4D/vsource/");
        } else {
          returnData = data;
        }
    return returnData;
  }
</script>

<div class="module-container" >
  <div class="heading" class:closed = {!visible}>
    <ModuleChevron bind:visible ></ModuleChevron>
    <div class="identifier">M{slot}:</div>
    <div class="identifier">Voltage Source</div>
  </div>
  <div class="body">
    {#if visible}
      <div class="content">
        {#each channel_list as _, i}
          <div transition:slide|global class="channel">
            <Channel
            ch={this_component_data.vsource.channels[i]}
            module_index={module_index}
            {onChannelChange}
          />
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>

  .identifier {
    margin-left: 10px;
    color: var(--module-icon-color);
    font-size: large;
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
