#!/usr/bin/env python3
"""Build or verify the text-only portable import directory."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "portable" / "storyboard-video-prompt-skill"
FILES = {
    Path("SKILL.md"): Path("SKILL.md"),
    Path("references/prompt-spec.md"): Path("references/prompt-spec.md"),
    Path("references/quality-checklist.md"): Path("references/quality-checklist.md"),
    Path("references/storyboard-plan-example.json"): Path("references/storyboard-plan-example.json"),
    Path("scripts/validate_storyboard_plan.py"): Path("scripts/validate_storyboard_plan.txt"),
}
ALLOWED_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml"}
MAX_SKILL_CHARACTERS = 20_000
MAX_SKILL_BYTES = 20_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the portable skill import directory.")
    parser.add_argument("--check", action="store_true", help="Verify without changing files")
    return parser.parse_args()


def portable_content(source: Path, content: str) -> str:
    if source != Path("SKILL.md"):
        return content
    content = content.replace(
        "[validate_storyboard_plan.py](scripts/validate_storyboard_plan.py)",
        "[validate_storyboard_plan.txt](scripts/validate_storyboard_plan.txt)",
    ).replace(
        "python3 scripts/validate_storyboard_plan.py <plan.json>",
        "python3 scripts/validate_storyboard_plan.txt <plan.json>",
    )
    maintainer_note = (
        "\nRepository maintainers can regenerate the file-format-safe import directory with "
        "[build_portable.py](scripts/build_portable.py). This keeps `SKILL.md` below 20,000 "
        "characters and excludes formats rejected by restricted importers.\n"
    )
    return content.replace(maintainer_note, "")


def expected_files() -> dict[Path, str]:
    expected: dict[Path, str] = {}
    for source_relative, target_relative in FILES.items():
        source = ROOT / source_relative
        content = source.read_text(encoding="utf-8")
        expected[target_relative] = portable_content(source_relative, content)
    return expected


def validate(expected: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    skill_chars = len(expected[Path("SKILL.md")])
    skill_bytes = len(expected[Path("SKILL.md")].encode("utf-8"))
    if skill_chars > MAX_SKILL_CHARACTERS:
        errors.append(
            f"SKILL.md contains {skill_chars} characters; maximum is {MAX_SKILL_CHARACTERS}"
        )
    if skill_bytes > MAX_SKILL_BYTES:
        errors.append(
            f"SKILL.md contains {skill_bytes} UTF-8 bytes; safety maximum is {MAX_SKILL_BYTES}"
        )

    actual_files = {
        path.relative_to(OUTPUT)
        for path in OUTPUT.rglob("*")
        if path.is_file()
    } if OUTPUT.exists() else set()
    expected_paths = set(expected)
    if actual_files != expected_paths:
        errors.append(
            f"portable file set differs: expected {sorted(map(str, expected_paths))}, "
            f"got {sorted(map(str, actual_files))}"
        )

    for relative, content in expected.items():
        target = OUTPUT / relative
        if target.suffix.lower() not in ALLOWED_EXTENSIONS:
            errors.append(f"unsupported portable extension: {relative}")
        if not target.exists():
            continue
        if target.read_text(encoding="utf-8") != content:
            errors.append(f"portable copy is stale: {relative}")
    return errors


def build(expected: dict[Path, str]) -> None:
    portable_root = (ROOT / "portable").resolve()
    output = OUTPUT.resolve()
    if portable_root not in output.parents:
        raise RuntimeError("refusing to modify a directory outside portable/")
    if output.exists():
        shutil.rmtree(output)
    for relative, content in expected.items():
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        expected = expected_files()
        if not args.check:
            build(expected)
        errors = validate(expected)
    except OSError as exc:
        print(f"ERROR: {exc}")
        return 2

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    skill_chars = len(expected[Path("SKILL.md")])
    skill_bytes = len(expected[Path("SKILL.md")].encode("utf-8"))
    print(
        f"Portable package is valid: {len(expected)} file(s), "
        f"SKILL.md {skill_chars}/{MAX_SKILL_CHARACTERS} characters, "
        f"{skill_bytes}/{MAX_SKILL_BYTES} UTF-8 bytes."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
