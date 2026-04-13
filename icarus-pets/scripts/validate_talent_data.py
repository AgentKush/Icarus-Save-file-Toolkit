"""Validate talent_data.py row names against game-created sample saves.

Run after game patches or talent data regeneration to detect mismatches
between what our talent trees emit and what the game actually writes.

Usage:
    python scripts/validate_talent_data.py

Reports:
    ✅ Types where all save row names match our tree
    ⚠️ Types where save row names DON'T match (need TREE_ALIAS or fix)
    ❓ Types with no sample save coverage (untested)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from icarus_pets.talent_data import (
    detect_type,
    get_talent_tree,
    get_all_types,
)

# Try to import icarus_core for binary parsing
try:
    CORE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "icarus-core")
    sys.path.insert(0, CORE_PATH)
    from icarus_core import BinaryReader, parse_properties
except ImportError:
    print("ERROR: icarus_core not found. Install or set PYTHONPATH.")
    sys.exit(1)

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "sample_mounts")


def extract_talents_from_saves():
    """Extract {type: {row_name: count}} from all sample saves."""
    type_talents = {}  # {creature_type: set(row_names)}

    for root, _dirs, files in os.walk(SAMPLE_DIR):
        for fname in files:
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, encoding="utf-8-sig") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                print(f"  ⚠️ Skipping unreadable file: {fname}")
                continue

            for mount in data.get("SavedMounts", []):
                bd = mount.get("RecorderBlob", {}).get("BinaryData", [])
                if not bd:
                    continue
                reader = BinaryReader(bytes(bd))
                props = parse_properties(reader)

                ai_setup = ""
                talent_names = set()
                for p in props:
                    if p.get("name") == "AISetupRowName":
                        ai_setup = p.get("value", "")
                    if p.get("name") == "Talents":
                        for elem in p.get("elements", []):
                            for tp in elem:
                                if tp.get("name") == "TalentRowName":
                                    talent_names.add(tp["value"])

                if not talent_names:
                    continue

                creature_type = detect_type(ai_setup=ai_setup)
                if creature_type == "Unknown":
                    print(f"  ❓ Unknown type for AI setup: {ai_setup} ({mount.get('MountName', '?')})")
                    continue

                if creature_type not in type_talents:
                    type_talents[creature_type] = set()
                type_talents[creature_type].update(talent_names)

    return type_talents


def main():
    print("Validating talent_data.py against sample saves...\n")

    save_talents = extract_talents_from_saves()
    all_types = get_all_types()

    matched = []
    mismatched = []
    uncovered = []

    for creature_type in sorted(all_types):
        tree = get_talent_tree(creature_type)
        tree_names = {t["name"] for t in tree}

        if creature_type not in save_talents:
            uncovered.append(creature_type)
            continue

        save_names = save_talents[creature_type]
        missing_from_tree = save_names - tree_names
        extra_in_tree = tree_names - save_names  # not an error, just unallocated

        if missing_from_tree:
            mismatched.append((creature_type, missing_from_tree, extra_in_tree))
        else:
            matched.append(creature_type)

    # Report
    print(f"{'='*60}")
    print(f"VALIDATION RESULTS")
    print(f"{'='*60}\n")

    if matched:
        print(f"✅ Validated ({len(matched)} types):")
        for t in matched:
            count = len(save_talents[t])
            print(f"   {t:25s} ({count} talents in saves)")

    if mismatched:
        print(f"\n⚠️  MISMATCHES ({len(mismatched)} types):")
        for t, missing, extra in mismatched:
            print(f"\n   {t}:")
            print(f"     Row names in save but NOT in our tree:")
            for m in sorted(missing):
                print(f"       - {m}")
            if extra:
                print(f"     In our tree but not in save (may be unallocated):")
                for e in sorted(extra):
                    print(f"       + {e}")

    if uncovered:
        print(f"\n❓ No sample save coverage ({len(uncovered)} types):")
        for t in uncovered:
            print(f"   {t}")

    print(f"\n{'='*60}")
    total = len(matched) + len(mismatched) + len(uncovered)
    print(f"Total: {total} types | ✅ {len(matched)} validated | ⚠️ {len(mismatched)} mismatched | ❓ {len(uncovered)} uncovered")

    return 1 if mismatched else 0


if __name__ == "__main__":
    sys.exit(main())
