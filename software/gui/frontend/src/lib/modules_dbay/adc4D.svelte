<script lang="ts">
  import SenseRow from "../SenseRow.svelte";
  import { system_state } from "../../state/systemState.svelte";
  import { slide } from "svelte/transition";
  import { adc4D } from "./adc4D_data.svelte";
  import type { VsenseChange } from "../addons/vsense/interface";
  import { requestSenseUpdate, requestPollingUpdate } from "../../api";
  import { VisibleState } from "../buttons/module_chevron";
  import ModuleHeading from "../ModuleHeading.svelte";
  import MenuButton from "../buttons/MenuButton.svelte";
  const adc4D_icon = "/assets/adc4D_icon.svg";

  interface MyProps {
    module_index: number;
  }
  let { module_index }: MyProps = $props();

  const this_component_data = system_state.data[module_index] as adc4D;

  let channel_list = [0, 1, 2, 3]; // 4 differential ADC channels

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

  // The rows have no per-channel expansion, so the module chevron just
  // toggles between collapsed and open.
  function rotateState() {
    visible =
      visible === VisibleState.Collapsed
        ? VisibleState.DoubleDown
        : VisibleState.Collapsed;

    localStorage.setItem("visible" + module_index, visible.toString());
  }

  // ── polling controls ──────────────────────────────────────────────
  let freqEditing = false;
  let freqText: string | number = $state(
    String(this_component_data.polling.frequency),
  );

  $effect(() => {
    if (!freqEditing) freqText = String(this_component_data.polling.frequency);
  });

  async function setPolling(running: boolean, frequency: number) {
    if (system_state.valid) {
      await requestPollingUpdate({ module_index, running, frequency });
    } else {
      this_component_data.polling.running = running;
      this_component_data.polling.frequency = frequency;
    }
  }

  function applyFrequency() {
    freqEditing = false;
    const parsed = parseFloat(String(freqText));
    if (!isNaN(parsed) && parsed > 0) {
      setPolling(this_component_data.polling.running, parsed);
    } else {
      freqText = String(this_component_data.polling.frequency);
    }
  }

  function handleFreqKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      applyFrequency();
      (event.target as HTMLInputElement).blur();
    }
  }
</script>

{#snippet menu_buttons()}
  <MenuButton
    onclick={() =>
      setPolling(
        !this_component_data.polling.running,
        this_component_data.polling.frequency,
      )}
    >{this_component_data.polling.running
      ? "Stop Polling"
      : "Start Polling"}</MenuButton
  >
  <div class="freq-row">
    <div class="freq-label">Polling rate (Hz)</div>
    <input
      class="freq-input"
      type="number"
      min="0.1"
      max="20"
      step="0.1"
      bind:value={freqText}
      onfocus={() => (freqEditing = true)}
      onblur={applyFrequency}
      onkeydown={handleFreqKeyDown}
    />
  </div>
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
        {#each channel_list as i (i)}
          <div transition:slide|global class="channel">
            <SenseRow
              ch={this_component_data.vsense.channels[i]}
              {module_index}
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

  .freq-row {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    padding: 0.25rem 0.25rem 0.25rem 0.5rem;
  }

  .freq-label {
    font-size: 1.1rem;
    color: var(--text-color);
  }

  .freq-input {
    width: 4.5rem;
    font-size: 1.1rem;
    color: var(--digits-color);
    background-color: transparent;
    border: 1.3px solid var(--value-border-color);
    border-radius: 4px;
    padding: 0.1rem 0.3rem;
  }

  .freq-input:focus {
    outline: none;
    border-color: var(--edit-blue);
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
