"""One-command talent data refresh for dev workflow (#56).

Auto-detects the Icarus game installation via Steam, extracts talent
data from pak files, and regenerates talent_data.py.

Usage:
    python refresh_talent_data.py           Auto-detect and refresh
    python refresh_talent_data.py --detect  Just show detected paths (dry run)
    python refresh_talent_data.py PATH      Use a specific data.pak path
"""
import os
import sys
import re
import glob
import shutil
import subprocess
import time

# Icarus Steam App ID
ICARUS_APP_ID = '1149460'
PAK_DIR = 'pak-files'


# ── Steam Detection ──────────────────────────────────────────────────────────

def find_steam_path():
    """Find Steam installation path from Windows Registry."""
    try:
        import winreg
        # Try HKLM first (most reliable)
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r'SOFTWARE\WOW6432Node\Valve\Steam')
        path, _ = winreg.QueryValueEx(key, 'InstallPath')
        winreg.CloseKey(key)
        return path
    except Exception:
        pass

    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'SOFTWARE\Valve\Steam')
        path, _ = winreg.QueryValueEx(key, 'SteamPath')
        winreg.CloseKey(key)
        return path.replace('/', '\\')
    except Exception:
        pass

    # Fallback: check common locations
    for p in [r'C:\Program Files (x86)\Steam', r'C:\Program Files\Steam',
              r'D:\Steam', r'D:\SteamLibrary']:
        if os.path.isdir(p):
            return p

    return None


def find_steam_libraries(steam_path):
    """Parse libraryfolders.vdf to find all Steam library folders."""
    vdf = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')
    if not os.path.isfile(vdf):
        return [steam_path]

    with open(vdf, encoding='utf-8') as f:
        content = f.read()

    paths = re.findall(r'"path"\s+"(.+?)"', content)
    return [p.replace('\\\\', '\\') for p in paths]


def find_icarus_data_pak():
    """Auto-detect Icarus data.pak from Steam installation.

    Returns (pak_path, details_dict) or (None, error_string).
    """
    steam = find_steam_path()
    if not steam:
        return None, "Steam not found in registry or common locations"

    libraries = find_steam_libraries(steam)
    if not libraries:
        return None, f"No Steam libraries found (Steam at {steam})"

    for lib in libraries:
        manifest = os.path.join(lib, 'steamapps', f'appmanifest_{ICARUS_APP_ID}.acf')
        if not os.path.isfile(manifest):
            continue

        data_dir = os.path.join(lib, 'steamapps', 'common', 'Icarus',
                                'Icarus', 'Content', 'Data')
        pak_path = os.path.join(data_dir, 'data.pak')

        if os.path.isfile(pak_path):
            size_mb = os.path.getsize(pak_path) / (1024 * 1024)
            mtime = os.path.getmtime(pak_path)
            return pak_path, {
                'steam': steam,
                'library': lib,
                'data_dir': data_dir,
                'size_mb': size_mb,
                'modified': time.ctime(mtime),
            }
        else:
            return None, f"Icarus installed at {lib} but data.pak not found at {pak_path}"

    return None, f"Icarus not found in any Steam library: {libraries}"


# ── Refresh Pipeline ─────────────────────────────────────────────────────────

def ensure_pak_dir():
    """Create pak-files/ directory if it doesn't exist."""
    os.makedirs(PAK_DIR, exist_ok=True)


def copy_pak(source_pak):
    """Copy data.pak to pak-files/ for extraction."""
    dest = os.path.join(PAK_DIR, 'data.pak')
    if os.path.isfile(dest):
        # Check if it's the same file
        if os.path.getsize(dest) == os.path.getsize(source_pak):
            if os.path.getmtime(dest) >= os.path.getmtime(source_pak):
                print("  pak-files/data.pak is up to date, skipping copy")
                return dest
    print(f"  Copying data.pak ({os.path.getsize(source_pak) / (1024*1024):.1f} MB)...")
    shutil.copy2(source_pak, dest)
    return dest


def run_step(description, script):
    """Run a Python script and check for success."""
    print(f"\n{'─' * 60}")
    print(f"Step: {description}")
    print(f"  Running: python {script}")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  FAILED (exit code {result.returncode})")
        if result.stderr:
            print(f"  stderr: {result.stderr[:500]}")
        return False

    # Show key output lines
    for line in result.stdout.strip().split('\n'):
        print(f"  {line}")
    return True


