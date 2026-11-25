<script lang="ts">
    /**
     * A styled range input.
     *
     * Native range inputs cannot be styled consistently across browsers, so the
     * track and thumb are drawn here with the app's design tokens. The filled
     * portion of the track is a gradient whose stop follows the value, which
     * avoids needing a second element behind the input.
     *
     * Two callbacks, because a slider has two distinct moments:
     *   oninput  — fires continuously while dragging (every pixel of movement)
     *   onrelease — fires once, when the user lets go
     *
     * Callers generally send a debounced command on `oninput` for live feedback,
     * and a final authoritative command on `onrelease`.
     */
    interface Props {
        value: number;
        min?: number;
        max?: number;
        step?: number;
        disabled?: boolean;
        unit?: string;
        label?: string;
        oninput?: (value: number) => void;
        onrelease?: (value: number) => void;
    }

    let {
        value,
        min = -1,
        max = 1,
        step = 0.01,
        disabled = false,
        unit = "V",
        label,
        oninput,
        onrelease,
    }: Props = $props();

    // Where the thumb sits, 0–100%, used to colour the filled part of the track.
    let fraction = $derived(
        Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100)),
    );

    // Enough decimals to show `step`, so 0.01 shows as "0.25 V" not "0.3 V".
    let decimals = $derived(
        String(step).includes(".") ? String(step).split(".")[1].length : 0,
    );

    function handleInput(event: Event) {
        const next = Number((event.currentTarget as HTMLInputElement).value);
        oninput?.(next);
    }

    function handleRelease(event: Event) {
        const next = Number((event.currentTarget as HTMLInputElement).value);
        onrelease?.(next);
    }
</script>

<div class="slider" class:disabled>
    {#if label}
        <span class="label">{label}</span>
    {/if}

    <input
        type="range"
        {min}
        {max}
        {step}
        {disabled}
        {value}
        aria-label={label ?? "value"}
        style="--fill: {fraction}%"
        oninput={handleInput}
        onchange={handleRelease}
        onpointerup={handleRelease}
        onkeyup={handleRelease}
    />

    <span class="readout">
        {value.toFixed(decimals)}<span class="unit">{unit}</span>
    </span>
</div>

<style>
    .slider {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 0.75rem;
        flex-grow: 1;
        padding: 0.4rem 0;
    }

    .label {
        font-size: 1.1rem;
        color: var(--text-color);
        white-space: nowrap;
    }

    .readout {
        font-family: "Roboto Flex", sans-serif;
        font-variant-numeric: tabular-nums;
        font-size: 1.1rem;
        color: var(--digits-color);
        min-width: 4.2rem;
        text-align: right;
        white-space: nowrap;
    }

    .unit {
        color: var(--icon-color);
        margin-left: 0.2rem;
    }

    .disabled .readout {
        color: var(--disabled-digits-color);
    }

    input[type="range"] {
        -webkit-appearance: none;
        appearance: none;
        flex-grow: 1;
        min-width: 6rem;
        height: 1.4rem;
        margin: 0;
        background: transparent;
        cursor: pointer;
    }

    input[type="range"]:disabled {
        cursor: default;
    }

    /* --- track: filled up to --fill, unfilled after ------------------- */

    input[type="range"]::-webkit-slider-runnable-track {
        height: 0.35rem;
        border-radius: 999px;
        background: linear-gradient(
            to right,
            var(--edit-blue) var(--fill),
            var(--value-border-color) var(--fill)
        );
        border: 1px solid var(--outer-border-color);
    }

    input[type="range"]::-moz-range-track {
        height: 0.35rem;
        border-radius: 999px;
        background: linear-gradient(
            to right,
            var(--edit-blue) var(--fill),
            var(--value-border-color) var(--fill)
        );
        border: 1px solid var(--outer-border-color);
    }

    input[type="range"]:disabled::-webkit-slider-runnable-track {
        background: var(--value-border-color);
    }

    input[type="range"]:disabled::-moz-range-track {
        background: var(--value-border-color);
    }

    /* --- thumb -------------------------------------------------------- */

    input[type="range"]::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 1.05rem;
        height: 1.05rem;
        margin-top: calc((0.35rem - 1.05rem) / 2);
        border-radius: 50%;
        background: var(--display-color);
        border: 1.5px solid var(--edit-blue);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.18);
        transition: transform 0.08s ease-out;
    }

    input[type="range"]::-moz-range-thumb {
        width: 1.05rem;
        height: 1.05rem;
        border-radius: 50%;
        background: var(--display-color);
        border: 1.5px solid var(--edit-blue);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.18);
        transition: transform 0.08s ease-out;
    }

    input[type="range"]:active::-webkit-slider-thumb {
        transform: scale(1.15);
    }

    input[type="range"]:active::-moz-range-thumb {
        transform: scale(1.15);
    }

    input[type="range"]:focus-visible {
        outline: none;
    }

    input[type="range"]:focus-visible::-webkit-slider-thumb {
        box-shadow: 0 0 0 3px var(--hover-body-color);
    }

    input[type="range"]:focus-visible::-moz-range-thumb {
        box-shadow: 0 0 0 3px var(--hover-body-color);
    }

    input[type="range"]:disabled::-webkit-slider-thumb {
        border-color: var(--disabled-digits-color);
    }

    input[type="range"]:disabled::-moz-range-thumb {
        border-color: var(--disabled-digits-color);
    }
</style>
