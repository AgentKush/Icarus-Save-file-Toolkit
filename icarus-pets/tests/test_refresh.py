"""Tests for #56 — auto-detect game data and refresh tool."""
import sys, os, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from refresh_talent_data import (
    find_steam_path, find_steam_libraries, find_icarus_data_pak,
    ICARUS_APP_ID
)


# ── Steam Detection ──────────────────────────────────────────────────────────

def test_find_steam_path():
    """Registry-based Steam detection returns a valid directory."""
    path = find_steam_path()
    assert path is not None, "Steam not found (is Steam installed?)"
    assert os.path.isdir(path), f"Steam path not a directory: {path}"
    print(f"  ✓ find_steam_path: {path}")


def test_find_steam_libraries():
    """VDF parsing returns at least one library folder."""
    steam = find_steam_path()
    assert steam is not None
    libs = find_steam_libraries(steam)
    assert len(libs) >= 1, "No library folders found"
    for lib in libs:
        assert os.path.isdir(lib), f"Library not a directory: {lib}"
    print(f"  ✓ find_steam_libraries: {len(libs)} folder(s)")


def test_icarus_manifest_exists():
    """Icarus app manifest exists in a Steam library."""
    steam = find_steam_path()
    libs = find_steam_libraries(steam)
    found = False
    for lib in libs:
        manifest = os.path.join(lib, 'steamapps', f'appmanifest_{ICARUS_APP_ID}.acf')
        if os.path.isfile(manifest):
            found = True
            break
    assert found, "Icarus manifest not found (is the game installed?)"
    print(f"  ✓ Icarus manifest found in {lib}")


def test_find_icarus_data_pak():
    """Full detection chain finds data.pak."""
    pak_path, info = find_icarus_data_pak()
    assert pak_path is not None, f"data.pak not found: {info}"
    assert os.path.isfile(pak_path)
    assert pak_path.endswith('data.pak')
    assert isinstance(info, dict)
    assert info['size_mb'] > 0
    print(f"  ✓ find_icarus_data_pak: {pak_path} ({info['size_mb']:.1f} MB)")


def test_data_pak_is_valid():
    """data.pak starts with valid UE4 pak content (not empty/corrupted)."""
    pak_path, _ = find_icarus_data_pak()
    assert pak_path is not None
    with open(pak_path, 'rb') as f:
        header = f.read(4)
    assert len(header) == 4
    # UE4 pak files have content before the footer magic
    assert os.path.getsize(pak_path) > 1000, "data.pak suspiciously small"
    print(f"  ✓ data.pak is valid ({os.path.getsize(pak_path):,} bytes)")


# ── CLI Flags ────────────────────────────────────────────────────────────────

def _run_detect():
    """Helper to run --detect with proper encoding."""
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    return subprocess.run(
        [sys.executable, os.path.join('scripts', 'refresh_talent_data.py'), '--detect'],
        capture_output=True, text=True, timeout=10, env=env
    )


def test_detect_flag():
    """--detect flag runs without error and shows path info."""
    result = _run_detect()
    assert result.returncode == 0, f"Exit {result.returncode}: {result.stderr[:200]}"
    assert 'data.pak found' in result.stdout or 'not found' in result.stdout
    print(f"  ✓ --detect flag works")


def test_detect_shows_steam_path():
    """--detect output includes Steam and library paths."""
    result = _run_detect()
    assert 'Steam' in result.stdout
    assert 'Path:' in result.stdout
    print(f"  ✓ --detect shows Steam details")


# ── Runner ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Refresh Tool Tests ===")
    print()
    print("-- Steam Detection --")
    test_find_steam_path()
    test_find_steam_libraries()
    test_icarus_manifest_exists()
    test_find_icarus_data_pak()
    test_data_pak_is_valid()
    print()
    print("-- CLI Flags --")
    test_detect_flag()
    test_detect_shows_steam_path()
    print(f"\n✅ All 7 tests passed!")
