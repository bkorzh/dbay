<script lang="ts">
  interface MyProps {
    triggerProps?: Record<string, unknown>;
    burgerMenu?: HTMLButtonElement;
    ariaLabel?: string;
  }

  let {
    triggerProps = {},
    burgerMenu = $bindable(),
    ariaLabel = "Open main menu",
  }: MyProps = $props();
</script>

<button
  type="button"
  {...triggerProps}
  class="hamburger"
  bind:this={burgerMenu}
  aria-label={ariaLabel}
>
    <svg
        class="h-5.5 w-6 my-2 mr-1"
        viewBox="0 0 22 22"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
    >
        <path d="M3 12h18M3 6h18M3 18h18" />
    </svg>
</button>

<style>
    .hamburger {
        display: flex;
        padding-top: 2px;
        padding-bottom: 2px;
        padding-left: 4px;
        padding-right: 4px;
        color: var(--text-color);
        border: none;
        background: transparent;
    }

    .hamburger:hover {
        cursor: pointer;
    }
</style>
