
import type { ChannelChange } from './state/systemState';
import type { Module4chState, ChState, SystemState } from './state/systemState';
import type { VMEParams } from './state/systemState';





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
            return response.json();
        });
}



export function getFullState() {
    return fetchWithConfig("/full-state", "GET");
}

export function requestFullStateUpdate(state: SystemState): Promise<SystemState> {
    return fetchWithConfig("/full-state", "PUT", state);
}

export function initializeState(channel_number: number) {
    return fetchWithConfig("/initialize", "POST", { channel_number });
}



export function initializeVsource(params: VMEParams) {
    return fetchWithConfig("/initialize-vsource", "POST", params);
}


export function requestChannelUpdate(dst: ChannelChange) {
    return fetchWithConfig("/channel", "PUT", dst);
}



export function initializeModule(slot: number, type: string) {
    return fetchWithConfig("/initialize-module", "POST", { slot, type });
}


// export function initializeState(channel_number: number) {
//     return fetch("/initialize", {
//         method: "POST",
//         signal: signal,
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({channel_number})
//     })
// }

// export function initializeVsouce(params: VsourceParams) {
//     return fetch("/initialize-vsource", {
//         method: "POST",
//         signal: signal,
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(params)
//     })
// }


// export function initializeModule(slot: number, type: string) {
//     return fetch("/initialize-module", {
//         method: "POST",
//         signal: signal,
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({slot, type})
//     }).then(response => {
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
//         return response.json();
//     })
// }

// const controller = new AbortController()
// const signal = controller.signal

// export function requestChannelUpdate(dst: ChannelChange) {
//     // console.log("dst: ", dst)
//     return fetch("/channel", {
//         method: "PUT",
//         signal: signal,
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(dst)
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
//         // console.log("response: ", response.json());
//         return response.json();
//     })
// }

// export function getFullState() {
//     return fetch("/full-state", {
//         method: "GET",
//         signal: signal,
//     })
//     .then(response => {
//         if (!response.ok || !response.headers.get('Content-Type')?.includes('application/json')) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
//         return response.json();
//     })
// }



// export function requestFullStateUpdate(state: SystemState): Promise<SystemState> {
//     return fetch("/full-state", {
//         method: "PUT",
//         signal: signal,
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(state)
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
//         return response.json();
//     })

// }


