<script>

 let { onclick } = $props()

function handleKeyDown(event) {
    if (event.key === "Enter" || event.key === " ") {
      event.target.click();
    }
  }
</script>

<div class="chev-button" {onclick} onkeydown={handleKeyDown} role="button" tabindex="0">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" stroke="currentColor" class="bi bi-chevron-compact-up" viewBox="0 0 16 16">
        <path fill-rule="evenodd" d="M7.776 5.553a.5.5 0 0 1 .448 0l6 3a.5.5 0 1 1-.448.894L8 6.56 2.224 9.447a.5.5 0 1 1-.448-.894l6-3z"
        stroke-width=".3"/>
      </svg>
</div>


<style>

  .chev-button {
    position: relative;
    color: var(--icon-color);
    padding: 0.5rem 0.35rem;
    background-color: var(--body-color);
    transition: background-color 0.1s ease-in-out;
    border-radius: 0.2rem;
    -webkit-transition-duration: 0.1s;
    transition-duration: 0.1s;
    text-decoration: none;
    overflow: hidden;
    cursor: pointer;
    user-select: none
  }

  .chev-button:hover {
    background-color: var(--hover-body-color);
  }



  .chev-button:after {
    content: "";
    display: block;
    position: absolute;
    left: 0;
    bottom: 0;
    width: 0;
    padding-top: 300%;
    padding-right: 300%;
    margin-bottom: -20px !important;
    margin-top: -0%;
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