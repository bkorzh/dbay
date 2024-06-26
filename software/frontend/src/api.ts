

import type { SharedVsourceChange, VsourceChange } from './lib/addons/vsource/interface';


import type { SystemState } from './state/systemState.svelte';
import type { VMEParams } from './state/systemState.svelte';
import type { JsonSystemState } from './state/systemState.svelte';





function fetchWithConfig(url: string, method: string, body?: any): Promise<any> {
    const headers = { 'Content-Type': 'application/json' };
    const controller = new AbortController();
    const signal = controller.signal;

    const config: RequestInit = {
        method,
        signal,
        headers,
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            // console.log(response)
            return response.json();
        });
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


export function requestChannelUpdate(dst: VsourceChange, endpoint: string): Promise<VsourceChange>{
    return fetchWithConfig(endpoint, "PUT", dst);
}

export function requestSharedChannelUpdate(dst: SharedVsourceChange, endpoint: string): Promise<SharedVsourceChange>{
    return fetchWithConfig(endpoint, "PUT", dst);
}



export function initializeModule(slot: number, type: string) {
    return fetchWithConfig("/initialize-module", "POST", { slot, type });
}



