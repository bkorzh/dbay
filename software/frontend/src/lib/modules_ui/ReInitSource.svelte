<script>
  import SubmitButton from "../SubmitButton.svelte";
  import { uiStateStore } from "../../state/uiState";
  import EditPencil from "../shared/EditPencil.svelte";
  import { initializeVsource } from "../../api"
  import { voltageStore } from "../../state/systemState";

  let ipEditable = false;
  let portEditable = false;
  let timeoutEditable = false;

  let ipaddr = "10.7.0.193"
  let port = 8880
  let timeout = 5
  let dev_mode = false

  function toggleIpEditable() {
    ipEditable = !ipEditable;
  }

  function togglePortEditable() {
    portEditable = !portEditable;
  }

  function toggleTimeoutEditable() {
    timeoutEditable = !timeoutEditable;
  }

  function submit() {
    console.log("dev mode: ", dev_mode)
    voltageStore.update((state) => {
        state.dev_mode = dev_mode;
        return state;
      });

    console.log("done")

    initializeVsource({ipaddr, port, timeout, dev_mode})
  }


</script>


<div class="basic-block">
  <!-- you CAN NOT use the class name "container" because that means something in tailwind -->
  <div class="top-bar">
    <div class="top-left">
      <h1 class="heading">Re-Initialize Source</h1>
    </div>
  </div>

  <div class="main-controlls">
    <div class="param">
      <div class="label">IP</div>
      <div class="input-params">
        <input type="text" bind:value={ipaddr} readonly={!ipEditable} class:non-editable={!ipEditable} />
        <div class="icon" on:click={toggleIpEditable} on:keydown={toggleIpEditable} role="button" tabindex="0">
          <EditPencil darkMode={$uiStateStore.colorMode} />
        </div>
      </div>
    </div>

    <div class="param">
      <div class="label">Port</div>
      <div class="input-params">
        <input type="text" bind:value={port} readonly={!portEditable} class:non-editable={!portEditable} />
        <div class="icon" role="button" tabindex="0" on:click={togglePortEditable} on:keydown={togglePortEditable}>
          <EditPencil darkMode={$uiStateStore.colorMode} />
        </div>
      </div>
    </div>

    <div class="param">
      <div class="label">Timeout</div>
      <div class="input-params">
        <input type="text" bind:value={timeout} readonly={!timeoutEditable} class:non-editable={!timeoutEditable} />
        <div class="icon" on:click={toggleTimeoutEditable} on:keydown={toggleTimeoutEditable} role="button" tabindex="0">
          <EditPencil darkMode={$uiStateStore.colorMode} />
        </div>
      </div>
    </div>

    <div class="param">
      <div class="label">Dev-Mode</div>
      <div class="input-params">
        <input class="check" type="checkbox" bind:checked={dev_mode} />
        
      </div>
    </div>


    <br>
    <SubmitButton {uiStateStore} on:submit={submit} >Re-Initialize</SubmitButton>
  </div>
</div>

<style>

  .check {
    width: 1.5rem;
    height: 1.5rem;
    margin: 0.0rem;
  }

  
  .non-editable {
    color: var(--disabled-digits-color);
  }

  .icon {
    margin-left: 0.5rem;
    border-radius: 4px;
    padding: 0.4rem;
    color: red;
  }

  .icon:hover {
    cursor: pointer;
    background-color: var(--hover-body-color);
    
  }

  .param {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0rem;
  }

  .input-params {
    display: flex;
    flex-direction: row;
    align-items: center;
    width: 13rem;
  }


  .label {
    font-size: 1.2rem;
    color: var(--text-color);
    margin: 0.3rem;
    width: 10rem;
  }

  .enable {
    font-size: 1.2rem;
    color: var(--text-color);
    margin: 0.3rem;
  }

  input {
    background-color: var(--display-color);
    border-radius: 4px;
    border: 1.5px solid var(--inner-border-color);
    padding: 0rem 0.3rem;
    /* font-family: "Roboto Flex", sans-serif;
    font-weight: 300; */
    font-size: 1.2rem;
    /* letter-spacing: 0.58rem; */
    color: var(--digits-color);
    width: 10rem;
    transition: background-color 0.1s ease-in-out;
  }

  .main-controlls {
    /* flex-grow: 1;
        flex-shrink: 1; */
    background-color: var(--body-color);
    /* transform: scaleY(1);
        transition: all .5s ease-in-out; */
    user-select: none;
    display: flex;
    flex-direction: column;
    /* justify-content: space-between; */
    background-color: var(--body-color);
    transition: background-color 0.1s ease-in-out;
    padding: 1rem;
  }

  .top-bar {
    display: flex;

    flex-direction: column;
    background-color: var(--heading-color);
    border-bottom: 1.3px solid var(--inner-border-color);
    justify-content: space-between;
    padding: 5px 10px;
    /* padding: 300px; */
    padding-right: 13px;
  }

  .basic-block {
    display: flex;
    flex-direction: column;
    justify-content: center;
    box-shadow: 0 0 7px rgba(0, 0, 0, 0.05);
    border: 1.3px solid var(--outer-border-color);
    background-color: var(--body-color);
    margin: 0.2rem 0rem;
  }

  @media (min-width: 460px) {
    .basic-block {
      margin: 5px 20px 5px 5px;
    }
  }

  @media (max-width: 460px) {
    .basic-block {
      margin: 5px 5px 5px 5px;
    }
  }
</style>
