---
name: storyboard-video-prompt-skill
description: Creates production-ready storyboard video prompts from scripts, spreadsheets, shot lists, reference images, and existing storyboard documents. It groups shots by scene, merges overly short adjacent beats without losing requirements, builds integer-second timelines, manages previous-video continuation chains, places input media, and validates source fidelity. Use for storyboard prompts, image-to-video or video-extension shot plans, scene-by-scene prompt tables, prompt localization, or auditing an existing storyboard document.
author: XianlinLu
---

# Storyboard Video Prompt Skill

Turn source rows into executable video prompts while preserving every stated visual, action, camera, dialogue, and duration requirement.

## Language

Choose the output language before drafting:

1. Follow an explicit language request.
2. Otherwise match the language of the user's latest substantive request: Chinese input produces Simplified Chinese; English input produces English.
3. For mixed-language input, use the dominant natural language. If dominance is unclear, ask once or use the document's established language.
4. Keep names, quoted dialogue, filenames, `@` references, and user-supplied terminology unchanged unless translation is requested.
5. Localize headings, table labels, prompt prose, notes, and status messages consistently. Do not produce bilingual output unless requested.

## Inputs

Accept any combination of:

- a spreadsheet, table, CSV, or shot list;
- a script or prose scene description;
- reference images, character sheets, environment images, or an existing video;
- a target document or template containing examples;
- a requested starting row, scene range, duration rule, or video model convention.

When links or files are supplied, read the source and the target examples before writing. Use the available spreadsheet, document, file, or browser capabilities; do not depend on a specific vendor's tool names.

Map equivalent source columns to this canonical record:

`scene`, `source_rows`, `dialogue`, `shot_size`, `camera_movement`, `character_action`, `visual_description`, `duration`, `input_assets`, `notes`.

Do not silently invent missing facts. If a non-critical field is absent, omit it. If duration or scene boundaries are missing and the user allows best effort, mark the estimate clearly in notes; otherwise ask for the missing decision.

## Workflow

### 1. Inspect and normalize

- Respect the requested starting row and do not reprocess demonstration rows unless asked.
- Read enough neighboring rows to identify scene boundaries and possible merges.
- Preserve row identifiers so every source requirement can be traced to an output shot.
- Treat dialogue, camera direction, character action, and visual description as hard constraints.

### 2. Segment by scene

Create one section and one storyboard table per scene. A scene boundary resets location/time continuity and the previous-video chain.

Never merge across a scene boundary, location or time jump, incompatible cast state, or explicit cut that carries narrative meaning.

### 3. Merge short beats

Use 4 seconds or less as the default short-beat threshold unless the user specifies another value.

Merge a short beat with the most compatible adjacent beat in the same scene when the combined prompt can show all requirements clearly. Prefer chronological adjacency and visual continuity. Preserve all dialogue, shot requirements, actions, props, and composition details, and record the full source-row range.

Do not merge merely to reduce row count. Keep a short beat separate when merging would create contradictory camera instructions, impossible simultaneous actions, or unreadable pacing.

### 4. Build an integer timeline

- Merge first, then calculate timing.
- Use round-half-up for every displayed duration and boundary: a fractional part below `.5` rounds down; `.5` or above rounds up.
- Show integer seconds only. Example: `5.5 seconds -> 6 seconds`; `2.5–5.5 seconds -> 3–6 seconds`.
- Start each prompt at `0`, keep adjacent segments contiguous, and make the final endpoint equal the displayed total duration.
- If rounding collapses a segment to zero, merge that beat or redistribute one second to preserve order and a positive duration.
- When editing an existing document, change only timing text inside prompt cells unless the user requests broader edits.

Use [prompt-spec.md](references/prompt-spec.md) for the exact allocation and repair rules.

### 5. Draft each prompt

Write deterministic, directly executable instructions in this order:

1. continuation instruction when applicable;
2. visual style, setting, lighting, and continuity anchors;
3. integer total duration;
4. contiguous timeline segments with shot size and camera behavior;
5. character blocking, expressions, gestures, props, and exact dialogue;
6. composition, background, atmosphere, audio or lip-sync requirements;
7. final continuity and quality constraints.

Keep the prompt fully aligned with the source. Do not offer alternatives or uncertain possibilities. Avoid words such as `可能`, `或者`, `maybe`, `perhaps`, and `might` when they make generation ambiguous.

### 6. Apply the previous-video chain

Within each scene:

- First shot: use scene/character reference inputs and omit the continuation instruction.
- Every later shot: include the immediately previous generated video as an input and begin the prompt with the localized continuation instruction.
- Chinese marker: `续写这个@视频。`
- English marker: `Continue this @video.`

At a new scene, do not use the previous scene's last video and do not include the continuation marker. Restart from the new scene's reference inputs.

### 7. Place input media

For the first shot of a scene, place the minimum sufficient environment and character references in the input column. For later shots, place the previous generated video first, then only new references needed for characters, props, wardrobe, or composition.

When the generated video does not exist yet, insert a localized placeholder such as `待粘贴：上一条生成视频` or `To attach: previous generated video`. Do not pretend a missing asset was attached.

### 8. Write the deliverable

Default table columns:

1. Input image/video
2. Prompt
3. Generated video
4. Notes

Use scene headings above tables. Keep one output row per final merged shot. In notes, record source rows, merge decisions, provisional timing, and unresolved asset needs without polluting the generation prompt.

When editing a live document, prefer precise block or cell updates over whole-document replacement. Preserve existing media, generated videos, formatting, and unrelated content.

### 9. Validate before completion

Confirm all of the following:

- every source row in scope is covered exactly once;
- all dialogue and required actions survive merges;
- prompt timing contains no decimals;
- every timeline starts at 0, is contiguous, and ends at total duration;
- scene-first rows have no continuation marker or previous-video input;
- later rows in each scene have both;
- prompts do not contain ambiguous alternatives;
- input assets and `@` references exist or are marked as placeholders;
- table count, scene count, and unrelated document content remain unchanged when auditing or editing.

For structured work, create a temporary plan using [storyboard-plan-example.json](references/storyboard-plan-example.json) and validate it with [validate_storyboard_plan.py](scripts/validate_storyboard_plan.py):

```bash
python3 scripts/validate_storyboard_plan.py <plan.json>
```

For a manual review or environments without Python, use [quality-checklist.md](references/quality-checklist.md).

Repository maintainers can regenerate the file-format-safe import directory with [build_portable.py](scripts/build_portable.py). This keeps `SKILL.md` below 20,000 characters and excludes formats rejected by restricted importers.

## Output standard

Lead with the completed artifact or modification. Report the number of scenes, final shots, merged source rows, and corrected timing values. Mention unresolved placeholders or assumptions explicitly. Do not claim media was inserted or a document was updated unless the operation succeeded and was verified by reading it back.
