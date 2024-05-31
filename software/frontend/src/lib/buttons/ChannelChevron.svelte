<script lang="ts">
    import { fly } from "svelte/transition";
    import { fade } from "svelte/transition";
    import { crossfade } from "svelte/transition";
    import { cubicInOut } from "svelte/easing";

    interface Props {
        isHovering: boolean;
        index: number;
        onChevronClick?: () => void
    }

    let {isHovering, index, onChevronClick}: Props = $props();

    let toggle_up = $state(false);
    let toggle_down = $state(true);
    let isConsistentHovering = $state(false);
    let hoverTimeout: number;

    function togglerRotateState() {
        if (onChevronClick) onChevronClick();
        toggle_up = !toggle_up;
        toggle_down = !toggle_down;
    }


    $effect(() => {
        clearTimeout(hoverTimeout);
        isHovering = isHovering;
        hoverTimeout = setTimeout(() => {
            
            isConsistentHovering = isHovering;
        }, 200);
    });

</script>

<div
    class="chevron-container"
    onclick={togglerRotateState}
    onkeydown={togglerRotateState}
    role="button"
    tabindex="0"
>
    {#if isConsistentHovering}
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="22"
            height="22"
            class="chevron"
            fill="currentColor"
            stroke="currentColor"
            class:toggle_up
            class:toggle_down
            viewBox="0 0 16 16"
            role="button"
            tabindex="0"
            in:fly={toggle_up ? { y: -7, duration: 200} : { x: -7, duration: 200}}
            out:fly={toggle_up ? { y: -7, duration: 200} : { x: -7, duration: 200}}
        >
            <path
                fill-rule="evenodd"
                d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
                stroke-width="0.8"
            />
        </svg>
    {:else}
        <h1
            class="heading"
            in:fly={{ x: 7, duration: 200}}
            out:fly={{ x: 7, duration: 200}}
        >
            {index}
        </h1>
    {/if}
</div>

<style>

    .heading {

        margin: auto;
        font-size: 1.5rem;
        color: var(--text-color);

    }

    .toggle_up {
        transform: rotate(-90deg);
        margin-top: 0.17rem;
        padding-top: 0.18rem;
        transition: transform 0.2s ease-in-out;
    }

    .toggle_down {
        transform: rotate(0);
        margin-top: 0.2rem;
        padding-top: 0.2rem;
        transition: transform 0.2s ease-in-out;
    }

    .chevron-container {
        

        margin: 0.15rem;
        border-radius: 5px;

        width: 2.5rem;
        color: var(--icon-color);
        height: 2.5rem;
        

        display: grid;
    }

    .chevron-container> * {
        grid-area: 1 / 1;
    }

    .chevron {
        margin: auto;
        color: var(--icon-color);
    }

    .chevron:focus {
        outline: none;
    }

    .chevron-container:focus {
        outline: none;
    }

    .chevron-container:hover {
        background-color: var(--hover-heading-color);
    }

    .chevron-container:active {
        transform: scale(0.90);
    }
</style>
