r"""
Icarus Icon Extractor v4 - Extracts ALL item icons from game exports.

Auto-detects your Icarus install location and texconv.exe.
Scans exported .uexp/.json texture files and converts them to PNG.

Usage:
  python extract_all_icons.py                          (auto-detect everything)
  python extract_all_icons.py --base "D:\Games\Icarus\Exports\Icarus\Content"
  python extract_all_icons.py --out "C:\MyIcons"
  python extract_all_icons.py --filter "Lithium"
  python extract_all_icons.py --force                  (re-extract all, overwrite existing)
"""
import struct, json, os, subprocess, glob, argparse, sys
try:
    import winreg
except ImportError:
    winreg = None  # Not on Windows — registry detection skipped


# ===================================================================
#  AUTO-DETECTION — finds Icarus exports, texconv, and output paths
# ===================================================================

def find_steam_libraries():
    """Find all Steam library folders on this PC."""
    libraries = []

    # Try reading Steam install path from Windows registry
    steam_path = None
    if winreg:
        for key_path in [
            r'SOFTWARE\Valve\Steam',
            r'SOFTWARE\WOW6432Node\Valve\Steam',
        ]:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                steam_path, _ = winreg.QueryValueEx(key, 'InstallPath')
                winreg.CloseKey(key)
                break
            except (OSError, FileNotFoundError):
                continue

        # Also try HKEY_CURRENT_USER
        if not steam_path:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Valve\Steam')
                steam_path, _ = winreg.QueryValueEx(key, 'SteamPath')
                winreg.CloseKey(key)
            except (OSError, FileNotFoundError):
                pass

    # Default Steam paths to check
    candidates = [
        os.path.join(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'), 'Steam'),
        os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), 'Steam'),
        r'C:\Steam',
    ]
    if steam_path:
        candidates.insert(0, steam_path)

    # Find the main steamapps folder and parse libraryfolders.vdf for extra libraries
    for candidate in candidates:
        steamapps = os.path.join(candidate, 'steamapps')
        if os.path.isdir(steamapps):
            libraries.append(steamapps)
            # Parse libraryfolders.vdf for additional library paths
            vdf = os.path.join(steamapps, 'libraryfolders.vdf')
            if os.path.isfile(vdf):
                try:
                    with open(vdf, encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if '"path"' in line:
                                # Extract path from: "path"   "D:\\Games\\Steam"
                                parts = line.split('"')
                                if len(parts) >= 4:
                                    lib_path = parts[3].replace('\\\\', '\\')
                                    lib_apps = os.path.join(lib_path, 'steamapps')
                                    if os.path.isdir(lib_apps) and lib_apps not in libraries:
                                        libraries.append(lib_apps)
                except Exception:
                    pass
            break  # Found main Steam, no need to check other candidates

    # Also brute-force check common drive letters
    for drive in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
        for subdir in [
            f'{drive}:\\SteamLibrary\\steamapps',
            f'{drive}:\\Steam\\steamapps',
            f'{drive}:\\Games\\Steam\\steamapps',
            f'{drive}:\\Games\\SteamLibrary\\steamapps',
            f'{drive}:\\Program Files (x86)\\Steam\\steamapps',
        ]:
            if os.path.isdir(subdir) and subdir not in libraries:
                libraries.append(subdir)

    return libraries


def find_icarus_exports():
    """Auto-detect the Icarus game exports directory."""
    libraries = find_steam_libraries()
    for lib in libraries:
        exports = os.path.join(lib, 'common', 'Icarus', 'Exports', 'Icarus', 'Content')
        if os.path.isdir(exports):
            return exports
    return None


def find_texconv():
    """Auto-detect texconv.exe — checks PATH, Desktop, Downloads, and common locations."""
    # Check if it's on PATH
    for cmd in ['texconv', 'texconv.exe']:
        try:
            r = subprocess.run([cmd, '--help'], capture_output=True, timeout=5)
            return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass

    # Common locations to check
    home = os.path.expanduser('~')
    search_dirs = [
        os.path.join(home, 'Desktop'),
        os.path.join(home, 'Downloads'),
        os.path.join(home, 'Documents'),
        os.getcwd(),
        os.path.dirname(os.path.abspath(__file__)),
    ]

    for d in search_dirs:
        path = os.path.join(d, 'texconv.exe')
        if os.path.isfile(path):
            return path

    # Recursive search of script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for root, dirs, files in os.walk(script_dir):
        if 'texconv.exe' in files:
            return os.path.join(root, 'texconv.exe')
        # Don't recurse too deep
        if root.count(os.sep) - script_dir.count(os.sep) > 2:
            dirs.clear()

    return None


def prompt_path(prompt_text, must_exist=True, is_dir=True):
    """Ask the user to enter a path, with validation."""
    while True:
        path = input(prompt_text).strip().strip('"').strip("'")
        if not path:
            return None
        path = os.path.expanduser(path)
        if must_exist:
            if is_dir and not os.path.isdir(path):
                print(f'  Directory not found: {path}')
                continue
            if not is_dir and not os.path.isfile(path):
                print(f'  File not found: {path}')
                continue
        return path

# All known icon directories under Assets/2DArt/UI
ICON_SEARCH_PATHS = [
    os.path.join('Assets', '2DArt', 'UI', 'Items', 'Item_Icons'),
    os.path.join('Assets', '2DArt', 'UI', 'Items'),
    os.path.join('Assets', '2DArt', 'UI', 'Workshop'),
    os.path.join('Assets', '2DArt', 'UI', 'Modules'),
    os.path.join('Assets', '2DArt', 'UI', 'Weapons'),
    os.path.join('Assets', '2DArt', 'UI', 'Tools'),
    os.path.join('Assets', '2DArt', 'UI', 'Equipment'),
    os.path.join('Assets', '2DArt', 'UI', 'Talents'),
    os.path.join('Assets', '2DArt', 'UI', 'Mounts'),
    os.path.join('Assets', '2DArt', 'UI', 'Pets'),
    os.path.join('Assets', '2DArt', 'UI', 'Resources'),
    os.path.join('Assets', '2DArt', 'UI', 'Armour'),
    os.path.join('Assets', '2DArt', 'UI', 'Consumables'),
    os.path.join('Assets', '2DArt', 'UI', 'StatusEffects'),
    os.path.join('Assets', '2DArt', 'UI'),
]

# DDS constants
DDS_MAGIC = b'DDS '
DDSD_CAPS        = 0x1
DDSD_HEIGHT      = 0x2
DDSD_WIDTH       = 0x4
DDSD_PIXELFORMAT = 0x1000
DDSD_LINEARSIZE  = 0x80000
DDPF_FOURCC      = 0x4
DDPF_RGB         = 0x40
DDPF_ALPHAPIXELS = 0x1
DDSCAPS_TEXTURE  = 0x1000

# UE4 .uexp structure constants (verified from binary analysis of Icarus exports):
#   Each mip entry: [BulkData header(24)] [pixel data] [SizeX(4) + SizeY(4) + SizeZ(4)]
#   After all mips: [bIsVirtual(4)] [FName_None(8)] [package_tag(4)]
BULK_HEADER_SIZE = 24   # FBulkData: flags(4) + count(4) + sizeOnDisk(4) + offsetInFile(8) + extra(4)
MIP_FOOTER_SIZE  = 12   # SizeX(4) + SizeY(4) + SizeZ(4) after each mip's payload
UEXP_TRAILER_SIZE = 16  # bIsVirtual(4) + FName_None(8) + package_tag(4)


def make_dds_header(width, height, pixel_format, data_size):
    """Build a DDS file header for the given texture format."""
    if pixel_format in ('PF_DXT5', 'PF_BC3'):
        fourcc = b'DXT5'
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_FOURCC, fourcc, 0, 0, 0, 0, 0)
    elif pixel_format in ('PF_DXT1', 'PF_BC1'):
        fourcc = b'DXT1'
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_FOURCC, fourcc, 0, 0, 0, 0, 0)
    elif pixel_format == 'PF_BC7':
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_FOURCC, b'DX10', 0, 0, 0, 0, 0)
    elif pixel_format == 'PF_B8G8R8A8':
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_RGB | DDPF_ALPHAPIXELS, b'\x00'*4,
            32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    else:
        return None

    flags = DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_LINEARSIZE
    header = struct.pack('<I I I I I I I', 124, flags, height, width, data_size, 0, 1)
    header += b'\x00' * 44  # reserved
    header += pf
    header += struct.pack('<I', DDSCAPS_TEXTURE)
    header += b'\x00' * 16  # caps2, reserved

    result = DDS_MAGIC + header
    if pixel_format == 'PF_BC7':
        result += struct.pack('<I I I I I', 98, 3, 0, 1, 0)  # DX10 ext header
    return result


