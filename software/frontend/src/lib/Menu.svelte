<script>
    import LightDarkToggle from "./LightDarkToggle.svelte";
    import { onMount, onDestroy } from "svelte";
    import { uiStateStore } from "../stores/uiStateStore";

    export let onClick;
    export let menuVisible;

    function handleKeyDown(event) {
        if (event.key === "Enter" || event.key === " ") {
            onClick();
        }
    }

    let menu;
    let closeButton;
    let justOpened = true;

    onMount(() => {
        justOpened = true;
        menu = document.querySelector(".dropdown");
        closeButton = menu.querySelector(".close-button");

        document.addEventListener("click", handleClickOutside);
    });

    onDestroy(() => {
        document.removeEventListener("click", handleClickOutside);
    });

    function handleClickOutside(event) {
        const isClickInsideMenu = menu.contains(event.target);

        if (menuVisible && !isClickInsideMenu && !justOpened) {
            // close the menu
            onClick();
        }

        justOpened = false;
    }

</script>

<div class="dropdown">
    <div class="settings-top">
        <h3>Settings</h3>

        <div class="close-buttom" on:click={onClick} on:keydown={handleKeyDown} role="button" tabindex="0">
            <svg
                xmlns="http://www.w3.org/2000/svg"
                x="0px"
                y="0px"
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="currentColor"
                stroke="currentColor"
            >
                <path
                    d="M 4.9902344 3.9902344 A 1.0001 1.0001 0 0 0 4.2929688 5.7070312 L 10.585938 12 L 4.2929688 18.292969 A 1.0001 1.0001 0 1 0 5.7070312 19.707031 L 12 13.414062 L 18.292969 19.707031 A 1.0001 1.0001 0 1 0 19.707031 18.292969 L 13.414062 12 L 19.707031 5.7070312 A 1.0001 1.0001 0 0 0 18.980469 3.9902344 A 1.0001 1.0001 0 0 0 18.292969 4.2929688 L 12 10.585938 L 5.7070312 4.2929688 A 1.0001 1.0001 0 0 0 4.9902344 3.9902344 z"
                    stroke-width=".8"
                />
            </svg>
        </div>
    </div>

    <!-- <ul>
        <li><button on:click={addModule}>Add a Module</button></li>
    </ul> -->
    <div class="dd">
        <!-- <button on:click={addModule}>Add a Module</button> -->
        <slot></slot>
    </div>
</div>

<style>

    /* li {
        padding: 0.2rem;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: left;
    } */

    

    .close-buttom {
        color: var(--icon-color);
    }

    .dropdown {
        width: 250px;
        position: absolute;
        top: 13px;
        left: 183px;
        /* top: 100%; */
        /* left: 0; */
        z-index: 1;
        background-color: white;

        border: 1px solid var(--outer-border-color);

        /* border-radius: 5px; */
        box-shadow: 0 0 7px rgba(0, 0, 0, 0.05);
        background-color: var(--body-color);
    }

    .dd {
        list-style: none;
        margin: 0;
        padding: 0.2rem;
    }



    /* li {
        padding: 5px;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
    } */

    h3 {
        padding-left: 0.5rem;
    }

    .settings-top {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        padding: 5px;
        border-bottom: 1px solid var(--inner-border-color);
    }

    .close-buttom:hover {
        cursor: pointer;
    }
</style>
