<script lang="ts" context="module">
    import "../app.css";
    export let activated;
</script>

<script lang="ts">
    import { uiStateStore } from "../stores/uiStateStore";
    // import { voltageStore } from "../stores/voltageStore"
    import Button from "./Button.svelte";
    import ChevButtonTop from "./ChevButtonTop.svelte";
    import ChevButtonBottom from "./ChevButtonBottom.svelte";
    import SubmitButton from "./SubmitButton.svelte";
    import { get } from "svelte/store";
    // import { voltageStore } from "../stores/voltageStore";
    import { requestChannelUpdate } from "../api";
    import type { ChannelChange } from "../stores/voltageStore";
    import App from "../App.svelte";
    import { onMount } from "svelte";
    import { voltageStore } from "../stores/voltageStore";
    import MenuSlotted from "./MenuSlotted.svelte";
    import MenuButton from "./MenuButton.svelte";

    export let index; // index of the bias control
    export let module_index;

    let bias_voltage;
    let activated;
    let heading_text;
    let immediate_text;
    let heading_editing = false;
    let measuring = true;

    let dotMenu;
    let menuLocation = { top: 0, left: 0 };

    immediate_text = heading_text;

    

    let showDropdown = false;
    function toggleMenu() {
        showDropdown = !showDropdown;
        const rect = dotMenu.getBoundingClientRect();
        menuLocation = { 
            top: rect.top + window.scrollY, 
            left: rect.right + window.scrollX 
        };
        console.log("menuLocation: ", menuLocation);
    }

    async function validateUpdateVoltage(voltage) {
        if (voltage >= 5) {
            voltage = 5;
        }
        if (voltage <= -5) {
            voltage = -5;
        }
        const data: ChannelChange = {
            module_index,
            bias_voltage: voltage,
            activated,
            heading_text,
            index,
            measuring,
        };
        updateChannel(data);
    }

    //// grab and update
    async function increment(value) {
        // bias_voltage =
        //     get(voltageStore).data[module_index - 1][index - 1].bias_voltage;

        let new_bias_voltage = bias_voltage + value;
        validateUpdateVoltage(new_bias_voltage);
    }

    //// grab and update
    function switchState() {
        // const activation = get(voltageStore).data[module_index - 1][index - 1].activated;

        const data: ChannelChange = {
            module_index,
            bias_voltage,
            activated: !activated,
            heading_text,
            index,
            measuring,
        };
        updateChannel(data);
    }

    function switchMeasurementMode() {
        measuring = !measuring;
        const data: ChannelChange = {
            module_index,
            bias_voltage,
            activated,
            heading_text,
            index,
            measuring,
        };
        updateChannel(data);
    }

    function updatedPlusMinus() {
        isPlusMinusPressed = true;
        const data: ChannelChange = {
            module_index,
            bias_voltage: -bias_voltage,
            activated,
            heading_text,
            index,
            measuring,
        };
        updateChannel(data);

        setTimeout(() => {
            isPlusMinusPressed = false;
        }, 1);
    }

    async function updateChannel(data: ChannelChange) {
        const returnData = await requestChannelUpdate(data);

        voltageStore.update((full_state) => {
            full_state.data[module_index - 1].channels[index - 1].activated =
                returnData.activated;
            full_state.data[module_index - 1].channels[index - 1].bias_voltage =
                returnData.bias_voltage;
            full_state.data[module_index - 1].channels[index - 1].heading_text =
                returnData.heading_text;
            full_state.data[module_index - 1].channels[index - 1].measuring =
                returnData.measuring;
            return full_state;
        });
    }

    // export let updateChannel;

    // function onStateChange

    // immediate_text = heading_text;

    let st = {
        action_string: "Turn Off",
        colorMode: false,
        opacity: 1,
    };

    let toggle_up = false;
    let toggle_down = true;

    // let alter = false;
    let visible = true;
    let no_border = false;

    function togglerRotateState() {
        toggle_up = !toggle_up;
        toggle_down = !toggle_down;
        // alter = !alter;
        visible = !visible;
        no_border = !no_border;
    }

    let sign = "+";

    let input_value = "";
    let isPlusMinusPressed = false;

    let ones = 0,
        tens = 0,
        hundreds = 0,
        thousands = 0,
        integer = 0;

    let isMounted = false;
    let updateComplete = false; //

    onMount(() => {
    isMounted = true;
    const rect = dotMenu.getBoundingClientRect();
    menuLocation = { 
        top: rect.top + window.scrollY, 
        left: rect.right + window.scrollX 
    };
});

    voltageStore.subscribe((full_state) => {
        // update local state
        const mst = full_state.data[module_index - 1].channels[index - 1];
        bias_voltage = mst.bias_voltage;
        activated = mst.activated;
        heading_text = mst.heading_text;
        measuring = mst.measuring;
        if (!heading_editing) {
            immediate_text = heading_text;
        }

        // distribute effects
        ones = Math.floor(Math.abs(bias_voltage)) % 10;
        integer = Math.round(Math.abs(bias_voltage * 1000));
        thousands = integer % 10;
        hundreds = Math.floor(integer / 10) % 10;
        tens = Math.floor(integer / 100) % 10;
        ones = Math.floor(integer / 1000) % 10;
        sign = bias_voltage < 0 ? "-" : "+";
        if (activated) {
            st = {
                action_string: "Turn Off",
                colorMode: false,
                opacity: 1,
            };
        } else {
            st = {
                action_string: "Turn On",
                colorMode: true,
                opacity: 0.2,
            };
        }
    });


    let isEditing = false;

    function handleInput(event) {
        immediate_text = event.target.value;
    }

    function handleKeyDown(event) {
        if (event.key === "Enter") {
            isEditing = false;
            updateChannel({
                module_index,
                bias_voltage,
                activated,
                heading_text: immediate_text,
                index,
                measuring,
            });
        }
    }

    let inputRef;
    function handleSubmitButtonClick() {
        console.log("Input value: " + inputRef.value);
        let input = parseFloat(inputRef.value);
        if (isNaN(input)) {
            console.log("Input is not a number");
            return;
        } else {
            validateUpdateVoltage(input);
            inputRef.value = ""; // Clear the input element in the DOM
            isPlusMinusPressed = true;
            setTimeout(() => {
                isPlusMinusPressed = false;
            }, 1);
        }
    }
    function handleInputKeyDown(event) {
        if (event.key === "Enter") {
            handleSubmitButtonClick();
        }
    }
