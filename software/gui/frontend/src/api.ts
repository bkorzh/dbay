

import type { SharedVsourceChange, VsourceChange } from './lib/addons/vsource/interface';
import type { VsenseChange } from './lib/addons/vsense/interface';


import type { SystemState } from './state/systemState.svelte';
import type { VMEParams } from './state/systemState.svelte';
import type { JsonSystemState, ServerInfo } from './state/systemState.svelte';
import { syncRuntime } from './sync/runtime.svelte';
// import { fetch } from '@tauri-apps/plugin-http';

// // Send a GET request
// const response = await fetch('http://test.tauri.app/data.json', {
//   method: 'GET',
// });
// console.log(response.status); // e.g. 200
// console.log(response.statusText); // e.g. "OK"

type FetchLike = (
    input: string | URL | Request,
    init?: RequestInit,
) => Promise<Response>;

let tauriFetch: FetchLike | undefined;


// if ('__TAURI_INTERNALS__' in window || import.meta.env.DEV) {

const hasWindow = typeof window !== "undefined";

if (hasWindow && '__TAURI_INTERNALS__' in window) {
    import('@tauri-apps/plugin-http').then(module => {

        console.log("using tuauri fetch");
        tauriFetch = (input, init) => module.fetch(input, init);


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
        headers
    }

    if (body) {
        config.body = JSON.stringify(body);
    }

    const isTauri = hasWindow && '__TAURI_INTERNALS__' in window;
    const useBackendBaseUrl = isTauri || import.meta.env.DEV;
    const fullUrl = useBackendBaseUrl ? `${baseUrl}${url}` : url;
    const fetchFunction = isTauri && tauriFetch ? tauriFetch : globalThis.fetch;

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
    const command = {
        "/dac4D/vsource/": "set_dac4d_vsource",
        "/dac16D/vsource/": "set_dac16d_vsource",
    }[endpoint];

    if (command) {
        return syncRuntime.sendCommand<VsourceChange>(command, { ...dst }).then(ack => {
            if (!ack.result) throw new Error(`${command} did not return a result`);
            return ack.result;
        });
    }

    return fetchWithConfig(endpoint, "PUT", dst);
}

export function requestSenseUpdate(dst: VsenseChange, endpoint: string): Promise<VsenseChange> {
    if (endpoint === "/adc4D/vsense/") {
        return syncRuntime.sendCommand<VsenseChange>("set_adc4d_vsense", { ...dst }).then(ack => {
            if (!ack.result) throw new Error("set_adc4d_vsense did not return a result");
            return ack.result;
        });
    }

    return fetchWithConfig(endpoint, "PUT", dst);
}

export function requestSharedChannelUpdate(dst: SharedVsourceChange, endpoint: string): Promise<SharedVsourceChange> {
    if (endpoint === "/dac16D/vsource_shared/") {
        return syncRuntime.sendCommand<SharedVsourceChange>("set_dac16d_vsource_shared", { ...dst }).then(ack => {
            if (!ack.result) throw new Error("set_dac16d_vsource_shared did not return a result");
            return ack.result;
        });
    }

    return fetchWithConfig(endpoint, "PUT", dst);
}



export function initializeModule(slot: number, type: string) {
    return fetchWithConfig("/initialize-module", "POST", { slot, type });
}

export function serverInfo(): Promise<ServerInfo> {
    return fetchWithConfig("/server-info", "GET");
}