def detect_inter_mip_gap(mips):
    """Auto-detect the gap between mip payloads using OffsetInFile from JSON metadata.
    Returns (bulk_header_size, mip_footer_size) or None if detection fails."""
    if len(mips) < 2:
        return None
    try:
        offsets = []
        sizes = []
        for m in mips:
            bd = m['BulkData']
            off_str = bd.get('OffsetInFile', '')
            if isinstance(off_str, str) and off_str.startswith('0x'):
                offsets.append(int(off_str, 16))
            elif isinstance(off_str, (int, float)):
                offsets.append(int(off_str))
            else:
                return None
            sizes.append(bd.get('SizeOnDisk', bd.get('ElementCount', 0)))

        # Compute gaps between consecutive mips
        gaps = [offsets[i+1] - (offsets[i] + sizes[i]) for i in range(len(mips)-1)]
        if not gaps or any(g <= 0 or g > 128 for g in gaps):
            return None

        # All gaps should be identical (bulk_header + mip_footer)
        gap = gaps[0]
        if not all(g == gap for g in gaps):
            return None

        # Gap = MIP_FOOTER(12) + BULK_HEADER
        # MIP_FOOTER is SizeX(4)+SizeY(4)+SizeZ(4) = 12 bytes
        return (gap - 12, 12)  # (bulk_header_size, mip_footer_size)
    except (KeyError, ValueError, TypeError):
        return None


