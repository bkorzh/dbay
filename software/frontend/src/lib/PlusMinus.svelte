<script lang="ts">
  import type { ChSourceStateClass } from "./addons";
  import type { ChangerFunction } from "./addons/vsource/vsource.svelte";

  interface Props {
    ch: ChSourceStateClass;
    onChannelChange: ChangerFunction;
  }

  let { ch, onChannelChange }: Props = $props();

  function updatedPlusMinus() {
    if (ch.editing) {
      ch.sign_temp = ch.sign_temp === "+" ? "-" : "+";
      return;
    }

    ch.isPlusMinusPressed = true; //needed for the animation

    ch.updateChannel({ voltage: -ch.bias_voltage }, onChannelChange);

    setTimeout(() => {
      ch.isPlusMinusPressed = false;
    }, 1);
  }
</script>

<div
  class="plus-minus"
  class:digit-off={!ch.activated}
  class:digit-edit={ch.editing}
  role="button"
  tabindex="0"
  onclick={updatedPlusMinus}
  onkeydown={updatedPlusMinus}
>
  {ch.sign_temp}
</div>

<style>
  

  .plus-minus {
    width: 8px;
    display: flex;
    justify-content: center;
    font-size: 1.5rem;
    color: var(--digits-color);
    font-family: "Roboto Flex", sans-serif;
    font-weight: 300;
    margin-top: auto;
    margin-bottom: auto;
    margin-left: 0.2rem;
    margin-right: 0.2rem;
    border-radius: 4px;
    /* opacity: var(--state_opacity); */
  }

  .digit-off {
    color: var(--digits-deactivated-color);
  }

  .digit-edit {
    color: var(--edit-blue);
    font-weight: 400;
  }
</style>
