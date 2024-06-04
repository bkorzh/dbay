<script lang="ts">
  interface Props {
    activated: boolean;
    onclick: (e: MouseEvent) => void;
  }

  let { activated, onclick }: Props = $props();

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter" || event.key === " ") {
      const target = event.target as HTMLElement;
      target.click();
    }
  }
</script>

<div class="container" {onclick} onkeydown={handleKeyDown}
role="button"
    tabindex="0">
  <svg
    width="15"
    height="17"
    viewBox="0 0 98 192"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"

  >
    <path
      class="outer"
      class:activated
      d="M11 122.5L11 141C11 151.078 15.0036 160.744 22.1299 167.87C29.2563 174.996 38.9218 179 49 179C59.0782 179 68.7437 174.996 75.8701 167.87C82.9964 160.744 87 151.078 87 141V122.5M87 69.5V51C87 40.9218 82.9964 31.2563 75.8701 24.1299C68.7437 17.0036 59.0782 13 49 13C38.9218 13 29.2563 17.0036 22.1299 24.1299C15.0036 31.2563 11 40.9218 11 51V69.5"
      stroke-width="21"
      stroke-linecap="round"
    />
    <path
      d="M49 141V96V51"
      class="inner"
      class:activated
      stroke-width="21"
      stroke-linecap="round"
    />
  </svg>
</div>

<style>
  .container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 1.8rem;
    margin-right: 0.2rem;
  }

  .container:hover {
    cursor: pointer;
    background-color: var(--hover-body-color);
    border-radius: 0.3rem;
  }

  .container:active {
    transform: scale(0.9);
  }

  .container:focus {
    outline: none;
  }

  svg:focus {
    outline: none;
  }

  .outer {
    stroke: var(--icon-color);
    opacity: 1;
  }

  .inner {
    stroke: var(--icon-color);
    opacity: 0;
  }

  .activated {
    stroke: var(--text-color);
    opacity: 1;
  }
</style>
