////////////////

// `bun build.ts --frontend` to build frontend
// `bun build.ts --backend` to build backend
// `bun build.ts --tauri` to build tauri
// `bun build.ts --all` to build frontend, then backend, then build the whole app installer with tauri


import { $ } from "bun";

import Bun from "bun";
import path from "node:path";
import { readdir } from "node:fs/promises";
import { parseArgs } from "util";
import { execSync } from "node:child_process";

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


const current_directory = import.meta.dir; // https://bun.sh/docs/api/import-meta

const dist_directory = path.join(current_directory, "/dist/");

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

if (!await folderExists(path.join(current_directory, "/src-tauri/python_binary"))) {
    await $`mkdir ${path.join(current_directory, "/src-tauri/python_binary")}`
}

const sidecar_directory = path.join(current_directory, "/src-tauri/python_binary");


if (!values.frontend && !values.backend && !values.tauri && !values.flatpak && !values.all) {
    console.log("Please specify either --frontend, --backend, --tauri, or --all");
    process.exit(1);
}


function newExecutableName() {
    let suffix
    // have you installed rust? Refer to the tauri pre-requisites: https://v2.tauri.app/start/prerequisites/
    if (process.platform === "win32") {
        suffix = execSync('rustc -Vv | Select-String "host:" | ForEach-Object {$_.Line.split(" ")[1]}', { shell: 'powershell.exe' }).toString().trim();
    } else {
        suffix = execSync('rustc -Vv | grep host | cut -f2 -d\' \'').toString().trim();
    }

    console.log("using suffix: ", suffix);

    // test this on ubuntu....
    let new_main_name = path.join("main" + "-" + suffix);

    // remove last character from new_main_name (it's a \n newline probably)
    // new_main_name = new_main_name.slice(0, -1);
    if (process.platform === "win32") {
        new_main_name = new_main_name + ".exe";
    }

    return new_main_name;
}

/////////////////////////////////
if (values.frontend || values.all) {
    console.log('\x1b[33m >>>>> Building frontend... \x1b[0m');
    await $`bun run build`;

    console.log('\x1b[33m >>>>> Moving compiled javascript, css, & html to /backend/backend/dbay_control/ \x1b[0m');
    // console.log("process.platform: ", process.platform);

    if (process.platform === "win32") {

        // rm -rf is not working in bun shell yet as of Bun 1.1.34
        // execSync(`del /Q /S ${path.join(output_directory,  "/*")}`, { stdio: 'inherit' });
        execSync(`rmdir /S /Q ${output_directory}`, { stdio: 'inherit' });
        execSync(`mkdir ${output_directory}`, { stdio: 'inherit' });
    } else {
        await $`rm -rf ${path.join(output_directory, "/*")}`;
    }
    // process.exit(1);

    await $`mkdir -p ${output_directory}`;
    await $`cp -R ${path.join(dist_directory, "assets")} ${output_directory}`;
    await $`cp ${path.join(dist_directory, "index.html")} ${output_directory}`;

}



if (values.backend || values.all) {

    if (process.platform === "win32") {
        execSync(`rmdir /S /Q ${path.join(backend_parent, "dist")}`, { stdio: 'inherit' });
        execSync(`rmdir /S /Q ${path.join(backend_parent, "build")}`, { stdio: 'inherit' });
    } else {
    // clean the output folders for pyinstaller
    await $`rm -rf ${path.join(backend_parent, "dist")}`;
    await $`rm -rf ${path.join(backend_parent, "build")}`;
    }


    /////////////////////////////////
    console.log('\x1b[33m >>>>> Running PyInstaller to build backend... \x1b[0m');


    await $`cd ${backend_parent} && poetry run pyinstaller backend/main.spec && cd ${current_directory}`;


    // const suffix = await $`echo "-$(uname -m)-unknown-$(uname -s | tr '[:upper:]' '[:lower:]')-gnu"`;

    let executable_name


    if (process.platform === "win32") {
        executable_name = "main.exe";
    } else {
        executable_name = "main";
    }



    const file = Bun.file(path.join(backend_parent, "/dist/main/", executable_name));

    // console.log("testing file: ", file);
    // console.log("testing file exists: ", await file.exists());


    


    if (await file.exists()) {
        // rename to include platform suffix
        await $`mv ${path.join(backend_parent, "/dist/main/", executable_name)} ${path.join(backend_parent, "/dist/main/" + newExecutableName())}`
    }

}


if (values.tauri || values.all) {
    console.log('\x1b[33m >>>>> Moving backend build to src-tauri/python_binary \x1b[0m');
    // having issues with use of * (wildcard) in mv command
    await $`cp -v ${path.join(backend_parent, "/dist/main/", newExecutableName())} ${sidecar_directory}`
    await $`cp -R ${path.join(backend_parent, "/dist/main/device-bay_internal/")} ${sidecar_directory}`


    console.log('\x1b[33m >>>>> Building tauri installers \x1b[0m');
    await $`bun run tauri build`;
}


