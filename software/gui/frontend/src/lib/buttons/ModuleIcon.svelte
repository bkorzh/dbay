<script lang="ts">
  import { hexToRGBA } from "../../util";

  interface Props {
    icon_name: string;
    iconElement?: HTMLButtonElement;
    glowColor: string | null;
    triggerProps?: Record<string, unknown>;
    ariaLabel?: string;
  }
  let {
    icon_name,
    iconElement = $bindable(),
    glowColor = $bindable(),
    triggerProps = {},
    ariaLabel = "Open module menu",
  }: Props = $props();

  let hover: boolean = $state(false);

  async function getSvgColor(url: string) {
    const response = await fetch(url);
    const svgText = await response.text();
    const parser = new DOMParser();
    const svgDoc = parser.parseFromString(svgText, "image/svg+xml");
    const paths = svgDoc.querySelectorAll("path[fill]");
    for (let i = 0; i < paths.length; i++) {
      const color = paths[i].getAttribute("fill");
      if (color && color !== "none") {
        return color;
      }
    }
    return null;
  }

  $effect(() => {
    getSvgColor(icon_name).then((color) => {
      glowColor = color;
    });
  });
</script>

<button
  type="button"
  {...triggerProps}
  class="module-icon"
  bind:this={iconElement}
  aria-label={ariaLabel}
  onmouseover={() => hover = true}
  onmouseout={() => hover = false}
  onfocus={() => hover = true}
  onblur={() => hover = false}
>
  <img
    class="icon"
    src={icon_name}
    alt="module icon"
    style="filter: {hover ? `drop-shadow(0 0 2px ${hexToRGBA(glowColor, 0.5)})` : 'none'};"
  />
</button>

<style>
  .module-icon {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    border-radius: 0.3rem;
    border: none;
    background: transparent;
    padding: 0;
  }

  .icon {
    margin: 0.1rem 0rem;
    margin-left: 0.8rem;
    margin-right: 0.05rem;
    width: 3rem; /* adjust as needed */
    height: 3rem; /* adjust as needed */
    transition: box-shadow 0.3s ease-in-out; /* add transition for smooth glow effect */
    transform: scale(1.03);
  }

  .icon:hover {
    cursor: pointer;
    transform: scale(1.06);
  }

  .module-icon:hover {
    cursor: pointer;
  }
</style>
