// fn main() {
//     app_lib::run();
// }

// Prevents additional console window on Windows in release, DO NOT REMOVE!!

// #![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]




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
use std::process::Command as StdCommand;
use std::sync::{Arc, Mutex};
use tauri_plugin_shell::process::CommandEvent;
use tauri_plugin_shell::ShellExt;
use std::io::{self, Write};


// use tauri::async_runtime::spawn;

fn main() {

    env::set_var("RUST_BACKTRACE", "full");

    // Shared state to store the PID
    let pid_state = Arc::new(Mutex::new(None));

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_http::init()) // YOU NEED THIS!!
        // if you don't have the init line, then you get an error with app.shell() below
        .setup({
            let pid_state = Arc::clone(&pid_state);
            move |app| {
                let current_dir = PathBuf::from("/");

                let shell = app.shell();

                let sid = shell.sidecar("main");

                let sidecar_command = sid.unwrap();

                // println!("this is the directory: {:?}", current_dir);

                // let alternate_dir = PathBuf::from("../share/device-bay/");

                // if !alternate_dir.exists() {
                //     println!("Alternate directory does not exist: {:?}", alternate_dir);
                // }

                let sidecar_command = sidecar_command.current_dir(current_dir); // Set the working directory

                let (mut rx, child) = sidecar_command.spawn().expect("failed to spawn sidecar");

                println!("child pid: {}", child.pid());

                // let pid = child.pid();
                // Store the PID in the shared state
                {
                    let mut pid = pid_state.lock().unwrap();
                    *pid = Some(child.pid());
                }

                // Spawn a task to read stdout
                #[cfg(not(dev))] // do not run sidecar in dev mode: https://github.com/tauri-apps/tauri/discussions/6453
                tauri::async_runtime::spawn(async move {
                    while let Some(event) = rx.recv().await {
                        match event {
                            CommandEvent::Stdout(line) => {
                                println!("sidecar stdout: {}", String::from_utf8_lossy(&line));
                                io::stdout().flush().unwrap(); // Flush stdout
                            }
                            CommandEvent::Stderr(line) => {
                                eprintln!("sidecar stderr: {}", String::from_utf8_lossy(&line));
                                io::stdout().flush().unwrap(); // Flush stdout
                            }
                            CommandEvent::Error(error) => {
                                eprintln!("sidecar error: {:?}", error);
                                io::stdout().flush().unwrap(); // Flush stdout
                            }
                            CommandEvent::Terminated(payload) => {
                                println!("sidecar terminated with: {:?}", payload);
                                io::stdout().flush().unwrap(); // Flush stdout
                                break;
                            }
                            _ => {}
                        }
                    }
                });

                Ok(())
            }
        })
        .on_window_event({
            let pid_state = Arc::clone(&pid_state);
            move |_window, event| {
                // println!("Window event triggered: {:?}", event);
                if let tauri::WindowEvent::CloseRequested { .. } = event {
                    // Retrieve the PID from the shared state
                    let pid = {
                        let pid = pid_state.lock().unwrap();
                        *pid
                    };

                    if let Some(pid) = pid {
                        println!("Killing process with PID: {}", pid);
                        match kill_process(pid) {
                            Ok(_) => println!("Process killed successfully."),
                            Err(e) => eprintln!("Failed to kill process: {}", e),
                        }
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running Tauri application");
}

fn kill_process(pid: u32) -> Result<(), Box<dyn std::error::Error>> {
    #[cfg(unix)]
    {
        let pid_str = pid.to_string();
        println!("Sending INT signal to process with PID: {}", pid_str);

        let mut kill = StdCommand::new("kill")
            .args(["-s", "SIGINT", &pid_str])
            .spawn()?;
        kill.wait()?;
    }

    #[cfg(windows)]
    {
        let pid_str = pid.to_string();
        println!("Sending taskkill to process with PID: {}", pid_str);

        let mut kill = StdCommand::new("taskkill")
            .args(["/PID", &pid_str, "/F"])
            .spawn()?;
        kill.wait()?;
    }

    Ok(())
}
