<script lang="ts">
  import BasicContainer from "../BasicContainer.svelte";

  interface MyProps {
    module_index: number;
  }

  let { module_index }: MyProps = $props();
  // let slot = 0;
</script>

<BasicContainer>
  <p class="text-red-500 p-3">
    Stand-in for the DAC16D module, with module index {module_index}
  </p>
</BasicContainer>
