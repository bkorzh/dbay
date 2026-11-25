/**
 * Guards the module registry against drift.
 *
 * Registering a module means two edits: a presentation entry in
 * `module_catalog.ts` and a code binding in `index.svelte.ts`. Everything else —
 * the module adder's list, the heading title, the icon — is derived. These tests
 * fail if the two lists ever disagree, which is what used to happen silently and
 * showed up only when a user picked the broken entry.
 */

import { beforeAll, describe, it, expect, vi } from "vitest";
import {
  MODULE_CATALOG,
  UNKNOWN_MODULE_ICON,
  addableModules,
  moduleCatalogEntry,
  moduleIcon,
  moduleTitle,
} from "../lib/modules_dbay/module_catalog";

let MODULE_BINDINGS: Record<string, { component?: unknown }>;
let assertRegistryMatchesCatalog: () => string[];

beforeAll(async () => {
  // The bindings live beside the module components, and importing those reaches
  // uiState, which touches window and document at import time. Stubbing the two
  // globals it needs is cheaper than adding a DOM implementation to the test
  // dependencies, and this suite never renders anything.
  vi.stubGlobal("window", {
    matchMedia: () => ({
      matches: false,
      addEventListener: () => {},
      removeEventListener: () => {},
    }),
  });
  vi.stubGlobal("document", {
    documentElement: { classList: { add: () => {}, remove: () => {} } },
  });
  vi.stubGlobal("localStorage", { getItem: () => null, setItem: () => {} });

  const registry = await import("../lib/modules_dbay/index.svelte");
  MODULE_BINDINGS = registry.MODULE_BINDINGS as typeof MODULE_BINDINGS;
  assertRegistryMatchesCatalog = registry.assertRegistryMatchesCatalog;
});

describe("module catalog and bindings", () => {
  it("cover exactly the same module types", () => {
    // The message is the useful part of this failing: it names what to fix.
    expect(assertRegistryMatchesCatalog()).toEqual([]);
  });

  it("agree on type strings between the two lists", () => {
    expect(Object.keys(MODULE_BINDINGS).sort()).toEqual(
      MODULE_CATALOG.map((entry) => entry.type).sort(),
    );
  });

  it("gives every addable module a component to draw it", () => {
    for (const entry of addableModules(true)) {
      expect(
        MODULE_BINDINGS[entry.type]?.component,
        `${entry.type} is addable but has no component`,
      ).toBeDefined();
    }
  });

  it("has no duplicate types", () => {
    const types = MODULE_CATALOG.map((entry) => entry.type);
    expect(new Set(types).size).toBe(types.length);
  });

  it("gives every entry a label, title, description, and icon", () => {
    for (const entry of MODULE_CATALOG) {
      expect(entry.label, `${entry.type} label`).toBeTruthy();
      expect(entry.title, `${entry.type} title`).toBeTruthy();
      expect(entry.description, `${entry.type} description`).toBeTruthy();
      expect(entry.icon, `${entry.type} icon`).toMatch(/^\/assets\/.+\.svg$/);
    }
  });
});

describe("what the module adder offers", () => {
  it("excludes empty slots, which are not something you add", () => {
    expect(addableModules(true).map((m) => m.type)).not.toContain("empty");
  });

  it("hides dev-only modules unless the backend reports dev_mode", () => {
    expect(addableModules(false).map((m) => m.type)).not.toContain("demoD");
    expect(addableModules(true).map((m) => m.type)).toContain("demoD");
  });

  it("offers the real hardware in both modes", () => {
    for (const devMode of [false, true]) {
      const offered = addableModules(devMode).map((m) => m.type);
      expect(offered).toEqual(expect.arrayContaining(["dac4D", "adc4D", "dac16D"]));
    }
  });
});

describe("lookups used by ModuleHeading", () => {
  it("returns the catalog title and icon for a known type", () => {
    expect(moduleTitle("dac4D")).toBe("Voltage Source");
    expect(moduleIcon("dac4D")).toBe("/assets/dac4D_icon.svg");
  });

  it("falls back for a type this build does not know", () => {
    // The backend can register modules a frontend has never heard of; a
    // placeholder icon is better than a broken image.
    expect(moduleCatalogEntry("fafd")).toBeUndefined();
    expect(moduleIcon("fafd")).toBe(UNKNOWN_MODULE_ICON);
    expect(moduleTitle("fafd")).toBe("fafd");
  });
});
