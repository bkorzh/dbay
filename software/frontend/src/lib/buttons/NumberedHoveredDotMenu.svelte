<script lang="ts">
  import { fly } from "svelte/transition";
  import { fade } from "svelte/transition";
  import { crossfade } from "svelte/transition";
  import { cubicInOut } from "svelte/easing";

  interface Props {
    isHovering: boolean;
    index: number;
    onclick: (e: MouseEvent) => void;
    onkeydown: (e: KeyboardEvent) => void;
    dotMenu: HTMLElement;
  }

  let {
    isHovering,
    index,
    onclick,
    onkeydown,
    dotMenu = $bindable(),
  }: Props = $props();

  // interface Props {
  //     isHovering: boolean;
  //     index: number;
  //     onChevronClick?: () => void
  // }

  // let {isHovering, index, onChevronClick}: Props = $props();

  // let toggle_up = $state(false);
  // let toggle_down = $state(true);
  let isConsistentHovering = $state(false);
  let hoverTimeout: number;

  $effect(() => {
    clearTimeout(hoverTimeout);
    isHovering = isHovering;
    hoverTimeout = setTimeout(() => {
      isConsistentHovering = isHovering;
    }, 200);
  });
</script>

<div
  class="container"
  {onclick}
  {onkeydown}
  bind:this={dotMenu}
  role="button"
  tabindex="0"
>
  {#if isConsistentHovering}
    <!-- <svg
            xmlns="http://www.w3.org/2000/svg"
            width="22"
            height="22"
            class="chevron"
            fill="currentColor"
            stroke="currentColor"
            class:toggle_up
            class:toggle_down
            viewBox="0 0 16 16"
            role="button"
            tabindex="0"
            in:fly={toggle_up ? { y: -7, duration: 200} : { x: -7, duration: 200}}
            out:fly={toggle_up ? { y: -7, duration: 200} : { x: -7, duration: 200}}
        >
            <path
                fill-rule="evenodd"
                d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
                stroke-width="0.8"
            />
        </svg> -->

    <div
      class="dot-menu"
      role="button"
      tabindex="0"
      in:fly={{ x: -7, duration: 200 }}
      out:fly={{ x: -7, duration: 200 }}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="21"
        height="21"
        fill="currentColor"
        stroke="currentColor"
        class="bi-three-dots"
        viewBox="0 -3 16 16"
        style="transform: rotate(90deg);"
      >
        <path
          d="M3 9.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"
          stroke-width="0.3"
        />
      </svg>
    </div>
  {:else}
    <!-- <div class="ch-number">{i + 9}</div> -->
    <div
      class="ch-number"
      in:fly={{ x: 7, duration: 200 }}
      out:fly={{ x: 7, duration: 200 }}
    >
      {index+1}
    </div>
  {/if}
</div>

<style>
  .container {
    margin: 0.15rem;
    border-radius: 5px;

    width: 2.5rem;
    color: var(--icon-color);
    height: 2.5rem;

    display: grid;
  }

  .container > * {
    grid-area: 1 / 1;
  }

  .ch-number {
    /* margin-left: 10px; */
    margin: auto;
    /* margin-right: 0.5rem; */
    /* margin-left: 0.8rem; */
    margin-right: 0.1rem;
    padding-bottom: 0.1rem;
    color: var(--icon-color);
    font-size: large;
    min-width: 1.7rem;
    text-align: right;
  }

  .dot-menu {
    /* margin: 0px 3px;
        padding: 0px 5px; */
    /* padding-top: 0.1rem;
        margin-bottom: 0.15rem;
        margin-top: 0.15rem; */
    /* padding-bottom: -10rem; */
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--icon-color);
    border-radius: 5px;
    transform: scale(0.85);
    height: 100%;
    padding-left: 0.5rem;
    /* padding: auto; */
  }

  .dot-menu:hover {
    /* cursor: pointer; */
    background-color: var(--hover-heading-color);
  }

  .dot-menu:active {
    transform: scale(0.8);
  }
</style>