def extract_texture_data(uexp_path, json_path):
    """Extract raw texture data from a .uexp file using its .json metadata."""
    if not os.path.exists(json_path) or not os.path.exists(uexp_path):
        return None, 'missing file'
    try:
        with open(json_path, encoding='utf-8') as f:
            meta = json.load(f)
        if isinstance(meta, list):
            meta = meta[0]

        w = meta.get('SizeX', 256)
        h = meta.get('SizeY', 256)
        fmt = meta.get('PixelFormat', 'PF_DXT5')
        mips = meta.get('Mips', [])
        if not mips:
            return None, 'no mips'

        num_mips = len(mips)
        mip0_size = mips[0]['BulkData'].get('SizeOnDisk',
                    mips[0]['BulkData'].get('ElementCount', 0))

        total_mip_data = sum(
            m['BulkData'].get('SizeOnDisk', m['BulkData'].get('ElementCount', 0))
            for m in mips)

        uexp_size = os.path.getsize(uexp_path)

        # Auto-detect bulk header size from OffsetInFile gaps, fall back to defaults
        detected = detect_inter_mip_gap(mips)
        if detected:
            bh_size, mf_size = detected
        else:
            bh_size, mf_size = BULK_HEADER_SIZE, MIP_FOOTER_SIZE

        # UE4 .uexp layout:
        #   [properties] [BH0][mip0][dim0] [BH1][mip1][dim1] ... [BHn][mipN][dimN] [trailer]
        # Each mip overhead = bulk_header + mip_footer (SizeX+SizeY+SizeZ)
        per_mip_overhead = bh_size + mf_size
        total_bulk = num_mips * per_mip_overhead + total_mip_data + UEXP_TRAILER_SIZE
        mip0_offset = uexp_size - total_bulk + bh_size

        if mip0_offset < 0 or mip0_offset + mip0_size > uexp_size:
            return None, f'bad offset {mip0_offset} (uexp={uexp_size})'

        with open(uexp_path, 'rb') as f:
            f.seek(mip0_offset)
            raw = f.read(mip0_size)

        if len(raw) < mip0_size:
            return None, f'short read {len(raw)}/{mip0_size}'

        return {
            'data': raw, 'width': w, 'height': h,
            'format': fmt, 'size': mip0_size,
        }, f'{fmt} {w}x{h} ({num_mips} mips)'
    except Exception as e:
        return None, str(e)


