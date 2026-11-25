#!/usr/bin/env bun

// Sets up the development environment: Python interpreter, backend virtual
// environment, frontend packages, and a verification run of both test suites.
//
// Not usually run directly — `./setup.sh` (macOS/Linux) and `.\setup.ps1`
// (Windows) install bun and uv if they are missing, then hand off to this
// script, which is the same on every platform.
//
// Every step echoes the command it runs, so this is a demonstration of the
// manual path in docs/content/Development/Start Here.md, not a replacement
// for understanding it.

import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { parseArgs } from "util";

const HELP = `Usage:
  ./setup.sh [options]              # macOS, Linux
  .\\setup.ps1 [options]             # Windows
  bun scripts/setup.ts [options]    # if bun and uv are already installed

Options:
  --check        Report what is installed and what is out of date; change nothing
  --tauri        Also set up the Rust toolchain for desktop development
  --skip-tests   Do not run the test suites at the end
  --yes          Do not prompt before installing missing tools
  --help         Show this help

Steps:
  1. check git, bun, and uv
  2. install a compatible Python (3.11-3.13) if none is present
  3. uv sync           in software/gui/backend
  4. bun install       in software/gui/frontend
  5. run both test suites to verify the result
`;

const { values } = parseArgs({
  args: Bun.argv,
  options: {
    check: { type: "boolean" },
    tauri: { type: "boolean" },
    "skip-tests": { type: "boolean" },
    yes: { type: "boolean" },
    help: { type: "boolean" },
  },
  strict: false,
  allowPositionals: true,
});

if (values.help) {
  console.log(HELP);
  process.exit(0);
}

const checkOnly = Boolean(values.check);
const skipTests = Boolean(values["skip-tests"]);
const assumeYes = Boolean(values.yes);
const withTauri = Boolean(values.tauri);

const repoRoot = path.resolve(import.meta.dir, "..");
const backendDir = path.join(repoRoot, "software/gui/backend");
const frontendDir = path.join(repoRoot, "software/gui/frontend");

const PYTHON_REQUIREMENT = ">=3.11,<3.14";

const problems: string[] = [];
const notes: string[] = [];

function heading(text: string) {
  console.log(`\n\x1b[1;33m>>> ${text}\x1b[0m`);
}

function ok(text: string) {
  console.log(`  \x1b[32m✓\x1b[0m ${text}`);
}

function warn(text: string) {
  console.log(`  \x1b[33m!\x1b[0m ${text}`);
}

function bad(text: string) {
  console.log(`  \x1b[31m✗\x1b[0m ${text}`);
}

/** Run a command, showing it first. Returns true on exit code 0. */
function run(command: string, args: string[], cwd: string): boolean {
  const where = path.relative(repoRoot, cwd) || ".";
  console.log(`  \x1b[2m${where} $ ${command} ${args.join(" ")}\x1b[0m`);
  const result = spawnSync(command, args, { cwd, stdio: "inherit" });
  return result.status === 0;
}

/** Run a command quietly and return its trimmed stdout, or null if it failed. */
function capture(command: string, args: string[], cwd = repoRoot): string | null {
  const result = spawnSync(command, args, { cwd, encoding: "utf-8" });
  if (result.error || result.status !== 0) return null;
  return (result.stdout || "").trim();
}

function toolVersion(command: string): string | null {
  return capture(command, ["--version"]);
}

// --------------------------------------------------------------- 1. tools

heading("Checking tools");

const gitVersion = toolVersion("git");
const bunVersion = toolVersion("bun");
const uvVersion = toolVersion("uv");

for (const [name, version] of [
  ["git", gitVersion],
  ["bun", bunVersion],
  ["uv", uvVersion],
] as const) {
  if (version) {
    // `uv --version` appends a commit hash and build date; keep just the number.
    ok(`${name} ${/\d+\.\d+\.\d+/.exec(version)?.[0] ?? version}`);
  } else {
    bad(`${name} not found`);
    problems.push(
      `${name} is not installed or not on PATH. Run ./setup.sh (macOS/Linux) or .\\setup.ps1 (Windows), which installs it for you.`,
    );
  }
}

