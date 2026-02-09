<script lang="ts">
  import GeneralButton from "./buttons/GeneralButton.svelte";
  import Button from "./buttons/Button.svelte";
  import { ChSenseStateClass } from "./addons";
  import type { ChSenseState, VsenseChange } from "./addons/vsense/interface";
  import type {
    SenseChangerFunction,
    SenseEffectFunction,
  } from "./addons/vsense/vsense.svelte";
  import SenseDisplay from "./SenseDisplay.svelte";

  interface Props {
    ch: ChSenseStateClass;
    onChannelChange?: SenseChangerFunction;
    effect?: SenseEffectFunction;
  }

  let { ch, onChannelChange, effect }: Props = $props();

  // optional overrides
  if (onChannelChange) {
    ch.onChannelChange = onChannelChange;
  }
  if (effect) {
    ch.effect = effect;
  }

  let st = $derived(
    ch.measuring
      ? {
          action_string: "Stop Measuring",
          colorMode: false,
          opacity: 1,
        }
      : {
          action_string: "Start Measuring",
          colorMode: true,
          opacity: 0.2,
        },
  );

  function switchMeasuring() {
    ch.updateChannel({ measuring: !ch.measuring });
  }

  function handleInputKeyDown(event: any) {
    if (event.key === "Enter") {
      // For voltage sensing, we might want to trigger a manual reading
      ch.updateChannel({ measuring: ch.measuring });
    }
  }
</script>

<div class="main-controlls">
  <div class="left">
    <div class="sensor-info">
      <div class="sensor-label">Voltage Reading:</div>
      <SenseDisplay {ch}></SenseDisplay>
    </div>

    <div class="measurement-controls">
      <Button onclick={switchMeasuring} redGreen={st.colorMode}
        >{st.action_string}</Button
      >
      <GeneralButton onclick={() => ch.updateChannel({ voltage: 0 })}
        >Zero Reading</GeneralButton
      >
    </div>
  </div>

  <div class="right">
    <div class="measurement-status">
      <div class="status-label">Status:</div>
      <div class="status-value" class:measuring={ch.measuring}>
        {ch.measuring ? "Measuring" : "Idle"}
      </div>

      <div class="voltage-range">
        <div class="range-label">Range: ±5.000V</div>
      </div>

      <div class="channel-info">
        <div class="info-label">Channel: {ch.index + 1}</div>
        <div class="info-label">Differential ADC</div>
      </div>
    </div>
  </div>
</div>

<style>
  @import url("https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,wght@8..144,100;8..144,200;8..144,300;8..144,400;8..144,500;8..144,600;8..144,700&display=swap");

  .main-controlls {
    display: flex;
    flex-direction: row;
    flex-grow: 1;
    justify-content: space-around;
    transition: background-color 0.1s ease-in-out;
    padding: 1rem;
    background-color: var(--body-color);
  }

  .left {
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    padding: 0rem 1rem;
    margin-right: 0.5rem;
    width: 50%;
    gap: 1rem;
  }

  .right {
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    padding: 0rem 1rem;
    margin-right: 0.5rem;
    width: 50%;
  }

  .sensor-info {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .sensor-label {
    font-size: 1.1rem;
    font-weight: 400;
    color: var(--text-color);
    font-family: "Roboto Flex", sans-serif;
  }

  .measurement-controls {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .measurement-status {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
  }

  .status-label,
  .range-label,
  .info-label {
    font-size: 1rem;
    font-weight: 300;
    color: var(--text-color);
    font-family: "Roboto Flex", sans-serif;
  }

  .status-value {
    font-size: 1.2rem;
    font-weight: 400;
    color: var(--digits-deactivated-color);
    font-family: "Roboto Flex", sans-serif;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    background-color: var(--display-color);
    border: 1px solid var(--value-border-color);
  }

  .status-value.measuring {
    color: var(--green-text);
    background-color: var(--green-highlight);
    border-color: var(--green-border);
  }

  .voltage-range {
    padding: 0.5rem 0;
    border-top: 1px solid var(--inner-border-color);
  }

  .channel-info {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    padding: 0.5rem 0;
    border-top: 1px solid var(--inner-border-color);
  }
</style>
