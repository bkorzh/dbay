<script lang="ts">
  import { VisibleState } from "./module_chevron";
  import { fade, draw, fly } from "svelte/transition";

  interface Props {
    visible: VisibleState;
    rotateState: () => void;
  }

  let { visible = $bindable(VisibleState.DoubleDown), rotateState }: Props =
    $props();


  let single_chevron = $derived.by(() => {
    if (visible === VisibleState.DoubleDown) {
      return false;
    } else {
      return true;
    }
  });


</script>

<div class="closer">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="20"
    height="20"
    fill="currentColor"
    stroke="currentColor"
    class="chevron animate"
    class:toggle_up={visible === VisibleState.Collapsed}
    class:toggle_down={visible === VisibleState.Down ||
      visible === VisibleState.DoubleDown}
    viewBox="0 0 16 16"
    role="button"
    tabindex="0"
    onclick={rotateState}
    onkeydown={rotateState}
  >
    {#if single_chevron}
      <path
        transition:fly={{ y: 0, duration: 200}}
        fill-rule="evenodd"
        d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
        stroke-width="0.8"
        transform="translate(0, 0)"
      />
    {:else}
      <path
        transition:fly={{ y: -2, duration: 200 }}
        fill-rule="evenodd"
        d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
        stroke-width="0.8"
        transform="translate(0, 2)"
      />
      <path
        transition:fly={{ y: 2, duration: 200 }}
        fill-rule="evenodd"
        d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
        stroke-width="0.8"
        transform="translate(0, -2)"
      />
    {/if}
  </svg>
</div>

<style>
  .chevron {
    margin-top: 0.25rem;
    margin-left: 0.2rem;
    color: var(--icon-color);
  }

  .animate {
    transition: transform 0.3s ease-in-out;
  }

  .chevron:focus {
    outline: none;
  }

  .toggle_up {
    transform: rotate(-90deg);
    transition: transform 0.2s ease-in-out;
  }

  .toggle_down {
    transform: rotate(0);
    transition: transform 0.2s ease-in-out;
  }
</style>
