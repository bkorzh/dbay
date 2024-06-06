<script lang="ts">
    import Channel from "./Channel.svelte";
    import ChannelChevron from "./buttons/ChannelChevron.svelte";
    import type { ChSourceStateClass } from "./addons";
    import type { ChangerFunction } from "./addons/vsource/vsource.svelte";


    // used for displaying the voltage using multiple digits that may be individually edited
    interface Props {
        ch: ChSourceStateClass
        spacing_small?: boolean;
        onChannelChange: ChangerFunction;
    }

    let {
        ch,
        spacing_small = false,
        onChannelChange,
    }: Props = $props();


    const sp = spacing_small ? {
        // small spacing
        spacer: -.75,
        period_spacer: -0.65
    } : {
        // normal spacing
        spacer: -0.17,
        period_spacer: -0.39
    }

    let ones_el = $state();
    let tens_el = $state();
    let hundreds_el = $state();
    let thousands_el = $state();
    // let focusing = $state(false);

    let inputs = $derived([
        ones_el,
        tens_el,
        hundreds_el,
        thousands_el,
    ]) as HTMLInputElement[];

    let input_values = $derived([ch.temp[0], ch.temp[1], ch.temp[2], ch.temp[3]]);

    function inputFocus(event: Event, index?: number) {
        const target = event.target as HTMLInputElement;
        if (typeof index === "number") {
            inputs[index].focus();
        }
        target.value = "";
        ch.focusing = true;
        ch.editing = true;
    }

    function inputBlur(event: Event, index: number) {
        const target = event.target as HTMLInputElement;
        ch.focusing = false;
        target.value = input_values[index].toString();
    }

    function handleDisplayInput(event: Event, index: number) {
        const target = event.target as HTMLInputElement;
        if (isNaN(parseFloat(target.value)) || target.value.includes(".")) {
            event.preventDefault();
            target.value = ""; // Clear the input if the value is not a number
        } else if (target.value.length > 0) {
            if (index < inputs.length - 1) {
                inputs[index + 1].value = ""; // Move the extra digit to the next input
                inputs[index + 1].focus();
            } else {
                // this is for allowing the last input to change its single digit
                // if another digit is entered before "Enter"
                inputs[index].value = target.value[target.value.length - 1];
                ch.temp[3] = parseFloat(
                    inputs[index].value[target.value.length - 1],
                );
            }
        }
    }

    function handleKeydown(event: KeyboardEvent, index: number) {
        const target = event.target as HTMLInputElement;
        // for any key other than 0-9, prevent the default action
        if (!event.key.match(/[0-9]/)) {
            event.preventDefault();
        }
        if (event.key === "Backspace" && target.value === "" && index > 0) {
            if (index + 1 < inputs.length) {
                inputs[index + 1].value = ""; // Clear the next input
            }
            inputs[index - 1].focus();
        }
        if (event.key === "Enter" && index === inputs.length - 1) {
            target.blur();
            ch.onSubmit(onChannelChange);
        }
    }






    let scrollable = $state(true);

  const wheel = (node, options) => {
    let { scrollable } = options;
    const handler = e => {
      // if the event comes from an input: then prevent default
      if (e.target.tagName === "INPUT") {
        e.preventDefault();
        let idx = 0;
        
        switch (e.target) {
            case ones_el:
                idx = 0;
                break;
            case tens_el:
                idx = 1;
                break;
            case hundreds_el:
                idx = 2;
                break;
            case thousands_el:
                idx = 3;
                break;
        }
        if (e.deltaY < 0) {
            scrollChange(idx, 1)
        }
        if (e.deltaY > 0) {
            scrollChange(idx, -1)
        }
        return;
      }
    };

    node.addEventListener('wheel', handler, { passive: false });

    return {
      update(options) {
        scrollable = options.scrollable;
      },
      destroy() {
        node.removeEventListener('wheel', handler, { passive: false });
      }
    };
  };


  async function scrollChange(index: number, value: number) {
        const scaling = [1, 0.1, 0.01, 0.001];
        const plus_minus = ch.sign_temp === "+" ? 1 : -1;

        // if (ch.editing) {
        //     ch.temp[index] += value * plus_minus;
        //     validateTemp(ch.temp);
        //     return;
        // }

        let new_bias_voltage =
            Math.round((ch.bias_voltage + scaling[index] * value) * 1000) /
            1000;
        ch.validateUpdateVoltage(new_bias_voltage, onChannelChange);
    }

