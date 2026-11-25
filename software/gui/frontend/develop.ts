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
// The uv project root, not the inner package directory: `backend.main` only
// imports when the project root is the working directory.
const backend_directory = path.join(current_directory, "../backend");

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


// Start the backend dev server. The backend is a Starlette app served by
// uvicorn; --reload-dir keeps the file watcher off .venv.
// uv run uvicorn backend.main:app --port 8345 --host 0.0.0.0 --reload --reload-dir backend
startProcess("uv", ["run", "uvicorn", "backend.main:app", "--port", "8345", "--host", "0.0.0.0", "--reload", "--reload-dir", "backend"], { cwd: backend_directory });


// wait for 0.3 second
await new Promise(resolve => setTimeout(resolve, 300));

// Start the frontend dev server

if (values.tauri) {
    startProcess("bun", ["run", "tauri", "dev"], { cwd: current_directory });
} else {
    console.log("Starting browser dev server...");
    startProcess("bun", ["run", "dev"], { cwd: current_directory });
}
