<script lang="ts">
  import "../app.css";
  import { onMount } from "svelte";
  import { uiStateStore, setMode } from "../stores/uiStateStore";

  // indicate if we're in dark mode or not
  let dark: boolean;

  // hide the control until we've decided what the intial mode is
  let hidden = true;

  onMount(() => {
    setMode($uiStateStore.colorMode);
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
  class="{$uiStateStore.colorMode
    ? 'bg-gray-500 '
    : ' bg-gray-800'} relative inline-flex flex-shrink-1 h-[1.22rem] w-[2.25rem] border-2 border-transparent rounded-full ease-in-out duration-200 my-auto mx-1 mr-4"
  on:click={toggle}
>
  <span class="sr-only">Toggle Dark Mode</span>
  <span
    class="{$uiStateStore.colorMode
      ? 'translate-x-0 bg-gray-700'
      : 'translate-x-4 bg-gray-600'} pointer-events-none relative inline-block h-4 w-4 rounded-full shadow transform ring-0 transition ease-in-out duration-200"
  >
    <span
      class="{$uiStateStore.colorMode
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
      class="{$uiStateStore.colorMode
        ? 'opacity-0 ease-out duration-100'
        : 'opacity-100 ease-in duration-200'} absolute inset-0 h-full w-full flex items-center justify-center transition-opacity"
      aria-hidden="true"
    >
      <!-- sun icon -->
      <svg
        class="h-4 w-4 text-yellow-300"
        viewBox="0 0 20 20"
        fill="currentColor"
      >
        <path
          fill-rule="evenodd"
          d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
          clip-rule="evenodd"
        />
      </svg>
    </span>
  </span>
</button>


<!-- <style>
  button {
    margin-right: 0.2rem;
  }
</style> -->

<!-- <button class="bg-green-400" type="button">This</button> -->
