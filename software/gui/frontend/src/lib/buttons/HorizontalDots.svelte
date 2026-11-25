<script lang="ts">
  interface Props {
    triggerProps?: Record<string, unknown>;
    dotMenu?: HTMLButtonElement;
    ariaLabel?: string;
  }

  let {
    triggerProps = {},
    dotMenu = $bindable(),
    ariaLabel = "Open menu",
  }: Props = $props();
</script>

<button
  type="button"
  {...triggerProps}
  class="dot-menu"
  bind:this={dotMenu}
  aria-label={ariaLabel}
>
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="21"
        height="21"
        fill="currentColor"
        stroke="currentColor"
        class="bi-three-dots"
        viewBox="0 -3 16 16"
    >
        <path
            d="M3 9.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"
            stroke-width="0.3"
        />
    </svg>
</button>


<style>
    .dot-menu {
        margin: 0px 3px;
        padding: 0px 5px;
        padding-top: 0.1rem;
        margin-bottom: 0.15rem;
        margin-top: 0.15rem;
        color: var(--icon-color);
        border-radius: 5px;
        border: none;
        background: transparent;
    }

    .dot-menu:hover {
        background-color: var(--hover-heading-color);
    }

    .dot-menu:active {
        transform: scale(0.95);
    }
</style>
