<script lang="ts">
  import { DropdownMenu } from "bits-ui";
  import type { Snippet } from "svelte";

  interface MyProps {
    onclick: () => void;
    children: Snippet;
  }

  let { onclick, children }: MyProps = $props();
</script>

<DropdownMenu.Item onSelect={onclick}>
  {#snippet child({ props }: { props: Record<string, unknown> })}
    <div {...props} class="menu-item">
      <div class="text">{@render children()}</div>
    </div>
  {/snippet}
</DropdownMenu.Item>

<style>
  .text {
    font-size: 1.1rem;
  }

  .menu-item {
    position: relative;
    display: block;
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
    border-radius: 0.3rem;
    padding: 0.25rem 0.25rem 0.25rem 0.5rem;
    text-align: left;
    color: inherit;
    cursor: pointer;
    user-select: none;
    outline: none;
    transition: background-color 0.1s;
  }

  .menu-item:hover,
  .menu-item[data-highlighted] {
    background-color: var(--heading-color);
  }

  .menu-item:after {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    width: 0;
    padding-top: 300%;
    padding-left: 300%;
    margin-left: -20px !important;
    margin-top: 0;
    opacity: 0;
    background: #e1e1e1;
    transition: all 0.6s;
  }

  .menu-item:active:after {
    padding: 0;
    margin: 0;
    opacity: 0.5;
    transition: 0s;
  }
</style>