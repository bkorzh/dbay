#!/usr/bin/env bun

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

type Target = "gui" | "client";
type BumpType = "patch" | "minor" | "major";

type Semver = {
  major: number;
  minor: number;
  patch: number;
};

const HELP = `Usage:
  bun scripts/release.ts <target> <bump> [options]

Targets:
  gui       Bump GUI versions (tauri.conf.json + Cargo.toml), create gui-vX.Y.Z tag
  client    Bump Python client version (pyproject.toml), create py-vX.Y.Z tag

Bump:
  patch | minor | major

Options:
  --dry-run      Show next version and planned changes, do not edit files
  --no-commit    Update files only, do not create git commit or tag
  --push         Push commit and tag to origin (requires commit/tag mode)
  --allow-dirty  Allow running with existing uncommitted changes
  --help         Show this help
`;

const args = process.argv.slice(2);
if (args.includes("--help") || args.includes("-h")) {
  console.log(HELP);
  process.exit(0);
}

if (args.length < 2) {
  console.error(HELP);
  process.exit(1);
}

const target = args[0] as Target;
const bumpType = args[1] as BumpType;

if (!["gui", "client"].includes(target)) {
  console.error(`Unknown target '${args[0]}'. Use 'gui' or 'client'.`);
  process.exit(1);
}

if (!["patch", "minor", "major"].includes(bumpType)) {
  console.error(`Unknown bump '${args[1]}'. Use patch, minor, or major.`);
  process.exit(1);
}

const optionArgs = new Set(args.slice(2));
const dryRun = optionArgs.has("--dry-run");
const noCommit = optionArgs.has("--no-commit");
const push = optionArgs.has("--push");
const allowDirty = optionArgs.has("--allow-dirty");

if (push && noCommit) {
  console.error("--push cannot be used with --no-commit.");
  process.exit(1);
}

const repoRoot = path.resolve(import.meta.dir, "..");

const guiFiles = {
  tauriConf: path.join(repoRoot, "software/gui/frontend/src-tauri/tauri.conf.json"),
  cargoToml: path.join(repoRoot, "software/gui/frontend/src-tauri/Cargo.toml"),
};

const clientFiles = {
  pyprojectToml: path.join(repoRoot, "software/client/pyproject.toml"),
};

function runGit(args: string[], capture = true): string {
  const result = spawnSync("git", args, {
    cwd: repoRoot,
    encoding: "utf-8",
    stdio: capture ? ["ignore", "pipe", "pipe"] : "inherit",
  });
  if (result.status !== 0) {
    const err = capture ? (result.stderr || "").trim() : "git command failed";
    throw new Error(`git ${args.join(" ")} failed: ${err}`);
  }
  return capture ? (result.stdout || "").trim() : "";
}

function parseSemver(value: string): Semver {
  const m = /^(\d+)\.(\d+)\.(\d+)$/.exec(value.trim());
  if (!m) {
    throw new Error(`Invalid semver '${value}'. Expected X.Y.Z`);
  }
  return {
    major: Number.parseInt(m[1], 10),
    minor: Number.parseInt(m[2], 10),
    patch: Number.parseInt(m[3], 10),
  };
}

function semverToString(v: Semver): string {
  return `${v.major}.${v.minor}.${v.patch}`;
}

function compareSemver(a: Semver, b: Semver): number {
  if (a.major !== b.major) return a.major - b.major;
  if (a.minor !== b.minor) return a.minor - b.minor;
  return a.patch - b.patch;
}

function bumpSemver(v: Semver, bump: BumpType): Semver {
  if (bump === "major") return { major: v.major + 1, minor: 0, patch: 0 };
  if (bump === "minor") return { major: v.major, minor: v.minor + 1, patch: 0 };
  return { major: v.major, minor: v.minor, patch: v.patch + 1 };
}

function readTagVersions(prefix: string): Semver[] {
  const output = runGit(["tag", "--list", `${prefix}*`]);
  if (!output) return [];
  return output
    .split("\n")
    .map((tag) => tag.trim())
    .filter(Boolean)
    .map((tag) => {
      const regex = new RegExp(`^${prefix.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}(\\d+\\.\\d+\\.\\d+)$`);
      const match = regex.exec(tag);
      return match ? parseSemver(match[1]) : null;
    })
    .filter((v): v is Semver => v !== null);
}

function maxSemver(versions: Semver[]): Semver {
  if (versions.length === 0) return { major: 0, minor: 0, patch: 0 };
  return versions.reduce((max, current) => (compareSemver(current, max) > 0 ? current : max));
}

