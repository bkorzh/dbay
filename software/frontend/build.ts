// Run this with "bun ./build.ts"


import { $ } from "bun";

import Bun from "bun";
import path from "node:path";
import { readdir } from "node:fs/promises";

// to stdout:
// const thing = await $`ls *.js`;


const current_directory = import.meta.dir; // https://bun.sh/docs/api/import-meta

const dist_directory = current_directory + "/dist";

const output_directory = path.join(current_directory, "../backend/backend/dbay_control");

const backend_parent = path.join(current_directory, "../backend");


async function folderExists(folder: string): Promise<boolean> {
    try {
        await readdir(folder);
        return true;
    } catch (err) {
        return false;
    }
}

if (!await folderExists(current_directory + "/src-tauri/python_binary")) {
    await $`mkdir ${current_directory + "/src-tauri/python_binary"}`
}

const sidecar_directory = current_directory + "/src-tauri/python_binary";


// let exists = false;
// try{
//   await readdir("./tmp");
//   exists = true;
// } catch{ /* handle error if you want */ }




// const backend_dist = path.join(backend_parent, "dist/*");
// const backend_build = path.join(backend_parent, "build/*");

// const files_inside_output_directory = output_directory + "/*";


// function stdoutToString(input: string[]): string {
//   const result = Bun.spawnSync(input);
//   return new TextDecoder().decode(result.stdout);
// }

// Bun.spawnSync(["npm", "run", "build"]);

await $`npm run build`;


await $`rm -rf ${output_directory + "/*"}`;


await $`cp -r ${dist_directory}/* ${output_directory}`;


// clean the output folders for pyinstaller
await $`rm -rf ${path.join(backend_parent, "dist")}`;
await $`rm -rf ${path.join(backend_parent, "build")}`;


// need to go to backend parent directory, spawn a process and activate poetry shell, then run pyinstaller backend/main.spec

console.log("process.platform: ", process.platform);


// this
await $`cd ${backend_parent} && poetry run pyinstaller backend/main.spec && cd ${current_directory}`;

console.log("before")

const suffix = await $`echo "-$(uname -m)-unknown-$(uname -s | tr '[:upper:]' '[:lower:]')-gnu"`;

console.log("suffix: ", suffix.text());

const file = Bun.file(path.join(backend_parent, "/dist/main/main"));

let new_main_name = path.join("main" + suffix.text());

// print new_main_name, with newlines shown as \n
console.log(new_main_name.replace(/\n/g, "\\n"));

// remove last character from new_main_name
new_main_name = new_main_name.slice(0, -1);

// print new_main_name, with newlines shown as \n
console.log(new_main_name.replace(/\n/g, "\\n"));


if (await file.exists()) {
    await $`mv ${path.join(backend_parent, "/dist/main/main")} ${path.join(backend_parent, "/dist/main/" + new_main_name)}`
}


// having issues with use of * (wildcard) in mv command
await $`cp -v ${path.join(backend_parent, "/dist/main/", new_main_name)} ${sidecar_directory}`
await $`cp -r ${path.join(backend_parent, "/dist/main/device-bay_internal/")} ${sidecar_directory}`



/// ugh having problems with tuari not recovnizing the binary file even though the suffix is correct