def count_talents():
    """Count talents in current talent_data.py for change detection."""
    try:
        import talent_data
        # Force reimport to get fresh data
        import importlib
        importlib.reload(talent_data)
        types = talent_data.get_all_types()
        total = sum(len(talent_data.get_talent_tree(t)) for t in types)
        return len(types), total
    except Exception:
        return 0, 0


def count_variations():
    """Count variation types in current variation_data.py for change detection."""
    try:
        import variation_data
        import importlib
        importlib.reload(variation_data)
        types_with = len(variation_data.TYPES_WITH_VARIATIONS)
        total = sum(variation_data.get_variation_count(t)
                    for t in variation_data.TYPES_WITH_VARIATIONS)
        return types_with, total
    except Exception:
        return 0, 0


def refresh(pak_path):
    """Run the full refresh pipeline (talents + variations)."""
    start = time.time()

    print(f"\nSource: {pak_path}")
    print(f"{'=' * 60}")

    # Count before
    types_before, talents_before = count_talents()
    var_types_before, var_total_before = count_variations()

    # Step 0: Copy pak file
    print("\nStep 0: Preparing pak file...")
    ensure_pak_dir()
    copy_pak(pak_path)

    # Step 1: Extract from pak
    ok = run_step("Extract chunks from data.pak", os.path.join("scripts", "pak_extract.py"))
    if not ok:
        print("\n❌ Extraction failed!")
        return False

    # Step 2: Parse talent entries
    ok = run_step("Parse talent entries from extracted chunks", os.path.join("scripts", "pak_talent_extract.py"))
    if not ok:
        print("\n❌ Talent parsing failed!")
        return False

    # Step 3: Generate talent_data.py
    ok = run_step("Generate talent_data.py", os.path.join("scripts", "generate_talent_data.py"))
    if not ok:
        print("\n❌ Talent code generation failed!")
        return False

    # Step 4: Parse variation entries
    ok = run_step("Parse variation entries from extracted chunks", os.path.join("scripts", "pak_variation_extract.py"))
    if not ok:
        print("\n❌ Variation parsing failed!")
        return False

    # Step 5: Generate variation_data.py
    ok = run_step("Generate variation_data.py", os.path.join("scripts", "generate_variation_data.py"))
    if not ok:
        print("\n❌ Variation code generation failed!")
        return False

    # Count after
    types_after, talents_after = count_talents()
    var_types_after, var_total_after = count_variations()

    elapsed = time.time() - start

    print(f"\n{'=' * 60}")
    print(f"✅ Refresh complete! ({elapsed:.1f}s)")
    print(f"   Types:      {types_before} → {types_after} ({types_after - types_before:+d})")
    print(f"   Talents:    {talents_before} → {talents_after} ({talents_after - talents_before:+d})")
    print(f"   Var types:  {var_types_before} → {var_types_after} ({var_types_after - var_types_before:+d})")
    print(f"   Var total:  {var_total_before} → {var_total_after} ({var_total_after - var_total_before:+d})")

    changes = (types_after != types_before or talents_after != talents_before
               or var_types_after != var_types_before or var_total_after != var_total_before)
    if changes:
        print(f"\n   ⚠ Changes detected — review and commit talent_data.py + variation_data.py")
    else:
        print(f"\n   No changes — data files are up to date")

    return True


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    print("Icarus Talent Data Refresh Tool")
    print()

    # --detect flag: just show paths, don't run
    if '--detect' in sys.argv:
        pak_path, info = find_icarus_data_pak()
        if pak_path:
            print(f"✅ Icarus data.pak found!")
            print(f"   Path:     {pak_path}")
            print(f"   Steam:    {info['steam']}")
            print(f"   Library:  {info['library']}")
            print(f"   Size:     {info['size_mb']:.1f} MB")
            print(f"   Modified: {info['modified']}")
        else:
            print(f"❌ {info}")
        return

    # Explicit path argument
    explicit_path = None
    for arg in sys.argv[1:]:
        if not arg.startswith('-') and os.path.isfile(arg):
            explicit_path = arg
            break

    if explicit_path:
        pak_path = explicit_path
        print(f"Using specified path: {pak_path}")
    else:
        print("Auto-detecting Icarus installation...")
        pak_path, info = find_icarus_data_pak()
        if not pak_path:
            print(f"❌ {info}")
            print(f"\nUsage: python refresh_talent_data.py [path/to/data.pak]")
            sys.exit(1)
        print(f"✅ Found: {pak_path}")
        if isinstance(info, dict):
            print(f"   Steam library: {info['library']}")
            print(f"   Last modified: {info['modified']}")

    success = refresh(pak_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
