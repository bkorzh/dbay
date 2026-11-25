declare module "svelte-qrcode" {
  import { SvelteComponent } from "svelte";

  export default class QrCode extends SvelteComponent<{
    value: string;
  }> {}
}
