import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig({
  // base: '/compiled_frontend/',  // You CAN'T use this for tauri builds...
  plugins: [tailwindcss(), svelte()],
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
