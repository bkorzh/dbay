// // Prevents additional console window on Windows in release, DO NOT REMOVE!!
// #![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// fn main() {
//     app_lib::run();
// }

// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// fn main() {
//   tauri::Builder::default()
//     .run(tauri::generate_context!())
//     .expect("error while running tauri application");
// }

// use tauri::api::process::Command;
use std::env;

// use std::env;
use std::path::PathBuf;


// switch?? 
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;

// use tauri::{Manager};


struct AppData {
    welcome_message: &'static str,
  }



// use tauri::async_runtime::spawn;


fn main() {

    // tauri::Builder::default()
    //     .plugin(tauri_plugin_shell::init())
    //     .run(tauri::generate_context!())
    //     .expect("error while running tauri application");



    println!("at very beginning");
    env::set_var("RUST_BACKTRACE", "full");
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init()) // YOU NEED THIS!! 
        // if you don't have the init line, then you get an error with app.shell() below
        .setup(|app| {
            let current_dir = PathBuf::from("/");

            // println!("starting"); // Print statement
            println!("hellooo??");
            
            println!("after shell ext import");

            
            // println!("after command event import");

            //   let (mut rx, child) = Command::new_sidecar("main")
            //       .expect("failed to create sidecar binary")
            //       .current_dir(current_dir) // Set the working directory
            //       .spawn()
            //       .expect("failed to spawn sidecar");

            //             app.manage(AppData {
            //     welcome_message: "Welcome to Tauri!",
            // });
            println!("after manage");

            let shell = app.shell();
            
            println!("shell made");
            let sid = shell.sidecar("main");
            println!("after sidecar but before unwrap");

            let sidecar_command = sid.unwrap();
            
            // let sidecar_command = app.shell().sidecar("main").unwrap();
            println!("after define sidecar_command");
            
            let sidecar_command = sidecar_command.current_dir(current_dir); // Set the working directory
            println!("after setting current directory");
            
            let (mut rx, child) = sidecar_command.spawn().expect("failed to spawn sidecar");
            println!("after spawning sidecar");

              


            // .current_dir(current_dir)

            println!("sidecar spawned"); // Print statement
            println!("child pid: {}", child.pid());

            // Spawn a task to read stdout
            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    match event {
                        CommandEvent::Stdout(line) => {
                            println!("sidecar stdout: {}", String::from_utf8_lossy(&line));
                        }
                        CommandEvent::Stderr(line) => {
                            eprintln!("sidecar stderr: {}", String::from_utf8_lossy(&line));
                        }
                        CommandEvent::Error(error) => {
                            eprintln!("sidecar error: {:?}", error);
                        }
                        CommandEvent::Terminated(payload) => {
                            println!("sidecar terminated with: {:?}", payload);
                            break;
                        }
                        _ => {}
                    }
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running Tauri application");

    
}



