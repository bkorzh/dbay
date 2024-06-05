<script lang="ts">
  import MenuButton from "./buttons/MenuButton.svelte";
  import ModuleChevron from "./buttons/ModuleChevron.svelte";
  import ModuleIcon from "./buttons/ModuleIcon.svelte";
  import { VisibleState } from "./buttons/module_chevron";
  import type { IModule } from "../state/systemState.svelte";
  import type { Snippet } from "svelte";
  import MenuSlotted from "./MenuSlotted.svelte";
  import { hexToRGBA } from "../util";


  interface Props {
    m: IModule;
    visible: VisibleState;
    rotateState: () => void;
    module_index: number;
    name: string;
    menu_buttons: Snippet;
    icon_name: string;
  }

  let { m, visible, rotateState, module_index, name, menu_buttons, icon_name }: Props =
    $props();

    let glowColor: string | null = $state("");

    let iconElement: HTMLElement
    let showDropdown = $state(false);
    let menuLocation = $state({ top: 0, left: 0 });
    // let dynamic_coor_name = $state("dynamic-color" + icon_name);

    let el; // reference to an element inside the component

    function toggleMenu() {
      console.log("toggleing")
      showDropdown = !showDropdown;
      const rect = iconElement.getBoundingClientRect();
      menuLocation = {
          top: rect.top + window.scrollY,
          left: rect.right + window.scrollX,
      };
      console.log("showDropdown: ", showDropdown)
      console.log("menuLocation: ", menuLocation)

    }

    $effect(() => {
      if (el) el.style.setProperty("--dynamic-color", hexToRGBA(glowColor, 0.07));
    });
</script>

<div bind:this={el} class="heading" class:closed={!visible}>
  <div class="left">
    <ModuleChevron bind:visible {rotateState}></ModuleChevron>
    <div class="identifier">M{module_index + 1}:</div>
    <div class="identifier">{name}</div>
  </div>
  <div class="right">
    <ModuleIcon
    {icon_name}
    onclick={toggleMenu}
    bind:iconElement
    bind:glowColor
  ></ModuleIcon>
  
  </div>

</div>

{#if showDropdown}
            <MenuSlotted
                onclick={toggleMenu}
                menuVisible={showDropdown}
                location={menuLocation}
            >
                {@render menu_buttons()}
            </MenuSlotted>
        {/if}

<style>

  .left {
    display: flex;
    flex-direction: row;
    align-items: center;
    padding-left: 0.4rem;
  }



  .right {
    
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-end;
  }

  .heading {
    display: flex;
    z-index: 1;
    overflow: hidden;
    position: relative;
    flex-direction: row;
    justify-content: space-between;
    /* justify-content: space-between; */
    background-color: var(--module-header-color);
    padding: 0.15rem;
    color: var(--text-color);
    font-size: 1.3rem;
    border: 1.3px solid var(--module-border-color);
    /* border-bottom: none; */
    border-top-left-radius: 0.4rem;
    border-top-right-radius: 0.4rem;
    
  }

  .heading::after {
    content: "";
    position: absolute;
    overflow: hidden;
    top: -180px;
    left: 210px;
    width: 150%;
    height: 190%;
    background: var(--dynamic-color);
    filter: blur(23px); 
    z-index: -1;
    transform: rotate(-48deg); 
    pointer-events: none; 
  }

  .identifier {
    margin-left: 10px;
    color: var(--module-icon-color);
    font-size: large;
  }

  .closed {
    border-bottom-left-radius: 0.4rem;
    border-bottom-right-radius: 0.4rem;
  }
</style>
