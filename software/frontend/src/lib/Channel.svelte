<script lang="ts">
    import { ui_state } from "../state/uiState.svelte";
    // import { voltageStore } from "../stores/voltageStore"
    import Button from "./buttons/Button.svelte";
    import ChevButtonTop from "./buttons/ChevButtonTop.svelte";
    import ChevButtonBottom from "./buttons/ChevButtonBottom.svelte";
    import SubmitButton from "./buttons/SubmitButton.svelte";
    import GeneralButton from "./buttons/GeneralButton.svelte";
    import { requestChannelUpdate } from "../api";

    import type {
        ChSourceState,
        VsourceChange,
    } from "./addons/vsource/interface";

    import { onMount } from "svelte";

    import { system_state } from "../state/systemState.svelte";
    import type { IModule } from "../state/systemState.svelte";

    import MenuSlotted from "./MenuSlotted.svelte";
    import MenuButton from "./buttons/MenuButton.svelte";

    import { dac4D } from "./modules_dbay/dac4D_data.svelte";
    import { ChSourceStateClass } from "./addons";
    import HorizontalDots from "./buttons/HorizontalDots.svelte";
    import ChannelChevron from "./buttons/ChannelChevron.svelte";
    import Display from "./Display.svelte";

    interface Props {
        ch: ChSourceStateClass;
        module_index: number;
        onChannelChange: (data: VsourceChange) => Promise<VsourceChange>;
        staticName?: boolean;
        borders?: boolean;
    }

    let {
        ch,
        module_index,
        onChannelChange,
        staticName = false,
        borders = true,
    }: Props = $props();

    // if this component is mounted, then the vsource addon should exist
    // let dac4d = system_state.data[module_index - 1] as dac4D;
    // let ch = dac4d.vsource.channels[index - 1];

    let dotMenu: HTMLElement;
    let menuLocation = $state({ top: 0, left: 0 });
    let immediate_text: string = $state(ch.heading_text);

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
        const plus_minus = ch.sign_temp === "+" ? 1 : -1;
        if (ch.editing) {
            ch.temp[index] += value * plus_minus;
            validateRefresh(ch.temp);
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
        if (ch.editing) {
            ch.sign_temp = ch.sign_temp === "+" ? "-" : "+";
            return;
        }

        ch.isPlusMinusPressed = true; //needed for the animation

        updateChannel({ voltage: -ch.bias_voltage });

        setTimeout(() => {
            ch.isPlusMinusPressed = false;
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
        const returnData = await onChannelChange(data);
        ch.setChannel(returnData);
    }

    function biasVoltage2DigitsTemp(bias_voltage: number) {
        const integer = Math.round(Math.abs(bias_voltage * 1000));
        ch.temp[3] = integer % 10;
        ch.temp[2] = Math.floor(integer / 10) % 10;
        ch.temp[1] = Math.floor(integer / 100) % 10;
        ch.temp[0] = Math.floor(integer / 1000) % 10;
        ch.sign_temp = bias_voltage < 0 ? "-" : "+";
    }

    // let alter = false;
    // let visible = $state(true);

    // let editing = $state(false);
    // let isHovering = $state(false);

    // let isPlusMinusPressed = $state(false);

    let isMounted = false;
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

    function validateRefresh(temp: number[]) {
        const v =
            (temp[3] * 0.001 + temp[2] * 0.01 + temp[1] * 0.1 + temp[0]) *
            (ch.sign_temp === "+" ? 1 : -1);
        biasVoltage2DigitsTemp(v);
    }

    function onSubmit() {
        const submitted_voltage = parseFloat(
            `${ch.sign_temp}${ch.temp[0]}.${ch.temp[1]}${ch.temp[2]}${ch.temp[3]}`,
        );

        validateUpdateVoltage(submitted_voltage);

        ch.editing = false;
        ch.focusing = false;
        ch.isPlusMinusPressed = true;
        setTimeout(() => {
            ch.isPlusMinusPressed = false;
        }, 1);
    }
    function handleInputKeyDown(event: any) {
        if (event.key === "Enter") {
            onSubmit();
        }
    }

    function exitEditing() {
        // edit the edit mode without changing the value. Return to the original bias voltage
        ch.temp[0] = ch.ones;
        ch.temp[1] = ch.tens;
        ch.temp[2] = ch.hundreds;
        ch.temp[3] = ch.thousands;
        ch.sign_temp = ch.sign;
        ch.editing = false;
    }

    function handleMouseEnter() {
        ch.isHovering = true;
    }

    function handleMouseLeave() {
        ch.isHovering = false;
    }

</script>

<div
    onmouseenter={handleMouseEnter}
    onmouseleave={handleMouseLeave}
    class="bound-box"
    class:borders
    role="region"
>
    <!-- notice how I use class:no_border here -->
    <!-- <div class="strip" class:animated={ch.measuring}></div> -->
    <div
        class="top-bar"
        class:animated={ch.measuring}
        class:no_border={!ch.visible}
    >
        <div class="top-left">
            {#if !staticName}
                <ChannelChevron
                    bind:down={ch.visible}
                    isHovering={ch.isHovering}
                    index={ch.index}
                ></ChannelChevron>
            {/if}
            <input
                class="heading-input"
                class:input-to-label={staticName}
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
                disabled={staticName}
            />
        </div>

        <div class="top-right">
            {#if !ch.visible}
                <div
                    class="heading-voltage"
                    class:digit-off={st.colorMode}
                    class:invalid={!ch.valid}
                >
                    {ch.bias_voltage.toFixed(3)}
                </div>
            {/if}
            <HorizontalDots
                onclick={toggleMenu}
                onkeydown={toggleMenu}
                bind:dotMenu
            ></HorizontalDots>
            <!-- here, class:something is a special svelte way of pointing to a class which may be toggled. It is a shorthand for class:something={something} -->
            <!-- where 'something' is both a boolean in javascript and a class -->
            {#if showDropdown}
                <MenuSlotted
                    onclick={toggleMenu}
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

            <!-- <ChannelChevron bind:down={visible}></ChannelChevron> -->
        </div>
    </div>
    {#if ch.visible}
        <div class="main-controlls">
            <div class="left">
                <div
                    class="plus-minus"
                    class:digit-off={st.colorMode}
                    class:digit-edit={ch.editing}
                    role="button"
                    tabindex="0"
                    onclick={updatedPlusMinus}
                    onkeydown={updatedPlusMinus}
                >
                    {ch.sign_temp}
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

                    <Display {ch} {onSubmit}></Display>

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
            {#if ch.editing}
                <div class="right-editing">
                    <SubmitButton onclick={onSubmit}
                        >Submit</SubmitButton
                    >
                    <GeneralButton onclick={exitEditing}>Cancel</GeneralButton>
                </div>
            {:else}
                <div class="right">
                    {#if ch.valid}
                        <Button onclick={switchState} redGreen={st.colorMode}
                            >{st.action_string}</Button
                        >
                    {:else}
                        <GeneralButton
                            onclick={(e) => {
                                ch.focusing = true;
                                ch.editing = true;
                            }}>Invalid</GeneralButton
                        >
                    {/if}
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
        color: var(--red-text);
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
        margin-right: 0.7rem;
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
        /* margin-bottom: 3rem; */
        padding-bottom: 0.15rem;
        /* height: 78%; */
        padding-right: 0rem;
        margin-top: 0.15rem;
        margin-bottom: 0.15rem;
        margin-left: 0.5rem;

        padding-top: 0.3rem;
        color: var(--digits-color);
        background-color: transparent;

        border: none;
        width: 75%;
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

    .input-to-label {
        margin-left: 0rem;
        color: var(--text-color);
        font-size: 1.5rem;
    }

    /* Deactivate the chevrons that appear on input type=number */
    /* input[type="number"]::-webkit-inner-spin-button,
    input[type="number"]::-webkit-outer-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }

    input[type="number"] {
        appearance: textfield;
        -moz-appearance: textfield;
    }
    input:focus {
        outline: none;
    } */

    .heading-input:hover {
        background-color: var(--hover-heading-color);
        /* border: 1.5px solid var(--inner-border-color); */
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

    .digit-off {
        color: var(--digits-deactivated-color);
    }

    /* .digit {
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
    } */

    /* 

    .invalid {
        color: rgba(0, 0, 0, 0);
    }

    .digit-edit {
        color: var(--edit-blue);
        font-weight: 400;
    } */

    /* .dot {
        margin-left: -0.7rem;
        margin-right: -0.7rem;
    } */

    /* .display {
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        border-radius: 4px;
        border: 1.5px solid var(--value-border-color);
        transition: background-color 0.1s ease-in-out;
        background-color: var(--display-color);
    } */

    /* .display-focus {
        background-color: var(--heading-color);
        border: 1.5px solid var(--outer-border-color);
    } */

    /* .display:after {
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
        background: var(--digits-color); */
    /* pointer-events: none is needed because we have
        input elements inside the area that gets
        the shimmer effect from this pseudo-element */
    /* pointer-events: none;
    } */

    /* .display.updating:after {
        padding: 0;
        margin: 0;
        opacity: 0.15;
        transition: 0s;
    }

    .spacer {
        width: 0.8rem;
    } */

    .spacer-chev {
        width: 0.2rem;
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

    /* :root {
    --module-border-color: 0, 0, 0;
} */

    .bound-box {
        display: flex;
        flex-direction: column;
        justify-content: center;
        /* box-shadow: 0 0 7px rgba(0, 0, 0, 0.05); */
        /* border: 1.3px solid var(--outer-border-color); */
        /* margin: 0.2rem 0rem; */
    }

    .borders {
        border-left: 1.3px solid var(--outer-border-color);
        border-right: 1.3px solid var(--outer-border-color);
        border-bottom: 1.3px solid var(--divider-border-color);
    }

    .top-bar {
        display: flex;
        /* position: relative; */
        flex-direction: row;
        background-color: var(--heading-color);
        border-bottom: 1.3px solid var(--inner-border-color);
        justify-content: space-between;
        /* align-items: start; */
        padding: 0rem 0rem;
        padding-bottom: 0rem;
        padding-right: 0px;
        /* box-shadow: 0 5px 7px rgba(0, 0, 0, 0.5); */
        padding-left: 0.7rem;
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
