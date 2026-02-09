<script lang="ts">
  import SenseChannel from "../SenseChannel.svelte";
  import { onMount } from "svelte";
  import { ui_state } from "../../state/uiState.svelte";
  import { system_state } from "../../state/systemState.svelte";
  import { slide } from "svelte/transition";
  import { blur } from "svelte/transition";
  import { adc4D } from "./adc4D_data.svelte";
  import type { VsenseChange } from "../addons/vsense/interface";
  import { requestSenseUpdate } from "../../api";
  import ModuleChevron from "../buttons/ModuleChevron.svelte";
  import { VisibleState } from "../buttons/module_chevron";
  import ModuleHeading from "../ModuleHeading.svelte";
  import MenuButton from "../buttons/MenuButton.svelte";
  import adc4D_icon from "/assets/adc4D_icon.svg";

  interface MyProps {
    module_index: number;
  }
  let { module_index }: MyProps = $props();

  const this_component_data = system_state.data[module_index] as adc4D;

  let down_array = $state([true, true, true, true, true]);

  let channel_list = [0, 1, 2, 3, 4]; // 5 channels for differential ADC

  let visible = $state(
    Number(localStorage.getItem("visible" + module_index)) ||
      VisibleState.DoubleDown,
  );

  // used to override the onChannelChange function specified in ChSenseStateClass
  async function onChannelChange(data: VsenseChange) {
    let returnData;
    if (system_state.valid) {
      returnData = await requestSenseUpdate(data, "/adc4D/vsense/");
    } else {
      returnData = data;
    }
    return returnData;
  }

  function rotateState() {
    if (visible === VisibleState.Collapsed) {
      visible = VisibleState.Down;
      down_array = [false, false, false, false, false];
    } else if (visible === VisibleState.Down) {
      visible = VisibleState.DoubleDown;
      down_array = [true, true, true, true, true];
    } else {
      visible = VisibleState.Collapsed;
    }

    // Store the visible state in localStorage
    localStorage.setItem("visible" + module_index, visible.toString());
  }

  function onChevClick(i: number) {
    down_array[i] = !down_array[i];
    if (down_array.every((val) => val === true)) {
      visible = VisibleState.DoubleDown;
    }

    // if all values of down_array are false, set visible to down
    if (down_array.every((val) => val === false)) {
      visible = VisibleState.Down;
    }
  }
</script>

{#snippet menu_buttons()}
  <MenuButton onclick={() => console.log("ADC4D menu action")}
    >Settings</MenuButton
  >
{/snippet}

<div class="module-container">
  <ModuleHeading
    m={this_component_data}
    {visible}
    {rotateState}
    {module_index}
    name={"Voltage Sensor"}
    {menu_buttons}
    icon_name={adc4D_icon}
  ></ModuleHeading>

  <div class="body">
    {#if !(visible == VisibleState.Collapsed)}
      <div class="content">
        {#each channel_list as _, i}
          <div transition:slide|global class="channel">
            <SenseChannel
              ch={this_component_data.vsense.channels[i]}
              {module_index}
              down={down_array[i]}
              onChevronClick={() => onChevClick(i)}
              {onChannelChange}
            />
          </div>
        {/each}
      </div>
    {/if}
  </div>
</div>

<style>
  .body {
    background-color: var(--body-color);
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
