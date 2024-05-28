<script lang="ts">

    // used for displaying the voltage using multiple digits that may be individually edited
    interface Props {
        onoff: boolean;
        temp: number[];
        editing: boolean;
        focusing: boolean;
        isPlusMinusPressed: boolean;
        invalid: boolean;
        handleSubmitButtonClick: () => void;
    }

    let {
        onoff,
        temp = $bindable([0, 0, 0, 0]),
        editing = $bindable(false),
        focusing = $bindable(false),
        isPlusMinusPressed,
        invalid,
        handleSubmitButtonClick,
    }: Props = $props();



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

    let input_values = $derived([temp[0], temp[1], temp[2], temp[3]]);

    function inputFocus(event: Event, index?: number) {
        const target = event.target as HTMLInputElement;
        if (typeof index === "number") {
            inputs[index].focus();
        }
        target.value = "";
        focusing = true;
        editing = true;
    }

    function inputBlur(event: Event, index: number) {
        const target = event.target as HTMLInputElement;
        focusing = false;
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
                temp[3] = parseFloat(
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
            handleSubmitButtonClick();
        }
    }
</script>

<div
    class="display {isPlusMinusPressed ? 'updating' : ''}"
    class:display-focus={editing}
    role="button"
    tabindex="-1"
>
    <input
        class="digit"
        type="number"
        class:digit-off={onoff}
        class:digit-edit={editing}
        class:invalid
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
        class:invalid
        role="button"
        tabindex="-1"
        class:digit-off={onoff}
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
        class:digit-off={onoff}
        class:digit-edit={editing}
        class:invalid
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
        class:digit-off={onoff}
        class:digit-edit={editing}
        class:invalid
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
        class:digit-off={onoff}
        class:digit-edit={editing}
        class:invalid
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
    }

    .dot {
        margin-left: -0.7rem;
        margin-right: -0.7rem;
    }

    .display {
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        border-radius: 4px;
        border: 1.5px solid var(--value-border-color);
        transition: background-color 0.1s ease-in-out;
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
