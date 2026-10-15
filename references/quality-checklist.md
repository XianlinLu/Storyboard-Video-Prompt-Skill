# Quality checklist

## Scope and traceability

- [ ] The requested starting row and ending scope are correct.
- [ ] Every in-scope source row maps to exactly one final shot.
- [ ] Scene headings and source-row ranges are recorded.
- [ ] Demonstration rows and unrelated document content are untouched.

## Source fidelity

- [ ] Every line of dialogue is verbatim and assigned to the correct speaker.
- [ ] Shot size and camera movement match the source.
- [ ] Character actions, expressions, eyelines, props, and blocking are preserved.
- [ ] Setting, composition, lighting, atmosphere, and audio requirements are preserved.
- [ ] No unsupported action, line, asset, or visual event was invented.

## Merging

- [ ] Beats at or below the configured threshold were evaluated for merging.
- [ ] No merge crosses a scene, location/time reset, or incompatible continuity state.
- [ ] Merged prompts retain every requirement in chronological order.
- [ ] A merge is rejected when it creates contradictory camera or performance instructions.

## Timing

- [ ] All displayed totals and boundaries are integers.
- [ ] Round-half-up was used (`5.5 -> 6`).
- [ ] Every timeline starts at 0.
- [ ] Adjacent ranges are continuous and positive.
- [ ] Final endpoint equals total duration.

## Previous-video chain

- [ ] The first shot of each scene has no previous-video input.
- [ ] The first shot of each scene has no continuation marker.
- [ ] Every later shot uses the immediately previous generated video.
- [ ] Every later Chinese prompt starts with `续写这个@视频。`.
- [ ] Every later English prompt starts with `Continue this @video.`.
- [ ] The chain resets at every scene boundary.

## Language and wording

- [ ] Output language follows the user's explicit choice or latest substantive language.
- [ ] All headings, labels, prompts, and notes use that language consistently.
- [ ] Names, dialogue, filenames, and `@` references remain unchanged unless translation was requested.
- [ ] Prompts contain no ambiguous alternatives such as `可能`, `或者`, `maybe`, or `perhaps`.

## Assets and delivery

- [ ] Every `@` reference points to an attached asset or a clearly labeled placeholder.
- [ ] First scene rows contain sufficient environment and character references.
- [ ] Later rows avoid redundant references unless they are needed for continuity.
- [ ] Live-document edits were read back and verified.
- [ ] The completion report states counts, merges, timing corrections, and unresolved placeholders.
