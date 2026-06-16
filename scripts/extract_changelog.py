#!/usr/bin/env python3
"""Print one version's section body from a Keep a Changelog file.

Usage:
    extract_changelog.py <changelog-path> <version>

Prints the lines between the ``## [<version>]`` heading and the next ``## ``
heading (exclusive), trimmed of surrounding blank lines. Used by the release
workflows to fill the GitHub Release body. Exits non-zero if the version has no
section, so a release can't silently ship empty notes.
"""

import pathlib
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: extract_changelog.py <changelog-path> <version>", file=sys.stderr)
        return 2

    path = pathlib.Path(sys.argv[1])
    version = sys.argv[2]
    needle = f"## [{version}]"

    capturing = False
    body: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(needle):
            capturing = True
            continue
        if capturing and line.startswith("## "):
            break
        if capturing:
            body.append(line)

    if not capturing:
        print(f"No section '{needle}' found in {path}", file=sys.stderr)
        return 1

    print("\n".join(body).strip("\n"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
