<script>
  import SubmitButton from "../buttons/SubmitButton.svelte";
  import { ui_state } from "../../state/uiState.svelte";
  import EditPencil from "../buttons/EditPencil.svelte";
  import { initializeVsource } from "../../api";
  import { system_state } from "../../state/systemState.svelte";
  import QrCode from "svelte-qrcode";
  import { onMount } from "svelte";
  import { serverInfo } from "../../api";
  import { copy } from "svelte-copy";

  function done() {
    ui_state.show_remote_access = false;
  }

  let access_string = $state("");
  let qr_border = $state("none");

  let text = "you copied correctly!";

  onMount(() => {
    serverInfo()
      .then((data) => {
        const port = data.port;
        const ipaddr = data.ipaddr;

        access_string = `http://${ipaddr}:${port}`;
      })
      .catch((error) => {
        console.error("Failed to fetch server info:", error);
        // Fallback to localhost and port 5173
        access_string = "http://localhost:5173";
        qr_border = "red";
      });
  });
</script>

<div class="basic-block">
  <!-- you CAN NOT use the class name "container" because that means something in tailwind -->
  <div class="top-bar">
    <div class="top-left">
      <h1 class="heading">Access Server Remotely</h1>
    </div>
  </div>

  <div class="main-controlls">
    <div class="outer-box">
      <div class="box" style="border: 4px solid {qr_border}">
        <QrCode value={access_string}></QrCode>
      </div>
    </div>

    <button use:copy={"Hello World"}> Copy </button>

    <SubmitButton onclick={done}>Done</SubmitButton>
  </div>
</div>

<style>
  .outer-box {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 1rem;
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
