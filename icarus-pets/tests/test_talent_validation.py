"""Validate talent row names against real game-created save files.

Reads every mount from tests/sample_mounts/, extracts talent row names
from the binary data, and asserts they exist in our talent_data.py trees.

This catches:
- Wrong row names (e.g., simplified names that don't match game saves)
- Missing talents in our trees
- Tree alias mismatches (sub-types using parent tree row names)

To add coverage for a new species: drop a game-created Mounts.json
into tests/sample_mounts/ with at least one mount of that species
that has talent points allocated in-game.
"""
import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from icarus_pets.talent_data import detect_type, get_talent_tree

# icarus_core may not be installed in test env — try import, skip if unavailable
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    from icarus_core import BinaryReader, parse_properties
    HAS_CORE = True
except ImportError:
    HAS_CORE = False

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_mounts")


def _iter_mounts_with_talents():
    """Yield (filename, mount_name, ai_setup, talent_row_names) from sample saves."""
    if not os.path.isdir(SAMPLE_DIR):
        return
    for root, _dirs, files in os.walk(SAMPLE_DIR):
        for fname in files:
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, encoding="utf-8-sig") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            for mount in data.get("SavedMounts", []):
                bd = mount.get("RecorderBlob", {}).get("BinaryData", [])
                if not bd:
                    continue
                reader = BinaryReader(bytes(bd))
                props = parse_properties(reader)

                ai_setup = ""
                talent_names = []
                for p in props:
                    if p.get("name") == "AISetupRowName":
                        ai_setup = p.get("value", "")
                    if p.get("name") == "Talents":
                        for elem in p.get("elements", []):
                            for tp in elem:
                                if tp.get("name") == "TalentRowName":
                                    talent_names.append(tp["value"])

                if talent_names:
                    yield (
                        os.path.relpath(fpath, SAMPLE_DIR),
                        mount.get("MountName", "?"),
                        ai_setup,
                        talent_names,
                    )


@pytest.mark.skipif(not HAS_CORE, reason="icarus_core not available")
class TestSaveTalentRowNames:
    """Validate that talent row names from game saves match our talent trees."""

    def _get_sample_mounts(self):
        return list(_iter_mounts_with_talents())

    def test_sample_saves_exist(self):
        """At least one sample save has mounts with talents."""
        mounts = self._get_sample_mounts()
        assert len(mounts) > 0, (
            "No sample mounts with talents found. "
            "Add game-created Mounts.json files to tests/sample_mounts/"
        )

    def test_all_talent_row_names_in_tree(self):
        """Every talent row name from a game save must exist in our tree for that type."""
        mounts = self._get_sample_mounts()
        errors = []
        for fname, mount_name, ai_setup, talent_names in mounts:
            creature_type = detect_type(ai_setup=ai_setup)
            if creature_type == "Unknown":
                continue  # Can't validate types we don't recognize

            tree = get_talent_tree(creature_type)
            tree_names = {t["name"] for t in tree}

            for tname in talent_names:
                if tname not in tree_names:
                    errors.append(
                        f"{fname}/{mount_name} ({creature_type}): "
                        f"'{tname}' not in tree (has {len(tree_names)} talents)"
                    )

        assert not errors, (
            f"Talent row name mismatches ({len(errors)}):\n"
            + "\n".join(f"  - {e}" for e in errors)
        )

    def test_detected_types_have_trees(self):
        """Every detected creature type from sample saves should have a talent tree."""
        mounts = self._get_sample_mounts()
        missing = set()
        for _fname, _name, ai_setup, _talents in mounts:
            creature_type = detect_type(ai_setup=ai_setup)
            if creature_type == "Unknown":
                continue
            tree = get_talent_tree(creature_type)
            if not tree:
                missing.add(creature_type)

        assert not missing, f"Types with no talent tree: {missing}"
