<script lang="ts">
  /**
   * demoD — the worked example from the Adding a Module guide. Not real hardware.
   *
   * Two halves, on purpose:
   *   - the output channel reuses `Channel`, the same component dac4D uses, so
   *     the digit display and on/off button come for free
   *   - the trim row uses `Slider`, a control with no existing building block,
   *     and shows how to drive a command from a continuous input
   */
  import Channel from "../Channel.svelte";
  import Slider from "../Slider.svelte";
  import ModuleHeading from "../ModuleHeading.svelte";
  import MenuButton from "../buttons/MenuButton.svelte";
  import { VisibleState } from "../buttons/module_chevron";
  import { slide } from "svelte/transition";
  import { system_state } from "../../state/systemState.svelte";
  import { requestDemodTrim, requestDemodVsource } from "../../api";
  import { syncErrors } from "../../sync/errors.svelte";
  import { joinJsonPointer } from "lab-link/core";
  import type { VsourceChange } from "../addons/vsource/interface";
  import { demoD } from "./demoD_data.svelte";


  // The slider's range, matching the backend's validation in demoD.py.
  const TRIM_MIN = -1;
  const TRIM_MAX = 1;

  // How long to wait after the last movement before sending a command. Short
  // enough to feel live, long enough that a drag across the track sends a
  // handful of commands instead of a hundred.
  const DEBOUNCE_MS = 120;

  interface MyProps {
    module_index: number;
  }
  let { module_index }: MyProps = $props();

  const this_component_data = system_state.data[module_index] as demoD;

  let visible = $state(
    Number(localStorage.getItem("visible" + module_index)) ||
      VisibleState.DoubleDown,
  );
  let down = $state(true);

  // Inline errors are filed by JSON pointer, so a trim error can be shown here
  // rather than as a toast in the corner of the app.
  const trimPath = joinJsonPointer("", "data", String(module_index), "trim_voltage");
  let trimError = $derived(syncErrors.byPath.get(trimPath));

  // ── the output channel ────────────────────────────────────────────
  // `Channel` calls this whenever the user changes the channel. Without a
  // backend (the offline fallback state) the change is echoed back unchanged so
  // the UI still responds.
  async function onChannelChange(data: VsourceChange) {
    if (!system_state.valid) return data;
    return await requestDemodVsource(data);
  }

  // ── the trim slider ───────────────────────────────────────────────
  let debounceTimer: ReturnType<typeof setTimeout> | undefined;

  function sendTrim(voltage: number) {
    if (!system_state.valid) return;
    requestDemodTrim({ module_index, voltage }).catch(() => {
      // The command failed and lab-link already surfaced the error. Fall back to
      // the server's value so the thumb cannot sit at a setting the hardware
      // never accepted.
      this_component_data.trim_voltage =
        this_component_data.sync.get<{ trim_voltage?: number }>(
          this_component_data.path,
        ).trim_voltage ?? 0;
    });
  }

  function onTrimInput(voltage: number) {
    // Move the thumb immediately: waiting for the server would feel laggy.
    // `dragging` blocks incoming patches while this is true, so the server
    // cannot yank the thumb out from under the user mid-drag.
    this_component_data.dragging = true;
    this_component_data.trim_voltage = voltage;

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => sendTrim(voltage), DEBOUNCE_MS);
  }

  function onTrimRelease(voltage: number) {
    // Cancel any pending debounce and send the final value straight away, so
    // the last thing the hardware receives is exactly where the thumb stopped.
    clearTimeout(debounceTimer);
    this_component_data.dragging = false;
    this_component_data.trim_voltage = voltage;
    sendTrim(voltage);
  }

  function rotateState() {
    visible =
      visible === VisibleState.Collapsed
        ? VisibleState.DoubleDown
        : VisibleState.Collapsed;
    localStorage.setItem("visible" + module_index, visible.toString());
  }
</script>

{#snippet menu_buttons()}
  <MenuButton onclick={() => console.log("demoD has no menu actions")}>
    undefined
  </MenuButton>
{/snippet}

<div class="module-container">
  <ModuleHeading
    m={this_component_data}
    {visible}
    {rotateState}
    {module_index}
    {menu_buttons}
  ></ModuleHeading>

  <div class="body">
    {#if !(visible == VisibleState.Collapsed)}
      <div class="content">
        <div transition:slide|global class="channel">
          <Channel
            ch={this_component_data.vsource.channels[0]}
            {module_index}
            {down}
            onChevronClick={() => (down = !down)}
            {onChannelChange}
            borders={false}
          />
        </div>

        <div transition:slide|global class="trim-row">
          <Slider
            label="Trim"
            value={this_component_data.trim_voltage}
            min={TRIM_MIN}
            max={TRIM_MAX}
            step={0.01}
            oninput={onTrimInput}
            onrelease={onTrimRelease}
          />
          {#if trimError}
            <span class="trim-error">{trimError.message}</span>
          {/if}
        </div>
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

  /* The channel is asked not to draw its own borders (borders={false}), because
     its bottom edge would divide the output from the trim. The two rows are one
     control surface, so the side edges are drawn here and the bottom edge only
     on the last row. */
  .channel {
    border-left: 1.3px solid var(--outer-border-color);
    border-right: 1.3px solid var(--outer-border-color);
  }

  .trim-row {
    display: flex;
    flex-direction: column;
    padding: 0.5rem 1rem 0.7rem 1rem;
    border-left: 1.3px solid var(--outer-border-color);
    border-right: 1.3px solid var(--outer-border-color);
    border-bottom: 1.3px solid var(--divider-border-color);
  }

  .trim-error {
    font-size: 0.95rem;
    color: var(--red-text);
    padding-top: 0.3rem;
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
