<script lang="ts">
  import { DropdownMenu } from "bits-ui";
  import LightDarkToggleFG from "./buttons/LightDarkToggleFG.svelte";
  import Hamburger from "./buttons/Hamburger.svelte";
  import { ui_state } from "../state/uiState.svelte";
  import MenuButton from "./buttons/MenuButton.svelte";
  import Button from "./buttons/Button.svelte";
  import {
    system_state,
    switch_on_off_system,
  } from "../state/systemState.svelte";

  let showDropdown = $state(false);

  async function allOn() {
    switch_on_off_system(system_state, true);
  }

  async function allOff() {
    switch_on_off_system(system_state, false);
  }

  function addModule() {
    ui_state.show_module_adder = true;
  }

  function showSourceReInit() {
    ui_state.show_source_reinit = !ui_state.show_source_reinit;
  }

  function showRemoteAccess() {
    ui_state.show_remote_access = true;
  }
</script>

<div class="bound-box">
  <div class="top-bar">
    <h1 class="heading">Device Bay Electronics System</h1>
    <LightDarkToggleFG />
    <DropdownMenu.Root bind:open={showDropdown}>
      <DropdownMenu.Trigger>
        {#snippet child({ props }: { props: Record<string, unknown> })}
          <Hamburger triggerProps={props} ariaLabel="System actions" />
        {/snippet}
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content side="bottom" align="end" sideOffset={6}>
          {#snippet child({ wrapperProps, props }: { wrapperProps: Record<string, unknown>; props: Record<string, unknown> })}
            <div {...wrapperProps}>
              <div {...props} class="dropdown-content">
                <MenuButton onclick={addModule}>Add a Module</MenuButton>
                <MenuButton onclick={showSourceReInit}>Re-Initialize Source</MenuButton>
                <MenuButton onclick={showRemoteAccess}>Remote Access</MenuButton>
              </div>
            </div>
          {/snippet}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  </div>

  <div class="button-bar">
    <Button redGreen={true} onclick={allOn}>All On</Button>
    <Button redGreen={false} onclick={allOff}>All Off</Button>
  </div>
</div>

<style>
  .bound-box {
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 0 7px rgba(0, 0, 0, 0.05);
    border: 1.3px solid var(--outer-border-color);
  }
  .top-bar {
    display: flex;

    flex-direction: row;
    background-color: var(--module-header-color);
    border-bottom: 1.3px solid var(--inner-border-color);
  }

  .dropdown-content {
    min-width: 15rem;
    overflow: hidden;
    border: 1.3px solid var(--outer-border-color);
    border-radius: 0.5rem;
    background-color: var(--body-color);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.09);
    padding: 0.2rem;
    outline: none;
    z-index: 1000;
  }

  .button-bar {
    flex-grow: 1;
    background-color: var(--body-color);
    padding: 1rem;
  }

  /* .bg-red-990 {
    background-color: #321818;

  } */

  /* .bg-cyan-990 {
    background-color: #183232;
  } */

  .heading {
    font-size: 1.3rem;
    margin-right: auto;
    margin-top: auto;
    margin-bottom: auto;

    padding-left: 8px;
    padding-right: 13px;
    padding-top: 5px;
    padding-bottom: 5px;
    color: var(--module-icon-color);
  }

  @media (min-width: 460px) {
    .bound-box {
      margin: 5px 20px 5px 5px;
    }
  }

  @media (max-width: 460px) {
    .bound-box {
      margin: 5px 5px 5px 5px;
    }
  }
</style>
