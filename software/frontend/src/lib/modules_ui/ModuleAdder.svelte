<script>
    import SubmitButton from "../SubmitButton.svelte";
    import GeneralButton from "../GeneralButton.svelte";
    import { uiStateStore } from "../../state/uiState";
    import {initializeModule} from "../../api";
    import { voltageStore } from "../../state/systemState";

    let selectedSlot = "";
    let selectedType = "";

    async function initialize() {
        console.log("submit button clicked");
        const response = await initializeModule(Number(selectedSlot), selectedType)
        voltageStore.set(response);
        selectedSlot = "";
        selectedType = "";
    }

    function finish_adding_modules() {
        uiStateStore.update((state) => {
            state.show_module_adder = false;
            return state;
        });
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
            <select bind:value={selectedSlot} style="height: 2.6rem; width: 100%">
                <option value="" selected>Select module slot</option>
                <option value="1">Slot 1</option>
                <option value="2">Slot 2</option>
                <option value="3">Slot 3</option>
                <option value="4">Slot 4</option>
                <option value="5">Slot 5</option>
                <option value="6">Slot 6</option>
                <option value="7">Slot 7</option>
                <option value="8">Slot 8</option>
            </select>
            <select bind:value={selectedType} style="height: 2.6rem; width: 100%">
                <option value="" selected>Select module type</option>
                <option value="1">4 Ch. Triax</option>
                <option value="1">16 Ch. Micro Coax (not implemented yet)</option>
            </select>
        </div>
        <SubmitButton {uiStateStore} on:submit={initialize}
            >Add Module</SubmitButton
        >
        <br>
        <GeneralButton {uiStateStore} on:submit={finish_adding_modules}
            >Finish Adding Modules</GeneralButton>
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
        /* margin: 0.5rem; */
        margin-bottom: 1rem;
        border: 1.5px solid var(--inner-border-color);
        background-color: var(--display-color);
        color: var(--text-color);
    }

    /* .warning {
        color: red;
        margin-bottom: 1rem;
    } */
</style>
