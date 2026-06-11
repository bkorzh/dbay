<script lang="ts">
  import { ChSenseStateClass } from "./addons";
  import type {
    SenseChangerFunction,
    SenseEffectFunction,
  } from "./addons/vsense/vsense.svelte";

  // Compact read-only voltage row: index, editable label, digit readout.
  interface Props {
    ch: ChSenseStateClass;
    module_index: number;
    borders?: boolean;
    onChannelChange?: SenseChangerFunction;
    effect?: SenseEffectFunction;
  }

  let { ch, module_index, borders = true, onChannelChange, effect }: Props = $props();

  // override the onChannelChange function if it is passed as a prop
  if (onChannelChange) {
    ch.onChannelChange = onChannelChange;
  }
  if (effect) {
    ch.effect = effect;
  }

  // Read-only readout text. toFixed(3) keeps one leading digit below 10 V
  // and grows to two ("12.345") at |v| >= 10. Rendered as a single text node
  // with tabular numerals — per-digit spans clip glyph edges in Safari.
  let formatted = $derived(
    (ch.voltage < -0.0005 ? "-" : "") + Math.abs(ch.voltage).toFixed(3),
  );

  function handleInput(event: Event) {
    const target = event.target as HTMLInputElement;
    ch.immediate_text = target.value;
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      ch.updateChannel({ name: ch.immediate_text });
      const target = event.target as HTMLInputElement;
      target.blur();
    }
  }

  function toggleMeasuring() {
    ch.updateChannel({ measuring: !ch.measuring });
  }
</script>

<div
  class="row"
  class:borders
  onmouseenter={() => (ch.isHovering = true)}
  onmouseleave={() => (ch.isHovering = false)}
  role="region"
>
  <div class="left">
    <div class="index">{ch.index + 1}</div>
    <input
      class="heading-input"
      type="text"
      value={ch.immediate_text}
      oninput={handleInput}
      onfocus={() => (ch.name_editing = true)}
      onblur={() => {
        ch.finishNameEditing();
        ch.updateChannel({ name: ch.immediate_text });
      }}
      onkeydown={handleKeyDown}
      tabindex="0"
    />
  </div>

  <button
    class="readout"
    onclick={toggleMeasuring}
    title={ch.measuring ? "Measuring — click to stop" : "Idle — click to start measuring"}
    aria-label={`Channel ${ch.index + 1} voltage readout`}
  >
    <span class="value" class:measuring={ch.measuring}>{formatted}</span>
    <span class="unit">V</span>
  </button>
</div>

<style>
  @import url("https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,wght@8..144,100;8..144,200;8..144,300;8..144,400;8..144,500;8..144,600;8..144,700&display=swap");

  .row {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 0.25rem 0.7rem 0.25rem 0.7rem;
    background-color: var(--body-color);
  }

  .row:hover {
    background-color: var(--hover-color);
  }

  .borders {
    border-left: 1.3px solid var(--outer-border-color);
    border-right: 1.3px solid var(--outer-border-color);
    border-bottom: 1.3px solid var(--divider-border-color);
  }

  .left {
    display: flex;
    flex-direction: row;
    align-items: center;
    flex-grow: 1;
    min-width: 0;
  }

  .index {
    width: 2.5rem;
    flex-shrink: 0;
    text-align: center;
    font-size: 1.5rem;
    color: var(--icon-color);
    user-select: none;
  }

  .heading-input {
    color: var(--digits-color);
    font-size: 1.5rem;
    margin-left: 0.5rem;
    padding: 0.15rem 0.3rem 0.15rem 0;
    background-color: transparent;
    border: none;
    border-radius: 4px;
    width: 100%;
    min-width: 3rem;
  }

  .heading-input:hover {
    background-color: var(--hover-heading-color);
  }

  .heading-input:focus {
    outline: none;
  }

  .readout {
    display: flex;
    flex-direction: row;
    align-items: baseline;
    flex-shrink: 0;
    appearance: none;
    -webkit-appearance: none;
    background: none;
    border: none;
    border-radius: 4px;
    padding: 0.1rem 0.4rem 0.1rem 0.5rem;
    margin-right: 0.3rem;
    cursor: pointer;
    user-select: none;
  }

  .readout:hover {
    background-color: var(--hover-heading-color);
  }

  .value {
    font-family: "Roboto Flex", sans-serif;
    font-weight: 300;
    font-size: 1.9rem;
    font-variant-numeric: tabular-nums;
    letter-spacing: 0.12em;
    color: var(--digits-color);
    opacity: 0.45;
    white-space: nowrap;
    transition: color 0.15s ease-in-out, opacity 0.15s ease-in-out;
  }

  .value.measuring {
    color: var(--edit-blue);
    opacity: 1;
  }

  .unit {
    font-family: "Roboto Flex", sans-serif;
    font-weight: 400;
    font-size: 1.7rem;
    color: var(--digits-deactivated-color);
    margin-left: 0.35rem;
  }
</style>
