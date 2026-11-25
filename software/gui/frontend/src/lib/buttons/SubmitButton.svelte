<script lang="ts">
  // import { createEventDispatcher } from 'svelte';
  // export let uiStateStore;
  import { ui_state } from "../../state/uiState.svelte";
  import type { Snippet } from "svelte";

  interface Props {
    onclick: () => void;
    children: Snippet;
  }

  let { onclick, children }: Props = $props();

  // const dispatch = createEventDispatcher();
  
  // function handleClick() {
  //   dispatch('submit');
  // }
</script>


<button
  class="{ ui_state.colorMode
      ? 'blue border-blue-500/50 text-blue-500 hover:bg-blue-900 hover:text-blue-400'
      : 'blue border-blue-500/50 bg-blue-50 text-blue-500 hover:bg-blue-100'
    } button rounded border-[1.5px] px-2 py-[0.42rem] font-medium"
{onclick}>
  {@render children()}
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
