<script lang="ts">
    import { onMount } from "svelte";
    import ChannelChevron from "./buttons/ChannelChevron.svelte";
    import HorizontalDots from "./buttons/HorizontalDots.svelte";
    import MenuSlotted from "./MenuSlotted.svelte";
    import MenuButton from "./buttons/MenuButton.svelte";
    import { ChSourceStateClass } from "./addons";
    import type { ChangerFunction } from "./addons/vsource/vsource.svelte";

    import type { Snippet } from "svelte";

    interface Props {
        onChannelChange: ChangerFunction;
        showDropdown: boolean;
        children: Snippet;
        down: boolean;
        ch?: ChSourceStateClass;
        staticName?: string;
        borderTop?: boolean;
    }

    let { onChannelChange, showDropdown = $bindable(), children, down = $bindable(), ch, staticName, borderTop = false}: Props = $props();


    let immediate_text: string = $state("NaN");

    if (ch) {
        immediate_text = ch.heading_text
    }

    if (staticName) {
        immediate_text = staticName
    }



    let heading_editing = false;
    let isEditing = false;
    let isMounted = false;

    let dotMenu: HTMLElement;
    let menuLocation = $state({ top: 0, left: 0 });
    // let showDropdown = $state(false);

    function handleInput(event: Event) {
        let target = event.target as HTMLInputElement;
        immediate_text = target.value;
    }

    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === "Enter") {
            isEditing = false;
            if (ch) ch.updateChannel({ heading_text: immediate_text }, onChannelChange);
        }
    }

    function toggleMenu() {
        showDropdown = !showDropdown;
        const rect = dotMenu.getBoundingClientRect();
        menuLocation = {
            top: rect.top + window.scrollY,
            left: rect.right + window.scrollX,
        };
    }

    onMount(() => {
        isMounted = true;
        const rect = dotMenu.getBoundingClientRect();
        menuLocation = {
            top: rect.top + window.scrollY,
            left: rect.right + window.scrollX,
        };
    });


</script>

<div
    class="top-bar"
    class:animated={ch ? ch.measuring : false}
    class:no_border={!down}
    class:border-top={borderTop}
>
    <div class="top-left">
        
        <!-- If it's a static label (not numbered), then always show the chevron -->
        <ChannelChevron
            bind:down={down}
            isHovering={ch ? (staticName ? true : ch.isHovering) : true}
            index={ch ? ch.index+1 : 0}
        ></ChannelChevron>


        <input
            class="heading-input"
            class:input-to-label={!!staticName}
            class:wide-input={!ch}
            type="text"
            value={immediate_text}
            oninput={handleInput}
            onfocus={() => (heading_editing = true)}
            onblur={() => {
                heading_editing = false;
                if (ch) ch.updateChannel(
                    { heading_text: immediate_text },
                    onChannelChange,
                );
            }}
            onkeydown={handleKeyDown}
            tabindex="0"
            disabled={!!staticName}
        />
        <!-- the double not (!!) converts the [string | undefined] to boolean -->
    </div>

    <div class="top-right">
        {#if !down && ch}
        <div
                class="heading-voltage"
                class:digit-off={!ch.activated}
            >
                {ch.valid ? ch.bias_voltage.toFixed(3): ""}
            </div>
            
        {/if}
        <HorizontalDots onclick={toggleMenu} onkeydown={toggleMenu} bind:dotMenu
        ></HorizontalDots>
        <!-- here, class:something is a special svelte way of pointing to a class which may be toggled. It is a shorthand for class:something={something} -->
        <!-- where 'something' is both a boolean in javascript and a class -->
        {#if showDropdown}
            <MenuSlotted
                onclick={toggleMenu}
                menuVisible={showDropdown}
                location={menuLocation}
            >
                {@render children()}
            </MenuSlotted>
        {/if}

        <!-- <ChannelChevron bind:down={visible}></ChannelChevron> -->
    </div>
</div>

<style>

@keyframes placeHolderShimmer {
        0% {
            background-position: -800px 0;
        }
        100% {
            background-position: 800px 0;
        }
    }

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

    

    .heading-input:hover {
        background-color: var(--hover-heading-color);
        /* border: 1.5px solid var(--inner-border-color); */
    }

    .input-to-label {
        margin-left: 0rem;
        color: var(--text-color);
        font-size: 1.5rem;
        
    }

    .wide-input {
        width: 15.5rem;
    }

    .input-to-label:hover {
        background-color: var(--heading-color)
    }

    .digit-off {
        color: var(--digits-deactivated-color);
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

    .no_border {
        border: none;
    }

    .border-top {
        border-top: 1.3px solid var(--divider-border-color);
    }
</style>
