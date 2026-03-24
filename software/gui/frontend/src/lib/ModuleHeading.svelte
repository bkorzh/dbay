<script lang="ts">
  import { DropdownMenu } from "bits-ui";
  import ModuleChevron from "./buttons/ModuleChevron.svelte";
  import ModuleIcon from "./buttons/ModuleIcon.svelte";
  import { VisibleState } from "./buttons/module_chevron";
  import type { IModule } from "../state/systemState.svelte";
  import type { Snippet } from "svelte";
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
  let showDropdown = $state(false);

  let el: HTMLDivElement | null = null;

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
    <DropdownMenu.Root bind:open={showDropdown}>
      <DropdownMenu.Trigger>
        {#snippet child({ props }: { props: Record<string, unknown> })}
          <ModuleIcon
            {icon_name}
            bind:glowColor
            triggerProps={props}
            ariaLabel={`${name} actions`}
          />
        {/snippet}
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content side="bottom" align="end" sideOffset={8}>
          {#snippet child({ wrapperProps, props }: { wrapperProps: Record<string, unknown>; props: Record<string, unknown> })}
            <div {...wrapperProps}>
              <div {...props} class="dropdown-content">
                {@render menu_buttons()}
              </div>
            </div>
          {/snippet}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  </div>

</div>

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

  .dropdown-content {
    min-width: 14rem;
    overflow: hidden;
    border: 1.3px solid var(--outer-border-color);
    border-radius: 0.5rem;
    background-color: var(--body-color);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.09);
    padding: 0.2rem;
    outline: none;
    z-index: 1000;
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
