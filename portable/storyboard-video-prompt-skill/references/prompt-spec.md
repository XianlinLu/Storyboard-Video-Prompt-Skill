# Storyboard prompt specification

Use this reference when timing, merging, or continuation behavior needs exact treatment.

## Source-to-prompt mapping

| Source field | Prompt treatment |
| --- | --- |
| Scene | Section boundary; resets the continuation chain |
| Dialogue | Preserve verbatim and assign it to the correct speaker |
| Shot size | State it at the start of the relevant timeline segment |
| Camera movement | State direction, speed, support, and whether the camera is fixed |
| Character action | Convert to chronological blocking and performance direction |
| Visual description | Preserve setting, composition, lighting, props, and atmosphere |
| Duration | Merge first; then convert to a contiguous integer timeline |
| Input image/video | Map to explicit `@` references and the input column |

When sources conflict, do not guess which instruction wins. Surface the conflict and ask, unless the target document's accepted example establishes a clear priority.

## Merge decision

For a source beat of 4 seconds or less:

1. Check the previous and next beats in the same scene.
2. Reject candidates with a location/time reset, incompatible wardrobe or cast state, contradictory camera grammar, or a required standalone reveal.
3. Prefer the candidate sharing subject, screen direction, and emotional beat.
4. Preserve chronological order inside the merged prompt.
5. List every source row in the notes.

Merged prompts may still contain hard cuts. A merge combines generation instructions and duration; it does not require a single continuous camera move.

## Integer timing

Use decimal arithmetic conceptually; do not use binary floating-point shortcuts when exact `.5` behavior matters.

### New prompt

1. Sum the raw durations in the merged shot.
2. Build raw cumulative boundaries from zero.
3. Apply round-half-up to each cumulative boundary.
4. Use the final rounded boundary as total duration.
5. Check that boundaries strictly increase. If two boundaries collide, merge those micro-beats or move one second from a longer neighboring segment while preserving the final total.

Example: raw segment durations `2.5, 3.0, 2.5` create cumulative boundaries `0, 2.5, 5.5, 8.0`, displayed as `0, 3, 6, 8`.

### Existing prompt

Round every displayed total and boundary half up, then verify adjacency. Change prompt timing only; do not alter media, dialogue, notes, or unrelated cells.

### Required invariants

- all values are integers;
- first start is `0`;
- each segment start equals the previous segment end;
- each segment duration is positive;
- final segment end equals total duration.

## Prompt templates

### Simplified Chinese: first shot in a scene

```text
[写实/动画等风格]，[场景、时段、光线、人物与参考图连续性]。总时长N秒。

0至A秒｜[景别]，[镜头动作]。[人物动作、表情、视线、道具与准确台词]。[构图与背景要求]。
A至N秒｜[景别]，[镜头动作]。[人物动作、表情、视线、道具与准确台词]。[构图与背景要求]。

[真实光影/动画一致性、口型、声音、空间位置、服装、镜头衔接等硬性要求]。
```

Do not prefix this row with `续写这个@视频。`.

### Simplified Chinese: later shot in the same scene

```text
续写这个@视频。[延续上一条视频的人物、服装、场景、光线与空间位置]。总时长N秒。

0至A秒｜...
A至N秒｜...

[连续性与生成质量要求]。
```

The input column must include the immediately previous generated video.

### English: first shot in a scene

```text
[Visual style], [setting, time of day, lighting, and continuity with reference images]. Total duration: N seconds.

0–A seconds | [Shot size], [camera behavior]. [Character action, expression, eyeline, props, and exact dialogue]. [Composition and background].
A–N seconds | [Shot size], [camera behavior]. [Character action, expression, eyeline, props, and exact dialogue]. [Composition and background].

[Hard requirements for lighting, lip sync, sound, spatial continuity, wardrobe, and transitions].
```

Do not prefix this row with `Continue this @video.`.

### English: later shot in the same scene

```text
Continue this @video. [Continue the people, wardrobe, setting, lighting, and spatial positions from the preceding video]. Total duration: N seconds.

0–A seconds | ...
A–N seconds | ...

[Continuity and generation-quality constraints].
```

The input column must include the immediately previous generated video.

## Deterministic wording

Specify one camera behavior, one blocking path, and one intended result for each beat. Replace ambiguous choices with the source-backed decision.

Avoid:

- `可能`, `或者`, `也许`, `大概`;
- `maybe`, `perhaps`, `might`, `could possibly`, `or alternatively`;
- conflicting instructions such as "fixed camera that follows the subject";
- unsupported additions of dialogue, emotion, props, weather, or camera movement.

## Input media rules

Scene-first row:

- environment reference;
- required character references;
- optional prop or wardrobe references;
- no previous-scene video.

Later row in the same scene:

- previous generated video first;
- only new references necessary for the next beat;
- continuation marker at the start of the prompt.

If the target interface binds an uploaded asset to an `@` mention, use its exact bound name. Never refer to `@image3` or `@video` unless that asset exists or is explicitly marked for later attachment.
