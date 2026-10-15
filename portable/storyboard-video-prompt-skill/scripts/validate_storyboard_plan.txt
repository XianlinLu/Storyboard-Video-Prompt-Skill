#!/usr/bin/env python3
"""Validate a storyboard prompt plan without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DECIMAL_TIME = re.compile(
    r"(?<![\w.])\d+\.\d+(?=\s*(?:秒|s\b|secs?\b|seconds?\b|至|[-–—]\s*\d))",
    re.IGNORECASE,
)
ZH_RANGE = re.compile(r"(\d+)\s*至\s*(\d+)\s*秒")
EN_RANGE = re.compile(r"(\d+)\s*[-–—]\s*(\d+)\s*(?:s\b|secs?\b|seconds?\b)", re.IGNORECASE)
ZH_TOTAL = re.compile(r"(?:总时长|暂定总时长)\s*[:：]?\s*(\d+)\s*秒")
EN_TOTAL = re.compile(r"total\s+duration\s*[:：]?\s*(\d+)\s*(?:s\b|secs?\b|seconds?\b)", re.IGNORECASE)
AMBIGUOUS = re.compile(r"可能|或者|也许|大概|\bmaybe\b|\bperhaps\b|\bmight\b|\bor alternatively\b", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a storyboard plan JSON file.")
    parser.add_argument("plan", type=Path, help="Path to a storyboard plan JSON file")
    return parser.parse_args()


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def main() -> int:
    args = parse_args()
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid JSON: {exc}")
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    language = str(plan.get("language", "")).lower()
    scenes = plan.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("plan.scenes must be a non-empty array")
        scenes = []

    seen_shot_ids: set[str] = set()
    seen_source_rows: dict[Any, str] = {}
    shot_count = 0

    for scene_index, scene in enumerate(scenes, start=1):
        scene_label = f"scene[{scene_index}]"
        if not isinstance(scene, dict):
            errors.append(f"{scene_label} must be an object")
            continue
        shots = scene.get("shots")
        if not isinstance(shots, list) or not shots:
            errors.append(f"{scene_label}.shots must be a non-empty array")
            continue

        for shot_index, shot in enumerate(shots, start=1):
            shot_count += 1
            label = f"{scene_label}.shot[{shot_index}]"
            if not isinstance(shot, dict):
                errors.append(f"{label} must be an object")
                continue

            shot_id = str(shot.get("shot_id", "")).strip()
            if not shot_id:
                errors.append(f"{label}.shot_id is required")
            elif shot_id in seen_shot_ids:
                errors.append(f"{label}.shot_id duplicates {shot_id!r}")
            else:
                seen_shot_ids.add(shot_id)

            source_rows = shot.get("source_rows", [])
            if not isinstance(source_rows, list) or not source_rows:
                warnings.append(f"{label}.source_rows is empty; traceability is incomplete")
            elif len(set(map(str, source_rows))) != len(source_rows):
                errors.append(f"{label}.source_rows contains duplicates")
            for row in source_rows if isinstance(source_rows, list) else []:
                row_key = json.dumps(row, ensure_ascii=False, sort_keys=True)
                if row_key in seen_source_rows:
                    errors.append(
                        f"{label}.source_rows repeats {row!r}, already used by {seen_source_rows[row_key]}"
                    )
                else:
                    seen_source_rows[row_key] = shot_id or label

            should_continue = shot_index > 1
            continues = shot.get("continues_previous")
            if continues is not should_continue:
                errors.append(
                    f"{label}.continues_previous must be {str(should_continue).lower()} at this scene position"
                )

            assets = shot.get("input_assets")
            if not isinstance(assets, list) or not assets:
                errors.append(f"{label}.input_assets must be a non-empty array")
                assets = []
            previous_video_count = sum(
                1
                for asset in assets
                if isinstance(asset, dict) and asset.get("type") == "previous_video"
            )
            if should_continue and previous_video_count != 1:
                errors.append(f"{label} must contain exactly one previous_video input")
            if not should_continue and previous_video_count:
                errors.append(f"{label} is scene-first and must not contain previous_video input")

            total = shot.get("total_duration")
            if not is_int(total) or total <= 0:
                errors.append(f"{label}.total_duration must be a positive integer")

            segments = shot.get("segments")
            if not isinstance(segments, list) or not segments:
                errors.append(f"{label}.segments must be a non-empty array")
                segments = []
            expected_start = 0
            structured_ranges: list[tuple[int, int]] = []
            for segment_index, segment in enumerate(segments, start=1):
                segment_label = f"{label}.segment[{segment_index}]"
                if not isinstance(segment, dict):
                    errors.append(f"{segment_label} must be an object")
                    continue
                start, end = segment.get("start"), segment.get("end")
                if not is_int(start) or not is_int(end):
                    errors.append(f"{segment_label} start/end must be integers")
                    continue
                structured_ranges.append((start, end))
                if start != expected_start:
                    errors.append(f"{segment_label}.start must be {expected_start}, got {start}")
                if end <= start:
                    errors.append(f"{segment_label}.end must be greater than start")
                expected_start = end
            if is_int(total) and segments and expected_start != total:
                errors.append(f"{label} final segment ends at {expected_start}, total is {total}")

            prompt = shot.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                errors.append(f"{label}.prompt must be non-empty text")
                continue
            prompt = prompt.strip()
            if DECIMAL_TIME.search(prompt):
                errors.append(f"{label}.prompt contains a decimal duration")

            if language.startswith("zh"):
                marker = "续写这个@视频。"
                prompt_ranges = [(int(a), int(b)) for a, b in ZH_RANGE.findall(prompt)]
                totals = [int(value) for value in ZH_TOTAL.findall(prompt)]
            elif language.startswith("en"):
                marker = "Continue this @video."
                prompt_ranges = [(int(a), int(b)) for a, b in EN_RANGE.findall(prompt)]
                totals = [int(value) for value in EN_TOTAL.findall(prompt)]
            else:
                marker = "@video"
                prompt_ranges = [
                    (int(a), int(b))
                    for a, b in ZH_RANGE.findall(prompt) + EN_RANGE.findall(prompt)
                ]
                totals = [int(value) for value in ZH_TOTAL.findall(prompt) + EN_TOTAL.findall(prompt)]

            has_marker = prompt.startswith(marker) if marker != "@video" else "@video" in prompt.split("\n", 1)[0]
            if should_continue and not has_marker:
                errors.append(f"{label}.prompt is missing the localized continuation marker")
            if not should_continue and has_marker:
                errors.append(f"{label}.prompt must not use a continuation marker")
            if totals and is_int(total) and totals[0] != total:
                errors.append(f"{label}.prompt total {totals[0]} does not match {total}")
            if not totals:
                warnings.append(f"{label}.prompt has no recognizable total-duration statement")
            if prompt_ranges and prompt_ranges != structured_ranges:
                errors.append(
                    f"{label}.prompt ranges {prompt_ranges!r} do not match structured ranges {structured_ranges!r}"
                )
            if not prompt_ranges:
                warnings.append(f"{label}.prompt has no recognizable timeline ranges")
            if AMBIGUOUS.search(prompt):
                warnings.append(f"{label}.prompt contains potentially ambiguous wording")

    for item in errors:
        print(f"ERROR: {item}")
    for item in warnings:
        print(f"WARNING: {item}")
    print(
        f"Validated {len(scenes)} scene(s), {shot_count} shot(s): "
        f"{len(errors)} error(s), {len(warnings)} warning(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