if (!bunVersion || !uvVersion) {
  // Nothing below can work without both.
  console.log("");
  for (const problem of problems) bad(problem);
  process.exit(1);
}

// --------------------------------------------------------------- 2. python

heading("Checking Python");

const foundPython = capture("uv", ["python", "find", PYTHON_REQUIREMENT], backendDir);

if (foundPython) {
  ok(`interpreter for ${PYTHON_REQUIREMENT}: ${foundPython}`);
} else if (checkOnly) {
  bad(`no interpreter matching ${PYTHON_REQUIREMENT}`);
  problems.push("No compatible Python. Run `uv python install 3.11`, or re-run without --check.");
} else {
  warn(`no interpreter matching ${PYTHON_REQUIREMENT}; installing 3.11`);
  if (!run("uv", ["python", "install", "3.11"], backendDir)) {
    problems.push("`uv python install 3.11` failed.");
  }
}

// --------------------------------------------------------------- 3. backend

heading(checkOnly ? "Checking the backend environment" : "Setting up the backend environment");

if (checkOnly) {
  const result = spawnSync("uv", ["sync", "--check"], { cwd: backendDir, encoding: "utf-8" });
  if (result.status === 0) {
    ok("software/gui/backend/.venv matches uv.lock");
  } else {
    bad("software/gui/backend/.venv is missing or out of date");
    problems.push("Backend environment out of date. Run `uv sync` in software/gui/backend.");
  }
} else if (run("uv", ["sync"], backendDir)) {
  ok("backend environment ready (.venv, plus software/client/ as an editable install)");
} else {
  problems.push("`uv sync` failed in software/gui/backend.");
}

// -------------------------------------------------------------- 4. frontend

heading(checkOnly ? "Checking frontend packages" : "Installing frontend packages");

/**
 * A stale node_modules is the most common broken-setup symptom in this repo:
 * it is gitignored, so a pull that adds or bumps a dependency leaves the old
 * install in place and the build fails on an import that genuinely is absent.
 * Checking package.json against what is on disk names the problem directly.
 */
function inspectFrontendInstall(): { missing: string[]; outdated: string[] } {
  const missing: string[] = [];
  const outdated: string[] = [];

  const manifest = JSON.parse(readFileSync(path.join(frontendDir, "package.json"), "utf-8"));
  const wanted: Record<string, string> = {
    ...(manifest.dependencies ?? {}),
    ...(manifest.devDependencies ?? {}),
  };

  for (const [name, range] of Object.entries(wanted)) {
    const installedManifest = path.join(frontendDir, "node_modules", name, "package.json");
    if (!existsSync(installedManifest)) {
      missing.push(name);
      continue;
    }

    // Only the common `^x.y.z` / `~x.y.z` / `x.y.z` forms are compared. Anything
    // else (workspace refs, tags, URLs) is left to bun.
    const minimum = /^[\^~]?(\d+)\.(\d+)\.(\d+)$/.exec(range.trim());
    if (!minimum) continue;

    const installedVersion = JSON.parse(readFileSync(installedManifest, "utf-8")).version as string;
    const actual = /^(\d+)\.(\d+)\.(\d+)/.exec(installedVersion);
    if (!actual) continue;

    const want = [Number(minimum[1]), Number(minimum[2]), Number(minimum[3])];
    const have = [Number(actual[1]), Number(actual[2]), Number(actual[3])];
    const older =
      have[0] < want[0] ||
      (have[0] === want[0] && have[1] < want[1]) ||
      (have[0] === want[0] && have[1] === want[1] && have[2] < want[2]);
    if (older) outdated.push(`${name} ${installedVersion} (package.json wants ${range})`);
  }

  return { missing, outdated };
}

if (checkOnly) {
  if (!existsSync(path.join(frontendDir, "node_modules"))) {
    bad("software/gui/frontend/node_modules does not exist");
    problems.push("Frontend packages not installed. Run `bun install` in software/gui/frontend.");
  } else {
    const { missing, outdated } = inspectFrontendInstall();
    if (missing.length === 0 && outdated.length === 0) {
      ok("node_modules matches package.json");
    } else {
      for (const name of missing) bad(`missing package: ${name}`);
      for (const entry of outdated) bad(`stale package: ${entry}`);
      problems.push(
        "node_modules is out of date — the usual cause of an unresolved import at build time. " +
          "Run `bun install` in software/gui/frontend (or `rm -rf node_modules && bun install`).",
      );
    }
  }
} else if (run("bun", ["install"], frontendDir)) {
  ok("frontend packages installed");
} else {
  problems.push("`bun install` failed in software/gui/frontend.");
}

