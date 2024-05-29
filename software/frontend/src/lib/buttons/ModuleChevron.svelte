<script lang="ts">
    let { visible = $bindable() } = $props();

    let toggle_up = $state(false);
    let toggle_down = $state(true);
    // let visible = $state(true);

    function togglerRotateState() {
        console.log("togglerRotateState");
        toggle_up = !toggle_up;
        toggle_down = !toggle_down;
        visible = !visible;
    }
</script>

<div class="closer">
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        fill="currentColor"
        stroke="currentColor"
        class="chevron"
        class:toggle_up
        class:toggle_down
        viewBox="0 0 16 16"
        role="button"
        tabindex="0"
        onclick={togglerRotateState}
        onkeydown={togglerRotateState}
    >
        <path
            fill-rule="evenodd"
            d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
            stroke-width="0.8"
            transform="translate(0, -2)"
        />
        <path
            fill-rule="evenodd"
            d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"
            stroke-width="0.8"
            transform="translate(0, 2)"
        />
    </svg>
</div>

<style>
    .chevron {
        margin-top: 0.25rem;
        margin-left: 0.2rem;
        color: var(--icon-color);
    }

    .chevron:focus {
        outline: none;
    }

    .toggle_up {
        transform: rotate(-90deg);
        transition: transform 0.2s ease-in-out;
    }

    .toggle_down {
        transform: rotate(0);
        transition: transform 0.2s ease-in-out;
    }
</style>
