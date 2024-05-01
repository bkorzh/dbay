## SNSPD Svelte Bias Controll

**Why use this over SvelteKit?**

- It brings its own routing solution which might not be preferable for some users.
- It is first and foremost a framework that just happens to use Vite under the hood, not a Vite app.

<!-- ![bias controll mockup](./svelte_snspd_bias_moc.png) -->

<div style="text-align:center">
  <img src="./svelte_snspd_bias_moc.png" alt="bias controll mockup" width="500">
</div>

[This webpage](https://www.section.io/engineering-education/svelte-with-vite-typescript-and-tailwind-css/) was helpul for setting up tailwind with vanilla svelte (not SvelteKit). One note is that the use of `purge` in `tailwind.config.js` is depreciated. Use `content: ['./src/**/*.{html,js,svelte,ts}']` instead.
