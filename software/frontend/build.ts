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

const flatpak_directory = path.join(current_directory, "/src-tauri/flatpak");
const flatpak_resources_directory = path.join(current_directory, "/src-tauri/flatpak_resources");


async function folderExists(folder: string): Promise<boolean> {
    try {
        await readdir(folder);
        return true;
    } catch (err) {
        return false;
    }
}

if (!await folderExists(path.join(current_directory, "/src-tauri/resources"))) {
    await $`mkdir ${path.join(current_directory, "/src-tauri/resouces")}`
}

const sidecar_directory = path.join(current_directory, "/src-tauri/resources");


if (!values.frontend && !values.backend && !values.tauri && !values.flatpak && !values.all) {
    console.log("Please specify either --frontend, --backend, --tauri, --flatpak, or --all");
    process.exit(1);
}


function newExecutableName() {
    // let suffix
    // // have you installed rust? Refer to the tauri pre-requisites: https://v2.tauri.app/start/prerequisites/
    // if (process.platform === "win32") {
    //     suffix = execSync('rustc -Vv | Select-String "host:" | ForEach-Object {$_.Line.split(" ")[1]}', { shell: 'powershell.exe' }).toString().trim();
    // } else {
    //     suffix = execSync('rustc -Vv | grep host | cut -f2 -d\' \'').toString().trim();
    // }

    // console.log("using suffix: ", suffix);

    // // test this on ubuntu....
    // let new_main_name = path.join("dbaybackend" + "-" + suffix);

    // // remove last character from new_main_name (it's a \n newline probably)
    // // new_main_name = new_main_name.slice(0, -1);
    // if (process.platform === "win32") {
    //     new_main_name = new_main_name + ".exe";
    // }

    let new_main_name = "dbaybackend";

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
        executable_name = "dbaybackend.exe";
    } else {
        executable_name = "dbaybackend";
    }



    const file = Bun.file(path.join(backend_parent, "/dist/dbaybackend/", executable_name));

    // console.log("testing file: ", file);
    // console.log("testing file exists: ", await file.exists());





    if (await file.exists()) {
        // rename to include platform suffix
        await $`mv ${path.join(backend_parent, "/dist/dbaybackend/", executable_name)} ${path.join(backend_parent, "/dist/dbaybackend/" + newExecutableName())}`
    }

}


if (values.tauri || values.all) {
    console.log('\x1b[33m >>>>> Moving backend build to src-tauri/resources \x1b[0m');
    // having issues with use of * (wildcard) in mv command
    await $`cp -v ${path.join(backend_parent, "/dist/dbaybackend/", newExecutableName())} ${sidecar_directory}`
    await $`cp -R ${path.join(backend_parent, "/dist/dbaybackend/device-bay_internal/")} ${sidecar_directory}`


    console.log('\x1b[33m >>>>> Building tauri installers \x1b[0m');
    await $`bun run tauri build`;
}

if (values.flatpak) {
    console.log('\x1b[33m >>>>> Building flatpak installer \x1b[0m');
    // get the name of the file that ends in .deb
    // check if platform is not linux, and if so, exit
    if (process.platform !== "linux") {
        console.log("Flatpak can only be built on Linux");
        process.exit(1);
    }

    // Clean flatpak directory except template and desktop file
    await $`rm -rf ${flatpak_directory}`;
    await $`mkdir -p ${flatpak_directory}`;
    await $`cp ${flatpak_resources_directory}/* ${flatpak_directory}`


    let deb_file = execSync(`ls ./src-tauri/target/release/bundle/deb/ | grep .deb`).toString().trim();
    deb_file = deb_file.split("\n")[0];
    console.log("deb_file: ", deb_file);

    const deb_directory = "./src-tauri/target/release/bundle/deb/";
    await $`cp ${path.join(deb_directory, deb_file)} ${flatpak_directory}`


    await $`cp ./src-tauri/flatpak/device-bay-flatpak-template.yml ./src-tauri/flatpak/device-bay-flatpak.yml`

    // edit the manifest file (device-bay-flatpak.yml) to include the name of the deb file using sed
    await $`sed -i "s|<-deb-filename->|${deb_file}|g" ./src-tauri/flatpak/device-bay-flatpak.yml`

    //await $`cd ${flatpak_directory} && flatpak-builder --force-clean build-dir device-bay-flatpak.yml && flatpak-builder --repo=repo --force-clean build-dir device-bay-flatpak.yml && flatpak build-bundle repo device-bay.flatpak com.device.bay`
    // await $`flatpak-builder --repo=repo --force-clean build-dir device-bay-flatpak.yml`
    await $`cd ${flatpak_directory} && \
flatpak-builder --force-clean --user --repo=repo --install builddir device-bay-flatpak.yml && \
flatpak build-bundle repo device-bay.flatpak com.device.bay --runtime-repo=https://flathub.org/repo/flathub.flatpakrepo`
}
