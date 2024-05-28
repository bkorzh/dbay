<script lang="ts">

    interface Props {
        onclick: (e: MouseEvent) => void;
        onkeydown: (e: KeyboardEvent) => void;
        dotMenu: HTMLElement;
    }

let { onclick, onkeydown, dotMenu = $bindable() }: Props = $props();


</script>

<div
    class="dot-menu"
    {onclick}
    {onkeydown}
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
        class="bi-three-dots"
        viewBox="0 -3 16 16"
    >
        <path
            d="M3 9.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm5 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"
            stroke-width="0.3"
        />
    </svg>
</div>


<style>
    .dot-menu {
        margin: 0px 3px;
        padding: 0px 5px;
        padding-top: 0.1rem;
        margin-bottom: 0.15rem;
        margin-top: 0.15rem;
        /* padding-bottom: -10rem; */
        color: var(--icon-color);
        border-radius: 5px;
    }

    .dot-menu:hover {
        /* cursor: pointer; */
        background-color: var(--hover-heading-color);
        
    }

    .dot-menu:active {
        transform: scale(0.95);
    }

    /* .dot-menu:hover {
        transform: scale(1.05);
    } */
</style>
