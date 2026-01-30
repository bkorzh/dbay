# FRONTEND for d-bay electronics control system

<div style="text-align:center">
  <img src="./svelte_snspd_bias_moc.png" alt="bias controll mockup" width="500">
</div>

This is a svelte 5 project. As of June 2024, svelte 5 is in release candidate stage, and the main tutorials on https://svelte.dev/ have not been updating to reflect the changed in version 5. 

See these pages for svelte 5 specific information:

https://svelte.dev/blog/svelte-5-release-candidate

https://svelte-5-preview.vercel.app/docs/introduction


## General Notes

[This webpage](https://www.section.io/engineering-education/svelte-with-vite-typescript-and-tailwind-css/) was helpul for setting up tailwind with vanilla svelte (not SvelteKit). One note is that the use of `purge` in `tailwind.config.js` is depreciated. Use `content: ['./src/**/*.{html,js,svelte,ts}']` instead.
