// Prevents additional console window on Windows in release
// #![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// use std::env;

// // use std::env;
// use std::path::PathBuf;

// // switch??
// use std::process::Command as StdCommand;
// use std::sync::{Arc, Mutex};
// use tauri_plugin_shell::process::CommandEvent;
// use tauri_plugin_shell::ShellExt;
// use std::io::{self, Write};
// use tauri::path::BaseDirectory;
// use tauri::Manager;

// fn main() {

//     env::set_var("RUST_BACKTRACE", "full");

//     // Shared state to store the PID
//     let pid_state = Arc::new(Mutex::new(None));

//     tauri::Builder::default()
//         .plugin(tauri_plugin_shell::init())
//         .plugin(tauri_plugin_http::init())
//         .plugin(tauri_plugin_fs::init())
//         .setup({
//             let pid_state = Arc::clone(&pid_state);
//             move |app| {
//                 let resource_path = app.path().resolve("device-bay_internal/", BaseDirectory::Resource)?;
//                 println!("Resource path: {:?}", resource_path);
//                 let current_dir = PathBuf::from("/");
//                 let shell = app.shell();
//                 let sid = shell.sidecar("dbaybackend");
//                 let sidecar_command = sid.unwrap();
//                 let sidecar_command = sidecar_command.current_dir(current_dir); // Set the working directory
//                 let (mut rx, child) = sidecar_command.spawn().expect("failed to spawn sidecar");
//                 println!("child pid: {}", child.pid());
//                 {
//                     let mut pid = pid_state.lock().unwrap();
//                     *pid = Some(child.pid());
//                 }

//                 // Spawn a task to read stdout
//                 #[cfg(not(dev))] // do not run sidecar in dev mode: https://github.com/tauri-apps/tauri/discussions/6453
//                 tauri::async_runtime::spawn(async move {
//                     while let Some(event) = rx.recv().await {
//                         match event {
//                             CommandEvent::Stdout(line) => {
//                                 println!("sidecar stdout: {}", String::from_utf8_lossy(&line));
//                                 io::stdout().flush().unwrap(); // Flush stdout
//                             }
//                             CommandEvent::Stderr(line) => {
//                                 eprintln!("sidecar stderr: {}", String::from_utf8_lossy(&line));
//                                 io::stdout().flush().unwrap(); // Flush stdout
//                             }
//                             CommandEvent::Error(error) => {
//                                 eprintln!("sidecar error: {:?}", error);
//                                 io::stdout().flush().unwrap(); // Flush stdout
//                             }
//                             CommandEvent::Terminated(payload) => {
//                                 println!("sidecar terminated with: {:?}", payload);
//                                 io::stdout().flush().unwrap(); // Flush stdout
//                                 break;
//                             }
//                             _ => {}
//                         }
//                     }
//                 });

//                 Ok(())
//             }
//         })
//         .on_window_event({
//             let pid_state = Arc::clone(&pid_state);
//             move |_window, event| {
//                 // println!("Window event triggered: {:?}", event);
//                 if let tauri::WindowEvent::CloseRequested { .. } = event {
//                     // Retrieve the PID from the shared state
//                     let pid = {
//                         let pid = pid_state.lock().unwrap();
//                         *pid
//                     };

//                     if let Some(pid) = pid {
//                         println!("Killing process with PID: {}", pid);
//                         match kill_process(pid) {
//                             Ok(_) => println!("Process killed successfully."),
//                             Err(e) => eprintln!("Failed to kill process: {}", e),
//                         }
//                     }
//                 }
//             }
//         })
//         .run(tauri::generate_context!())
//         .expect("error while running Tauri application");
// }

use std::env;
use std::io::{self, BufRead, BufReader, Write};
// use std::path::PathBuf;
use std::process::Command;
use std::sync::{Arc, Mutex};
// use std::thread;
use tauri::path::BaseDirectory;
use tauri::Manager;

fn main() {
    env::set_var("RUST_BACKTRACE", "full");
    let pid_state = Arc::new(Mutex::new(None));

    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .plugin(tauri_plugin_fs::init())
        .setup({
            let pid_state = Arc::clone(&pid_state);
            move |app| {
                let resource_path = app.path().resolve("resources", BaseDirectory::Resource)?;
                println!("Resource path: {:?}", resource_path);

                let backend_path = resource_path.join("dbaybackend");
                println!("Backend path: {:?}", backend_path);

                // Spawn the backend process
                let child = Command::new(backend_path)
                    .spawn()
                    .expect("failed to spawn backend");

                println!("child pid: {}", child.id());

                // Store the PID
                {
                    let mut pid = pid_state.lock().unwrap();
                    *pid = Some(child.id());
                }

                // Handle process output
                #[cfg(not(dev))]
                {
                    let mut child = child;
                    tauri::async_runtime::spawn(async move {
                        if let Some(stdout) = child.stdout.take() {
                            let reader = BufReader::new(stdout);
                            for line in reader.lines() {
                                if let Ok(line) = line {
                                    println!("backend stdout: {}", line);
                                    io::stdout().flush().unwrap();
                                }
                            }
                        }

                        // Wait for the process to finish
                        match child.wait() {
                            Ok(status) => println!("Backend process exited with: {:?}", status),
                            Err(e) => eprintln!("Error waiting for backend process: {}", e),
                        }
                    });
                }

                Ok(())
            }
        })
        .on_window_event({
            let pid_state = Arc::clone(&pid_state);
            move |_window, event| {
                if let tauri::WindowEvent::CloseRequested { .. } = event {
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

// Keep the existing kill_process function unchanged

fn kill_process(pid: u32) -> Result<(), Box<dyn std::error::Error>> {
    #[cfg(unix)]
    {
        let pid_str = pid.to_string();
        println!("Sending INT signal to process with PID: {}", pid_str);

        let mut kill = Command::new("kill")
            .args(["-s", "SIGINT", &pid_str])
            .spawn()?;
        kill.wait()?;
    }
    #[cfg(windows)]
    {
        let pid_str = pid.to_string();
        println!("Sending taskkill to process with PID: {}", pid_str);

        let mut kill = Command::new("taskkill")
            .args(["/PID", &pid_str, "/F"])
            .spawn()?;
        kill.wait()?;
    }

    Ok(())
}