def extract_icon(uexp_path, out_png_path, dds_dir, texconv, out_dir):
    """Extract a single icon from .uexp to .png via DDS intermediate."""
    json_path = uexp_path.replace('.uexp', '.json')
    result, msg = extract_texture_data(uexp_path, json_path)
    if result is None:
        return False, msg

    dds_header = make_dds_header(result['width'], result['height'],
                                  result['format'], result['size'])
    if dds_header is None:
        return False, f"unsupported: {result['format']}"

    base = os.path.splitext(os.path.basename(out_png_path))[0]
    dds_path = os.path.join(dds_dir, base + '.dds')
    with open(dds_path, 'wb') as f:
        f.write(dds_header)
        f.write(result['data'])

    try:
        r = subprocess.run([texconv, '-ft', 'png', '-y', '-o', out_dir, dds_path],
                          capture_output=True, text=True, timeout=30)
        expected = os.path.join(out_dir, base + '.png')
        if os.path.exists(expected):
            if expected != out_png_path:
                if os.path.exists(out_png_path):
                    os.remove(out_png_path)
                os.rename(expected, out_png_path)
            return True, msg
        else:
            return False, f'texconv fail: {r.stderr[:200]}'
    except Exception as e:
        return False, f'texconv error: {e}'


def find_all_icons(base_path, search_paths, name_filter=None):
    """
    Recursively scan all icon directories for .uexp files with matching .json metadata.
    Returns a dict of {output_name: uexp_path}.
    """
    icons = {}
    scanned_dirs = set()

    for rel_path in search_paths:
        search_dir = os.path.join(base_path, rel_path)
        if not os.path.isdir(search_dir):
            continue

        for root, dirs, files in os.walk(search_dir):
            # Skip already-scanned directories (from overlapping search paths)
            real_root = os.path.realpath(root)
            if real_root in scanned_dirs:
                continue
            scanned_dirs.add(real_root)

            for filename in files:
                if not filename.lower().endswith('.uexp'):
                    continue

                uexp_path = os.path.join(root, filename)
                json_path = uexp_path.replace('.uexp', '.json')

                # Must have matching .json metadata
                if not os.path.exists(json_path):
                    continue

                # Quick check: verify the .json describes a texture (has Mips)
                try:
                    with open(json_path, encoding='utf-8') as f:
                        meta = json.load(f)
                    if isinstance(meta, list):
                        meta = meta[0]
                    if 'Mips' not in meta or not meta['Mips']:
                        continue
                except:
                    continue

                # Build output name from relative path
                rel = os.path.relpath(uexp_path, base_path)
                # Create a clean name: Category_SubCategory_FileName.png
                parts = rel.replace('\\', '/').split('/')
                # Remove common prefixes
                clean_parts = []
                skip = {'Assets', '2DArt', 'UI', 'Items', 'Item_Icons'}
                for p in parts:
                    if p in skip:
                        continue
                    clean_parts.append(p)

                if clean_parts:
                    # Last part is the filename
                    stem = os.path.splitext(clean_parts[-1])[0]
                    # Prefix with subdirectory for organization
                    if len(clean_parts) > 1:
                        subdir = clean_parts[-2]
                        out_name = f"{subdir}_{stem}.png"
                    else:
                        out_name = f"{stem}.png"
                else:
                    out_name = os.path.splitext(filename)[0] + '.png'

                # Apply name filter if specified
                if name_filter:
                    if name_filter.lower() not in out_name.lower() and \
                       name_filter.lower() not in uexp_path.lower():
                        continue

                # Avoid duplicates (prefer shorter paths)
                if out_name not in icons or len(uexp_path) < len(icons[out_name]):
                    icons[out_name] = uexp_path

    return icons


