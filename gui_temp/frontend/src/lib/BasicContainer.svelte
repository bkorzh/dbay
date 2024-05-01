
<div class="basic-block">
  <!-- you CAN NOT use the class name "container" because that means something in tailwind -->
  <div class="top-bar"><h1>Info</h1></div>
    <slot></slot>
</div>


<style>

.top-bar {
        display: flex;

        flex-direction: column;
        background-color: var(--heading-color);
        border-bottom: 1.3px solid var(--inner-border-color);
        justify-content: space-between;
        padding: 5px 10px;
        /* padding: 300px; */
        color: var(--text-color);
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

