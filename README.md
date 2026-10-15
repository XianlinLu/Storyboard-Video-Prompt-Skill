# Storyboard Video Prompt Skill

[English](README.md) | [简体中文](README.zh-CN.md)

A tool-agnostic Skill for turning scripts, spreadsheets, shot lists, reference images, and existing storyboard documents into production-ready video prompts.

It captures the workflow used for reliable storyboard generation:

- group output by scene;
- merge adjacent beats of 4 seconds or less when continuity allows;
- preserve every dialogue, shot, camera, action, and visual requirement;
- convert all displayed timing to contiguous integer seconds with round-half-up;
- use the previous generated video as the next input within a scene;
- reset that continuation chain at every scene boundary;
- map names to approved front/side/back character sheets without guessing identity;
- match every environment reference to the exact scripted scene;
- preserve existing numbered `@image` and `@video` bindings while placing media;
- validate the completed document by reading it back;
- answer in Simplified Chinese for Chinese requests and English for English requests.

The instructions are vendor-neutral, so any agent with document/file capabilities can use them. Lark/Feishu, local Markdown/JSON, and other spreadsheet/document systems are supported through the agent's available tools.

## Quick start

### Import into an agent UI

Import this directory only:

```text
portable/storyboard-video-prompt-skill/
```

The portable package contains only `.md`, `.json`, and `.txt` files. It intentionally excludes `.skillignore`, `.py` files, and repository metadata. Its validator is stored as a Python-compatible `.txt` file and can still be run with `python3`.

### Use from a Git checkout

Point the agent's Skill loader at the repository root or copy the root Skill files into its normal skills directory. `SKILL.md` is the entry point; detailed rules are under `references/`.

Example request:

```text
Starting from row 5, convert the dialogue, shot size, camera movement,
character action, visual description, and duration into storyboard video
prompts. Group them by scene, merge shots at or below 4 seconds when safe,
and use the preceding generated video for continuation inside each scene.
```

The Skill automatically matches the output language to the user's latest substantive request unless a language is explicitly specified.

## Why the portable package exists

Some importers reject or warn about two conditions:

1. `SKILL.md` longer than 20,000 characters.
2. files outside `.md`, `.txt`, `.json`, `.yaml`, and `.yml`, including `.skillignore`.

This repository prevents both:

- canonical `SKILL.md` is checked against the 20,000-character limit;
- `portable/storyboard-video-prompt-skill/` contains only accepted formats;
- the included package checker verifies that the portable copy is current and contains no unsupported files.

Do not upload the whole repository to a file-limited importer. Upload the portable directory.

## Validation

Validate the included example plan:

```bash
python3 scripts/validate_storyboard_plan.py references/storyboard-plan-example.json
```

Rebuild and verify the portable package:

```bash
python3 scripts/build_portable.py
python3 scripts/build_portable.py --check
```

The plan validator checks integer timing, continuous ranges, total duration, source-row uniqueness, input assets, scene-boundary resets, and localized continuation markers.

## Repository layout

```text
SKILL.md                                  Canonical agent instructions
references/prompt-spec.md                 Prompt, merge, timing, and continuation rules
references/quality-checklist.md           Manual verification checklist
references/storyboard-plan-example.json   Structured validation example
scripts/validate_storyboard_plan.py       Deterministic plan validator
scripts/build_portable.py                  Portable-package builder/checker
portable/storyboard-video-prompt-skill/   Import-safe text-only package
```

## Core continuation rule

Within one scene, every shot after the first uses the immediately previous generated video and starts with:

- Chinese: `续写这个@视频。`
- English: `Continue this @video.`

The first shot of every new scene uses new scene references and does not use that marker.

## Character and scene reference rule

Build explicit `character name -> approved three-view` and `scene name -> approved environment image` mappings before editing. Prefer a full-body front/side/back sheet; a composite with a clear face close-up is ideal. Never match a person by appearance alone, and never substitute a similar-looking location for the source scene. If an existing prompt refers to numbered inputs, replace assets in place or append supplemental references after them so the numbering remains stable.
