<script>
    // export let color = 'currentColor';
</script>


<div class="chev-button">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" stroke="currentColor" class="bi bi-chevron-compact-down" 
    viewBox="0 0 16 16"
    transform="scale(0.8, 1.5)">
      <path fill-rule="evenodd" d="M1.553 6.776a.5.5 0 0 1 .67-.223L8 9.44l5.776-2.888a.5.5 0 1 1 .448.894l-6 3a.5.5 0 0 1-.448 0l-6-3a.5.5 0 0 1-.223-.67z"
      stroke-width=".3"/>
    </svg>
  </div>


<style>

    
    svg {
        display: block;
        color: var(--icon-color);

    }

    .chev-button {
        position: absolute;
        right: 0.75rem;
        top: 35%;
        transform: translateY(-50%);
        pointer-events: none;
        z-index: 100;
  }

  .chev-button:hover {
    background-color: var(--hover-body-color);
  }



  .chev-button:after {
    content: "";
    display: block;
    position: absolute;
    left: 0;
    top: 0;
    width: 0;
    padding-top: 300%;
    padding-right: 300%;
    margin-top: -20px !important;
    /* margin-top: -0%; */
    margin-bottom: -0%;
    opacity: 0;
    transition: all 0.3s;
  }

  .chev-button:after {
    background: #898989;
  }


  .chev-button:active:after {
    padding: 0;
    margin: 0;
    opacity: 0.4;
    transition: 0s;
  }
</style>