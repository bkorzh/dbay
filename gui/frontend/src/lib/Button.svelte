<script>
  export let uiStateStore;
  export let redGreen;
</script>


<button on:click
  class="{redGreen
    ? $uiStateStore.colorMode
      ? 'teal text-teal-500 hover:text-teal-400 border-teal-500 hover:bg-teal-900'
      : 'teal text-teal-500 bg-teal-50 border-teal-500 hover:bg-teal-100'
    : $uiStateStore.colorMode
      ? 'red text-red-500 hover:text-red-400 border-red-500 hover:bg-red-900'
      : 'red text-red-500 bg-red-50 border-red-500 hover:bg-red-100'} 
    text-s font-medium border-2 border-opacity-50 rounded px-4 py-1 button"

>
  <slot />
  <!-- my-2 ml-2 -->
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

  .button.red:after {
    background: #f36666;
  }

  .button.teal:after {
    background: #26f4ba;
  }

  .button:active:after {
    padding: 0;
    margin: 0;
    opacity: 0.5;
    transition: 0s;
  }
</style>
