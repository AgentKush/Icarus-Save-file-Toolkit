"""#54: Changed-files test check — warns when source changes lack test changes.

Compares changed .py files in a commit/MR against changed test files.
If source files changed but no corresponding test files changed, issues a warning.

Exempt files (documentation, config, scripts):
- *.md, *.yml, *.yaml, *.spec, *.json, *.txt
- build.py, VERSION, .gitignore
- scripts/*.py (utility scripts, not core source)
- tests/run_all.py (test infrastructure, not a test)

Source → Test mapping:
- ue4_parser.py        → tests/test_ue4_parser.py
- ue4_serializer.py    → tests/test_ue4_serializer.py
- editor/mount_model.py→ tests/test_mount_model.py
- talent_data.py       → tests/test_talent_data.py
- mount_editor.py      → tests/test_packaging.py, tests/test_save_backup.py

Usage:
    python scripts/check_test_changes.py                  # check HEAD commit
    python scripts/check_test_changes.py --ref origin/main  # compare against branch
"""
import os
import sys
import subprocess


# Source file → test file(s) mapping
SOURCE_TEST_MAP = {
    "ue4_parser.py": ["tests/test_ue4_parser.py"],
    "ue4_serializer.py": ["tests/test_ue4_serializer.py"],
    "editor/mount_model.py": ["tests/test_mount_model.py", "tests/test_species_swap.py"],
    "talent_data.py": ["tests/test_talent_data.py", "tests/test_species_swap.py"],
    "mount_editor.py": ["tests/test_packaging.py", "tests/test_save_backup.py"],
    "editor/overview_tab.py": ["tests/test_species_swap.py"],
    "editor/genetics_tab.py": [],
    "editor/talents_tab.py": [],
    "editor/advanced_tab.py": [],
    "editor/__init__.py": [],
    "editor/tooltip.py": [],
    "scripts/refresh_talent_data.py": ["tests/test_refresh.py"],
}

# File patterns to exempt from the check
EXEMPT_EXTENSIONS = {".md", ".yml", ".yaml", ".spec", ".json", ".txt", ".toml", ".cfg"}
EXEMPT_FILES = {"build.py", "VERSION", ".gitignore", ".gitlab-ci.yml", "mount_editor.spec"}
EXEMPT_DIRS = {"scripts", "docs", "wiki", "build", "dist", "pak-files"}


def get_changed_files(ref=None):
    """Get list of changed files compared to ref (or HEAD~1)."""
    if ref:
        cmd = ["git", "diff", "--name-only", ref, "HEAD"]
    else:
        cmd = ["git", "diff", "--name-only", "HEAD~1", "HEAD"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except subprocess.CalledProcessError:
        # Fallback: show staged changes
        result = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True, text=True,
        )
        return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]


def is_exempt(filepath):
    """Check if a file is exempt from the test-change requirement."""
    _, ext = os.path.splitext(filepath)
    if ext in EXEMPT_EXTENSIONS:
        return True

    basename = os.path.basename(filepath)
    if basename in EXEMPT_FILES:
        return True

    # Files in exempt directories
    parts = filepath.replace("\\", "/").split("/")
    if parts[0] in EXEMPT_DIRS:
        return True

    return False


def is_test_file(filepath):
    """Check if a file is a test file."""
    return os.path.basename(filepath).startswith("test_")


def is_source_file(filepath):
    """Check if a file is a tracked source file (not test, not exempt)."""
    if is_test_file(filepath):
        return False
    if is_exempt(filepath):
        return False
    if not filepath.endswith(".py"):
        return False
    return True


def main():
    ref = None
    if "--ref" in sys.argv:
        idx = sys.argv.index("--ref")
        if idx + 1 < len(sys.argv):
            ref = sys.argv[idx + 1]

    changed = get_changed_files(ref)
    if not changed:
        print("ℹ️  No changed files detected.")
        return 0

    print(f"📁 Changed files ({len(changed)}):")
    for f in changed:
        tag = ""
        if is_test_file(f):
            tag = " [test]"
        elif is_exempt(f):
            tag = " [exempt]"
        elif is_source_file(f):
            tag = " [source]"
        print(f"  {f}{tag}")
    print()

    # Separate source and test files
    source_files = [f for f in changed if is_source_file(f)]
    test_files = [f for f in changed if is_test_file(f)]
    exempt_files = [f for f in changed if is_exempt(f)]

    if not source_files:
        if exempt_files and not test_files:
            print("✅ Only exempt files changed (docs/config) — no tests required.")
        elif test_files:
            print("✅ Only test files changed — good practice!")
        else:
            print("ℹ️  No source files changed.")
        return 0

    # Check each source file for corresponding test changes
    warnings = []
    covered = []

    for src in source_files:
        # Normalize path separators
        src_normalized = src.replace("\\", "/")
        expected_tests = SOURCE_TEST_MAP.get(src_normalized, [])

        if not expected_tests:
            # Unknown source file — check if any test file mentions it
            warnings.append((src, "no test mapping defined"))
            continue

        # Check if any expected test was changed
        test_changed = any(
            t.replace("\\", "/") in [f.replace("\\", "/") for f in test_files]
            for t in expected_tests
        )

        if test_changed:
            covered.append(src)
        else:
            test_names = ", ".join(os.path.basename(t) for t in expected_tests)
            warnings.append((src, f"expected changes in: {test_names}"))

    # Report
    if covered:
        print(f"✅ Source files with test coverage ({len(covered)}):")
        for src in covered:
            print(f"  ✓ {src}")
        print()

    if warnings:
        print(f"⚠️  Source files changed WITHOUT corresponding test changes ({len(warnings)}):")
        for src, reason in warnings:
            print(f"  ⚠ {src} — {reason}")
        print()
        print("Consider updating tests to cover your source changes.")
        print("If this change doesn't need tests, this warning can be ignored.")
        return 1  # Soft failure — CI job uses allow_failure: true

    print("✅ All source changes have corresponding test changes!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
