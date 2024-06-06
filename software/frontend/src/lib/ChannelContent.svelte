<script lang="ts">
    import ChevButtonBottom from "./buttons/ChevButtonBottom.svelte";
    import ChevButtonTop from "./buttons/ChevButtonTop.svelte";
    import Display from "./Display.svelte";
    import GeneralButton from "./buttons/GeneralButton.svelte";
    import SubmitButton from "./buttons/SubmitButton.svelte";
    import Button from "./buttons/Button.svelte";
    import { ChSourceStateClass } from "./addons";
    import type {
        ChSourceState,
        VsourceChange,
    } from "./addons/vsource/interface";
    import type { ChangerFunction } from "./addons/vsource/vsource.svelte";
  import PlusMinus from "./PlusMinus.svelte";

    interface Props {
        ch: ChSourceStateClass;
        onChannelChange: ChangerFunction;
    }

    let { ch, onChannelChange }: Props = $props();

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

    async function increment(index: number, value: number) {
        const scaling = [1, 0.1, 0.01, 0.001];
        const plus_minus = ch.sign_temp === "+" ? 1 : -1;

        if (ch.editing) {
            ch.temp[index] += value * plus_minus;
            validateTemp(ch.temp);
            return;
        }

        let new_bias_voltage =
            Math.round((ch.bias_voltage + scaling[index] * value) * 1000) /
            1000;
        ch.validateUpdateVoltage(new_bias_voltage, onChannelChange);
    }


    function validateTemp(temp: number[]) {
        const v =
            (temp[3] * 0.001 + temp[2] * 0.01 + temp[1] * 0.1 + temp[0]) *
            (ch.sign_temp === "+" ? 1 : -1);
        applyTemp(v);
    }


    function applyTemp(bias_voltage: number) {
        const integer = Math.round(Math.abs(bias_voltage * 1000));
        ch.temp[3] = integer % 10;
        ch.temp[2] = Math.floor(integer / 10) % 10;
        ch.temp[1] = Math.floor(integer / 100) % 10;
        ch.temp[0] = Math.floor(integer / 1000) % 10;
        ch.sign_temp = bias_voltage < 0 ? "-" : "+";
    }

    function switchState() {
        ch.updateChannel({ activated: !ch.activated }, onChannelChange);
    }

    

    function handleInputKeyDown(event: any) {
        if (event.key === "Enter") {
            ch.onSubmit(onChannelChange);
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
</script>

<div class="main-controlls">
    <div class="left">
        <!-- <div
            class="plus-minus"
            class:digit-off={st.colorMode}
            class:digit-edit={ch.editing}
            role="button"
            tabindex="0"
            onclick={updatedPlusMinus}
            onkeydown={updatedPlusMinus}
        >
            {ch.sign_temp}
        </div> -->
        <PlusMinus {ch} {onChannelChange}></PlusMinus>
        <!-- <div class="spacer-chev"></div>
        <div class="spacer-chev"></div> -->
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

            <Display {ch} {onChannelChange}></Display>

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
            <SubmitButton onclick={() => ch.onSubmit(onChannelChange)}
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

<style>



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
        padding: 0rem 1rem;
        margin-right: 0.5rem;
        width: 45%;
        padding-right: 1.5rem;
        padding-top: 0;
        padding-bottom: 0;
        /* padding-left: 5rem; */
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
        padding-right: 1.5rem;
    }

    .main-controlls {
        /* flex-grow: 1;
        flex-shrink: 1; */
        /* background-color: var(--body-color); */
        /* transform: scaleY(1);
        transition: all .5s ease-in-out; */
        /* user-select: none; */
        display: flex;
        flex-direction: row;
        flex-grow: 1;
        justify-content: space-around;
        /* align-items: space-between; */
        /* align-items: center; */
        /* justify-content: space-between; */
        /* background-color: var(--body-color); */
        transition: background-color 0.1s ease-in-out;
    }

    
</style>