def main():
    parser = argparse.ArgumentParser(
        description='Icarus Icon Extractor — auto-detects game location and extracts all item icons to PNG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='If no arguments are given, the script will auto-detect paths and ask if needed.')
    parser.add_argument('--base', default=None,
                        help='Path to Icarus exports Content folder (auto-detected if omitted)')
    parser.add_argument('--out', default=None,
                        help='Output directory for PNG files (default: Desktop/icarus_icons)')
    parser.add_argument('--texconv', default=None,
                        help='Path to texconv.exe (auto-detected if omitted)')
    parser.add_argument('--filter', default=None,
                        help='Only extract icons matching this keyword (e.g. "Lithium", "Bow")')
    parser.add_argument('--dry-run', action='store_true',
                        help='List icons that would be extracted without actually extracting')
    parser.add_argument('--force', action='store_true',
                        help='Re-extract icons even if they already exist (overwrite)')
    parser.add_argument('--organize', action='store_true', default=True,
                        help='Organize output into subdirectories by category')
    args = parser.parse_args()

    print(f'=== Icarus Icon Extractor v4 ===\n')

    # --- Resolve game exports path ---
    base_path = args.base
    if not base_path:
        print('[*] Looking for Icarus game exports...')
        base_path = find_icarus_exports()
        if base_path:
            print(f'    Found: {base_path}')
        else:
            print('    Could not auto-detect Icarus exports directory.')
            print('    You need to export game assets first (e.g. with FModel).')
            print('    The exports folder should contain: Assets/2DArt/UI/Items/...\n')
            base_path = prompt_path('    Enter path to Icarus/Exports/Icarus/Content: ')
            if not base_path:
                print('ERROR: No exports path provided. Exiting.')
                sys.exit(1)

    if not os.path.isdir(base_path):
        print(f'ERROR: Directory not found: {base_path}')
        sys.exit(1)

    # --- Resolve output directory ---
    out_dir = args.out
    if not out_dir:
        # Default to Desktop/icarus_icons
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        if os.path.isdir(desktop):
            out_dir = os.path.join(desktop, 'icarus_icons')
        else:
            out_dir = os.path.join(os.getcwd(), 'icarus_icons')
        print(f'[*] Output directory: {out_dir}')

    dds_dir = os.path.join(out_dir, 'dds_temp')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(dds_dir, exist_ok=True)

    # --- Resolve texconv.exe ---
    texconv = args.texconv
    if not texconv and not args.dry_run:
        print('[*] Looking for texconv.exe...')
        texconv = find_texconv()
        if texconv:
            print(f'    Found: {texconv}')
        else:
            print('    Could not find texconv.exe automatically.')
            print('    Download from: https://github.com/microsoft/DirectXTex/releases')
            print('    (Get texconv.exe and place it anywhere, e.g. your Desktop)\n')
            texconv = prompt_path('    Enter path to texconv.exe (or press Enter to abort): ',
                                  must_exist=True, is_dir=False)
            if not texconv:
                print('ERROR: texconv.exe is required for PNG conversion. Exiting.')
                sys.exit(1)

    if texconv and not os.path.isfile(texconv) and not args.dry_run:
        print(f'ERROR: texconv.exe not found at {texconv}')
        sys.exit(1)

    print(f'\n[*] Scanning: {base_path}')
    if args.filter:
        print(f'[*] Filter: {args.filter}')
    print()

    # Find all icon textures
    icons = find_all_icons(base_path, ICON_SEARCH_PATHS, args.filter)

    if not icons:
        print('No icons found! Check your exports path.')
        print(f'  Searched: {base_path}')
        print('  Looking for .uexp files with matching .json metadata under Assets/2DArt/UI/')
        sys.exit(1)

    print(f'Found {len(icons)} icon textures to extract\n')

    if args.dry_run:
        for name in sorted(icons.keys()):
            print(f'  {name}')
        print(f'\nTotal: {len(icons)} icons (dry run, nothing extracted)')
        return

    # Extract all icons
    good, bad, skipped = [], [], []
    for i, (out_name, src) in enumerate(sorted(icons.items()), 1):
        # Organize into subdirectories if requested
        if args.organize and '_' in out_name:
            category = out_name.split('_')[0]
            cat_dir = os.path.join(out_dir, category)
            os.makedirs(cat_dir, exist_ok=True)
            out_path = os.path.join(cat_dir, out_name)
        else:
            out_path = os.path.join(out_dir, out_name)

        # Skip if already extracted (unless --force)
        if os.path.exists(out_path) and not args.force:
            skipped.append(out_name)
            continue

        ok, msg = extract_icon(src, out_path, dds_dir, texconv,
                               os.path.dirname(out_path))
        status = 'OK  ' if ok else 'FAIL'
        print(f'  [{i}/{len(icons)}] {status}  {out_name} ({msg})')
        (good if ok else bad).append(out_name if ok else (out_name, msg))

    # Cleanup DDS temp files
    for f in glob.glob(os.path.join(dds_dir, '*.dds')):
        try:
            os.remove(f)
        except:
            pass
    try:
        os.rmdir(dds_dir)
    except:
        pass

    # Summary
    print(f'\n=== RESULTS ===')
    print(f'Extracted: {len(good)}')
    if skipped:
        print(f'Skipped (already exist): {len(skipped)}')
    if bad:
        print(f'Failed: {len(bad)}')
        for item in bad[:20]:
            if isinstance(item, tuple):
                print(f'  - {item[0]}: {item[1]}')
        if len(bad) > 20:
            print(f'  ... and {len(bad) - 20} more')
    print(f'Total icons: {len(icons)}')
    print(f'\nOutput: {out_dir}')


if __name__ == '__main__':
    main()
