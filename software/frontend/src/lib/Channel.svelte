<script lang="ts">
    import { ui_state } from "../state/uiState.svelte";
    // import { voltageStore } from "../stores/voltageStore"
    import Button from "./Button.svelte";
    import ChevButtonTop from "./ChevButtonTop.svelte";
    import ChevButtonBottom from "./ChevButtonBottom.svelte";
    import SubmitButton from "./SubmitButton.svelte";
    import GeneralButton from "./GeneralButton.svelte";
    import { get } from "svelte/store";
    import { requestChannelUpdate } from "../api";

    import type { VsourceChange } from "./addons/vsource/interface";

    import App from "../App.svelte";
    import { onMount } from "svelte";

    import { system_state } from "../state/systemState.svelte";
    import type { IModule } from "../state/systemState.svelte";

    import MenuSlotted from "./MenuSlotted.svelte";
    import MenuButton from "./MenuButton.svelte";

    import { dac4D } from "./modules_dbay/dac4D_data.svelte";

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

    let thousands = $state(0);
    let hundreds = $state(0);
    let tens = $state(0);
    let ones = $state(0);
    let sign = $state("+");

    let sign_temp = $state("+");

    let temp = $state([0, 0, 0, 0]);

    $effect(() => {
        console.log("temp: ", temp);
    });

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

    async function increment(index: number, value: number) {
        const scaling = [1, 0.1, 0.01, 0.001];
        const plus_minus = sign_temp === "+" ? 1 : -1;
        if (editing) {
            temp[index] += value * plus_minus;
            validateRefresh(temp);
            return;
        }
        let new_bias_voltage =
            Math.round((ch.bias_voltage + scaling[index] * value) * 1000) /
            1000;
        validateUpdateVoltage(new_bias_voltage);
    }

    function switchState() {
        updateChannel({ activated: !ch.activated });
    }

    function updatedPlusMinus() {
        if (editing) {
            sign_temp = sign_temp === "+" ? "-" : "+";
            return;
        }

        isPlusMinusPressed = true; //needed for the animation

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
        console.log(
            "sending: ",
            data.bias_voltage,
            "activated: ",
            data.activated,
        );
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
        biasVoltage2Digits(ch.bias_voltage);
    }

    function biasVoltage2DigitsTemp(bias_voltage: number) {
        const integer = Math.round(Math.abs(bias_voltage * 1000));
        temp[3] = integer % 10;
        temp[2] = Math.floor(integer / 10) % 10;
        temp[1] = Math.floor(integer / 100) % 10;
        temp[0] = Math.floor(integer / 1000) % 10;
        sign_temp = bias_voltage < 0 ? "-" : "+";
    }

    function biasVoltage2Digits(bias_voltage: number) {
        const integer = Math.round(Math.abs(bias_voltage * 1000));
        thousands = integer % 10;
        hundreds = Math.floor(integer / 10) % 10;
        tens = Math.floor(integer / 100) % 10;
        ones = Math.floor(integer / 1000) % 10;
        sign = bias_voltage < 0 ? "-" : "+";

        temp[3] = thousands;
        temp[2] = hundreds;
        temp[1] = tens;
        temp[0] = ones;
        sign_temp = sign;
    }

    let toggle_up = $state(false);
    let toggle_down = $state(true);

    // let alter = false;
    let visible = $state(true);
    let no_border = $state(false);

    let editing = $state(false);

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

    function validateRefresh(temp) {
        const v =
            (temp[3] * 0.001 + temp[2] * 0.01 + temp[1] * 0.1 + temp[0]) *
            (sign_temp === "+" ? 1 : -1);
        biasVoltage2DigitsTemp(v);
    }

    function handleSubmitButtonClick() {
        const submitted_voltage = parseFloat(
            `${sign_temp}${temp[0]}.${temp[1]}${temp[2]}${temp[3]}`,
        );

        validateUpdateVoltage(submitted_voltage);

        editing = false;
        focusing = false;
        isPlusMinusPressed = true;
        setTimeout(() => {
            isPlusMinusPressed = false;
        }, 1);
    }
    function handleInputKeyDown(event: any) {
        if (event.key === "Enter") {
            handleSubmitButtonClick();
        }
    }

    let ones_el = $state();
    let tens_el = $state();
    let hundreds_el = $state();
    let thousands_el = $state();
    let focusing = $state(false);
    let submit_button = $state();

    let inputs = $derived([
        ones_el,
        tens_el,
        hundreds_el,
        thousands_el,
    ]) as HTMLInputElement[];
    let input_values = $derived([temp[0], temp[1], temp[2], temp[3]]);

    function handleDisplayInput(event, index) {
        if (isNaN(event.target.value) || event.target.value.includes(".")) {
            event.preventDefault();
            event.target.value = ""; // Clear the input if the value is not a number
        } else if (event.target.value.length > 0) {
            if (index < inputs.length - 1) {
                inputs[index + 1].value = ""; // Move the extra digit to the next input
                inputs[index + 1].focus();
            } else {
                // this is for allowing the last input to change its single digit
                // if another digit is entered before "Enter"
                inputs[index].value =
                    event.target.value[event.target.value.length - 1];
                temp[3] = parseFloat(
                    inputs[index].value[event.target.value.length - 1],
                );
            }
        }
    }

    function handleKeydown(event, index) {
        var key = event.charCode ? event.charCode : event.keyCode;
        // for any key other than 0-9, prevent the default action
        if (key < 48 || key > 57) {
            event.preventDefault();
        }
        if (
            event.key === "Backspace" &&
            event.target.value === "" &&
            index > 0
        ) {
            if (index + 1 < inputs.length) {
                inputs[index + 1].value = ""; // Clear the next input
            }
            inputs[index - 1].focus();
        }
        if (event.key === "Enter" && index === inputs.length - 1) {
            event.target.blur();
            handleSubmitButtonClick();
        }
    }

    function inputFocus(event, index) {
        if (!isNaN(index)) {
            inputs[index].focus();
        }
        event.target.value = "";
        focusing = true;
        editing = true;
    }

    function inputBlur(event, index) {
        focusing = false;
        event.target.value = input_values[index];
    }

    function exitEditing() {
        temp[0] = ones;
        temp[1] = tens;
        temp[2] = hundreds;
        temp[3] = thousands;
        sign_temp = sign;
        editing = false;
    }