</script>

<div
    class="display {ch.isPlusMinusPressed ? 'updating' : ''}"
    class:display-focus={ch.editing}
    role="button"
    tabindex="-1"
    use:wheel={{scrollable}}
>
    
    <input
        class="digit"
        type="number"
        class:digit-off={!ch.activated}
        class:digit-edit={ch.editing}
        class:invalid = {!ch.valid}
        bind:value={ch.temp[0]}
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
        style="margin-left: {sp.period_spacer}rem; margin-right: {sp.period_spacer}rem;"
        onclick={(e) => inputFocus(e, 0)}
        onkeydown={(e) => inputFocus(e, 0)}
        role="button"
        tabindex="-1"
    ></div>
    <div
        class="digit dot"
        onclick={(e) => inputFocus(e, 0)}
        onkeydown={(e) => inputFocus(e, 0)}
        class:invalid = {!ch.valid}
        role="button"
        tabindex="-1"
        class:digit-off={!ch.activated}
        class:digit-edit={ch.editing}
    >
        .
    </div>
    <div
        class="short-spacer"
        style="margin-left: {sp.period_spacer}rem; margin-right: {sp.period_spacer}rem;"
        onclick={(e) => inputFocus(e, 1)}
        onkeydown={(e) => inputFocus(e, 1)}
        role="button"
        tabindex="-1"
    ></div>
    <input
        class="digit"
        type="number"
        class:digit-off={!ch.activated}
        class:digit-edit={ch.editing}
        class:invalid = {!ch.valid}
        bind:value={ch.temp[1]}
        oninput={(e) => handleDisplayInput(e, 1)}
        onkeydown={(e) => handleKeydown(e, 1)}
        onfocus={inputFocus}
        onblur={(e) => inputBlur(e, 1)}
        bind:this={tens_el}
        tabindex="-1"
        maxlength="1"
    />
    <!-- margin-left: {short_spacer}rem; margin-right: {short_spacer}rem; -->
    <div
        class="spacer"
        style="margin-left: {sp.spacer}rem; margin-right: {sp.spacer}rem;"
        onclick={(e) => inputFocus(e, 1)}
        onkeydown={(e) => inputFocus(e, 1)}
        role="button"
        tabindex="-1"
    ></div>
    <input
        class="digit"
        type="number"
        class:digit-off={!ch.activated}
        class:digit-edit={ch.editing}
        class:invalid = {!ch.valid}
        bind:value={ch.temp[2]}
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
        style="margin-left: {sp.spacer}rem; margin-right: {sp.spacer}rem;"
        onclick={(e) => inputFocus(e, 2)}
        onkeydown={(e) => inputFocus(e, 2)}
        role="button"
        tabindex="-1"
    ></div>
    <input
        class="digit"
        type="number"
        class:digit-off={!ch.activated}
        class:digit-edit={ch.editing}
        class:invalid = {!ch.valid}
        bind:value={ch.temp[3]}
        oninput={(e) => handleDisplayInput(e, 3)}
        onkeydown={(e) => handleKeydown(e, 3)}
        onfocus={inputFocus}
        onblur={(e) => inputBlur(e, 3)}
        bind:this={thousands_el}
        tabindex="-1"
        maxlength="1"
    />
</div>



<style>
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

    /* Deactivate the chevrons that appear on input type=number */
    input[type="number"]::-webkit-inner-spin-button,
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
        /* height: 1.0rem; */
    }

    /* .dot {
        margin-left: -0.7rem;
        margin-right: -0.7rem;
    } */

    /* .dot {
        height: 50%;
    } */

    .display {
        /* border-box */
        box-sizing: border-box;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        border-radius: 4px;
        border: 1.3px solid var(--value-border-color);
        transition: background-color 0.1s ease-in-out;
        background-color: var(--display-color);
    }

    .display-focus {
        background-color: var(--heading-color);
        border: 1.3px solid var(--outer-border-color);
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
        /* pointer-events: none is needed because we have
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

    .short-spacer {
        width: 0rem;
    }

    .digit-off {
        color: var(--digits-deactivated-color);
    }

    .invalid {
        color: rgba(0, 0, 0, 0);
    }

    .digit-edit {
        color: var(--edit-blue);
        font-weight: 400;
    }

</style>
