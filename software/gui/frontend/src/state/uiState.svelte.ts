// export interface UIState {
//   show_module_adder: boolean;
//   show_source_reinit: boolean;
//   colorMode: boolean;
// }

// export let ui_state: UIState = {
//   show_module_adder: $state(false),
//   show_source_reinit: $state(false),
//   colorMode: $state(false)
// };

export class UIState {
  show_module_adder: boolean = $state(false);
  show_remote_access: boolean = $state(false);
  show_source_reinit: boolean = $state(false);
  colorMode: boolean = $state(false);

  constructor(show_module_adder = false, show_source_reinit = false, colorMode = false, show_remote_access = false) {
    this.show_module_adder = show_module_adder;
    this.show_source_reinit = show_source_reinit;
    this.show_remote_access = show_remote_access;
    this.colorMode = colorMode;
  }
}

export let ui_state = new UIState();

const isDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
setMode(isDarkMode);

window.matchMedia('(prefers-color-scheme: dark)')
  .addEventListener('change', ({ matches }) => {
    setMode(matches);
  })

export function setMode(value: boolean) {

  ui_state.colorMode = value;

  // update page styling
  if (value) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }

  // store the theme as a local override
  localStorage.theme = value ? "dark" : "light";

  // if the toggled-to theme matches the system defined theme, clear the local override
  // this effectively provides a way to override or revert to "automatic" setting mode
  if (
    window.matchMedia(`(prefers-color-scheme: ${localStorage.theme})`).matches
  ) {
    localStorage.removeItem("theme");
  }

  return value;
}