</script>

<div class="bound-box">
    <!-- notice how I use class:no_border here -->
    <div class="strip" class:animated={ch.measuring}></div>
    <div class="top-bar" class:no_border>
        <div class="top-left">
            <h1 class="heading">{index}</h1>
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
            {#if !visible}
            <div class="heading-voltage" class:digit-off={st.colorMode}>{(ch.bias_voltage).toFixed(3)}</div>
            {/if}
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
                    viewBox="0 -3 16 16"
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
                <div
                    class="plus-minus"
                    class:digit-off={st.colorMode}
                    class:digit-edit={editing}
                    role="button"
                    tabindex="0"
                    onclick={updatedPlusMinus}
                    onkeydown={updatedPlusMinus}
                >
                    {sign_temp}
                </div>
                <div class="controls">
                    <div class="buttons-top">
                        <ChevButtonTop onclick={() => increment(0, 1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonTop onclick={() => increment(1, 1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonTop onclick={() => increment(2, 1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonTop onclick={() => increment(3, 1)} />
                    </div>

                    <div
                        class="display {isPlusMinusPressed ? 'updating' : ''}"
                        class:display-focus={editing}
                        role="button"
                        tabindex="-1"
                    >
                        <input
                            class="digit"
                            type="number"
                            class:digit-off={st.colorMode}
                            class:digit-edit={editing}
                            bind:value={temp[0]}
                            oninput={(e) => handleDisplayInput(e, 0)}
                            onkeydown={(e) => handleKeydown(e, 0)}
                            onfocus={inputFocus}
                            onblur={(e) => inputBlur(e, 0)}
                            bind:this={ones_el}
                            tabindex="-1"
                            maxlength="1"
                        />
                        <div
                            class="short-spacer"
                            onclick={(e) => inputFocus(e, 0)}
                            onkeydown={(e) => inputFocus(e, 0)}
                            role="button"
                            tabindex="-1"
                        ></div>
                        <div
                            class="digit dot"
                            onclick={(e) => inputFocus(e, 0)}
                            onkeydown={(e) => inputFocus(e, 0)}
                            role="button"
                            tabindex="-1"
                            class:digit-off={st.colorMode}
                            class:digit-edit={editing}
                        >
                            .
                        </div>
                        <div
                            class="short-spacer"
                            onclick={(e) => inputFocus(e, 1)}
                            onkeydown={(e) => inputFocus(e, 1)}
                            role="button"
                            tabindex="-1"
                        ></div>
                        <input
                            class="digit"
                            type="number"
                            class:digit-off={st.colorMode}
                            class:digit-edit={editing}
                            bind:value={temp[1]}
                            oninput={(e) => handleDisplayInput(e, 1)}
                            onkeydown={(e) => handleKeydown(e, 1)}
                            onfocus={inputFocus}
                            onblur={(e) => inputBlur(e, 1)}
                            bind:this={tens_el}
                            tabindex="-1"
                            maxlength="1"
                        />
                        <div
                            class="spacer"
                            onclick={(e) => inputFocus(e, 1)}
                            onkeydown={(e) => inputFocus(e, 1)}
                            role="button"
                            tabindex="-1"
                        ></div>
                        <input
                            class="digit"
                            type="number"
                            class:digit-off={st.colorMode}
                            class:digit-edit={editing}
                            bind:value={temp[2]}
                            oninput={(e) => handleDisplayInput(e, 2)}
                            onkeydown={(e) => handleKeydown(e, 2)}
                            onfocus={inputFocus}
                            onblur={(e) => inputBlur(e, 2)}
                            bind:this={hundreds_el}
                            tabindex="-1"
                            maxlength="1"
                        />
                        <div
                            class="spacer"
                            onclick={(e) => inputFocus(e, 2)}
                            onkeydown={(e) => inputFocus(e, 2)}
                            role="button"
                            tabindex="-1"
                        ></div>
                        <input
                            class="digit"
                            type="number"
                            class:digit-off={st.colorMode}
                            class:digit-edit={editing}
                            bind:value={temp[3]}
                            oninput={(e) => handleDisplayInput(e, 3)}
                            onkeydown={(e) => handleKeydown(e, 3)}
                            onfocus={inputFocus}
                            onblur={(e) => inputBlur(e, 3)}
                            bind:this={thousands_el}
                            tabindex="-1"
                            maxlength="1"
                        />
                    </div>

                    <div class="buttons-bottom">
                        <ChevButtonBottom onclick={() => increment(0, -1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonBottom onclick={() => increment(1, -1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonBottom onclick={() => increment(2, -1)} />
                        <div class="spacer-chev"></div>
                        <ChevButtonBottom onclick={() => increment(3, -1)} />
                    </div>
                </div>
                <div class="voltage">V</div>
            </div>
            {#if editing}
                <div class="right-editing">
                    <SubmitButton
                        onclick={handleSubmitButtonClick}
                        bind:this={submit_button}>Submit</SubmitButton
                    >

                    <GeneralButton onclick={exitEditing}>Cancel</GeneralButton>
                    <!-- <input
                    type="number"
                    bind:this={inputRef}
                    onkeydown={handleInputKeyDown}
                /> -->
                </div>
            {:else}
                <div class="right">
                    <Button onclick={switchState} redGreen={st.colorMode}
                        >{st.action_string}</Button
                    >
                </div>
            {/if}
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

    .heading-voltage {
        color: var(--digits-color);
        font-size: 1.5rem;
        letter-spacing: 0.58rem;
        /* padding: 0.3rem 0.5rem; */
        /* margin: 0;
        margin-top: 0.2rem; */
        /* margin-bottom: auto; */
        /* opacity: 0.5; */
        font-family: "Roboto Flex", sans-serif;
        font-weight: 300;
        margin: auto;
        margin-left: 0;
        margin-right: 3rem;
    }

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
        /* justify-content: start; */
        align-items: flex-end;
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
        font-size: 1.5rem;
        letter-spacing: 0rem;
        /* padding: 0.7rem 0.0rem; */
        /* margin: 0; */
        padding-right: 0rem;
        /* margin-bottom: -18px; */
        height: 78%;
        padding-right: 0rem;
        margin: auto;
        margin-left: 0.5rem;

        padding-top: 0.3rem;
        color: var(--digits-color);
        background-color: var(--heading-color);
        border: 1.5px solid var(--heading-color);
        /* justify-content: left;
        text-align: left; */
        width: 80%;
        /* padding: 0; */
        /* height: 80%; */
        /* padding: 0.0rem 0.5rem; */
        /* padding: 0; */
    }

    .heading {
        margin-right: 0rem;
        margin-top: 0.25rem;
        margin-bottom: auto;
        padding: 0rem 0rem;
        padding-right: 0.8rem;
        padding-bottom: 0.25rem;
        opacity: 0.5;
        font-size: 1.5rem;
        color: var(--text-color);
    }

    input {
        background-color: transparent;
        border-radius: 4px;
        border: 1.5px solid var(--value-border-color);
        padding: 0rem 0.3rem;
        font-family: "Roboto Flex", sans-serif;
        font-weight: 300;
        font-size: 1.7rem;
        letter-spacing: 0.58rem;
        color: var(--digits-color);
        /* transition: background-color 0.1s ease-in-out; */
    }

    /* Deactivate the chevrons that appear on input type=number */
    input[type="number"]::-webkit-inner-spin-button,
    input[type="number"]::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

    input[type="number"] {
        -moz-appearance: textfield;
    }
    input:focus {
        outline: none;
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
        width: 2rem;
        font-size: 1.5rem;
        color: var(--digits-color);
        font-family: "Roboto Flex", sans-serif;
        font-weight: 300;
        font-size: 1.7rem;
        opacity: var(--state_opacity);
        border: none;
        text-align: center;
        letter-spacing: 0;
        margin-left: 0;
        margin-right: 0;
        background-color: none;
    }

    .digit-off {
        color: var(--digits-deactivated-color);
    }


    .digit-edit {
        color: var(--edit-blue);
        font-weight: 400;
    }

    .dot {
        margin-left: -0.7rem;
        margin-right: -0.7rem;
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
        /* padding: 0rem 0.44rem; */
        transition: background-color 0.1s ease-in-out;
        /* margin: -0.5rem 0rem; */
        background-color: var(--display-color);
    }

    .display-focus {
        background-color: var(--heading-color);
        border: 1.5px solid var(--outer-border-color);
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
        /* this is needed because we have
        input elements inside the area that gets
        the shimmer effect from this pseudo-element */
        pointer-events: none;
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
        /* cursor: pointer; */
        background-color: var(--hover-body-color);
    }

    .left {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        padding: 0.3rem 0rem;
        padding-left: 1rem;

        /* flex: 10; */
        /* padding-right: 13px; */
    }

    .right-editing {
        display: flex;
        flex-direction: column;
        justify-content: space-evenly;
        padding: 1rem 1rem;
        padding-right: 0.2rem;
        margin-right: 0.5rem;
        width: 45%;
        /* padding-right: 13px; */
    }

    .right {
        display: flex;
        flex-direction: column;
        justify-content: space-evenly;
        padding: 1rem 1rem;
        padding-right: 0.2rem;
        margin-right: 0.5rem;
        width: 45%;
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
        /* box-shadow: 0 0 7px rgba(0, 0, 0, 0.05); */
        /* border: 1.3px solid var(--outer-border-color); */
        border-left: 1.3px solid var(--outer-border-color);
        border-right: 1.3px solid var(--outer-border-color);
        border-bottom: 1.3px solid var(--divider-border-color);
        /* margin: 0.2rem 0rem; */
    }
    .top-bar {
        display: flex;
        /* position: relative; */
        flex-direction: row;
        background-color: var(--heading-color);
        border-bottom: 1.3px solid var(--inner-border-color);
        justify-content: space-between;
        /* align-items: start; */
        padding: 0rem 1rem;
        padding-bottom: 0rem;
        padding-right: 0px;
        /* box-shadow: 0 5px 7px rgba(0, 0, 0, 0.5); */
    }

    /* .top-bar::after {
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: -12px;
        height: 12px;
        background: linear-gradient(rgba(0, 0, 0, 0.05), transparent);
    } */

    .dot-menu {
        margin: 0px 3px;
        padding: 0px 5px;
        padding-top: 0.1rem;
        margin-bottom: 0.25rem;
        /* padding-bottom: -10rem; */
        color: var(--icon-color);
        border-radius: 5px;
    }

    .dot-menu:hover {
        /* cursor: pointer; */
        background-color: var(--hover-heading-color);
    }

    .chevron {
        margin: auto;
        margin-bottom: 0rem;
        margin-top: 0rem;
        margin-right: 0.25rem;
        padding: 0px 5px;
        /* padding-bottom: 1rem; */
        padding-top: 0rem;
        border-radius: 5px;
        /* margin-top: 0.01rem;
        padding-top: 0.2rem; */

        color: var(--icon-color);
    }

    .chevron:focus {
        outline: none;
    }

    .chevron:hover {
        /* cursor: pointer; */
        background-color: var(--hover-heading-color);
    }

    .main-controlls {
        /* flex-grow: 1;
        flex-shrink: 1; */
        background-color: var(--body-color);
        /* transform: scaleY(1);
        transition: all .5s ease-in-out; */
        /* user-select: none; */
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
