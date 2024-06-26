<!-- <script lang="ts" context="module">
    import "../app.css";
    export let activated;
</script> -->

<script lang="ts">
    import { ui_state } from "../../state/uiState.svelte";
    // import { voltageStore } from "../stores/voltageStore"
    import Button from "../Button.svelte";
    import ChevButtonTop from "../ChevButtonTop.svelte";
    import ChevButtonBottom from "../ChevButtonBottom.svelte";
    import SubmitButton from "../SubmitButton.svelte";
    import { get } from "svelte/store";
    // import { voltageStore } from "../stores/voltageStore";
    import { requestChannelUpdate } from "../../api";

    import type { VsourceChange } from "../addons/vsource/interface";

    import App from "../../App.svelte";
    import { onMount } from "svelte";

    import { system_state } from "../../state/systemState.svelte";
    import type { IModule } from "../../state/systemState.svelte";

    import MenuSlotted from "../MenuSlotted.svelte";
    import MenuButton from "../MenuButton.svelte";

    import { dac4D } from "../modules_dbay/dac4D_data.svelte";

    interface Props {
        index: number;
        module_index: number;
    }

    let { index, module_index }: Props = $props();

    // if this component is mounted, then the vsource addon should exist
    let dac4d = system_state.data[module_index - 1] as dac4D;
    let ch = dac4d.vsource.channels[index - 1];

    let dotMenu: HTMLElement;
    let menuLocation = $state({ top: 0, left: 0 });
    let immediate_text: string = $state("");
    let integer = $derived(Math.round(Math.abs(ch.bias_voltage * 1000)));
    let thousands = $derived(integer % 10);
    let hundreds = $derived(Math.floor(integer / 10) % 10);
    let tens = $derived(Math.floor(integer / 100) % 10);
    let ones = $derived(Math.floor(integer / 1000) % 10);
    let sign = $derived(ch.bias_voltage < 0 ? "-" : "+");

    // $effect(() => {
    //     console.log("ch.measuring: ", ch.measuring);
    // });

    let st = $derived(
        ch.activated
            ? {
                  action_string: "Turn Off",
                  colorMode: false,
                  opacity: 1,
              }
            : {
                  action_string: "Turn On",
                  colorMode: true,
                  opacity: 0.2,
              },
    );

    let showDropdown = $state(false);
    function toggleMenu() {
        showDropdown = !showDropdown;
        const rect = dotMenu.getBoundingClientRect();
        menuLocation = {
            top: rect.top + window.scrollY,
            left: rect.right + window.scrollX,
        };
        // console.log("menuLocation: ", menuLocation);
    }

    async function validateUpdateVoltage(voltage: number) {
        if (voltage >= 5) {
            voltage = 5;
        }
        if (voltage <= -5) {
            voltage = -5;
        }
        updateChannel({ voltage: voltage });
    }

    async function increment(value: number) {
        let new_bias_voltage = ch.bias_voltage + value;
        validateUpdateVoltage(new_bias_voltage);
    }

    function switchState() {
        updateChannel({ activated: !ch.activated });
    }

    function switchMeasurementMode() {
        updateChannel({ measuring: !ch.measuring });
    }

    function updatedPlusMinus() {
        isPlusMinusPressed = true;

        updateChannel({ voltage: -ch.bias_voltage });

        setTimeout(() => {
            isPlusMinusPressed = false;
        }, 1);
    }

    async function updateChannel({
        voltage = ch.bias_voltage,
        activated = ch.activated,
        heading_text = ch.heading_text,
        index = ch.index,
        measuring = ch.measuring,
    } = {}) {
        const data: VsourceChange = {
            module_index,
            bias_voltage: voltage,
            activated,
            heading_text,
            index,
            measuring,
        };
        if (system_state.valid) {
            const returnData = await requestChannelUpdate(data);

            ch.activated = returnData.activated;
            ch.bias_voltage = returnData.bias_voltage;
            ch.heading_text = returnData.heading_text;
            ch.measuring = returnData.measuring;
        } else {
            ch.activated = data.activated;
            ch.bias_voltage = data.bias_voltage;
            ch.heading_text = data.heading_text;
            ch.measuring = data.measuring;
        }
    }

    let toggle_up = $state(false);
    let toggle_down = $state(true);

    // let alter = false;
    let visible = $state(true);
    let no_border = $state(false);

    function togglerRotateState() {
        toggle_up = !toggle_up;
        toggle_down = !toggle_down;
        // alter = !alter;
        visible = !visible;
        no_border = !no_border;
    }

    let input_value = "";
    let isPlusMinusPressed = $state(false);

    let isMounted = false;
    let updateComplete = false; //
    let heading_editing = false;

    onMount(() => {
        isMounted = true;
        const rect = dotMenu.getBoundingClientRect();
        menuLocation = {
            top: rect.top + window.scrollY,
            left: rect.right + window.scrollX,
        };
    });

    let isEditing = false;

    function handleInput(event: Event) {
        let target = event.target as HTMLInputElement;
        immediate_text = target.value;
    }

    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === "Enter") {
            isEditing = false;
            updateChannel({ heading_text: immediate_text });
        }
    }

    let inputRef: HTMLInputElement = $state();
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
    <div class="strip" class:animated={ch.measuring}></div>
    <div class="top-bar" class:no_border>
        <div class="top-left">
            <h1 class="heading">{index}</h1>
            <!-- {#if isEditing} -->
            <input
                class="heading-input"
                type="text"
                value={immediate_text}
                oninput={handleInput}
                onfocus={() => (heading_editing = true)}
                onblur={() => {
                    heading_editing = false;
                    updateChannel({ heading_text: immediate_text });
                }}
                onkeydown={handleKeyDown}
                tabindex="0"
            />
        </div>
        <div class="top-right">
            <div
                class="dot-menu"
                onclick={toggleMenu}
                onkeydown={toggleMenu}
                bind:this={dotMenu}
                role="button"
                tabindex="0"
            >
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
                <MenuSlotted
                    onClick={toggleMenu}
                    menuVisible={showDropdown}
                    location={menuLocation}
                >
                    <MenuButton
                        onclick={() => {
                            updateChannel({ measuring: !ch.measuring });
                            showDropdown = !showDropdown;
                        }}>Toggle Measurement Mode</MenuButton
                    >
                </MenuSlotted>
            {/if}

            <svg
                xmlns="http://www.w3.org/2000/svg"
                width="32"
                height="32"
                fill="currentColor"
                stroke="currentColor"
                class="chevron"
                class:toggle_up
                class:toggle_down
                viewBox="0 0 16 16"
                role="button"
                tabindex="0"
                onclick={togglerRotateState}
                onkeydown={togglerRotateState}
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
                <Button onclick={switchState} redGreen={st.colorMode}
                    >{st.action_string}</Button
                >
                <input
                    type="number"
                    bind:this={inputRef}
                    onkeydown={handleInputKeyDown}
                />
                <SubmitButton onclick={handleSubmitButtonClick}
                    >Submit</SubmitButton
                >
            </div>

            <div class="right">
                <div
                    class="plus-minus"
                    class:digit-off={st.colorMode}
                    role="button"
                    tabindex="0"
                    onclick={updatedPlusMinus}
                    onkeydown={updatedPlusMinus}
                >
                    {sign}
                </div>
                <div class="controls">
                    <div class="buttons-top">
                        <ChevButtonTop onclick={() => increment(1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonTop onclick={() => increment(0.1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonTop onclick={() => increment(0.01)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonTop onclick={() => increment(0.001)} />
                    </div>

                    <div class="display {isPlusMinusPressed ? 'updating' : ''}">
                        <!-- <div class="display updating"> -->
                        <div
                            class="digit"
                            class:digit-off={st.colorMode}
                        >
                            {ones}
                        </div>
                        <div class="short-spacer"></div>
                        <div
                            class="digit dot"
                            class:digit-off={st.colorMode}
                        >
                            .
                        </div>
                        <div class="short-spacer"></div>
                        <div
                            class="digit"
                            class:digit-off={st.colorMode}
                        >
                            {tens}
                        </div>
                        <div class="spacer"></div>
                        <div
                            class="digit"
                            class:digit-off={st.colorMode}
                        >
                            {hundreds}
                        </div>
                        <div class="spacer"></div>
                        <div
                            class="digit"
                            class:digit-off={st.colorMode}
                        >
                            {thousands}
                        </div>
                    </div>

                    <div class="buttons-bottom">
                        <ChevButtonBottom onclick={() => increment(-1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonBottom onclick={() => increment(-0.1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonBottom onclick={() => increment(-0.01)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonBottom onclick={() => increment(-0.001)} />
                    </div>
                </div>
                <div class="voltage">V</div>
            </div>
        </div>
    {/if}
</div>

<style>
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
        padding-bottom: 0.2rem;
        opacity: 0.5;
        color: var(--text-color);
    }

    input {
        background-color: var(--display-color);
        border-radius: 4px;
        border: 1.5px solid var(--value-border-color);
        padding: 0rem 0.3rem;
        font-family: "Roboto Flex", sans-serif;
        font-weight: 300;
        font-size: 1.7rem;
        letter-spacing: 0.58rem;
        color: var(--digits-color);
        transition: background-color 0.1s ease-in-out;
    }

    /* Deactivate the chevrons that appear on input type=number */
    input[type='number']::-webkit-inner-spin-button,
    input[type='number']::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

    input[type='number'] {
        -moz-appearance: textfield;
    }

    .heading-input {
        color: var(--digits-color);
        background-color: var(--heading-color);
        border: 1.5px solid var(--heading-color);
        padding-bottom: 0.2rem;
    }

    .heading-input:hover {
        background-color: var(--hover-heading-color);
        border: 1.5px solid var(--inner-border-color);
    }

    .heading-input:focus {
        background-color: var(--hover-heading-color);
        border: 1.5px solid var(--inner-border-color);
    }

    .plus-minus {
        width: 18px;
        display: flex;
        justify-content: center;
        font-size: 1.5rem;
        color: var(--digits-color);
        font-family: "Roboto Flex", sans-serif;
        font-weight: 300;
        margin-top: auto;
        margin-bottom: auto;
        margin-left: 0.2rem;
        margin-right: 0.2rem;
        border-radius: 4px;
        /* opacity: var(--state_opacity); */
    }

    .digit {
        font-size: 1.5rem;
        color: var(--digits-color);
        font-family: "Roboto Flex", sans-serif;
        font-weight: 300;
        font-size: 1.7rem;
        opacity: var(--state_opacity);
    }

    .digit-off {
        color: var(--digits-deactivated-color);
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
        border: 1.5px solid var(--value-border-color);
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
        justify-content: space-around;
        padding: 1rem 1rem;
        padding-right: 0.2rem;
        margin-right: 0.5rem;
        width: 45%;
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
        padding: 0.0rem 1rem;
        padding-bottom: 0.2rem;
        padding-right: 0px;
    }

    .dot-menu {
        margin: 0px 3px;
        padding: 0px 5px;
        padding-top: 0.42rem;
        color: var(--icon-color);
        border-radius: 5px;
    }

    .dot-menu:hover {
        cursor: pointer;
        background-color: var(--hover-heading-color);
    }

    .chevron {
        margin: 0px 5px;
        padding: 0px 5px;
        padding-top: 0.0rem;
        border-radius: 5px;
        /* margin-top: 0.01rem;
        padding-top: 0.2rem; */
        
        color: var(--icon-color);
    }

    .chevron:focus {
        outline: none;
    }

    .chevron:hover {
        cursor: pointer;
        background-color: var(--hover-heading-color);
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


    .no_border {
        border: none;
    }

</style>
