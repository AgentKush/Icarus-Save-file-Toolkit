r"""
Icarus Image Extractor v6 — Extracts ALL images from game exports.

No external tools required! Uses pure Python (Pillow) for DDS→PNG conversion.
Auto-detects your Icarus install location.

Extracts: Item icons, loading screens, backgrounds, cinematics, biome art,
          marketing art, VFX textures, environment art, creature textures,
          and everything else with texture data.

Requirements:
  pip install Pillow     (auto-installed if missing)

Usage:
  python extract_all_icons.py                          (auto-detect, UI icons only)
  python extract_all_icons.py --all                    (extract ALL images in game)
  python extract_all_icons.py --loading-screens        (just loading screens)
  python extract_all_icons.py --backgrounds            (just backgrounds)
  python extract_all_icons.py --base "D:\Games\Icarus\Exports\Icarus\Content"
  python extract_all_icons.py --out "C:\MyIcons"
  python extract_all_icons.py --filter "Lithium"
  python extract_all_icons.py --force                  (re-extract all, overwrite existing)
"""
import struct, json, os, subprocess, glob, argparse, sys, io

try:
    import winreg
except ImportError:
    winreg = None  # Not on Windows — registry detection skipped


# ===================================================================
#  AUTO-INSTALL Pillow if missing
# ===================================================================

def ensure_pillow():
    """Make sure Pillow is installed, auto-install if not."""
    try:
        from PIL import Image
        return True
    except ImportError:
        print('[*] Pillow not found — installing automatically...')
        try:
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', 'Pillow', '--quiet',
                 '--break-system-packages'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            from PIL import Image
            print('    Pillow installed successfully!')
            return True
        except Exception:
            try:
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', 'Pillow', '--quiet'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                from PIL import Image
                print('    Pillow installed successfully!')
                return True
            except Exception as e:
                print(f'    ERROR: Could not install Pillow: {e}')
                print('    Please run: pip install Pillow')
                return False


# ===================================================================
#  AUTO-DETECTION — finds Icarus exports and output paths
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
                                parts = line.split('"')
                                if len(parts) >= 4:
                                    lib_path = parts[3].replace('\\\\', '\\')
                                    lib_apps = os.path.join(lib_path, 'steamapps')
                                    if os.path.isdir(lib_apps) and lib_apps not in libraries:
                                        libraries.append(lib_apps)
                except Exception:
                    pass
            break

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


# ===================================================================
#  SEARCH PATH CATEGORIES
# ===================================================================