function ensureCleanWorktree() {
  const status = runGit(["status", "--porcelain"]);
  if (status.trim().length > 0) {
    throw new Error(
      "Working tree is not clean. Commit/stash changes first, or rerun with --allow-dirty."
    );
  }
}

function readGuiVersion(): string {
  const tauriVersion = JSON.parse(readFileSync(guiFiles.tauriConf, "utf-8")).version as string;
  const cargoText = readFileSync(guiFiles.cargoToml, "utf-8");
  const cargoMatch = cargoText.match(/^\[package\][\s\S]*?^version\s*=\s*"([^"]+)"/m);
  if (!cargoMatch) {
    throw new Error("Could not locate [package].version in Cargo.toml");
  }
  const cargoVersion = cargoMatch[1];
  if (tauriVersion !== cargoVersion) {
    throw new Error(
      `GUI version mismatch: tauri.conf.json=${tauriVersion}, Cargo.toml=${cargoVersion}`
    );
  }
  parseSemver(tauriVersion);
  return tauriVersion;
}

function updateGuiVersion(nextVersion: string) {
  const tauri = JSON.parse(readFileSync(guiFiles.tauriConf, "utf-8"));
  tauri.version = nextVersion;
  writeFileSync(guiFiles.tauriConf, `${JSON.stringify(tauri, null, 2)}\n`, "utf-8");

  const cargoText = readFileSync(guiFiles.cargoToml, "utf-8");
  const replaced = cargoText.replace(
    /^(\[package\][\s\S]*?^version\s*=\s*)"([^"]+)"/m,
    `$1"${nextVersion}"`
  );
  if (replaced === cargoText) {
    throw new Error("Failed to update Cargo.toml [package].version");
  }
  writeFileSync(guiFiles.cargoToml, replaced, "utf-8");
}

function readClientVersion(): string {
  const text = readFileSync(clientFiles.pyprojectToml, "utf-8");
  const match = text.match(/^version\s*=\s*"([^"]+)"/m);
  if (!match) {
    throw new Error("Could not locate version in software/client/pyproject.toml");
  }
  parseSemver(match[1]);
  return match[1];
}

function updateClientVersion(nextVersion: string) {
  const text = readFileSync(clientFiles.pyprojectToml, "utf-8");
  const replaced = text.replace(/^version\s*=\s*"([^"]+)"/m, `version = "${nextVersion}"`);
  if (replaced === text) {
    throw new Error("Failed to update version in software/client/pyproject.toml");
  }
  writeFileSync(clientFiles.pyprojectToml, replaced, "utf-8");
}

function main() {
  if (!allowDirty && !dryRun) {
    ensureCleanWorktree();
  }

  const tagPrefix = target === "gui" ? "gui-v" : "py-v";
  const currentVersion = target === "gui" ? readGuiVersion() : readClientVersion();
  const currentSemver = parseSemver(currentVersion);
  const maxTagSemver = maxSemver(readTagVersions(tagPrefix));
  const base = compareSemver(currentSemver, maxTagSemver) >= 0 ? currentSemver : maxTagSemver;
  const next = bumpSemver(base, bumpType);
  const nextVersion = semverToString(next);
  const tagName = `${tagPrefix}${nextVersion}`;

  const existingTag = runGit(["tag", "--list", tagName]);
  if (existingTag.trim().length > 0) {
    throw new Error(`Tag ${tagName} already exists`);
  }

  const filesToUpdate =
    target === "gui"
      ? [guiFiles.tauriConf, guiFiles.cargoToml]
      : [clientFiles.pyprojectToml];

  console.log(`Target: ${target}`);
  console.log(`Current version: ${currentVersion}`);
  console.log(`Next version: ${nextVersion}`);
  console.log(`Tag to create: ${tagName}`);
  console.log(`Files to update:\n- ${filesToUpdate.join("\n- ")}`);

  if (dryRun) {
    console.log("Dry run complete. No files changed.");
    return;
  }

  if (target === "gui") {
    updateGuiVersion(nextVersion);
  } else {
    updateClientVersion(nextVersion);
  }

  if (noCommit) {
    console.log("Updated files only (--no-commit).");
    return;
  }

  runGit(["add", ...filesToUpdate], false);
  runGit(["commit", "-m", `release(${target}): ${tagName}`], false);
  runGit(["tag", "-a", tagName, "-m", `Release ${target} ${nextVersion}`], false);
  console.log(`Created commit and tag ${tagName}.`);

  if (push) {
    runGit(["push", "origin", "HEAD"], false);
    runGit(["push", "origin", tagName], false);
    console.log("Pushed commit and tag to origin.");
  } else {
    console.log(`Next steps:\n  git push origin HEAD\n  git push origin ${tagName}`);
  }
}

try {
  main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
