<script lang="ts">
  import { DropdownMenu } from "bits-ui";
  import ChannelChevron from "./buttons/ChannelChevron.svelte";
  import HorizontalDots from "./buttons/HorizontalDots.svelte";
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
    effect: channelEffect,
  }: Props = $props();

  $effect(() => {
    if (onChannelChange && ch) {
      ch.onChannelChange = onChannelChange;
    }
  });

  $effect(() => {
    if (channelEffect && ch) {
      ch.effect = channelEffect;
    }
  });


  

  function handleInput(event: Event) {
    let target = event.target as HTMLInputElement;

    if (ch) ch.immediate_text = target.value;
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      if (ch) ch.updateChannel({ heading_text: ch.immediate_text });
      const target = event.target as HTMLInputElement;
      target.blur();
    }
  }
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
    <DropdownMenu.Root bind:open={showDropdown}>
      <DropdownMenu.Trigger>
        {#snippet child({ props }: { props: Record<string, unknown> })}
          <HorizontalDots
            triggerProps={props}
            ariaLabel={staticName ?? (ch ? `Channel ${ch.index + 1} actions` : "Channel actions")}
          />
        {/snippet}
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content side="bottom" align="end" sideOffset={6}>
          {#snippet child({ wrapperProps, props }: { wrapperProps: Record<string, unknown>; props: Record<string, unknown> })}
            <div {...wrapperProps}>
              <div {...props} class="dropdown-content">
                {@render children()}
              </div>
            </div>
          {/snippet}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
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

  .dropdown-content {
    min-width: 13rem;
    overflow: hidden;
    border: 1.3px solid var(--outer-border-color);
    border-radius: 0.5rem;
    background-color: var(--body-color);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.09);
    padding: 0.2rem;
    outline: none;
    z-index: 1000;
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
