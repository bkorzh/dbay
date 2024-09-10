<script lang="ts">
  import MenuSlotted from "../MenuSlotted.svelte";
  import type { Snippet } from "svelte";
  import { onMount } from "svelte";
  import { get } from "svelte/store";
  import { hexToRGBA } from "../../util";

  interface Props {
    icon_name: string;
    onclick: () => void;
    iconElement: HTMLElement;
    glowColor: string | null;
  }
  let { icon_name, onclick, iconElement = $bindable(), glowColor=$bindable() }: Props = $props();

  let isMounted = false;
  let menuLocation = $state({ top: 0, left: 0 });

//   let glowColor: string | null = $state("");
  let hover: boolean = $state(false);

  onMount(() => {
    isMounted = true;
    const rect = iconElement.getBoundingClientRect();
    menuLocation = {
      top: rect.top + window.scrollY,
      left: rect.right + window.scrollX,
    };
  });


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

  getSvgColor(icon_name).then((color) => {
    glowColor = color;
  });

  // getSvgColor(icon_name).then((color) => {console.log("color: ", color)})
</script>

<div
  class="module-icon"
  {onclick}
  onkeydown={onclick}
  role="button"
  tabindex="0"
  bind:this={iconElement}
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
</div>

<style>
  .module-icon {
    /* width: 4rem; */
    /* margin: 0.2rem 0rem; */
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    border-radius: 0.3rem;
  }

  .icon {
    margin: 0.1rem 0rem;
    margin-left: 0.8rem;
    margin-right: 0.3rem;
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
    /* background-color: var(--hover-heading-color); */
  }
</style>