// ----------------------------------------------------------------- 5. tauri

if (withTauri) {
  heading(checkOnly ? "Checking the Tauri toolchain" : "Setting up the Tauri toolchain");

  const rustc = toolVersion("rustc");
  if (rustc) {
    ok(rustc);
  } else if (checkOnly) {
    bad("rustc not found");
    problems.push("Rust is not installed; Tauri builds need it.");
  } else if (process.platform === "win32") {
    warn("Rust is not installed. Install it with the rustup installer:");
    console.log("      https://www.rust-lang.org/tools/install");
    problems.push("Rust is not installed (install rustup, then re-run with --tauri).");
  } else if (confirm("Install Rust with rustup (https://sh.rustup.rs)?")) {
    const installed = run(
      "sh",
      ["-c", "curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh -s -- -y"],
      repoRoot,
    );
    if (installed) {
      notes.push("Rust was installed. Open a new terminal (or source ~/.cargo/env) before building.");
    } else {
      problems.push("The rustup installer failed.");
    }
  } else {
    problems.push("Rust is not installed; skipped on request.");
  }

  if (process.platform === "linux") {
    // Deliberately not run: this needs sudo, and a setup script should not
    // escalate privileges on someone's machine.
    notes.push(
      "Tauri on Debian/Ubuntu also needs system packages. Run this yourself:\n" +
        "      sudo apt-get update && sudo apt-get install -y build-essential libssl-dev \\\n" +
        "        libgtk-3-dev libwebkit2gtk-4.1-dev libsoup-3.0-dev libayatana-appindicator3-dev \\\n" +
        "        librsvg2-dev libxdo-dev patchelf",
    );
  }
  if (process.platform === "darwin") {
    notes.push("Tauri on macOS also needs the Xcode command line tools: xcode-select --install");
  }
}

/** Ask the user a yes/no question; --yes and non-interactive shells answer yes/no respectively. */
function confirm(question: string): boolean {
  if (assumeYes) return true;
  if (!process.stdin.isTTY) {
    warn(`${question} — no terminal to ask on; skipping (use --yes to accept).`);
    return false;
  }
  const answer = prompt(`  ${question} [y/N]`);
  return /^y(es)?$/i.test((answer ?? "").trim());
}

// ----------------------------------------------------------------- 6. verify

if (!checkOnly && !skipTests && problems.length === 0) {
  heading("Verifying (running both test suites)");

  if (run("uv", ["run", "pytest", "-q"], backendDir)) {
    ok("backend tests passed");
  } else {
    problems.push("Backend tests failed. See the output above.");
  }

  if (run("bun", ["run", "test"], frontendDir)) {
    ok("frontend tests passed");
  } else {
    problems.push("Frontend tests failed. See the output above.");
  }
} else if (!checkOnly && skipTests) {
  notes.push("Skipped the test suites (--skip-tests).");
}

// ---------------------------------------------------------------- 7. summary

console.log("");

if (problems.length > 0) {
  heading(checkOnly ? "Problems found" : "Setup did not complete");
  for (const problem of problems) bad(problem);
  for (const note of notes) warn(note);
  console.log(
    "\nTroubleshooting: docs/content/Development/Troubleshooting.md" +
      (checkOnly ? "" : "\nRe-run this script after fixing; it is safe to run repeatedly."),
  );
  process.exit(1);
}

if (checkOnly) {
  heading("Everything checks out");
  for (const note of notes) warn(note);
  process.exit(0);
}

heading("Ready");
for (const note of notes) warn(note);
console.log(`
Start the app (backend on port 8345, Vite on port 5173):

  ./software/gui/dev-browser.sh        # macOS, Linux
  cd software/gui/frontend; bun run develop   # Windows

Then open http://localhost:5173

Docs: docs/content/Development/Start Here.md`);
