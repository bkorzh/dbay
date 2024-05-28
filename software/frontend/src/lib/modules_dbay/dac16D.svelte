<script lang="ts">
  import Channel from "../Channel.svelte";
  import { onMount } from "svelte";
  import { ui_state } from "../../state/uiState.svelte";
  // import { voltageStore } from "../../state/systemState.svelte";
  import { system_state } from "../../state/systemState.svelte";
  import { slide } from "svelte/transition";
  import { blur } from "svelte/transition";
  import { dac16D } from "./dac16D_data.svelte";
  import type { ChSourceState, VsourceChange } from "../addons/vsource/interface";
  import { requestChannelUpdate } from "../../api";
  import { ChSourceStateClass } from "../addons";
    import ModuleChevron from "../ModuleChevron.svelte";

  interface MyProps {
    module_index: number;
  }
  let { module_index }: MyProps = $props();
  let slot = $derived(system_state.data[module_index - 1]?.core.slot);

  const this_component_data = system_state.data[module_index - 1] as dac16D;

  let channel_list = Array.from({length: 16}, (_, i) => i + 1);

  let visible = $state(true);

  // function togglerRotateState() {
  //   console.log("togglerRotateState");
  //   visible = !visible;
  // }

  async function distributeChannelChange(data: VsourceChange) {
    let intermediate_data;
    if (system_state.valid) {
      // the /shared_voltage/ endpoint is a special case for the dac16D module
      intermediate_data = await requestChannelUpdate(data, "/dac16D/shared_voltage/");
    } else {
      intermediate_data = data;
    }

    this_component_data.vsource.channels.forEach((channel: ChSourceStateClass) => {
      channel.setChannel(intermediate_data);
    })

    return intermediate_data;
  }

  async function modifySingleChannel(data: VsourceChange, current_index: number) {
    let new_voltage = data.bias_voltage;
    let new_activated = data.activated;

    // if the equality is broken, then set the shared_voltage to invalid
    for (let i = 0; i < this_component_data.vsource.channels.length; i++) {
      if (i !== current_index) {
        if (this_component_data.vsource.channels[i].bias_voltage !== new_voltage || 
            this_component_data.vsource.channels[i].activated !== new_activated) {

          this_component_data.shared_voltage.setInvalid();
          return data;
        }
      }
    }
    this_component_data.shared_voltage.setValid(data);
    return data;
  }

  // you would check to see if every one of the 16 channels matches the 'set all' value
</script>

<div class="module-container">
  <div class="heading" class:closed={!visible}>
    <ModuleChevron bind:visible></ModuleChevron>
    <div class="identifier">M{slot}:</div>
    <div class="identifier">16 Ch. Voltage Source</div>
  </div>
  <div class="body">
    {#if visible}
      <div class="content">
        <Channel
          ch={this_component_data.shared_voltage}
          {module_index}
          onChannelChange={distributeChannelChange}
          staticName={true}
        />
        {#each channel_list as _, i}
          <div transition:slide|global class="channel">
            <Channel
            ch={this_component_data.vsource.channels[i]}
            module_index={module_index}
            onChannelChange = {(e) => modifySingleChannel(e, i)}
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
