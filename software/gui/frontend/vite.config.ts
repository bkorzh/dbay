import { defineConfig } from 'vite'
// import postcss from './postcss.config.js';
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  // base: '/dbay_control/',  // You CAN'T use this for tauri builds...
  plugins: [svelte()],
  // css: {
  //   postcss
  // },
  // build: {
  //   rollupOptions: {
  //     output: {
  //       // if I wanted to disable cache busting for the .js file
  //       // Though I don't know a way to disable it for css
  //       // entryFileNames: `[name].js`
  //     }
  //   }
  // }
})
