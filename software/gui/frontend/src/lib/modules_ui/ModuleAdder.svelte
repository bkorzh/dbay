<script lang="ts">
  import { DropdownMenu } from "bits-ui";
  import SubmitButton from "../buttons/SubmitButton.svelte";
  import GeneralButton from "../buttons/GeneralButton.svelte";
  import { ui_state } from "../../state/uiState.svelte";
  import { initializeModule } from "../../api";
  import { updateSystemStatefromJson } from "../modules_dbay/index.svelte";

  const dac4D_icon = "/assets/dac4D_icon.svg";
  const adc4D_icon = "/assets/adc4D_icon.svg";
  const dac16D_icon = "/assets/dac16D_icon.svg";

  let selectedSlot = $state("");
  let selectedType = $state("");

  const slots = [
    { value: "0", label: "Slot 1" },
    { value: "1", label: "Slot 2" },
    { value: "2", label: "Slot 3" },
    { value: "3", label: "Slot 4" },
    { value: "4", label: "Slot 5" },
    { value: "5", label: "Slot 6" },
    { value: "6", label: "Slot 7" },
    { value: "7", label: "Slot 8" },
  ];

  const moduleTypes = [
    {
      value: "dac4D",
      label: "dac4D",
      description: "4 ch. differential",
      icon: dac4D_icon,
    },
    {
      value: "adc4D",
      label: "adc4D",
      description: "5 ch. voltage sensing",
      icon: adc4D_icon,
    },
    {
      value: "dac16D",
      label: "dac16D",
      description: "16 ch. differential",
      icon: dac16D_icon,
    },
  ];

  let selectedSlotLabel = $derived(
    slots.find((s) => s.value === selectedSlot)?.label ?? "Select module slot"
  );
  let selectedTypeInfo = $derived(
    moduleTypes.find((m) => m.value === selectedType)
  );

  async function initialize() {
    const response = await initializeModule(Number(selectedSlot), selectedType);
    updateSystemStatefromJson(response);
    selectedSlot = "";
    selectedType = "";
  }

  function finish_adding_modules() {
    ui_state.show_module_adder = false;
  }
</script>

