import type { SharedVsourceChange, VsourceChange } from './lib/addons/vsource/interface';
import type { VsenseChange } from './lib/addons/vsense/interface';


import type { VMEParams } from './state/systemState.svelte';
import type { JsonSystemState, ServerInfo } from './state/systemState.svelte';
import { system_state } from './state/systemState.svelte';
import { syncRuntime } from './sync/runtime.svelte';

function sendCommand<T>(command: string, params: Record<string, unknown> = {}): Promise<T> {
    return syncRuntime.sendCommand<T>(command, params).then(ack => {
        if (!ack.result) throw new Error(`${command} did not return a result`);
        return ack.result;
    });
}

function inferVsourceCommand(dst: VsourceChange, endpoint?: string): string {
    const command = {
        "/dac4D/vsource/": "set_dac4d_vsource",
        "/dac16D/vsource/": "set_dac16d_vsource",
        "/dac16D/vsb/": "set_dac16d_vsb",
    }[endpoint ?? ""];

    if (command) return command;

    const moduleType = system_state.data[dst.module_index]?.core.type;
    if (moduleType === "dac4D") return "set_dac4d_vsource";
    if (moduleType === "dac16D") return "set_dac16d_vsource";
    throw new Error(`No voltage-source command for module type: ${moduleType ?? "unknown"}`);
}

export function initializeVsource(params: VMEParams): Promise<VMEParams> {
    return sendCommand<VMEParams>("initialize_vsource", { ...params });
}

export function requestChannelUpdate(dst: VsourceChange, endpoint?: string): Promise<VsourceChange> {
    return sendCommand<VsourceChange>(inferVsourceCommand(dst, endpoint), { ...dst });
}

export function requestSenseUpdate(dst: VsenseChange, endpoint?: string): Promise<VsenseChange> {
    if (endpoint && endpoint !== "/adc4D/vsense/") {
        throw new Error(`No sense command for endpoint: ${endpoint}`);
    }

    return sendCommand<VsenseChange>("set_adc4d_vsense", { ...dst });
}

export interface AdcPollingChange {
    module_index: number;
    running: boolean;
    frequency: number;
}

export function requestPollingUpdate(dst: AdcPollingChange): Promise<AdcPollingChange> {
    return sendCommand<AdcPollingChange>("set_adc4d_polling", { ...dst });
}

export function requestSharedChannelUpdate(dst: SharedVsourceChange, endpoint: string): Promise<SharedVsourceChange> {
    if (endpoint !== "/dac16D/vsource_shared/") {
        throw new Error(`No shared voltage-source command for endpoint: ${endpoint}`);
    }

    return sendCommand<SharedVsourceChange>("set_dac16d_vsource_shared", { ...dst });
}



export function initializeModule(slot: number, type: string): Promise<JsonSystemState> {
    return sendCommand<JsonSystemState>("initialize_module", { slot, type });
}

export function serverInfo(): Promise<ServerInfo> {
    return sendCommand<ServerInfo>("get_server_info");
}
