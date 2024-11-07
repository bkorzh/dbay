////////////////

// `bun build.ts --frontend` to build frontend
// `bun build.ts --backend` to build backend
// `bun build.ts --tauri` to build tauri
// `bun build.ts --all` to build frontend, then backend, then build the whole app installer with tauri


import { $ } from "bun";

import Bun from "bun";
import path from "node:path";
import { readdir } from "node:fs/promises";
// import { process } from "node:process";
import { parseArgs } from "util";

const { values, positionals } = parseArgs({
    args: Bun.argv,
    options: {
        frontend: {
            type: 'boolean',
        },
        backend: {
            type: 'boolean',
        },
        tauri: {
            type: 'boolean',
        },
        flatpak: {
            type: 'boolean',
        },
        all: {
            type: 'boolean',
        },
    },
    strict: true,
    allowPositionals: true,
});


// if (values.frontend || values.all) {
//     console.log("Building frontend...");
// }


// process.exit(0);


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


if (!values.frontend && !values.backend && !values.tauri && values.flatpak && !values.all) {
    console.log("Please specify either --frontend, --backend, --tauri, or --all");
    process.exit(1);
}

/////////////////////////////////
if (values.frontend || values.all) {
    console.log('\x1b[33m >>>>> Building frontend... \x1b[0m');
    await $`npm run build`;

    console.log('\x1b[33m >>>>> Moving compiled javascript, css, & html to /backend/backend/dbay_control/ \x1b[0m');
    await $`rm -rf ${output_directory + "/*"}`;
    await $`cp -r ${dist_directory}/* ${output_directory}`;

}

if (values.backend || values.all) {
    // clean the output folders for pyinstaller
    await $`rm -rf ${path.join(backend_parent, "dist")}`;
    await $`rm -rf ${path.join(backend_parent, "build")}`;



    // console.log("process.platform: ", process.platform);

    /////////////////////////////////
    console.log('\x1b[33m >>>>> Running PyInstaller to build backend... \x1b[0m');


    await $`cd ${backend_parent} && poetry run pyinstaller backend/main.spec && cd ${current_directory}`;


    // something like "-x86_64-unknown-linux-gnu"
    const suffix = await $`echo "-$(uname -m)-unknown-$(uname -s | tr '[:upper:]' '[:lower:]')-gnu"`;

    // console.log("suffix: ", suffix.text());

    const file = Bun.file(path.join(backend_parent, "/dist/main/main"));

    let new_main_name = path.join("main" + suffix.text());

    // remove last character from new_main_name (it's a \n newline probably)
    new_main_name = new_main_name.slice(0, -1);


    if (await file.exists()) {
        await $`mv ${path.join(backend_parent, "/dist/main/main")} ${path.join(backend_parent, "/dist/main/" + new_main_name)}`
    }

}


if (values.tauri || values.all) {
    console.log('\x1b[33m >>>>> Moving backend build to src-tauri/python_binary \x1b[0m');
    // having issues with use of * (wildcard) in mv command
    await $`cp -v ${path.join(backend_parent, "/dist/main/", new_main_name)} ${sidecar_directory}`
    await $`cp -r ${path.join(backend_parent, "/dist/main/device-bay_internal/")} ${sidecar_directory}`


    console.log('\x1b[33m >>>>> Building tauri installers \x1b[0m');
    await $`npm run tauri build`;
}


