// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_http::init())
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

// use tauri::Manager;
// tauri::Builder::default().setup(|app| {
//     #[cfg(debug_assertions)] // only include this code on debug builds
//     {
//       let window = app.get_window("main").unwrap();
//       window.open_devtools();
//       window.close_devtools();
//     }
//     Ok(())
//   });