</script>

<div class="bound-box">
    <!-- notice how I use class:no_border here -->
    <div class="strip" class:animated={measuring}></div>
    <div class="top-bar" class:no_border>
        <div class="top-left">
            <h1 class="heading">{index}</h1>
            <!-- {#if isEditing} -->
            <input
                class="heading-input"
                type="text"
                value={immediate_text}
                on:input={handleInput}
                on:focus={() => (heading_editing = true)}
                on:blur={() => {
                    heading_editing = false;
                    updateChannel({
                        module_index,
                        bias_voltage,
                        activated,
                        heading_text: immediate_text,
                        index,
                        measuring,
                    });
                }}
                on:keydown={handleKeyDown}
                tabindex="0"
            />
            <!-- {:else}
                <h1
                    class="heading-label"
                    on:click={() => {isEditing = true}}
                    on:keydown={handleKeyDown}
                >
                    {immediate_text}
                </h1>
            {/if} -->
        </div>
        <div class="top-right">
            <div class="dot-menu" on:click={toggleMenu} on:keydown={toggleMenu} bind:this={dotMenu} role="button" tabindex="0">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="21"
                    height="21"
                    fill="currentColor"
                    stroke="currentColor"
                    class="bi bi-three-dots"
                    viewBox="0 0 16 16"
                >
                    <path
                        d="M3 9.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"
                        stroke-width="0.3"
                    />
                </svg>
            </div>
            <!-- here, class:something is a special svelte way of pointing to a class which may be toggled. It is a shorthand for class:something={something} -->
            <!-- where 'something' is both a boolean in javascript and a class -->
            {#if showDropdown}
                <MenuSlotted onClick={toggleMenu} menuVisible={showDropdown} location={menuLocation}>
                    <MenuButton on:click={switchMeasurementMode}>Toggle Measurement Mode</MenuButton>
                </MenuSlotted>
            {/if}

            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="23"
                height="23"
                fill="currentColor"
                stroke="currentColor"
                class="chevron"
                class:toggle_up
                class:toggle_down
                viewBox="0 0 16 16"
                role="button"
                tabindex="0"
                on:click={togglerRotateState}
                on:keydown={togglerRotateState}
            >
                <path
                    fill-rule="evenodd"
                    d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
                    stroke-width="0.8"
                />
            </svg>
        </div>
    </div>
    {#if visible}
        <div class="main-controlls">
            <div class="left">
                <Button
                    on:click={switchState}
                    redGreen={st.colorMode}
                    {uiStateStore}>{st.action_string}</Button
                >
                <input
                    type="number"
                    bind:this={inputRef}
                    on:keydown={handleInputKeyDown}
                />
                <SubmitButton {uiStateStore} on:submit={handleSubmitButtonClick}
                    >Submit</SubmitButton
                >
            </div>

            <div class="right">
                <div
                    class="plus-minus"
                    style="--state_opacity: {st.opacity}"
                    role="button"
                    tabindex="0"
                    on:click={updatedPlusMinus}
                    on:keydown={updatedPlusMinus}
                >
                    {sign}
                </div>
                <div class="controls">
                    <div class="buttons-top">
                        <ChevButtonTop on:click={() => increment(1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonTop on:click={() => increment(0.1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonTop on:click={() => increment(0.01)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonTop on:click={() => increment(0.001)} />
                    </div>

                    <div class="display {isPlusMinusPressed ? 'updating' : ''}">
                        <!-- <div class="display updating"> -->
                        <div
                            class="digit"
                            style="--state_opacity: {st.opacity}"
                        >
                            {ones}
                        </div>
                        <div class="short-spacer"></div>
                        <div
                            class="digit dot"
                            style="--state_opacity: {st.opacity}"
                        >
                            .
                        </div>
                        <div class="short-spacer"></div>
                        <div
                            class="digit"
                            style="--state_opacity: {st.opacity}"
                        >
                            {tens}
                        </div>
                        <div class="spacer"></div>
                        <div
                            class="digit"
                            style="--state_opacity: {st.opacity}"
                        >
                            {hundreds}
                        </div>
                        <div class="spacer"></div>
                        <div
                            class="digit"
                            style="--state_opacity: {st.opacity}"
                        >
                            {thousands}
                        </div>
                    </div>

                    <div class="buttons-bottom">
                        <ChevButtonBottom on:click={() => increment(-1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonBottom on:click={() => increment(-0.1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonBottom on:click={() => increment(-0.01)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonBottom on:click={() => increment(-0.001)} />
                    </div>
                </div>
                <div class="voltage">V</div>
            </div>
        </div>
    {/if}
</div>

<style>
    /* @import url('https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,wght@8..144,400;8..144,500&display=swap'); */
    /* @import url('https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz@8..144&display=swap'); */
    @import url("https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,wght@8..144,100;8..144,200;8..144,300;8..144,400;8..144,500;8..144,600;8..144,700&display=swap");


    @keyframes placeHolderShimmer {
        0% {
            background-position: -800px 0;
        }
        100% {
            background-position: 800px 0;
        }
    }
    /* .background-masker {
        background-color: #ab0000;
        position: absolute;
    } */

    .strip {
        background-color: var(--heading-color);
        position: relative;
        height: 2.5px;
    }

    .animated {
        animation-duration: 1.3s;
        animation-fill-mode: forwards;
        animation-iteration-count: infinite;
        animation-name: placeHolderShimmer;
        animation-timing-function: linear;
        background-color: #f6f7f8;
        background: linear-gradient(
            to right,
            var(--heading-color) 1%,
            var(--red-highlight) 40%,
            var(--heading-color) 80%
        );
        background-size: 800px 104px;
    }

    .top-left {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        /* padding: 5px 10px;
        padding-right: 13px; */
    }

    .top-right {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        /* padding: 5px 10px;
        padding-right: 13px; */
    }

    .heading-input {
        color: var(--text-color);
        font-size: 1.2rem;
        letter-spacing: 0rem;
        /* padding: 0.7rem 0.0rem; */
        padding-right: 2rem;
        /* padding: 0.0rem 0.5rem; */
        /* padding: 0; */
    }

    .heading {
        margin-right: auto;
        margin-top: auto;
        margin-bottom: auto;
        padding: 0rem 0rem;
        padding-right: 0.8rem;
        padding-bottom: 0.20rem;
        opacity: 0.5;
        color: var(--text-color);
    }

    /* .heading-label {
        min-width: 230px;
        padding-right: 0rem;
        padding: 0.01rem 0.5rem;
        border-radius: 0.2rem;
        border: 1.5px solid var(--heading-color);
    } */

    /* .heading-label:hover {
        background-color: var(--hover-heading-color);
        border: 1.5px solid var(--inner-border-color);
    } */

    input {
        background-color: var(--display-color);
        border-radius: 4px;
        border: 1.5px solid var(--inner-border-color);
        padding: 0rem 0.3rem;
        font-family: "Roboto Flex", sans-serif;
        font-weight: 300;
        font-size: 1.7rem;
        letter-spacing: 0.58rem;
        color: var(--digits-color);
        transition: background-color 0.1s ease-in-out;
    }

    .heading-input {
        color: var(--digits-color);
        background-color: var(--heading-color);
        border: 1.5px solid var(--heading-color);
        padding-bottom: 0.20rem;
    }

    .heading-input:hover {
        background-color: var(--hover-heading-color);
        border: 1.5px solid var(--inner-border-color);
    }

    .heading-input:focus {
        background-color: var(--hover-heading-color);
        border: 1.5px solid var(--inner-border-color);
    }

    .digit {
        font-size: 1.5rem;
        font-weight: 300;
        color: var(--digits-color);
        font-family: "Roboto Flex", sans-serif;
        font-weight: 300;
        font-size: 1.7rem;
        opacity: var(--state_opacity);
    }

    .dot {
        margin-left: -0.03rem;
        margin-right: -0.03rem;
    }

    /* .button-box {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin: 0.75rem;
    } */

    .display {
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        /* padding: 5px 10px;
        padding-right: 13px; */
        /* background-color: var(--display-color); */
        border-radius: 4px;
        border: 1.5px solid var(--inner-border-color);
        padding: 0rem 0.44rem;
        transition: background-color 0.1s ease-in-out;
        /* margin: -0.5rem 0rem; */
        background-color: var(--display-color);
    }

    .display:after {
        content: "";
        display: block;
        position: absolute;
        left: 0;
        top: 0;
        width: 0;
        padding-top: 300%;
        padding-left: 300%;
        margin-left: -20px !important;
        margin-top: -50%;
        opacity: 0;
        transition: all 0.4s;
        background: var(--digits-color);
    }

    .display.updating:after {
        padding: 0;
        margin: 0;
        opacity: 0.15;
        transition: 0s;
    }

    .spacer {
        width: 0.8rem;
    }

    .spacer-chev {
        width: 0.2rem;
    }

    .short-spacer {
        width: 0rem;
    }

    .buttons-top {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        /* margin-bottom: 0.2rem; */
        padding-bottom: 0.5rem;
    }

    .buttons-bottom {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        /* margin-top: 0.2rem; */
        padding-top: 0.5rem;
    }

    .controls {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        /* padding: 0.5rem 0.3rem;
        margin: 0.3rem 0.3rem; */
        /* padding: 10px 10px; */
        /* padding-right: 13px; */
    }

    .voltage {
        font-size: 1.5rem;
        font-weight: 300;
        color: var(--icon-color);
        font-family: "Roboto Flex", sans-serif;
        font-weight: 400;
        margin-top: auto;
        margin-bottom: auto;
        margin-left: 0.3rem;
        margin-right: 0.3rem;
    }

    .plus-minus {
        width: 18px;
        display: flex;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 300;
        color: var(--digits-color);
        font-family: "Roboto Flex", sans-serif;
        font-weight: 300;
        margin-top: auto;
        margin-bottom: auto;
        margin-left: 0.2rem;
        margin-right: 0.2rem;
        border-radius: 4px;
        opacity: var(--state_opacity);
    }

    .plus-minus:hover {
        cursor: pointer;
        background-color: var(--hover-body-color);
    }

    .right {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        padding: 1rem 1rem;
        padding-left: 0.2rem;

        /* flex: 10; */
        /* padding-right: 13px; */
    }

    .left {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 1rem 1rem;
        padding-right: 0.2rem;
        width: 46%;
        /* flex: 1; */
        /* padding-right: 13px; */
    }

    .toggle_up {
        transform: rotate(90deg);
        margin-top: 0.17rem;
        padding-top: 0.2rem;
        transition: transform 0.2s ease-in-out;
    }

    .toggle_down {
        transform: rotate(0);
        margin-top: 0.1rem;
        padding-top: 0.2rem;
        transition: transform 0.2s ease-in-out;
    }

    .chevron {
        /* margin-top: 0.01rem;
        padding-top: 0.2rem; */
        color: var(--icon-color);
    }

    .chevron:focus {
        outline: none;
    }

    .bound-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 0 7px rgba(0, 0, 0, 0.05);
        border: 1.3px solid var(--outer-border-color);
        margin: 0.2rem 0rem;
    }
    .top-bar {
        display: flex;
        flex-direction: row;
        background-color: var(--heading-color);
        border-bottom: 1.3px solid var(--inner-border-color);
        justify-content: space-between;
        padding: 0.2rem 1rem;
        padding-right: 13px;
    }

    .dot-menu {
        padding: 0px 12px;
        padding-top: 0.25rem;
        color: var(--icon-color);
    }

    .dot-menu:hover {
        cursor: pointer;
    }

    .main-controlls {
        /* flex-grow: 1;
        flex-shrink: 1; */
        background-color: var(--body-color);
        /* transform: scaleY(1);
        transition: all .5s ease-in-out; */
        user-select: none;
        display: flex;
        flex-direction: row;
        /* justify-content: space-between; */
        background-color: var(--body-color);
        transition: background-color 0.1s ease-in-out;
    }

    /* .alter {

        display: none;
    } */

    .no_border {
        border: none;
    }

    /* @media (min-width: 400px) {
        .bound-box {
            margin: 5px 20px 5px 5px;
        }
    }

    @media (max-width: 400px) {
        .bound-box {
            margin: 5px 5px 5px 5px;
        }
    } */
</style>
