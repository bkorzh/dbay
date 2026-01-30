<script lang="ts">
    import type { Snippet } from "svelte";
    interface MyProps {
        onclick: () => void;
        children: Snippet;
    }
    let { onclick, children }: MyProps = $props();
    
</script>

<button {onclick}>
    <div class="text">{@render children()}</div>
</button>


<style>

    .text {
        font-size: 1.1rem;
    }
    
    button {
        
        /* margin: 0.2rem; */
        padding: 0.25rem;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: left;
        position: relative;
        -webkit-transition-duration: 0.1s;
        transition-duration: 0.1s;
        text-decoration: none;
        overflow: hidden;
        cursor: pointer;
        user-select: none;
        border: none;
        background: none;
        outline: none;
        /* padding: 0; */
        cursor: pointer;
        color: inherit;
        font: inherit;
        text-align: left;
        /* margin: 0; */
        padding-left: 0.5rem;
        border-radius: 0.3rem;
        box-sizing: border-box;
        display: block;
        width: 100%;
        -webkit-transition-duration: 0.1s;
        transition-duration: 0.1s;
    }

    button:hover {
        background-color: var(--heading-color);
    }

    button:after {
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

    button:after {
    background: #e1e1e1;
  }


  button:active:after {
    padding: 0;
    margin: 0;
    opacity: 0.5;
    transition: 0s;
  }
</style>