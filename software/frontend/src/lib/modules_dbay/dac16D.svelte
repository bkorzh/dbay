<script lang="ts">
  import Channel from "../Channel.svelte";
  import { onMount } from "svelte";
  import { ui_state } from "../../state/uiState.svelte";
  // import { voltageStore } from "../../state/systemState.svelte";
  import { system_state } from "../../state/systemState.svelte";
  import { slide } from "svelte/transition";
  import { blur } from "svelte/transition";
  import { dac16D } from "./dac16D_data.svelte";
  import type {
    ChSourceState,
    VsourceChange,
  } from "../addons/vsource/interface";
  import { requestChannelUpdate } from "../../api";
  import { ChSourceStateClass } from "../addons";
  import ModuleChevron from "../buttons/ModuleChevron.svelte";
  import Display from "../Display.svelte";

  import ChannelChevron from "../buttons/ChannelChevron.svelte";
  import HorizontalDots from "../buttons/HorizontalDots.svelte";
  import MenuSlotted from "../MenuSlotted.svelte";
  import MenuButton from "../buttons/MenuButton.svelte";
  import VerticalDots from "../buttons/VerticalDots.svelte";
  import ChannelBar from "../ChannelBar.svelte";
  import { VisibleState } from "../buttons/module_chevron";
  import ChannelContent from "../ChannelContent.svelte";
  import Link from "../buttons/Link.svelte";
  import PlusMinus from "../PlusMinus.svelte";
  import NumberedHoveredDotMenu from "../buttons/NumberedHoveredDotMenu.svelte";
  import ModuleHeading from "../ModuleHeading.svelte";

  interface MyProps {
    module_index: number;
  }
  let { module_index }: MyProps = $props();
  let slot = $derived(system_state.data[module_index]?.core.slot);

  let show_dropdown = $state(Array.from({ length: 16 }, (_, i) => false));
  let link_enabled = $state(Array.from({ length: 16 }, (_, i) => true));

  const c = system_state.data[module_index] as dac16D;

  let channel_list = Array.from({ length: 16 }, (_, i) => i + 1);

  let half_channel_list = channel_list.slice(0, 8);

  let visible = $state(VisibleState.DoubleDown);
  let down_array = $state([true, true]);
  let visible_all_channels = $state(true);
  let visible_ind_channels = $state(true);
  let showDropdown = $state(false);

  // these become poiters to
  let dotMenu = $state() as HTMLElement;
  let verticalDotMenu = $state() as HTMLElement;

  let menuLocation = $state({ top: 0, left: 0 });

  // single to all
  async function distributeChannelChange(data: VsourceChange) {
    let intermediate_data;
    if (system_state.valid) {
      // the /shared_voltage/ endpoint is a special case for the dac16D module
      intermediate_data = await requestChannelUpdate(
        data,
        "/dac16D/shared_voltage/"
      );
    } else {
      intermediate_data = data;
    }

    c.vsource.channels.forEach((channel: ChSourceStateClass) => {
      if (link_enabled[channel.index]) {
        channel.setChannel(intermediate_data);
      }
      // channel.setChannel(intermediate_data);
    });

    return intermediate_data;
  }

  // all affect single
  async function checkValidAllChannel(
    data: VsourceChange,
    current_index: number
  ) {
    console.log("current index: ", current_index);
    let new_voltage = data.bias_voltage;
    let new_activated = data.activated;

    // only do any validation if the channel currently edited is linked
    if (link_enabled[current_index]) {
      for (let i = 0; i < c.vsource.channels.length; i++) {
        // if the new channel that is edited or newly included does not
        // match every other linked channel, then set the shared_voltage to invalid
        if (link_enabled[i] && i !== current_index) {
          // console.log("checking channel: ", i, "with ", current_index);
          if (
            c.vsource.channels[i].bias_voltage !== new_voltage ||
            c.vsource.channels[i].activated !== new_activated
          ) {
            // console.log(
            //   "setting invalid because this does not match other linked"
            // );
            c.shared_voltage.setInvalid();
            return data;
          }
        }
      }

      c.shared_voltage.setValid(data, true);
      return data;
    }
  }

  async function onChannelChange(data: VsourceChange) {
    let returnData;
    if (system_state.valid) {
      returnData = await requestChannelUpdate(data, "/dac16D/vsource/");
    } else {
      returnData = data;
    }

    checkValidAllChannel(returnData, returnData.index);

    return returnData;
  }

  function rotateState() {
    if (visible === VisibleState.Collapsed) {
      visible = VisibleState.Down;
      down_array = [false, false];
    } else if (visible === VisibleState.Down) {
      visible = VisibleState.DoubleDown;
      down_array = [true, true];
    } else {
      visible = VisibleState.Collapsed;
    }
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

  function showControls(i: number) {
    // set all elemeents to false except the ith element
    for (let j = 0; j < show_dropdown.length; j++) {
      if (j !== i) {
        show_dropdown[j] = false;
      }
    }
    show_dropdown[i] = !show_dropdown[i];
  }

  function changeLinkState(i: number) {
    link_enabled[i] = !link_enabled[i];

    // the added channel might break the link and set the "set all linked" feature to invalid.
    if (link_enabled[i]) {
      const edited_channel_data = c.vsource.channels[i].currentStateAsChange();
      checkValidAllChannel(edited_channel_data, i);
    }

    // the removed link might bring the linked channels back into a synchronized state
    // find first item in link_enabled that's true. The way I've written checkValidAllChannel,
    // it needs to be passed data on one connected channel. 
    let first_true = link_enabled.findIndex((val) => val === true);
    if (first_true !== -1) {
      const edited_channel_data = c.vsource.channels[first_true].currentStateAsChange();
      checkValidAllChannel(edited_channel_data, first_true);
    }

  }

  function handleMouseEnter(i: number) {
    c.vsource.channels[i].isHovering = true;
  }

  function handleMouseLeave(i: number) {
    c.vsource.channels[i].isHovering = false;
  }


  let parent_width = $state(0);
  let left_width = $state(0);
  let right_width = $state(0);
  let vl_width = $state(0);
</script>

{#snippet menu_buttons()}
  <MenuButton onclick={() => console.log("todo")}>undefined</MenuButton>
{/snippet}



<div class="module-container">
  <ModuleHeading m = {c} 
    visible={visible} 
    rotateState={rotateState} 
    {module_index} 
    name={"16 Ch. Voltage Source"} 
    {menu_buttons}
    icon_name="./dac16D_icon.svg"
    ></ModuleHeading>

  {#if visible}
    <div class="content">
      <div class="box" transition:slide|global>
        <Channel
          ch={c.shared_voltage}
          {module_index}
          onChannelChange={distributeChannelChange}
          staticName={c.shared_voltage.heading_text}
          borders={false}
          down={down_array[0]}
          onChevronClick={() => onChevClick(0)}
        />
      </div>

      <div class="box" transition:slide|global>
        <ChannelBar
          {onChannelChange}
          bind:showDropdown
          down={down_array[1]}
          staticName="Set Individual Channels"
          borderTop={true}
          onChevronClick={() => onChevClick(1)}
        >
          <MenuButton
            onclick={() => {
              console.log("something");
            }}>Do Something</MenuButton
          >
        </ChannelBar>
        {#if down_array[1]}
          <div transition:slide|global class="individual-body">
            {#each half_channel_list as ch, i}
              <div class="side-by-side" bind:clientWidth={parent_width}>
                <div class="channel left" bind:clientWidth={left_width}>
                  <div class="channel" class:tab-parent={show_dropdown[i]}>
                    <div
                      class="tab"
                      role="cell"
                      tabindex="0"
                      onmouseenter={() => handleMouseEnter(i)}
                      onmouseleave={() => handleMouseLeave(i)}
                      class:popout={show_dropdown[i]}
                    >
                      <!-- <div class="ch-number">{i + 1}</div> -->
                      <NumberedHoveredDotMenu
                        isHovering={c.vsource.channels[i].isHovering}
                        index={i}
                        onclick={(e) => showControls(i)}
                        onkeydown={(e) => showControls(i)}
                        bind:dotMenu={verticalDotMenu}
                      ></NumberedHoveredDotMenu>

                      <PlusMinus ch={c.vsource.channels[i]} {onChannelChange}
                      ></PlusMinus>
                      <Display
                        ch={c.vsource.channels[i]}
                        {onChannelChange}
                        spacing_small={true}
                      ></Display>
                      <Link
                        activated={link_enabled[i]}
                        onclick={() => changeLinkState(i)}
                      ></Link>
                    </div>
                  </div>
                </div>

                <div class="vl" bind:clientWidth={vl_width}></div>

                <div class="channel right" bind:clientWidth={right_width}>
                  <div class="channel" class:tab-parent={show_dropdown[i + 8]}>
                    <div
                      class="tab"
                      role="cell"
                      tabindex="0"
                      onmouseenter={() => handleMouseEnter(i + 8)}
                      onmouseleave={() => handleMouseLeave(i + 8)}
                      class:popout={show_dropdown[i + 8]}
                    >
                      <!-- <div class="ch-number">{i + 9}</div> -->
                      <NumberedHoveredDotMenu
                        isHovering={c.vsource.channels[i + 8].isHovering}
                        index={i + 8}
                        onclick={(e) => showControls(i + 8)}
                        onkeydown={(e) => showControls(i + 8)}
                        bind:dotMenu={verticalDotMenu}
                      ></NumberedHoveredDotMenu>

                      <PlusMinus
                        ch={c.vsource.channels[i + 8]}
                        {onChannelChange}
                      ></PlusMinus>
                      <Display
                        ch={c.vsource.channels[i + 8]}
                        {onChannelChange}
                        spacing_small={true}
                      ></Display>
                      <Link
                        activated={link_enabled[i + 8]}
                        onclick={() => changeLinkState(i + 8)}
                      ></Link>
                    </div>
                  </div>
                </div>
              </div>

              <!-- {#if show_dropdown[i] || show_dropdown[i + 8]} -->
              <div class="parent" style="margin-left: {(parent_width -
                left_width -
                right_width -
                vl_width) /
                6 +
                1.6}px; margin-right: {(parent_width -
                left_width -
                right_width -
                vl_width) /
                6 +
                1.6}px;">
                {#if show_dropdown[i]}
                  <div
                    class="white left"
                    transition:slide|global
                    
                  >
                    <ChannelContent ch={c.vsource.channels[i]} {onChannelChange}
                    ></ChannelContent>
                  </div>
                {:else if show_dropdown[i + 8]}
                  <div
                    class="white right"
                    transition:slide|global
                  >
                    <ChannelContent
                      ch={c.vsource.channels[i + 8]}
                      {onChannelChange}
                    ></ChannelContent>
                  </div>
                {/if}
              </div>
              <!-- {/if} -->
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .vl {
    border-left: 1px solid var(--module-border-color);
    /* flex-grow: 1; */
    /* height: 38px; */
    align-items: stretch;
    /* position: absolute; */
    left: 90%;
    margin-left: 0px;
    top: 9px;
    /* width: 3px; */
  }
  .parent {
    position: relative;
    box-sizing: border-box;
  }

  .tab-parent {
    position: relative;
    opacity: 1;
  }

  .channel {
    display: flex;
    flex-direction: row;
    /* border box */
    box-sizing: border-box;
  }

  .channel:after {
    /* Initial state */
    content: "";
    position: relative;
    top: 3px; /* Offset from the top */
    left: 3px; /* Offset from the left */
    width: 100%; /* Match the width of the element */
    height: 100%; /* Match the height of the element */
    background-color: rgba(0, 0, 0, 0.05); /* Set the shadow color */
    z-index: 5; /* Put the shadow behind the element */
    opacity: 0; /* Start invisible */
    transition: opacity 0.5s ease-in-out; /* Transition the opacity */
    filter: blur(5px);
  }

  .tab {
    /* position: relative; */
    padding: 0.2rem;

    padding-top: 0.2rem;
    padding-bottom: 0.2rem;
    box-sizing: border-box;
    display: flex;
    flex-direction: row;
    border-top: 1px solid var(--body-color);
    border-right: 1px solid var(--body-color);
    border-left: 1px solid var(--body-color);
    border-top-right-radius: 0.4rem;
    border-top-left-radius: 0.4rem;
    background-color: transparent;
    transition:
      background-color 0.3s ease-in-out,
      border-color 0.3s ease-in-out;
  }

  .popout {
    position: relative;
    z-index: 1;
    background-color: var(--extra-light);
    border-top: 1px solid var(--outer-border-color);
    border-right: 1px solid var(--outer-border-color);
    border-left: 1px solid var(--outer-border-color);
    border-top-right-radius: 0.4rem;
    border-top-left-radius: 0.4rem;
    box-sizing: border-box;
    z-index: 20;
  }

  .white {
    position: relative;
    z-index: 1;
    background-color: var(--extra-light);
    border: 1px solid var(--module-border-color);

    /* border-top-left-radius: 0.4rem; */
    border-bottom-left-radius: 0.4rem;
    border-bottom-right-radius: 0.4rem;
    border-color: var(--outer-border-color);
    /* box-shadow: 0 0 12px rgba(0, 0, 0, 0.3); */
    box-sizing: border-box;
    z-index: 20;
  }

  .parent:after {
    opacity: 1;
    content: "";
    position: absolute;
    top: 3px; /* Offset from the top */
    left: 3px; /* Offset from the left */
    width: 100%; /* Match the width of the element */
    height: 100%; /* Match the height of the element */
    background-color: rgba(0, 0, 0, 0.05); /* Set the shadow color */
    z-index: 5; /* Put the shadow behind the element */
    filter: blur(5px);
  }

  /* .popout-shadow {
    position: relative;
  } */

  .tab-parent:after {
    content: "";
    position: absolute;
    top: 3px; /* Offset from the top */
    left: 3px; /* Offset from the left */
    width: 100%; /* Match the width of the element */
    height: 100%; /* Match the height of the element */
    background-color: rgba(0, 0, 0, 0.05); /* Set the shadow color */
    z-index: 1; /* Put the shadow behind the element */
    opacity: 1; /* Start invisible */
    filter: blur(5px);
  }

  /* .white:before {
    background-color: white;
  } */

  .left {
    border-top-right-radius: 0.4rem;
  }

  .right {
    border-top-left-radius: 0.4rem;
  }

  .individual-body {
    margin-top: 0.5rem;
    /* margin-left: 1rem;
    margin-right: 1rem; */
  }

  .side-by-side {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    padding-left: 0.2rem;
    padding-right: 0.2rem;
    /* padding: 0.1rem; */
  }

  /* .left {
    margin-right: 3rem;
  } */


  .content {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    width: 100%;
    background-color: var(--body-color);
    box-sizing: border-box;
    display: flex;
    border-left: 1.3px solid var(--module-border-color);
    border-right: 1.3px solid var(--module-border-color);
    border-bottom: 1.3px solid var(--module-border-color);
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
