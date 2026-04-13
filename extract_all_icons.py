"""
Icarus icon extractor v3 - Extracts ALL item icons from game exports.
Scans the entire Item_Icons directory tree for .uexp files with matching .json metadata.
Creates DDS files then converts to PNG with texconv.

Usage:
  python extract_all_icons.py
  python extract_all_icons.py --base "E:\SteamLibrary\steamapps\common\Icarus\Exports\Icarus\Content"
  python extract_all_icons.py --out "C:\Users\you\Desktop\all_icons"
  python extract_all_icons.py --filter "Lithium"  # only extract icons matching a keyword
"""
import struct, json, os, subprocess, glob, argparse, sys

# ===== CONFIGURATION =====
DEFAULT_TEXCONV = r'C:\Users\finla\Desktop\texconv.exe'
DEFAULT_OUT_DIR = r'C:\Users\finla\Desktop\icarus_icons'
DEFAULT_BASE = r'E:\SteamLibrary\steamapps\common\Icarus\Exports\Icarus\Content'

# All known icon directories under Assets/2DArt/UI
ICON_SEARCH_PATHS = [
    r'Assets\2DArt\UI\Items\Item_Icons',
    r'Assets\2DArt\UI\Items',
    r'Assets\2DArt\UI\Workshop',
    r'Assets\2DArt\UI\Modules',
    r'Assets\2DArt\UI\Weapons',
    r'Assets\2DArt\UI\Tools',
    r'Assets\2DArt\UI\Equipment',
    r'Assets\2DArt\UI\Talents',
    r'Assets\2DArt\UI\Mounts',
    r'Assets\2DArt\UI\Pets',
    r'Assets\2DArt\UI\Resources',
    r'Assets\2DArt\UI\Armour',
    r'Assets\2DArt\UI\Consumables',
    r'Assets\2DArt\UI\StatusEffects',
    r'Assets\2DArt\UI',
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

UEXP_TRAILER_SIZE = 28
BULK_HEADER_SIZE = 20


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

        # Offset formula: uexp = [properties] [bulk_hdr_0][mip0] [bulk_hdr_1][mip1] ... [trailer]
        total_bulk = num_mips * BULK_HEADER_SIZE + total_mip_data + UEXP_TRAILER_SIZE
        mip0_offset = uexp_size - total_bulk + BULK_HEADER_SIZE

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
    parser = argparse.ArgumentParser(description='Extract ALL Icarus item icons from game exports')
    parser.add_argument('--base', default=DEFAULT_BASE,
                        help='Path to Icarus/Exports/Icarus/Content')
    parser.add_argument('--out', default=DEFAULT_OUT_DIR,
                        help='Output directory for PNG files')
    parser.add_argument('--texconv', default=DEFAULT_TEXCONV,
                        help='Path to texconv.exe')
    parser.add_argument('--filter', default=None,
                        help='Only extract icons matching this keyword (e.g. "Lithium", "Bow")')
    parser.add_argument('--dry-run', action='store_true',
                        help='List icons that would be extracted without actually extracting')
    parser.add_argument('--organize', action='store_true', default=True,
                        help='Organize output into subdirectories by category')
    args = parser.parse_args()

    dds_dir = os.path.join(args.out, 'dds_temp')
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(dds_dir, exist_ok=True)

    if not os.path.exists(args.texconv) and not args.dry_run:
        print(f'ERROR: texconv.exe not found at {args.texconv}')
        print('Download from: https://github.com/microsoft/DirectXTex/releases')
        sys.exit(1)

    if not os.path.isdir(args.base):
        print(f'ERROR: Game exports directory not found: {args.base}')
        print('Make sure you have exported the game assets first.')
        sys.exit(1)

    print(f'=== Icarus Icon Extractor v3 ===')
    print(f'Scanning: {args.base}')
    if args.filter:
        print(f'Filter: {args.filter}')
    print()

    # Find all icon textures
    icons = find_all_icons(args.base, ICON_SEARCH_PATHS, args.filter)

    if not icons:
        print('No icons found! Check your --base path.')
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
            cat_dir = os.path.join(args.out, category)
            os.makedirs(cat_dir, exist_ok=True)
            out_path = os.path.join(cat_dir, out_name)
        else:
            out_path = os.path.join(args.out, out_name)

        # Skip if already extracted
        if os.path.exists(out_path):
            skipped.append(out_name)
            continue

        ok, msg = extract_icon(src, out_path, dds_dir, args.texconv,
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
    print(f'\nOutput: {args.out}')


if __name__ == '__main__':
    main()
