#!/usr/bin/env python3
"""Validate scene JSON files expected by DataLoader.

Usage:
  python tools/validate_scenes.py <file_or_folder>

If a folder is given, the script will validate any .json files found inside.
The expected shape is a top-level dict with an episode key (e.g. 'EP_1') mapping
to a list of scene objects. Each scene should contain at minimum:
  - id: string
  - titulo: string
  - texto: list

Return code 0 on success, 1 on validation errors.
"""
import json
import os
import sys
from typing import Tuple


def validate_scene_obj(scene) -> Tuple[bool, str]:
    if 'id' not in scene:
        return False, "missing 'id'"
    if not isinstance(scene['id'], str):
        return False, "'id' must be a string"
    if 'titulo' not in scene:
        return False, "missing 'titulo'"
    if not isinstance(scene['titulo'], str):
        return False, "'titulo' must be a string"
    if 'texto' not in scene:
        return False, "missing 'texto'"
    if not isinstance(scene['texto'], list):
        return False, "'texto' must be a list"
    return True, ''


def validate_file(path: str) -> Tuple[bool, list]:
    errors = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return False, [f'Failed to load JSON: {e}']

    if not isinstance(data, dict):
        return False, ['Top-level JSON must be an object/dict']

    # Expect at least one episode key mapping to a list
    for ep_key, scenes in data.items():
        if not isinstance(scenes, list):
            errors.append(f"Episode '{ep_key}' must be a list of scenes")
            continue
        for i, scene in enumerate(scenes):
            ok, msg = validate_scene_obj(scene)
            if not ok:
                errors.append(f"{os.path.basename(path)}[{ep_key}][{i}]: {msg}")

    return (len(errors) == 0), errors


def collect_json_files(target: str):
    if os.path.isfile(target):
        return [target]
    out = []
    for root, _, files in os.walk(target):
        for f in files:
            if f.lower().endswith('.json'):
                out.append(os.path.join(root, f))
    return out


def main():
    if len(sys.argv) < 2:
        print('Usage: python tools/validate_scenes.py <file_or_folder>')
        sys.exit(2)

    target = sys.argv[1]
    files = collect_json_files(target)
    if not files:
        print('No JSON files found at', target)
        sys.exit(1)

    overall_ok = True
    for f in files:
        ok, errs = validate_file(f)
        if ok:
            print(f'[OK] {f}')
        else:
            overall_ok = False
            print(f'[ERROR] {f}')
            for e in errs:
                print('  -', e)

    if not overall_ok:
        print('\nValidation failed')
        sys.exit(1)
    print('\nAll validated JSON files look good')


if __name__ == '__main__':
    main()
