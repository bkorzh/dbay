<script lang="ts">
  import { ui_state } from "../state/uiState.svelte";
  // import { voltageStore } from "../stores/voltageStore"
  import Button from "./buttons/Button.svelte";
  import ChevButtonTop from "./buttons/ChevButtonTop.svelte";
  import ChevButtonBottom from "./buttons/ChevButtonBottom.svelte";
  import SubmitButton from "./buttons/SubmitButton.svelte";
  import GeneralButton from "./buttons/GeneralButton.svelte";
  import { requestChannelUpdate } from "../api";

  import type {
    ChSourceState,
    VsourceChange,
  } from "./addons/vsource/interface";

  import { onMount } from "svelte";

  import { system_state } from "../state/systemState.svelte";
  import type { IModule } from "../state/systemState.svelte";

  import MenuSlotted from "./MenuSlotted.svelte";
  import MenuButton from "./buttons/MenuButton.svelte";

  import { dac4D } from "./modules_dbay/dac4D_data.svelte";
  import { ChSourceStateClass } from "./addons";
  import HorizontalDots from "./buttons/HorizontalDots.svelte";
  import ChannelChevron from "./buttons/ChannelChevron.svelte";
  import Display from "./Display.svelte";
  import ChannelContent from "./ChannelContent.svelte";
  import type { ChangerFunction } from "./addons/vsource/vsource.svelte";
  import ChannelBar from "./ChannelBar.svelte";
  import { slide } from "svelte/transition";

  interface Props {
    ch: ChSourceStateClass;
    module_index: number;
    onChannelChange: ChangerFunction;
    staticName?: string;
    borders?: boolean;
    down: boolean;
    onChevronClick: () => void;
  }

  let {
    ch,
    module_index,
    onChannelChange,
    staticName,
    borders = true,
    down,
    onChevronClick,
  }: Props = $props();

  // let down = $state(true);

  let showDropdown = $state(false);

  function handleMouseEnter() {
    ch.isHovering = true;
  }

  function handleMouseLeave() {
    ch.isHovering = false;
  }
</script>

<div
  onmouseenter={handleMouseEnter}
  onmouseleave={handleMouseLeave}
  class="bound-box"
  class:borders
  role="region"
>
  <!-- notice how I use class:no_border here -->
  <!-- <div class="strip" class:animated={ch.measuring}></div> -->
  <ChannelBar
    {ch}
    bind:showDropdown
    {down}
    {onChannelChange}
    {staticName}
    {onChevronClick}
  >
    <MenuButton
      onclick={() => {
        ch.updateChannel({ measuring: !ch.measuring }, onChannelChange);
        showDropdown = !showDropdown;
      }}>Toggle Measurement Mode</MenuButton
    >
  </ChannelBar>
  {#if down}
    <div transition:slide|global class="slider">
      <ChannelContent {ch} {onChannelChange}></ChannelContent>
    </div>
  {/if}
</div>

<style>
  @import url("https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,wght@8..144,100;8..144,200;8..144,300;8..144,400;8..144,500;8..144,600;8..144,700&display=swap");

  .slider {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
  }

  .bound-box {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  .borders {
    border-left: 1.3px solid var(--outer-border-color);
    border-right: 1.3px solid var(--outer-border-color);
    border-bottom: 1.3px solid var(--divider-border-color);
  }
</style>
