<script lang="ts">
  import Channel from "../Channel.svelte";
  import { onMount } from "svelte";
  import { ui_state } from "../../state/uiState.svelte";
  // import { voltageStore } from "../../state/systemState.svelte";
  import { system_state } from "../../state/systemState.svelte";
  import { slide } from "svelte/transition";
  import { blur } from "svelte/transition";
  import { dac4D } from "./dac4D_data.svelte";
  import type { VsourceChange } from "../addons/vsource/interface";
  import { requestChannelUpdate } from "../../api";
  import ModuleChevron from "../buttons/ModuleChevron.svelte";
  import { VisibleState } from "../buttons/module_chevron";
  import ModuleHeading from "../ModuleHeading.svelte";
  import MenuButton from "../buttons/MenuButton.svelte";
  import dac4D_icon from "/dac4D_icon.svg";

  interface MyProps {
    module_index: number;
  }
  let { module_index }: MyProps = $props();

  const this_component_data = system_state.data[module_index] as dac4D;

  let down_array = $state([true, true, true, true]);

  // let module_ = $derived(system_state.data[module_index]?.core.slot);
  let channel_list = [1, 2, 3, 4];
  // let visible = $state(VisibleState.DoubleDown);

  let visible = $state(
    Number(localStorage.getItem("visible" + module_index)) ||
      VisibleState.DoubleDown,
  );

  // used to override the onChannelChange function specified in ChSourceStateClass
  async function onChannelChange(data: VsourceChange) {
    let returnData;
    if (system_state.valid) {
      returnData = await requestChannelUpdate(data, "/dac4D/vsource/");
    } else {
      returnData = data;
    }
    return returnData;
  }

  function rotateState() {
    if (visible === VisibleState.Collapsed) {
      visible = VisibleState.Down;
      down_array = [false, false, false, false];
    } else if (visible === VisibleState.Down) {
      visible = VisibleState.DoubleDown;
      down_array = [true, true, true, true];
    } else {
      visible = VisibleState.Collapsed;
    }

    // Store the visible state in localStorage
    localStorage.setItem("visible" + module_index, visible.toString());
  }

  function onChevClick(i: number) {
    // console.log("clicked!");
    down_array[i] = !down_array[i];
    if (down_array.every((val) => val === true)) {
      visible = VisibleState.DoubleDown;
    }

    // if all values of down_array are false, set visible to down
    if (down_array.every((val) => val === false)) {
      visible = VisibleState.Down;
    }
    // console.log("down array: ", down_array);
  }
</script>

{#snippet menu_buttons()}
  <MenuButton onclick={() => console.log("todo")}>undefined</MenuButton>
{/snippet}

<div class="module-container">
  <ModuleHeading
    m={this_component_data}
    {visible}
    {rotateState}
    {module_index}
    name={"Voltage Source"}
    {menu_buttons}
    icon_name={dac4D_icon}
  ></ModuleHeading>

  <div class="body">
    {#if !(visible == VisibleState.Collapsed)}
      <div class="content">
        {#each channel_list as _, i}
          <div transition:slide|global class="channel">
            <Channel
              ch={this_component_data.vsource.channels[i]}
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
