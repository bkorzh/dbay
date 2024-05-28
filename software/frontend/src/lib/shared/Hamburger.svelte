<script lang="ts">
    // import { writable } from 'svelte/store';
    // import { componentInstance } from '../../state/componentInstanceStore'

    // export let onClick;

    interface MyProps {
        onclick: () => void;
        burgerMenu: any;
    }
    let { onclick, burgerMenu = $bindable() }: MyProps = $props();


    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === "Enter" || event.key === " ") {
            console.log("onclick: ", onclick)
            onclick();
        }
    }
</script>

<div class="hamburger" onclick={onclick} onkeydown={handleKeyDown} bind:this={burgerMenu} role="button" tabindex="0">
    <svg
        class="h-5.5 w-6 my-1 mr-1"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
    >
        <path d="M3 12h18M3 6h18M3 18h18" />
    </svg>
</div>

<style>
    .hamburger {
        display: flex;
        padding-top: 2px;
        padding-bottom: 2px;
        padding-left: 4px;
        padding-right: 4px;
        color: var(--text-color);
    }

    .hamburger:hover {
        cursor: pointer;
    }
</style>
