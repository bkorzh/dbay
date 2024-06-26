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
    SharedVsourceChange,
  } from "../addons/vsource/interface";
  import { requestSharedChannelUpdate, requestChannelUpdate } from "../../api";
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
  import dac16D_icon from "/dac16D_icon.svg";

  interface MyProps {
    module_index: number;
  }
  let { module_index }: MyProps = $props();
  let slot = $derived(system_state.data[module_index]?.core.slot);

  let show_dropdown = $state(Array.from({ length: 16 }, (_, i) => false));
  // let link_enabled = $state(Array.from({ length: 16 }, (_, i) => true));

  let vsb_popout = $state(false);

  const c = system_state.data[module_index] as dac16D;

  let channel_list = Array.from({ length: 16 }, (_, i) => i + 1);

  let half_channel_list = channel_list.slice(0, 8);

  let visible = $state(VisibleState.DoubleDown);
  let down_array = $state([true, true, true]);
  let visible_all_channels = $state(true);
  let visible_ind_channels = $state(true);

  let showDropdown_1 = $state(false);
  let showDropdown_2 = $state(false);

  // these become poiters to
  let dotMenu = $state() as HTMLElement;
  let verticalDotMenu = $state() as HTMLElement;

  let menuLocation = $state({ top: 0, left: 0 });

  // single to all
  async function distributeChannelChange(data: VsourceChange) {
    let intermediate_data;

    let shared_data: SharedVsourceChange = {
      change: data,
      link_enabled: c.link_enabled,
    };

    if (system_state.valid) {
      // the /shared_voltage/ endpoint is a special case for the dac16D module
      intermediate_data = await requestSharedChannelUpdate(
        shared_data,
        "/dac16D/vsource_shared/",
      );
    } else {
      intermediate_data = shared_data;
    }

    c.vsource.channels.forEach((channel: ChSourceStateClass) => {
      if (intermediate_data.link_enabled[channel.index]) {
        channel.setChannel(intermediate_data.change);
      }
      // channel.setChannel(intermediate_data);
    });

    return intermediate_data.change;
  }

  async function individualChannelChange(data: VsourceChange) {
    let return_data;
    return_data = system_state.valid
      ? await requestChannelUpdate(data, "/dac16D/vsource/")
      : data;
    c.validateLinks();
    return return_data;
  }

  async function vsbChange(data: VsourceChange) {
    return system_state.valid
      ? await requestChannelUpdate(data, "/dac16D/vsb/")
      : data;
  }

  function rotateState() {
    if (visible === VisibleState.Collapsed) {
      visible = VisibleState.Down;
      down_array = [false, false, false];
    } else if (visible === VisibleState.Down) {
      visible = VisibleState.DoubleDown;
      down_array = [true, true, true];
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
    c.link_enabled[i] = !c.link_enabled[i];

    c.validateLinks();
  }

  function linkAll() {
    for (let i = 0; i < 16; i++) {
      c.link_enabled[i] = true;
    }
    c.validateLinks();
  }

  function unlinkAll() {
    for (let i = 0; i < 16; i++) {
      c.link_enabled[i] = false;
    }
    c.validateLinks();
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

  $effect(() => {
    console.log("parent_width: ", parent_width);
    console.log("left_width: ", left_width);
    console.log("right_width: ", right_width);
    console.log("vl_width: ", vl_width);
  });

  let popout_margin_size = $derived(
    (parent_width - left_width - right_width - vl_width) / 6 - 0.3,
  );
</script>

{#snippet menu_buttons()}
  <MenuButton onclick={() => console.log("todo")}>undefined</MenuButton>
{/snippet}

<div class="module-container">
  <ModuleHeading
    m={c}
    {visible}
    {rotateState}
    {module_index}
    name={"16 Ch. Voltage Source"}
    {menu_buttons}
    icon_name={dac16D_icon}
  ></ModuleHeading>

  {#if visible}
    <div class="content">
      <div class="box" transition:slide|global>
        <Channel
          ch={c.shared_voltage}
          {module_index}
          down={down_array[0]}
          staticName={c.shared_voltage.heading_text}
          borders={false}
          onChevronClick={() => onChevClick(0)}
          onChannelChange={distributeChannelChange}
        />
      </div>

      <div class="box" transition:slide|global>
        <ChannelBar
          bind:showDropdown={showDropdown_1}
          down={down_array[1]}
          staticName="Set Individual Channels"
          borderTop={true}
          onChevronClick={() => onChevClick(1)}
        >
          <MenuButton onclick={linkAll}>Link all channels</MenuButton>
          <MenuButton onclick={unlinkAll}>Unlink all channels</MenuButton>
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

                      <PlusMinus ch={c.vsource.channels[i]}></PlusMinus>
                      <Display
                        ch={c.vsource.channels[i]}
                        spacing_small={true}
                        onChannelChange={individualChannelChange}
                        effect={c.validateLinks}
                      ></Display>
                      <Link
                        activated={c.link_enabled[i]}
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

                      <PlusMinus ch={c.vsource.channels[i + 8]}></PlusMinus>
                      <Display
                        ch={c.vsource.channels[i + 8]}
                        spacing_small={true}
                        onChannelChange={individualChannelChange}
                        effect={c.validateLinks}
                      ></Display>
                      <Link
                        activated={c.link_enabled[i + 8]}
                        onclick={() => changeLinkState(i + 8)}
                      ></Link>
                    </div>
                  </div>
                </div>
              </div>

              <!-- {#if show_dropdown[i] || show_dropdown[i + 8]} -->
              <div
                class="parent"
                style="margin-left: {popout_margin_size}px; margin-right: {popout_margin_size}px;"
              >
                {#if show_dropdown[i]}
                  <div class="white left" transition:slide|global>
                    <!-- onChannelChange -> individualChannelChange and the effect
                     where already injected into c.vsource.channels[i]. No need to do it here -->
                    <ChannelContent ch={c.vsource.channels[i]}></ChannelContent>
                  </div>
                {:else if show_dropdown[i + 8]}
                  <div class="white right" transition:slide|global>
                    <ChannelContent ch={c.vsource.channels[i + 8]}
                    ></ChannelContent>
                  </div>
                {/if}
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="box" transition:slide|global>
        <ChannelBar
          bind:showDropdown={showDropdown_2}
          down={down_array[2]}
          staticName="Supply Voltages"
          borderTop={true}
          onChevronClick={() => onChevClick(2)}
        >
          <MenuButton onclick={() => console.log("undefined")}
            >undefined</MenuButton
          >
        </ChannelBar>
        {#if down_array[2]}
          <div transition:slide|global class="supply-body">
            <div class="side-by-side">
              <div class="channel right label">VSB1</div>

              <div class="channel left">
                <div class="channel">
                  <div
                    class="tab"
                    role="cell"
                    tabindex="0"
                    class:popout={vsb_popout}
                  >
                    <!-- <div class="ch-number">{i + 9}</div> -->
                    <NumberedHoveredDotMenu
                      isHovering={true}
                      index={0}
                      onclick={(e) => (vsb_popout = !vsb_popout)}
                      onkeydown={(e) => (vsb_popout = !vsb_popout)}
                      bind:dotMenu={verticalDotMenu}
                    ></NumberedHoveredDotMenu>

                    <PlusMinus ch={c.vsb}></PlusMinus>
                    <Display
                      ch={c.vsb}
                      onChannelChange={vsbChange}
                      spacing_small={true}
                    ></Display>
                  </div>
                </div>
              </div>
            </div>
            <div
              class="parent"
              style="margin-left: {popout_margin_size}px; margin-right: {popout_margin_size}px;"
            >
              {#if vsb_popout}
                <div class="white left" transition:slide|global>
                  <!-- onChannelChange -> individualChannelChange and the effect
                     where already injected into c.vsource.channels[i]. No need to do it here -->
                  <ChannelContent ch={c.vsb}></ChannelContent>
                </div>
              {/if}
            </div>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .label {
    text-align: center;
    font-size: 1.2rem;
    margin-top: auto;
    margin-bottom: auto;
    color: var(--text-color);
  }

  .vl {
    box-sizing: border-box;
    border-left: 1px solid var(--module-border-color);
    align-items: stretch;
    left: 90%;
    margin-left: 0px;
    top: 9px;
  }
  .parent {
    position: relative;
    box-sizing: border-box;
  }

  .tab-parent {
    box-sizing: border-box;
    position: relative;
    opacity: 1;
  }

  .channel {
    display: flex;
    flex-direction: row;
    box-sizing: border-box;
  }

  .channel:after {
    content: "";
    position: relative;
    top: 3px;
    left: 3px;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.05);
    z-index: 5;
    opacity: 0;
    transition: opacity 0.5s ease-in-out;
    filter: blur(5px);
  }

  .tab {
    box-sizing: border-box;
    padding: 0.2rem;
    padding-top: 0.2rem;
    padding-bottom: 0.2rem;

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
    top: 3px;
    left: 3px;
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
    top: 3px;
    left: 3px;
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
    margin-top: 0.8rem;
    margin-bottom: 0.8rem;
    /* margin-left: 1rem;
    margin-right: 1rem; */
  }

  .side-by-side {
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    padding-left: 0px;
    padding-right: 0px;
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
