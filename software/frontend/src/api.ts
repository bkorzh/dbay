

import type { SharedVsourceChange, VsourceChange } from './lib/addons/vsource/interface';


import type { SystemState } from './state/systemState.svelte';
import type { VMEParams } from './state/systemState.svelte';
import type { JsonSystemState, ServerInfo } from './state/systemState.svelte';
// import { fetch } from '@tauri-apps/plugin-http';

// // Send a GET request
// const response = await fetch('http://test.tauri.app/data.json', {
//   method: 'GET',
// });
// console.log(response.status); // e.g. 200
// console.log(response.statusText); // e.g. "OK"

let tauriFetch: typeof fetch | undefined;


// if ('__TAURI_INTERNALS__' in window || import.meta.env.DEV) {


if ('__TAURI_INTERNALS__' in window) {
    import('@tauri-apps/plugin-http').then(module => {

        console.log("using tuauri fetch");
        tauriFetch = module.fetch;


        // tauriFetch = fetch
    });
} else {
    console.log("using browser fetch");
}


function fetchWithConfig(url: string, method: string, body?: any): Promise<any> {
    const headers = { 'Content-Type': 'application/json' };
    const controller = new AbortController();
    const signal = controller.signal;

    // Specify the base URL of the different server
    const baseUrl = "http://127.0.0.1:8345";

    const config: RequestInit = {
        method,
        signal,
        headers,
        connectTimeout: 1
    }

    if (body) {
        config.body = JSON.stringify(body);
    }

    const isTauriOrVite = '__TAURI_INTERNALS__' in window;
    const fullUrl = isTauriOrVite ? `${baseUrl}${url}` : url;
    const fetchFunction = isTauriOrVite && tauriFetch ? tauriFetch : window.fetch;

    console.log("fullUrl: ", fullUrl);

    const result_promise = fetchFunction(fullUrl, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Fetch error:', error);
            throw new Error(`Failed to fetch: ${error.message}`);
        });

    return result_promise;
}



export function getFullState(): Promise<JsonSystemState> {
    return fetchWithConfig("/full-state", "GET");
}

// export function requestFullStateUpdate(state: SystemState): Promise<SystemState> {
//     return fetchWithConfig("/full-state", "PUT", state);
// }

export function initializeState(channel_number: number) {
    return fetchWithConfig("/initialize", "POST", { channel_number });
}



export function initializeVsource(params: VMEParams) {
    return fetchWithConfig("/initialize-vsource", "POST", params);
}


export function requestChannelUpdate(dst: VsourceChange, endpoint: string): Promise<VsourceChange> {
    return fetchWithConfig(endpoint, "PUT", dst);
}

export function requestSharedChannelUpdate(dst: SharedVsourceChange, endpoint: string): Promise<SharedVsourceChange> {
    return fetchWithConfig(endpoint, "PUT", dst);
}



export function initializeModule(slot: number, type: string) {
    return fetchWithConfig("/initialize-module", "POST", { slot, type });
}

export function serverInfo(): Promise<ServerInfo> {
    return fetchWithConfig("/server-info", "GET");
}



