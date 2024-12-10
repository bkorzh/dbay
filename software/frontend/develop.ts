import { spawn } from "child_process";
import path from "node:path";
import { parseArgs } from "util";

const { values, positionals } = parseArgs({
    args: Bun.argv,
    options: {
        tauri: {
            type: 'boolean',
        },

    },
    strict: true,
    allowPositionals: true,
});


const current_directory = import.meta.dir;
const backend_directory = path.join(current_directory, "../backend/backend");

// Function to start a process and pipe its output to the current terminal
function startProcess(command: string, args: string[], options: { cwd?: string }) {
    const process = spawn(command, args, { stdio: "inherit", ...options });

    process.on("close", (code) => {
        console.log(`${command} process exited with code ${code}`);
    });

    process.on("error", (err) => {
        console.error(`Failed to start ${command} process: ${err}`);
    });
}


// Start the backend dev server
// uv run fastapi dev main.py --port 8345 --host 0.0.0.0
startProcess("uv", ["run", "fastapi", "dev", "main.py", "--port", "8345", "--host", "0.0.0.0"], { cwd: backend_directory });


// wait for 0.3 second
await new Promise(resolve => setTimeout(resolve, 300));

// Start the frontend dev server

if (values.tauri) {
    startProcess("bun", ["run", "tauri", "dev"], { cwd: current_directory });
} else {
    startProcess("bun", ["run", "dev"], { cwd: current_directory });
}
