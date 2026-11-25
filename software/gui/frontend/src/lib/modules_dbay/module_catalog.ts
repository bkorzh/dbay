/**
 * Every module type the frontend knows about, described once.
 *
 * This file is the single source for a module's presentation: the title in its
 * heading, the label and blurb in the module adder, and its icon. Before it
 * existed, each of those lived in a different file, so adding a module meant
 * remembering four places and a module could end up with (say) artwork in its
 * heading and a placeholder in the adder.
 *
 * Deliberately free of imports. `ModuleHeading` and `ModuleAdder` both read it,
 * and so does `index.svelte.ts`, which is imported by the module components
 * themselves — anything imported here would risk an import cycle.
 *
 * The class and component bound to each type live in `index.svelte.ts`, which
 * checks at load that the two lists agree. `module_registry.test.ts` fails the
 * build if they drift.
 */

export const UNKNOWN_MODULE_ICON = "/assets/unknown_icon.svg";

export interface ModuleCatalogEntry {
  /** Matches the backend's `core.type` and `module_type` exactly. */
  type: string;
  /** Short name, shown in the module adder's dropdown. */
  label: string;
  /** Title shown in the module's heading bar. */
  title: string;
  /** One-line description, shown under the label in the adder. */
  description: string;
  icon: string;
  /** False for types a user cannot add to a slot. Defaults to true. */
  addable?: boolean;
  /** True for types only offered when the backend reports dev_mode. */
  devOnly?: boolean;
}

export const MODULE_CATALOG: ModuleCatalogEntry[] = [
  {
    type: "empty",
    label: "empty",
    title: "Empty",
    description: "an empty rack slot",
    icon: UNKNOWN_MODULE_ICON,
    addable: false,
  },
  {
    type: "dac4D",
    label: "dac4D",
    title: "Voltage Source",
    description: "4 ch. differential",
    icon: "/assets/dac4D_icon.svg",
  },
  {
    type: "adc4D",
    label: "adc4D",
    title: "Voltage Sensor",
    description: "5 ch. voltage sensing",
    icon: "/assets/adc4D_icon.svg",
  },
  {
    type: "dac16D",
    label: "dac16D",
    title: "16 Ch. Voltage Source",
    description: "16 ch. differential",
    icon: "/assets/dac16D_icon.svg",
  },
  {
    // Not real hardware: the worked example in the Adding a Module guide. It has
    // no icon of its own, and dev_mode keeps it out of a normal install.
    type: "demoD",
    label: "demoD",
    title: "Demo Module",
    description: "tutorial module (dev only)",
    icon: UNKNOWN_MODULE_ICON,
    devOnly: true,
  },
];

const byType = new Map(MODULE_CATALOG.map((entry) => [entry.type, entry]));

export function moduleCatalogEntry(type: string): ModuleCatalogEntry | undefined {
  return byType.get(type);
}

/** The heading title for a type; falls back to the type itself. */
export function moduleTitle(type: string): string {
  return byType.get(type)?.title ?? type;
}

/** The icon for a type; unknown types get the question-mark placeholder. */
export function moduleIcon(type: string): string {
  return byType.get(type)?.icon ?? UNKNOWN_MODULE_ICON;
}

/**
 * What the module adder should offer. `devMode` comes from the backend, so a
 * released app never lists dev-only types.
 */
export function addableModules(devMode: boolean): ModuleCatalogEntry[] {
  return MODULE_CATALOG.filter(
    (entry) => entry.addable !== false && (!entry.devOnly || devMode),
  );
}
