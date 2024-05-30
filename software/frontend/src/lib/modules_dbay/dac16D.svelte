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

  interface MyProps {
    module_index: number;
  }
  let { module_index }: MyProps = $props();
  let slot = $derived(system_state.data[module_index - 1]?.core.slot);

  let show_dropdown = $state(Array.from({ length: 16 }, (_, i) => false));

  const c = system_state.data[module_index - 1] as dac16D;

  let channel_list = Array.from({ length: 16 }, (_, i) => i + 1);

  let half_channel_list = channel_list.slice(0, 8);

  // let temps = Array.from({length: 16}, (_, i) => $state([0,0,0,0]));

  // class tempState {
  //   public temp = $state([0, 0, 0, 0]);
  // }

  let visible = $state(true);
  let visible_all_channels = $state(true);
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
      channel.setChannel(intermediate_data);
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

    // if the equality is broken, then set the shared_voltage to invalid
    for (let i = 0; i < c.vsource.channels.length; i++) {
      if (i !== current_index) {
        if (
          c.vsource.channels[i].bias_voltage !== new_voltage ||
          c.vsource.channels[i].activated !== new_activated
        ) {
          c.shared_voltage.setInvalid();
          return data;
        }
      }
    }
    c.shared_voltage.setValid(data);
    return data;
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

  // function toggleMenu() {
  //   showDropdown = !showDropdown;
  //   const rect = dotMenu.getBoundingClientRect();
  //   menuLocation = {
  //     top: rect.top + window.scrollY,
  //     left: rect.right + window.scrollX,
  //   };
  // }

  function showControls(i: number) {
    show_dropdown[i] = true;
  }
</script>

<div class="module-container">
  <div class="heading" class:closed={!visible}>
    <ModuleChevron bind:visible></ModuleChevron>
    <div class="identifier">M{slot}:</div>
    <div class="identifier">16 Ch. Voltage Source</div>
  </div>

  {#if visible}
    <div class="content">
      <div class="box" transition:slide|global>
        <Channel
          ch={c.shared_voltage}
          {module_index}
          onChannelChange={distributeChannelChange}
          staticName={c.shared_voltage.heading_text}
          borders={false}
        />
      </div>

      <div class="box" transition:slide|global>
        <ChannelBar
          {onChannelChange}
          bind:showDropdown
          bind:down={visible_all_channels}
          staticName="Set Individual Channels"
          borderTop={true}
        >
          <MenuButton
            onclick={() => {
              console.log("something");
            }}>Do Something</MenuButton
          >
        </ChannelBar>
        {#if visible_all_channels}
          <div class="individual-body">
            {#each half_channel_list as ch, i}
              <div class="side-by-side">
                <div class="channel left">
                  <div class="ch-number">{i + 1}</div>
                  <Display
                    ch={c.vsource.channels[i]}
                    {onChannelChange}
                    spacing_small={true}
                  ></Display>
                  <VerticalDots
                    onclick={(e) => showControls(i)}
                    onkeydown={(e) => showControls(i)}
                    bind:dotMenu={verticalDotMenu}
                  ></VerticalDots>
                </div>

                <div class="channel">
                  <div class="ch-number">{i + 9}</div>
                  <Display
                    ch={c.vsource.channels[i + 8]}
                    {onChannelChange}
                    spacing_small={true}
                  ></Display>
                  <VerticalDots
                    onclick={(e) => {
                      show_dropdown[i + 8] = true;
                    }}
                    onkeydown={(e) => {
                      show_dropdown[i + 8] = true;
                    }}
                    bind:dotMenu={verticalDotMenu}
                  ></VerticalDots>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .individual-body {
    margin-top: 0.5rem;
    margin-left: 1rem;
    margin-right: 1rem;
  }

  .side-by-side {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    padding: 0.25rem;
  }

  .ch-number {
    /* margin-left: 10px; */

    margin: auto;
    margin-right: 0.5rem;
    margin-left: 0.8rem;
    color: var(--icon-color);
    font-size: large;
    min-width: 1.8rem;
  }

  .channel {
    display: flex;
    flex-direction: row;
  }

  /* .left {
    margin-right: 3rem;
  } */

  .identifier {
    margin-left: 10px;
    color: var(--module-icon-color);
    font-size: large;
  }

  .content {
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    width: 100%;
    background-color: var(--bg-color);
    box-sizing: border-box;
    display: flex;
    border-left: 1.3px solid var(--module-border-color);
    border-right: 1.3px solid var(--module-border-color);
    border-bottom: 1.3px solid var(--module-border-color);
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
