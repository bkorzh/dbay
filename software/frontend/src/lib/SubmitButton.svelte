<script lang="ts">
  // import { createEventDispatcher } from 'svelte';
  // export let uiStateStore;
  import { ui_state } from "../state/uiState.svelte";

  interface Props {
    onclick: () => void;
  }

  let { onclick }: Props = $props();

  // const dispatch = createEventDispatcher();
  
  // function handleClick() {
  //   dispatch('submit');
  // }
</script>


<button
  class="{ ui_state.colorMode
      ? 'blue text-blue-500 hover:text-blue-400 border-blue-500 hover:bg-blue-900'
      : 'blue text-blue-500 bg-blue-50 border-blue-500 hover:bg-blue-100'
    } text-s font-medium border-2 border-opacity-50 rounded px-4 py-1 button"
{onclick}>
  <slot />
</button>


<style>

.button {
    position: relative;

    -webkit-transition-duration: 0.1s;
    transition-duration: 0.1s;
    text-decoration: none;
    overflow: hidden;
    cursor: pointer;
    user-select: none
  }

  .button:after {
    content: "";
    display: block;
    position: absolute;
    left: 0;
    top: 0;
    width: 0;
    padding-top: 300%;
    padding-left: 300%;
    margin-left: -20px !important;
    margin-top: -0%;
    opacity: 0;
    transition: all 0.6s;
  }

  .button.blue:after {
    background: #666df3;
  }

  /* .button.blue:after {
    background: #26f4ba;
  } */

  .button:active:after {
    padding: 0;
    margin: 0;
    opacity: 0.5;
    transition: 0s;
  }
</style>