<div class="basic-block">
  <div class="top-bar">
    <div class="top-left">
      <h1 class="heading">Add a module</h1>
    </div>
  </div>
  <div class="main-controlls">
    <div class="selectors">
      <!-- Slot selector -->
      <DropdownMenu.Root>
        <DropdownMenu.Trigger>
          {#snippet child({ props }: { props: Record<string, unknown> })}
            <button {...props} class="dropdown-trigger">
              <span class="trigger-label">{selectedSlotLabel}</span>
              <svg class="caret" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path fill-rule="evenodd" d="M1.553 6.776a.5.5 0 0 1 .67-.223L8 9.44l5.776-2.888a.5.5 0 1 1 .448.894l-6 3a.5.5 0 0 1-.448 0l-6-3a.5.5 0 0 1-.223-.67z"/>
              </svg>
            </button>
          {/snippet}
        </DropdownMenu.Trigger>
        <DropdownMenu.Content sideOffset={4}>
          {#snippet child({ wrapperProps, props }: { wrapperProps: Record<string, unknown>; props: Record<string, unknown> })}
            <div {...wrapperProps}>
              <div {...props} class="dropdown-content">
                {#each slots as slot}
                  <DropdownMenu.Item onSelect={() => (selectedSlot = slot.value)}>
                    {#snippet child({ props: itemProps }: { props: Record<string, unknown> })}
                      <div
                        {...itemProps}
                        class="dropdown-item {selectedSlot === slot.value ? 'item-selected' : ''}"
                      >
                        {slot.label}
                      </div>
                    {/snippet}
                  </DropdownMenu.Item>
                {/each}
              </div>
            </div>
          {/snippet}
        </DropdownMenu.Content>
      </DropdownMenu.Root>

      <!-- Module type selector -->
      <DropdownMenu.Root>
        <DropdownMenu.Trigger>
          {#snippet child({ props }: { props: Record<string, unknown> })}
            <button {...props} class="dropdown-trigger">
              {#if selectedTypeInfo}
                <span class="trigger-type-selected">
                  <img src={selectedTypeInfo.icon} alt={selectedTypeInfo.label} class="trigger-icon" />
                  <span class="trigger-label">{selectedTypeInfo.label}</span>
                </span>
              {:else}
                <span class="trigger-label placeholder">Select module type</span>
              {/if}
              <svg class="caret" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path fill-rule="evenodd" d="M1.553 6.776a.5.5 0 0 1 .67-.223L8 9.44l5.776-2.888a.5.5 0 1 1 .448.894l-6 3a.5.5 0 0 1-.448 0l-6-3a.5.5 0 0 1-.223-.67z"/>
              </svg>
            </button>
          {/snippet}
        </DropdownMenu.Trigger>
        <DropdownMenu.Content sideOffset={4}>
          {#snippet child({ wrapperProps, props }: { wrapperProps: Record<string, unknown>; props: Record<string, unknown> })}
            <div {...wrapperProps}>
              <div {...props} class="dropdown-content">
                {#each moduleTypes as mod}
                  <DropdownMenu.Item onSelect={() => (selectedType = mod.value)}>
                    {#snippet child({ props: itemProps }: { props: Record<string, unknown> })}
                      <div
                        {...itemProps}
                        class="dropdown-item module-item {selectedType === mod.value ? 'item-selected' : ''}"
                      >
                        <img src={mod.icon} alt={mod.label} class="module-icon" />
                        <span class="module-info">
                          <span class="module-name">{mod.label}</span>
                          <span class="module-desc">{mod.description}</span>
                        </span>
                      </div>
                    {/snippet}
                  </DropdownMenu.Item>
                {/each}
              </div>
            </div>
          {/snippet}
        </DropdownMenu.Content>
      </DropdownMenu.Root>
    </div>

    <SubmitButton onclick={initialize}>Add Module</SubmitButton>
    <br />
    <GeneralButton onclick={finish_adding_modules}>Finish Adding Modules</GeneralButton>
  </div>
</div>

<style>
  .basic-block {
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 0 7px rgba(0, 0, 0, 0.05);
    border: 1.3px solid var(--outer-border-color);
    margin: 0.2rem 0rem;
  }

  @media (min-width: 460px) {
    .basic-block {
      margin: 5px 20px 5px 5px;
    }
  }

  @media (max-width: 460px) {
    .basic-block {
      margin: 5px 5px 5px 5px;
    }
  }

  .main-controlls {
    background-color: var(--body-color);
    user-select: none;
    display: flex;
    flex-direction: column;
    transition: background-color 0.1s ease-in-out;
    padding: 1rem;
  }

  .top-bar {
    display: flex;
    flex-direction: row;
    background-color: var(--heading-color);
    border-bottom: 1.3px solid var(--inner-border-color);
    justify-content: space-between;
    padding: 5px 10px;
    padding-right: 13px;
  }

  .selectors {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-bottom: 1rem;
  }

  /* Trigger button */
  .dropdown-trigger {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    height: 2.6rem;
    padding: 0 0.6rem 0 0.5rem;
    margin-bottom: 0.75rem;
    border: 1.5px solid var(--inner-border-color);
    border-radius: 0.55rem;
    background-color: var(--display-color);
    color: var(--text-color);
    cursor: pointer;
    text-align: left;
    font-size: 1rem;
    font-family: inherit;
    transition: border-color 0.15s ease, background-color 0.15s ease;
  }

  .dropdown-trigger:hover {
    border-color: var(--divider-border-color);
    background-color: var(--hover-body-color);
  }

  .trigger-label {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .trigger-type-selected {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    flex: 1;
    overflow: hidden;
  }

  .trigger-icon {
    width: 1.8rem;
    height: 1.8rem;
    flex-shrink: 0;
  }

  .caret {
    color: var(--icon-color);
    flex-shrink: 0;
    margin-left: 0.4rem;
  }

  /* Dropdown content */
  .dropdown-content {
    background-color: var(--display-color);
    border: 1.5px solid var(--outer-border-color);
    border-radius: 0.55rem;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.09);
    min-width: var(--bits-dropdown-menu-anchor-width);
    padding: 0.25rem 0;
    z-index: 1000;
    outline: none;
    overflow: hidden;
  }

  /* Items */
  .dropdown-item {
    display: flex;
    align-items: center;
    padding: 0.45rem 0.6rem;
    cursor: pointer;
    color: var(--text-color);
    font-size: 1rem;
    outline: none;
    transition: background-color 0.1s ease;
  }

  .dropdown-item:hover,
  .dropdown-item[data-highlighted] {
    background-color: var(--hover-body-color);
    color: var(--hl-text-color);
  }

  .dropdown-item.item-selected {
    color: var(--hl-text-color);
    background-color: var(--hover-heading-color);
  }

  /* Module type items */
  .module-item {
    padding: 0.35rem 0.6rem;
    gap: 0.5rem;
  }

  .module-icon {
    width: 2.5rem;
    height: 2.5rem;
    flex-shrink: 0;
  }

  .module-info {
    display: flex;
    flex-direction: column;
  }

  .module-name {
    font-size: 1rem;
    color: var(--hl-text-color);
    line-height: 1.2;
  }

  .module-desc {
    font-size: 0.9rem;
    color: var(--text-color);
    line-height: 1.2;
  }
</style>
