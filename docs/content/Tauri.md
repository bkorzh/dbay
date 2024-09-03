

Notes from getting [tauri](https://tauri.app/) working:

1. I had to remove the `dbay_control` base directory in `vite.config.ts`:
```ts
import { defineConfig } from 'vite'
// import postcss from './postcss.config.js';
import { svelte } from '@sveltejs/vite-plugin-svelte'
// https://vitejs.dev/config/
export default defineConfig({
// base: '/dbay_control/', // You CAN'T use this for tauri builds...
plugins: [svelte()],
// css: {
// postcss
// },
// build: {
// rollupOptions: {
// output: {
// // if I wanted to disable cache busting for the .js file
// // Though I don't know a way to disable it for css
// // entryFileNames: `[name].js`
// }
// }
// }
})
```

I eventually figured this out after (a) turning on the dev tools feature for tauri builds. This showed me that there seemed to be MIME type errors for javascript and css. It turns out the directory just wasn't working for the javascript and css. The tauri webview couldn't find them. It found them when I removed the `dbay_control` portion of the address. Huh. 

2. Inside the `api.ts` file, I did some checks to get the fastapi-served (for web browser access) and tauri-served versions of the app to behave the same. 
```ts
const baseUrl = "http://127.0.0.1:8000";

// other code...

let isTauriOrVite = false;

if ('__TAURI_INTERNALS__' in window || import.meta.env.DEV) {
isTauriOrVite = true;
}
const fullUrl = isTauriOrVite ? `${baseUrl}${url}` : url;
```

With this setup, the only thing that doesn't connect to the python server correctly is `npm run preview` (serving the built program directly from node). This is because that `meta.env.DEV` feature thing is no longer there or `true`, but the app is being served by something other than the python webserver. I've set it up so that any direct-browser access will go to the python webserver. 

For now, I'm using `npm run build` to build the frontend, and `npm run migrate` to move the built files to `backend/backend/dbay_control` which is where the static assets are served from with this python code in `main.py`:

```python
app.mount(
	"/dbay_control/",
	StaticFiles(directory=Path(BASE_DIR, "dbay_control")),
	name="",
)
@app.get("/", response_class=HTMLResponse)
async def return_index(request: Request):
	mimetypes.add_type('application/javascript', '.js')
	return FileResponse(Path(BASE_DIR, "dbay_control", "index.html"))
```

3. When you first search for [how to detect if you're in a browser or in tauri](https://github.com/tauri-apps/tauri/discussions/6119) , the suggestion is to use `window.__TAURI__`. During my debugging with the above issues I upgraded to tauri v2, which no longer has the `__TAURI__` namespace. So I'm using `__TAURI_INTERNALS__` instead. 