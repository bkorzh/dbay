<script lang="ts">
  import { ui_state } from "../state/uiState.svelte";
  import Button from "./buttons/Button.svelte";
  import GeneralButton from "./buttons/GeneralButton.svelte";
  import { requestChannelUpdate } from "../api";

  import type { ChSenseState, VsenseChange } from "./addons/vsense/interface";

  import { onMount } from "svelte";

  import { system_state } from "../state/systemState.svelte";
  import type { IModule } from "../state/systemState.svelte";

  import MenuSlotted from "./MenuSlotted.svelte";
  import MenuButton from "./buttons/MenuButton.svelte";

  import { adc4D } from "./modules_dbay/adc4D_data.svelte";
  import { ChSenseStateClass } from "./addons";
  import HorizontalDots from "./buttons/HorizontalDots.svelte";
  import ChannelChevron from "./buttons/ChannelChevron.svelte";
  import SenseDisplay from "./SenseDisplay.svelte";
  import SenseChannelContent from "./SenseChannelContent.svelte";
  import SenseChannelBar from "./SenseChannelBar.svelte";
  import type {
    SenseChangerFunction,
    SenseEffectFunction,
  } from "./addons/vsense/vsense.svelte";
  import { slide } from "svelte/transition";

  interface Props {
    ch: ChSenseStateClass;
    module_index: number;
    down: boolean;
    staticName?: string;
    borders?: boolean;
    onChevronClick: () => void;
    onChannelChange?: SenseChangerFunction;
    effect?: SenseEffectFunction;
  }

  let {
    ch,
    module_index,
    staticName,
    borders = true,
    down,
    onChevronClick,
    onChannelChange,
    effect,
  }: Props = $props();

  // override the onChannelChange function if it is passed as a prop
  if (onChannelChange) {
    ch.onChannelChange = onChannelChange;
  }

  // override the effect function if it is passed as a prop. Used for updating other parts
  // of a module after a channel has finished updating.
  if (effect) {
    ch.effect = effect;
  }

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
  <SenseChannelBar {ch} bind:showDropdown {down} {staticName} {onChevronClick}>
    <MenuButton
      onclick={() => {
        ch.updateChannel({ measuring: !ch.measuring });
        showDropdown = !showDropdown;
      }}>Toggle Measurement Mode</MenuButton
    >
  </SenseChannelBar>
  {#if down}
    <div transition:slide|global class="slider">
      <SenseChannelContent {ch}></SenseChannelContent>
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
    border-bottom: 1.3px solid var(--outer-border-color);
  }

  .borders:first-child {
    border-top: 1.3px solid var(--outer-border-color);
  }

  .bound-box:hover {
    background-color: var(--hover-color);
  }
</style>
