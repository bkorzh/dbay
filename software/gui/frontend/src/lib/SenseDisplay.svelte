<script lang="ts">
  import type { ChSenseStateClass } from "./addons";
  import type {
    SenseChangerFunction,
    SenseEffectFunction,
  } from "./addons/vsense/vsense.svelte";

  // used for displaying voltage readings from sensing (read-only)
  interface Props {
    ch: ChSenseStateClass;
    spacing_small?: boolean;
    onChannelChange?: SenseChangerFunction;
    effect?: SenseEffectFunction;
  }

  let { ch, spacing_small = false, onChannelChange, effect }: Props = $props();

  // optional overrides
  if (onChannelChange) {
    ch.onChannelChange = onChannelChange;
  }
  if (effect) {
    ch.effect = effect;
  }

  const sp = spacing_small
    ? {
        // small spacing
        spacer: -0.75,
        period_spacer: -0.65,
      }
    : {
        // normal spacing
        spacer: -0.17,
        period_spacer: -0.39,
      };

  // Derived values for voltage display (read-only)
  let integer = $derived(Math.round(Math.abs(ch.voltage * 1000)));
  let thousands = $derived(integer % 10);
  let hundreds = $derived(Math.floor(integer / 10) % 10);
  let tens = $derived(Math.floor(integer / 100) % 10);
  let ones = $derived(Math.floor(integer / 1000) % 10);
  let sign = $derived(ch.voltage < 0 ? "-" : "+");
</script>

<div class="display" class:display-measuring={ch.measuring} role="status">
  <div
    class="digit"
    class:digit-off={!ch.measuring}
    style="margin-right: {sp.spacer}rem;"
  >
    {sign}
  </div>
  <div
    class="digit"
    class:digit-off={!ch.measuring}
    style="margin-right: {sp.spacer}rem;"
  >
    {ones}
  </div>
  <div
    class="digit dot"
    class:digit-off={!ch.measuring}
    style="margin-right: {sp.period_spacer}rem;"
  >
    .
  </div>
  <div
    class="digit"
    class:digit-off={!ch.measuring}
    style="margin-right: {sp.spacer}rem;"
  >
    {tens}
  </div>
  <div
    class="digit"
    class:digit-off={!ch.measuring}
    style="margin-right: {sp.spacer}rem;"
  >
    {hundreds}
  </div>
  <div
    class="digit"
    class:digit-off={!ch.measuring}
    style="margin-right: {sp.spacer}rem;"
  >
    {thousands}
  </div>
  <div class="voltage-unit">V</div>
</div>

<style>
  @import url("https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,wght@8..144,100;8..144,200;8..144,300;8..144,400;8..144,500;8..144,600;8..144,700&display=swap");

  .display {
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    border-radius: 4px;
    border: 1.5px solid var(--value-border-color);
    padding: 0rem 0.44rem;
    transition: background-color 0.1s ease-in-out;
    background-color: var(--display-color);
    user-select: none;
  }

  .display-measuring {
    background-color: var(--green-highlight);
    border-color: var(--green-border);
  }

  .digit {
    font-size: 1.5rem;
    color: var(--digits-color);
    font-family: "Roboto Flex", sans-serif;
    font-weight: 300;
    font-size: 1.7rem;
    text-align: center;
    min-width: 1ch;
  }

  .digit-off {
    color: var(--digits-deactivated-color);
  }

  .dot {
    margin-left: -0.03rem;
    margin-right: -0.03rem;
  }

  .voltage-unit {
    font-size: 1.5rem;
    font-weight: 300;
    color: var(--icon-color);
    font-family: "Roboto Flex", sans-serif;
    font-weight: 400;
    margin-left: 0.3rem;
  }
</style>
