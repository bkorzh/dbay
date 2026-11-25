<script lang="ts">
  import SubmitButton from "../buttons/SubmitButton.svelte";
  import { ui_state } from "../../state/uiState.svelte";
  import QrCode from "svelte-qrcode";
  import { onMount } from "svelte";
  import { serverInfo } from "../../api";
  import { copy } from "svelte-copy";

  function done() {
    ui_state.show_remote_access = false;
  }

  let urls: string[] = $state([]);
  let selected = $state(0);
  let qr_border = $state("none");

  let access_string = $derived(urls[selected] ?? "http://localhost:5173");

  onMount(() => {
    serverInfo()
      .then((data) => {
        // The server may be reachable on several addresses (multiple NICs).
        const ipaddrs = data.ipaddrs?.length ? data.ipaddrs : [data.ipaddr];
        urls = ipaddrs.map((ipaddr) => `http://${ipaddr}:${data.port}`);
        selected = 0;
      })
      .catch((error) => {
        console.error("Failed to fetch server info:", error);
        // Fallback to localhost and port 5173
        urls = [];
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

    <div class="url-list">
      {#each urls as url, i (url)}
        <div class="url-row" class:selected={i === selected}>
          <button
            class="url-text"
            onclick={() => (selected = i)}
            title="Show QR code for this address"
          >
            {url}
          </button>
          <button class="copy-wrapper" aria-label="copy-button" use:copy={url}>
            <div class="copybutton">
              <svg
                width="100%"
                height="100%"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M5 15C4.06812 15 3.60218 15 3.23463 14.8478C2.74458 14.6448 2.35523 14.2554 2.15224 13.7654C2 13.3978 2 12.9319 2 12V5.2C2 4.0799 2 3.51984 2.21799 3.09202C2.40973 2.71569 2.71569 2.40973 3.09202 2.21799C3.51984 2 4.0799 2 5.2 2H12C12.9319 2 13.3978 2 13.7654 2.15224C14.2554 2.35523 14.6448 2.74458 14.8478 3.23463C15 3.60218 15 4.06812 15 5M12.2 22H18.8C19.9201 22 20.4802 22 20.908 21.782C21.2843 21.5903 21.5903 21.2843 21.782 20.908C22 20.4802 22 19.9201 22 18.8V12.2C22 11.0799 22 10.5198 21.782 10.092C21.5903 9.71569 21.2843 9.40973 20.908 9.21799C20.4802 9 19.9201 9 18.8 9H12.2C11.0799 9 10.5198 9 10.092 9.21799C9.71569 9.40973 9.40973 9.71569 9.21799 10.092C9 10.5198 9 11.0799 9 12.2V18.8C9 19.9201 9 20.4802 9.21799 20.908C9.40973 21.2843 9.71569 21.5903 10.092 21.782C10.5198 22 11.0799 22 12.2 22Z"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
            </div>
          </button>
        </div>
      {:else}
        <div class="url-row">
          <div class="url-text">{access_string}</div>
        </div>
      {/each}
    </div>

    <SubmitButton onclick={done}>Done</SubmitButton>
  </div>
</div>

<style>
  .url-list {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    width: 100%;
    margin-bottom: 1rem;
  }

  .url-row {
    position: relative;
    display: flex;
    flex-direction: row;
    align-items: center;
    border: 1.5px solid var(--outer-border-color);
    border-radius: 0.3rem;
    background-color: var(--display-color);
    transition: border-color 0.1s ease-in-out;
  }

  .url-row.selected {
    border-color: var(--edit-blue);
  }

  .url-text {
    flex-grow: 1;
    font-family: "Roboto Flex", sans-serif;
    font-weight: 300;
    font-size: 1.4rem;
    color: var(--digits-color);
    text-align: left;
    background: none;
    border: none;
    padding: 0.3rem 2.6rem 0.3rem 0.4rem;
    cursor: pointer;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .copy-wrapper {
    background: none;
    border: none;
    padding: 0;
    cursor: pointer;
  }

  .copybutton {
    color: var(--digits-color);
    position: absolute;
    width: 1.5rem;
    height: 1.5rem;
    z-index: 3;
    right: 0.5rem;
    top: 0.45rem;
    opacity: 0.2;
  }

  .copybutton:hover {
    opacity: 0.4;
  }

  .copybutton:active {
    transform: scale(0.95);
  }

  .outer-box {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 2rem;
    margin-top: 1rem;
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
