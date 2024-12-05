import { spawn } from "child_process";
import path from "node:path";

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

// Start the frontend dev server
startProcess("npm", ["run", "tauri", "dev"], { cwd: current_directory });

// Start the backend dev server
startProcess("poetry", ["run", "fastapi", "dev", "main.py"], { cwd: backend_directory });