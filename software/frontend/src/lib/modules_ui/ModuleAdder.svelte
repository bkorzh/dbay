<script>
    import SubmitButton from "../buttons/SubmitButton.svelte";
    import GeneralButton from "../buttons/GeneralButton.svelte";
    import { ui_state } from "../../state/uiState.svelte";
    import {initializeModule} from "../../api";
    import { system_state } from "../../state/systemState.svelte";
    import { updateSystemStatefromJson } from "../modules_dbay/index.svelte";
    import CaretIcon from "../buttons/CaretIcon.svelte";

    let selectedSlot = "";
    let selectedType = "";

    async function initialize() {
        // console.log("submit button clicked");
        const response = await initializeModule(Number(selectedSlot), selectedType)
        updateSystemStatefromJson(response)
        selectedSlot = "";
        selectedType = "";
    }

    function finish_adding_modules() {
        // uiStateStore.update((state) => {
        //     state.show_module_adder = false;
        //     return state;
        // });
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
        <!-- <div class="warning">Server not initialized. Add a module:</div> -->
        <div
            style="display: flex; flex-direction: column; justify-content: space-between;"
        >   
        <div class="select-wrapper">
            <select bind:value={selectedSlot} style="height: 2.6rem; width: 100%">
                <option value="" selected>Select module slot</option>
                <option value="0">Slot 1</option>
                <option value="1">Slot 2</option>
                <option value="2">Slot 3</option>
                <option value="3">Slot 4</option>
                <option value="4">Slot 5</option>
                <option value="5">Slot 6</option>
                <option value="6">Slot 7</option>
                <option value="7">Slot 8</option>
            </select>
            <CaretIcon />
        </div>
        <div class="select-wrapper">
            <select bind:value={selectedType} style="height: 2.6rem; width: 100%">
                <option value="" selected>Select module type</option>
                <option value="dac4D">dac4D: 4 ch. differential</option>
                <option value="dac16D">dac16D: 16 ch. differential </option>
            </select>
            <CaretIcon />
            </div>
        </div>
        <SubmitButton onclick={initialize}
            >Add Module</SubmitButton
        >
        <br>
        <GeneralButton onclick={finish_adding_modules}
            >Finish Adding Modules</GeneralButton>
    </div>
</div>

<style>
    
    .select-wrapper {
        position: relative; /* This makes it the positioned ancestor */
        display: inline-block;
        width: 100%;
    }

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
        /* flex-grow: 1;
        flex-shrink: 1; */
        background-color: var(--body-color);
        /* transform: scaleY(1);
        transition: all .5s ease-in-out; */
        user-select: none;
        display: flex;
        flex-direction: column;
        /* justify-content: space-between; */
        background-color: var(--body-color);
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

    select {
        -webkit-appearance: none; /* Remove default Safari styling */
        -moz-appearance: none; /* Remove default Firefox styling */
        appearance: none; /* Remove default styling for other browsers */
        background: none; /* Remove default background */
        margin-bottom: 1rem;
        padding: 0.5rem;
        border: 1.5px solid var(--inner-border-color);
        background-color: var(--display-color);
        color: var(--text-color);
    }

    /* .warning {
        color: red;
        margin-bottom: 1rem;
    } */
</style>
