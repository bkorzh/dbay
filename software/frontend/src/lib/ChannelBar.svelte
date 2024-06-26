<script lang="ts">
  import { onMount } from "svelte";
  import ChannelChevron from "./buttons/ChannelChevron.svelte";
  import HorizontalDots from "./buttons/HorizontalDots.svelte";
  import MenuSlotted from "./MenuSlotted.svelte";
  import MenuButton from "./buttons/MenuButton.svelte";
  import { ChSourceStateClass } from "./addons";
  import type {
    ChangerFunction,
    EffectFunction,
  } from "./addons/vsource/vsource.svelte";

  import type { Snippet } from "svelte";

  interface Props {
    showDropdown: boolean;
    children: Snippet;
    down: boolean;
    ch?: ChSourceStateClass;
    staticName?: string;
    borderTop?: boolean;
    onChevronClick?: () => void;
    onChannelChange?: ChangerFunction;
    effect?: EffectFunction;
  }

  let {
    showDropdown = $bindable(),
    children,
    down,
    ch,
    staticName,
    borderTop = false,
    onChevronClick,
    onChannelChange,
    effect,
  }: Props = $props();

  // override the onChannelChange function if it is passed as a prop
  if (onChannelChange && ch) {
    ch.onChannelChange = onChannelChange;
  }

  // override the effect function if it is passed as a prop. Used for updating other parts
  // of a module after a channel has finished updating.
  if (effect && ch) {
    ch.effect = effect;
  }


  

  // let heading_editing = false;
  let isEditing = false;
  let isMounted = false;

  let dotMenu = $state() as unknown as HTMLElement;
  let menuLocation = $state({ top: 0, left: 0 });
  // let showDropdown = $state(false);

  function handleInput(event: Event) {
    let target = event.target as HTMLInputElement;

    if (ch) ch.immediate_text = target.value;
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      isEditing = false;
      if (ch) ch.updateChannel({ heading_text: ch.immediate_text });
      const target = event.target as HTMLInputElement;
      target.blur();
    }
  }

  function toggleMenu() {
    showDropdown = !showDropdown;
    const rect = dotMenu.getBoundingClientRect();
    menuLocation = {
      top: rect.top + window.scrollY,
      left: rect.right + window.scrollX,
    };
  }

  onMount(() => {
    isMounted = true;
    const rect = dotMenu.getBoundingClientRect();
    menuLocation = {
      top: rect.top + window.scrollY,
      left: rect.right + window.scrollX,
    };
  });
</script>

<div
  class="top-bar"
  class:animated={ch ? ch.measuring : false}
  class:no_border={!down}
  class:border-top={borderTop}
>
  <div class="top-left">
    <!-- If it's a static label (not numbered), then always show the chevron -->
    <ChannelChevron
      {onChevronClick}
      {down}
      isHovering={ch ? (staticName ? true : ch.isHovering) : true}
      index={ch ? ch.index + 1 : 0}
    ></ChannelChevron>

    {#if staticName}
      <div class="heading-input input-to-label wide-input">{staticName}</div>
    {:else if ch}
      <input
        class="heading-input"
        type="text"
        value={ch.immediate_text}
        oninput={handleInput}
        onfocus={() => (ch.heading_editing = true)}
        onblur={() => {
          ch.heading_editing = false;
          if (ch) ch.updateChannel({ heading_text: ch.immediate_text });
        }}
        onkeydown={handleKeyDown}
        tabindex="0"
        disabled={!!staticName}
      />
    {:else}
      <div class="heading-input input-to-label wide-input">NaN</div>
    {/if}
    <!-- the double not (!!) converts the [string | undefined] to boolean -->
  </div>

  <div class="top-right">
    {#if !down && ch}
      <div class="heading-voltage" class:digit-off={!ch.activated}>
        {ch.valid ? ch.bias_voltage.toFixed(3) : ""}
      </div>
    {/if}
    <HorizontalDots onclick={toggleMenu} onkeydown={toggleMenu} bind:dotMenu
    ></HorizontalDots>
    <!-- here, class:something is a special svelte way of pointing to a class which may be toggled. It is a shorthand for class:something={something} -->
    <!-- where 'something' is both a boolean in javascript and a class -->
    {#if showDropdown}
      <MenuSlotted
        onclick={toggleMenu}
        menuVisible={showDropdown}
        location={menuLocation}
      >
        {@render children()}
      </MenuSlotted>
    {/if}

    <!-- <ChannelChevron bind:down={visible}></ChannelChevron> -->
  </div>
</div>

<style>
  @keyframes placeHolderShimmer {
    0% {
      background-position: -800px 0;
    }
    100% {
      background-position: 800px 0;
    }
  }

  .heading-voltage {
    color: var(--red-text);
    font-size: 1.5rem;
    letter-spacing: 0.58rem;
    font-family: "Roboto Flex", sans-serif;
    font-weight: 300;
    margin: auto;
    margin-left: 0;
    margin-right: 0.7rem;
  }

  .animated {
    animation-duration: 1.3s;
    animation-fill-mode: forwards;
    animation-iteration-count: infinite;
    animation-name: placeHolderShimmer;
    animation-timing-function: linear;
    background-color: #f6f7f8;
    background: linear-gradient(
      to right,
      var(--heading-color) 1%,
      var(--red-highlight) 40%,
      var(--heading-color) 80%
    );
    background-size: 800px 104px;
  }

  .top-left {
    display: flex;
    flex-direction: row;
    align-items: flex-end;
  }

  .top-right {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .heading-input {
    color: var(--text-color);
    font-size: 1.5rem;
    letter-spacing: 0rem;
    padding-right: 0rem;
    padding-bottom: 0.15rem;
    padding-right: 0rem;
    margin-top: 0.15rem;
    margin-bottom: 0.15rem;
    margin-left: 0.5rem;

    padding-top: 0.3rem;
    color: var(--digits-color);
    background-color: transparent;

    border: none;
    width: 75%;
  }

  input {
    background-color: transparent;
    border-radius: 4px;
    border: 1.5px solid var(--value-border-color);
    padding: 0rem 0.3rem;
    font-family: "Roboto Flex", sans-serif;
    font-weight: 300;
    font-size: 1.7rem;
    letter-spacing: 0.58rem;
    color: var(--digits-color);
  }

  .heading-input:hover {
    background-color: var(--hover-heading-color);
  }

  .input-to-label {
    margin-left: 0rem;
    color: var(--text-color);
    font-size: 1.5rem;
  }

  .wide-input {
    width: 15.5rem;
  }

  .input-to-label:hover {
    background-color: var(--heading-color);
  }

  .digit-off {
    color: var(--digits-deactivated-color);
  }

  .top-bar {
    display: flex;
    flex-direction: row;
    background-color: var(--heading-color);
    border-bottom: 1.3px solid var(--inner-border-color);
    justify-content: space-between;
    padding: 0rem 0rem;
    padding-bottom: 0rem;
    padding-right: 0px;
    padding-left: 0.7rem;
  }

  .no_border {
    border: none;
  }

  .border-top {
    border-top: 1.3px solid var(--divider-border-color);
  }
</style>
