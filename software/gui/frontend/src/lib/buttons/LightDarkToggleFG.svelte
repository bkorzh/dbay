<script lang="ts">
  import { onMount } from "svelte";
  import { ui_state, setMode } from "../../state/uiState.svelte";

  // indicate if we're in dark mode or not
  let dark: boolean;

  // hide the control until we've decided what the intial mode is
  let hidden = true;

  onMount(() => {
    setMode(ui_state.colorMode);
  });

  function handleChange({ matches: dark }: MediaQueryListEvent) {
    // only set if we haven't overridden the theme
    console.log("running handle change");
    if (!localStorage.theme) {
      setMode(dark);
    }
  }

  function toggle() {
    // console.log("running toggle");
    // the ! needs to be here!!
    dark = setMode(!dark);
  }

</script>

<svelte:head>
  <script>
    if (
      localStorage.theme === "dark" ||
      (!localStorage.theme &&
        window.matchMedia("(prefers-color-scheme: dark)").matches)
    ) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  </script>
</svelte:head>

<!-- animated switch version -->
<button
  class="{ui_state.colorMode
    ? 'bg-gray-500 '
    : ' bg-gray-300'} relative my-auto mx-1 mr-4 inline-flex h-[1.22rem] w-[2.25rem] shrink-0 rounded-full border-2 border-transparent duration-200 ease-in-out"
  on:click={toggle}
>
  <span class="sr-only">Toggle Dark Mode</span>
  <span
    class="{ui_state.colorMode
      ? 'translate-x-0 bg-gray-700'
      : 'translate-x-4 bg-gray-200'} pointer-events-none relative inline-block h-4 w-4 rounded-full shadow-sm ring-0 transition duration-200 ease-in-out"
  >
    <span
      class="{ui_state.colorMode
        ? 'opacity-100 ease-in duration-200'
        : 'opacity-0 ease-out duration-100'} absolute inset-0 h-full w-full flex items-center justify-center transition-opacity"
      aria-hidden="true"
    >
      <!-- moon icon -->
      <svg
        class="h-4 w-4 text-gray-200"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"
        />
      </svg>
    </span>
    <span
      class="{ui_state.colorMode
        ? 'opacity-0 ease-out duration-100'
        : 'opacity-100 ease-in duration-200'} absolute inset-0 h-full w-full flex items-center justify-center transition-opacity"
      aria-hidden="true"
    >
    </span>
  </span>
</button>