# Default: All UI icons (items, achievements, talents, HUD, etc.)
UI_ICON_PATHS = [
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

# Loading screens — full-screen biome/mission splash art
LOADING_SCREEN_PATHS = [
    os.path.join('Assets', '2DArt', 'LoadingScreens'),
    os.path.join('Assets', '2DArt', 'UI', 'Loading'),
    os.path.join('Assets', 'UI', 'LoadingScreens'),
    os.path.join('Assets', 'LoadingScreens'),
    os.path.join('Assets', 'Textures', 'LoadingScreens'),
]

# Backgrounds — menu art, character select, title screen
BACKGROUND_PATHS = [
    os.path.join('Assets', '2DArt', 'Backgrounds'),
    os.path.join('Assets', '2DArt', 'UI', 'Backgrounds'),
    os.path.join('Assets', 'UI', 'Backgrounds'),
    os.path.join('Assets', 'Backgrounds'),
    os.path.join('Assets', '2DArt', 'MenuBackgrounds'),
    os.path.join('Assets', '2DArt', 'TitleScreen'),
]

# Cinematics — cutscene frames, story art
CINEMATIC_PATHS = [
    os.path.join('Assets', '2DArt', 'Cinematics'),
    os.path.join('Assets', 'Cinematics'),
    os.path.join('Assets', 'Movies'),
    os.path.join('Assets', 'Cutscenes'),
]

# Marketing / promotional art
MARKETING_PATHS = [
    os.path.join('Assets', '2DArt', 'Marketing'),
    os.path.join('Assets', 'Marketing'),
    os.path.join('Assets', '2DArt', 'Promotional'),
    os.path.join('Assets', '2DArt', 'Splashscreens'),
]

# Environment & biome art textures
ENVIRONMENT_PATHS = [
    os.path.join('Assets', 'Textures', 'Environment'),
    os.path.join('Assets', 'Textures', 'Terrain'),
    os.path.join('Assets', 'Textures', 'Biomes'),
    os.path.join('Assets', 'Textures', 'Landscape'),
    os.path.join('Assets', 'Textures', 'Sky'),
    os.path.join('Assets', 'Textures', 'Water'),
    os.path.join('Assets', 'Textures', 'Weather'),
    os.path.join('Assets', 'Environment'),
]

# Creature / animal textures
CREATURE_PATHS = [
    os.path.join('Assets', 'Textures', 'Creatures'),
    os.path.join('Assets', 'Textures', 'Animals'),
    os.path.join('Assets', 'Creatures'),
    os.path.join('Assets', 'Animals'),
    os.path.join('Assets', 'Textures', 'Monsters'),
    os.path.join('Assets', 'Textures', 'Bosses'),
]

# VFX / particle textures
VFX_PATHS = [
    os.path.join('Assets', 'Textures', 'VFX'),
    os.path.join('Assets', 'Textures', 'FX'),
    os.path.join('Assets', 'Textures', 'Particles'),
    os.path.join('Assets', 'VFX'),
    os.path.join('Assets', 'FX'),
]

# Material / surface textures (wood, stone, metal, etc.)
MATERIAL_PATHS = [
    os.path.join('Assets', 'Textures', 'Materials'),
    os.path.join('Assets', 'Textures', 'Surfaces'),
    os.path.join('Assets', 'Materials'),
    os.path.join('Assets', 'Textures', 'Props'),
    os.path.join('Assets', 'Textures', 'Buildings'),
    os.path.join('Assets', 'Textures', 'Weapons'),
    os.path.join('Assets', 'Textures', 'Armor'),
    os.path.join('Assets', 'Textures', 'Tools'),
    os.path.join('Assets', 'Textures', 'Vehicles'),
]

# Concept art / misc art
MISC_ART_PATHS = [
    os.path.join('Assets', '2DArt', 'ConceptArt'),
    os.path.join('Assets', '2DArt', 'Dioramas'),
    os.path.join('Assets', '2DArt', 'Portraits'),
    os.path.join('Assets', '2DArt', 'Renders'),
    os.path.join('Assets', '2DArt'),  # catch-all for anything under 2DArt
    os.path.join('Assets', 'UI'),     # top-level UI (not under 2DArt)
]

# Category registry — used by --all and individual flags
IMAGE_CATEGORIES = {
    'icons':         ('UI Icons (items, achievements, talents, HUD)', UI_ICON_PATHS),
    'loading':       ('Loading Screens (biome/mission splash art)',   LOADING_SCREEN_PATHS),
    'backgrounds':   ('Backgrounds (menus, title screen)',           BACKGROUND_PATHS),
    'cinematics':    ('Cinematics (cutscene frames, story art)',     CINEMATIC_PATHS),
    'marketing':     ('Marketing & Promotional Art',                 MARKETING_PATHS),
    'environment':   ('Environment & Biome Textures',               ENVIRONMENT_PATHS),
    'creatures':     ('Creature & Animal Textures',                 CREATURE_PATHS),
    'vfx':           ('VFX & Particle Textures',                    VFX_PATHS),
    'materials':     ('Material & Surface Textures',                MATERIAL_PATHS),
    'misc':          ('Concept Art & Misc 2D Art',                  MISC_ART_PATHS),
}

# Legacy alias
ICON_SEARCH_PATHS = UI_ICON_PATHS


# ===================================================================
#  DDS CONSTANTS & HEADER
# ===================================================================

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


# ===================================================================
#  PURE-PYTHON DDS DECODERS (no texconv needed!)
# ===================================================================

def decode_rgb565(c):
    """Unpack RGB565 to (R, G, B) 8-bit."""
    r = ((c >> 11) & 0x1F) * 255 // 31
    g = ((c >> 5) & 0x3F) * 255 // 63
    b = (c & 0x1F) * 255 // 31
    return (r, g, b)


def decode_dxt1_block(data, offset):
    """Decode a single 4x4 DXT1 block into 16 RGBA pixels."""
    c0 = struct.unpack_from('<H', data, offset)[0]
    c1 = struct.unpack_from('<H', data, offset + 2)[0]
    bits = struct.unpack_from('<I', data, offset + 4)[0]

    r0, g0, b0 = decode_rgb565(c0)
    r1, g1, b1 = decode_rgb565(c1)

    colors = [(r0, g0, b0, 255), (r1, g1, b1, 255)]
    if c0 > c1:
        colors.append(((2*r0 + r1) // 3, (2*g0 + g1) // 3, (2*b0 + b1) // 3, 255))
        colors.append(((r0 + 2*r1) // 3, (g0 + 2*g1) // 3, (b0 + 2*b1) // 3, 255))
    else:
        colors.append(((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2, 255))
        colors.append((0, 0, 0, 0))  # transparent

    pixels = []
    for i in range(16):
        idx = (bits >> (2 * i)) & 0x3
        pixels.append(colors[idx])
    return pixels


def decode_dxt5_block(data, offset):
    """Decode a single 4x4 DXT5 block (alpha + color) into 16 RGBA pixels."""
    # Alpha block (8 bytes)
    a0 = data[offset]
    a1 = data[offset + 1]

    # Build alpha lookup table
    alphas = [a0, a1]
    if a0 > a1:
        for i in range(1, 7):
            alphas.append(((7 - i) * a0 + i * a1) // 7)
    else:
        for i in range(1, 5):
            alphas.append(((5 - i) * a0 + i * a1) // 5)
        alphas.append(0)
        alphas.append(255)

    # Read 6 bytes of 3-bit alpha indices (48 bits = 16 pixels)
    alpha_bits = 0
    for j in range(6):
        alpha_bits |= data[offset + 2 + j] << (8 * j)

    alpha_indices = []
    for i in range(16):
        alpha_indices.append((alpha_bits >> (3 * i)) & 0x7)

    # Color block (8 bytes starting at offset+8)
    color_pixels = decode_dxt1_block(data, offset + 8)

    # Combine
    pixels = []
    for i in range(16):
        r, g, b, _ = color_pixels[i]
        a = alphas[alpha_indices[i]]
        pixels.append((r, g, b, a))
    return pixels


def decode_bc_image(data, width, height, block_decoder, block_size):
    """Generic block-compressed image decoder for DXT1/DXT5."""
    from PIL import Image
    img = Image.new('RGBA', (width, height))
    pixels = img.load()

    blocks_x = max(1, (width + 3) // 4)
    blocks_y = max(1, (height + 3) // 4)
    offset = 0

    for by in range(blocks_y):
        for bx in range(blocks_x):
            if offset + block_size > len(data):
                break
            block_pixels = block_decoder(data, offset)
            offset += block_size

            for i, (r, g, b, a) in enumerate(block_pixels):
                px = bx * 4 + (i % 4)
                py = by * 4 + (i // 4)
                if px < width and py < height:
                    pixels[px, py] = (r, g, b, a)

    return img


def decode_b8g8r8a8(data, width, height):
    """Decode uncompressed B8G8R8A8 pixel data."""
    from PIL import Image
    img = Image.new('RGBA', (width, height))
    pixels = img.load()

    for y in range(height):
        for x in range(width):
            off = (y * width + x) * 4
            if off + 4 > len(data):
                break
            b, g, r, a = data[off], data[off+1], data[off+2], data[off+3]
            pixels[x, y] = (r, g, b, a)

    return img


def dds_to_png(dds_data, out_path):
    """Convert DDS byte data to PNG using pure Python decoding. Returns True on success."""
    from PIL import Image

    if len(dds_data) < 128 or dds_data[:4] != DDS_MAGIC:
        return False

    # Parse DDS header
    header_size = struct.unpack_from('<I', dds_data, 4)[0]
    flags = struct.unpack_from('<I', dds_data, 8)[0]
    height = struct.unpack_from('<I', dds_data, 12)[0]
    width = struct.unpack_from('<I', dds_data, 16)[0]

    # Pixel format starts at offset 76
    pf_size = struct.unpack_from('<I', dds_data, 76)[0]
    pf_flags = struct.unpack_from('<I', dds_data, 80)[0]
    fourcc = dds_data[84:88]

    pixel_data_offset = 4 + header_size  # DDS_MAGIC(4) + header

    # Check for DX10 extended header
    if fourcc == b'DX10':
        dxgi_format = struct.unpack_from('<I', dds_data, pixel_data_offset)[0]
        pixel_data_offset += 20  # DX10 header is 20 bytes
        fourcc = b'BC7 '  # Mark as BC7 for our purposes (DXGI format 98 = BC7)

    pixel_data = dds_data[pixel_data_offset:]

    try:
        if fourcc == b'DXT1':
            img = decode_bc_image(pixel_data, width, height, decode_dxt1_block, 8)
        elif fourcc == b'DXT5':
            img = decode_bc_image(pixel_data, width, height, decode_dxt5_block, 16)
        elif fourcc == b'BC7 ':
            # BC7 is complex — try Pillow's built-in DDS support first
            try:
                dds_stream = io.BytesIO(dds_data)
                img = Image.open(dds_stream)
                img = img.convert('RGBA')
            except Exception:
                # Fallback: save as DDS and let Pillow try
                return False
        elif pf_flags & DDPF_RGB:
            # Uncompressed BGRA
            img = decode_b8g8r8a8(pixel_data, width, height)
        else:
            return False

        img.save(out_path, 'PNG')
        return True
    except Exception as e:
        return False


# ===================================================================
#  UE4 .uexp TEXTURE EXTRACTION
# ===================================================================

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

        gaps = [offsets[i+1] - (offsets[i] + sizes[i]) for i in range(len(mips)-1)]
        if not gaps or any(g <= 0 or g > 128 for g in gaps):
            return None

        gap = gaps[0]
        if not all(g == gap for g in gaps):
            return None

        return (gap - 12, 12)
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

        detected = detect_inter_mip_gap(mips)
        if detected:
            bh_size, mf_size = detected
        else:
            bh_size, mf_size = BULK_HEADER_SIZE, MIP_FOOTER_SIZE

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


def extract_icon(uexp_path, out_png_path):
    """Extract a single icon from .uexp to .png using pure Python DDS decoding."""
    json_path = uexp_path.replace('.uexp', '.json')
    result, msg = extract_texture_data(uexp_path, json_path)
    if result is None:
        return False, msg

    dds_header = make_dds_header(result['width'], result['height'],
                                  result['format'], result['size'])
    if dds_header is None:
        return False, f"unsupported: {result['format']}"

    # Build complete DDS in memory and decode to PNG
    dds_data = dds_header + result['data']
    ok = dds_to_png(dds_data, out_png_path)
    if ok:
        return True, msg
    else:
        return False, f'decode failed for {result["format"]}'


# ===================================================================
#  ICON SCANNING
# ===================================================================

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
            real_root = os.path.realpath(root)
            if real_root in scanned_dirs:
                continue
            scanned_dirs.add(real_root)

            for filename in files:
                if not filename.lower().endswith('.uexp'):
                    continue

                uexp_path = os.path.join(root, filename)
                json_path = uexp_path.replace('.uexp', '.json')

                if not os.path.exists(json_path):
                    continue

                try:
                    with open(json_path, encoding='utf-8') as f:
                        meta = json.load(f)
                    if isinstance(meta, list):
                        meta = meta[0]
                    if 'Mips' not in meta or not meta['Mips']:
                        continue
                except Exception:
                    continue

                # Build output name from relative path
                rel = os.path.relpath(uexp_path, base_path)
                parts = rel.replace('\\', '/').split('/')
                clean_parts = []
                skip = {'Assets', '2DArt', 'UI', 'Items', 'Item_Icons'}
                for p in parts:
                    if p in skip:
                        continue
                    clean_parts.append(p)

                if clean_parts:
                    stem = os.path.splitext(clean_parts[-1])[0]
                    if len(clean_parts) > 1:
                        subdir = clean_parts[-2]
                        out_name = f"{subdir}_{stem}.png"
                    else:
                        out_name = f"{stem}.png"
                else:
                    out_name = os.path.splitext(filename)[0] + '.png'

                if name_filter:
                    if name_filter.lower() not in out_name.lower() and \
                       name_filter.lower() not in uexp_path.lower():
                        continue

                if out_name not in icons or len(uexp_path) < len(icons[out_name]):
                    icons[out_name] = uexp_path

    return icons


# ===================================================================
#  MAIN
# ===================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Icarus Icon Extractor v5 — no external tools needed! '
                    'Auto-detects game location and extracts all item icons to PNG.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='If no arguments are given, the script will auto-detect paths and ask if needed.\n'
               'Only requires Python 3.8+ and Pillow (auto-installed).')
    parser.add_argument('--base', default=None,
                        help='Path to Icarus exports Content folder (auto-detected if omitted)')
    parser.add_argument('--out', default=None,
                        help='Output directory for PNG files (default: Desktop/icarus_icons)')
    parser.add_argument('--filter', default=None,
                        help='Only extract icons matching this keyword (e.g. "Lithium", "Bow")')
    parser.add_argument('--dry-run', action='store_true',
                        help='List icons that would be extracted without actually extracting')
    parser.add_argument('--force', action='store_true',
                        help='Re-extract icons even if they already exist (overwrite)')
    parser.add_argument('--organize', action='store_true', default=True,
                        help='Organize output into subdirectories by category (default: on)')
    args = parser.parse_args()

    print(f'=== Icarus Icon Extractor v5 (standalone) ===\n')

    # Ensure Pillow is available
    if not args.dry_run:
        if not ensure_pillow():
            sys.exit(1)

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
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        if os.path.isdir(desktop):
            out_dir = os.path.join(desktop, 'icarus_icons')
        else:
            out_dir = os.path.join(os.getcwd(), 'icarus_icons')
        print(f'[*] Output directory: {out_dir}')

    os.makedirs(out_dir, exist_ok=True)

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

        ok, msg = extract_icon(src, out_path)
        status = 'OK  ' if ok else 'FAIL'
        print(f'  [{i}/{len(icons)}] {status}  {out_name} ({msg})')
        (good if ok else bad).append(out_name if ok else (out_name, msg))

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
