r"""
Icarus Image Extractor v8 — Extracts ALL images from the game.

No external tools required! Extracts directly from game PAK files or FModel exports.
Uses pure Python (Pillow) for DDS→PNG conversion. Auto-detects your Icarus install.

Extracts 23,000+ Texture2D assets: item icons, loading screens, backgrounds,
cinematics, biome art, marketing art, VFX textures, environment art, creature
textures, weapon textures, character textures, world textures, and everything else.

Requirements:
  pip install Pillow     (auto-installed if missing)

Usage:
  python extract_all_icons.py                          (extract ALL ~20k textures!)
  python extract_all_icons.py --icons                  (UI icons only)
  python extract_all_icons.py --game                   (force PAK extraction, skip FModel)
  python extract_all_icons.py --loading-screens        (just loading screens)
  python extract_all_icons.py --backgrounds            (just backgrounds)
  python extract_all_icons.py --base "D:\Exports\Icarus\Content" (use FModel exports)
  python extract_all_icons.py --out "C:\MyIcons"
  python extract_all_icons.py --filter "Lithium"
  python extract_all_icons.py --force                  (re-extract all, overwrite existing)
"""
import struct, json, os, subprocess, glob, argparse, sys, io, tempfile, shutil

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
    'loading_screens':('Loading Screens (biome/mission splash art)',   LOADING_SCREEN_PATHS),
    'backgrounds':   ('Backgrounds (menus, title screen)',           BACKGROUND_PATHS),
    'cinematics':    ('Cinematics (cutscene frames, story art)',     CINEMATIC_PATHS),
    'marketing':     ('Marketing & Promotional Art',                 MARKETING_PATHS),
    'environment':   ('Environment & Biome Textures',               ENVIRONMENT_PATHS),
    'creatures':     ('Creature & Animal Textures',                 CREATURE_PATHS),
    'vfx':           ('VFX & Particle Textures',                    VFX_PATHS),
    'materials':     ('Material & Surface Textures',                MATERIAL_PATHS),
    'misc_art':      ('Concept Art & Misc 2D Art',                  MISC_ART_PATHS),
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
DDPF_LUMINANCE   = 0x20000
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
    elif pixel_format == 'PF_BC5':
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_FOURCC, b'DX10', 0, 0, 0, 0, 0)
    elif pixel_format == 'PF_BC4':
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_FOURCC, b'DX10', 0, 0, 0, 0, 0)
    elif pixel_format == 'PF_B8G8R8A8':
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_RGB | DDPF_ALPHAPIXELS, b'\x00'*4,
            32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    elif pixel_format in ('PF_G8', 'PF_R8'):
        # 8-bit single-channel grayscale
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_LUMINANCE, b'\x00'*4,
            8, 0xFF, 0, 0, 0)
    elif pixel_format == 'PF_A8':
        # 8-bit alpha only
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_ALPHAPIXELS, b'\x00'*4,
            8, 0, 0, 0, 0xFF)
    elif pixel_format in ('PF_FloatRGBA', 'PF_A16B16G16R16'):
        # 16-bit per channel RGBA — use DX10 extended header
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_FOURCC, b'DX10', 0, 0, 0, 0, 0)
    elif pixel_format == 'PF_R16F':
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_FOURCC, b'DX10', 0, 0, 0, 0, 0)
    elif pixel_format in ('PF_G16R16', 'PF_G16R16F'):
        pf = struct.pack('<I I 4s I I I I I', 32, DDPF_FOURCC, b'DX10', 0, 0, 0, 0, 0)
    else:
        return None

    flags = DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_LINEARSIZE
    header = struct.pack('<I I I I I I I', 124, flags, height, width, data_size, 0, 1)
    header += b'\x00' * 44  # reserved
    header += pf
    header += struct.pack('<I', DDSCAPS_TEXTURE)
    header += b'\x00' * 16  # caps2, reserved

    result = DDS_MAGIC + header

    # DX10 extended header for formats that need it
    # DXGI format mapping
    dx10_formats = {
        'PF_BC7': 98,        # DXGI_FORMAT_BC7_UNORM
        'PF_BC5': 83,        # DXGI_FORMAT_BC5_UNORM
        'PF_BC4': 80,        # DXGI_FORMAT_BC4_UNORM
        'PF_FloatRGBA': 10,  # DXGI_FORMAT_R16G16B16A16_FLOAT
        'PF_A16B16G16R16': 11, # DXGI_FORMAT_R16G16B16A16_UNORM
        'PF_R16F': 54,       # DXGI_FORMAT_R16_FLOAT
        'PF_G16R16': 35,     # DXGI_FORMAT_R16G16_UNORM
        'PF_G16R16F': 34,    # DXGI_FORMAT_R16G16_FLOAT
    }
    if pixel_format in dx10_formats:
        dxgi_fmt = dx10_formats[pixel_format]
        result += struct.pack('<I I I I I', dxgi_fmt, 3, 0, 1, 0)

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


def decode_g8(data, width, height):
    """Decode 8-bit grayscale (PF_G8 / PF_R8) pixel data to RGBA."""
    from PIL import Image
    img = Image.new('RGBA', (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            off = y * width + x
            if off >= len(data):
                break
            v = data[off]
            pixels[x, y] = (v, v, v, 255)
    return img


def decode_a8(data, width, height):
    """Decode 8-bit alpha-only (PF_A8) pixel data to RGBA."""
    from PIL import Image
    img = Image.new('RGBA', (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            off = y * width + x
            if off >= len(data):
                break
            a = data[off]
            pixels[x, y] = (255, 255, 255, a)
    return img


def decode_float_rgba(data, width, height):
    """Decode 16-bit float RGBA (PF_FloatRGBA) pixel data to RGBA.
    Each pixel is 4x float16 (8 bytes total per pixel)."""
    from PIL import Image
    import math
    img = Image.new('RGBA', (width, height))
    pixels = img.load()

    for y in range(height):
        for x in range(width):
            off = (y * width + x) * 8
            if off + 8 > len(data):
                break
            # Read 4 half-floats (16-bit each)
            r_half = struct.unpack_from('<e', data, off)[0]
            g_half = struct.unpack_from('<e', data, off + 2)[0]
            b_half = struct.unpack_from('<e', data, off + 4)[0]
            a_half = struct.unpack_from('<e', data, off + 6)[0]

            # Clamp and convert to 0-255
            r = max(0, min(255, int(r_half * 255)))
            g = max(0, min(255, int(g_half * 255)))
            b = max(0, min(255, int(b_half * 255)))
            a = max(0, min(255, int(a_half * 255)))
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
    pf_bpp = struct.unpack_from('<I', dds_data, 88)[0]  # bits per pixel

    pixel_data_offset = 4 + header_size  # DDS_MAGIC(4) + header
    dxgi_format = 0

    # Check for DX10 extended header
    if fourcc == b'DX10':
        dxgi_format = struct.unpack_from('<I', dds_data, pixel_data_offset)[0]
        pixel_data_offset += 20  # DX10 header is 20 bytes

    pixel_data = dds_data[pixel_data_offset:]

    try:
        # Try Pillow's built-in DDS support first for complex formats
        if dxgi_format in (10, 11, 34, 35, 54, 80, 83, 98):
            try:
                dds_stream = io.BytesIO(dds_data)
                img = Image.open(dds_stream)
                img = img.convert('RGBA')
                img.save(out_path, 'PNG')
                return True
            except Exception:
                pass  # Fall through to manual decoders

        if fourcc == b'DXT1':
            img = decode_bc_image(pixel_data, width, height, decode_dxt1_block, 8)
        elif fourcc == b'DXT5':
            img = decode_bc_image(pixel_data, width, height, decode_dxt5_block, 16)
        elif dxgi_format == 98:  # BC7
            try:
                dds_stream = io.BytesIO(dds_data)
                img = Image.open(dds_stream)
                img = img.convert('RGBA')
            except Exception:
                return False
        elif dxgi_format == 10:  # R16G16B16A16_FLOAT (FloatRGBA)
            img = decode_float_rgba(pixel_data, width, height)
        elif dxgi_format == 83:  # BC5_UNORM
            try:
                dds_stream = io.BytesIO(dds_data)
                img = Image.open(dds_stream)
                img = img.convert('RGBA')
            except Exception:
                return False
        elif pf_flags & DDPF_RGB:
            img = decode_b8g8r8a8(pixel_data, width, height)
        elif pf_flags & DDPF_LUMINANCE:
            img = decode_g8(pixel_data, width, height)
        elif pf_flags & DDPF_ALPHAPIXELS and not (pf_flags & DDPF_RGB):
            img = decode_a8(pixel_data, width, height)
        else:
            # Last resort: try Pillow's DDS support
            try:
                dds_stream = io.BytesIO(dds_data)
                img = Image.open(dds_stream)
                img = img.convert('RGBA')
            except Exception:
                return False

        img.save(out_path, 'PNG')
        return True
    except Exception as e:
        return False


# ===================================================================
#  UE4 PAK FILE READER — reads directly from game install
# ===================================================================

import zlib

PAK_MAGIC = 0x5A6F12E1
# Known footer sizes by PAK version
PAK_FOOTER_SIZES = [222, 221, 204, 189, 61, 60, 45, 44]

# Compression method names (index in PAK v8+ compression methods array)
COMPRESS_NONE = 0
COMPRESS_ZLIB = 1

# BulkData flags
BULKDATA_PayloadAtEndOfFile = 0x0001
BULKDATA_ForceInlinePayload = 0x0001  # same bit in some UE4 versions (context-dependent)
BULKDATA_PayloadInSeperateFile = 0x0200

# Safety cap: max single mip read (256 MB — 8K RGBA uncompressed)
MAX_MIP_READ_SIZE = 256 * 1024 * 1024

# All pixel formats we can detect in binary data
KNOWN_PIXEL_FORMATS = [
    'PF_DXT1', 'PF_DXT5', 'PF_BC7', 'PF_B8G8R8A8',
    'PF_BC1', 'PF_BC3', 'PF_BC5', 'PF_G8', 'PF_FloatRGBA',
    'PF_A8', 'PF_R8G8', 'PF_R8', 'PF_BC4', 'PF_BC6H',
    'PF_R16F', 'PF_R32F', 'PF_G16R16', 'PF_G16R16F',
    'PF_A16B16G16R16', 'PF_R16G16B16A16_UNORM', 'PF_R16G16B16A16_SNORM',
    'PF_ASTC_4x4', 'PF_ASTC_6x6', 'PF_ASTC_8x8', 'PF_ASTC_10x10',
    'PF_ETC2_RGB', 'PF_ETC2_RGBA',
]


def find_game_paks_dir():
    """Find the Icarus game Paks directory (where .pak files live)."""
    libraries = find_steam_libraries()
    for lib in libraries:
        # Standard UE4 pak location
        paks = os.path.join(lib, 'common', 'Icarus', 'Icarus', 'Content', 'Paks')
        if os.path.isdir(paks):
            return paks
        # Some installs put it directly under the game folder
        paks2 = os.path.join(lib, 'common', 'Icarus', 'Content', 'Paks')
        if os.path.isdir(paks2):
            return paks2
    return None


def read_pak_footer(f, file_size):
    """Read PAK file footer to find index offset and version."""
    # Read the last 512 bytes and scan for the magic
    scan_size = min(512, file_size)
    f.seek(file_size - scan_size)
    tail = f.read(scan_size)

    # Scan backwards for the magic value
    for i in range(len(tail) - 4, -1, -1):
        val = struct.unpack_from('<I', tail, i)[0]
        if val == PAK_MAGIC and i + 24 <= len(tail):
            version = struct.unpack_from('<i', tail, i + 4)[0]
            index_offset = struct.unpack_from('<q', tail, i + 8)[0]
            index_size = struct.unpack_from('<q', tail, i + 16)[0]
            if 0 < version < 20 and 0 <= index_offset < file_size and 0 < index_size < file_size:
                return version, index_offset, index_size
    return None, None, None


def read_fstring(data, offset):
    """Read a UE4 FString (int32 length, then chars with null terminator)."""
    if offset + 4 > len(data):
        return '', offset
    length = struct.unpack_from('<i', data, offset)[0]
    offset += 4
    if length == 0:
        return '', offset
    if length < 0:
        # UTF-16
        char_count = -length
        if offset + char_count * 2 > len(data):
            return '', offset + char_count * 2
        s = data[offset:offset + char_count * 2].decode('utf-16-le', errors='replace').rstrip('\0')
        return s, offset + char_count * 2
    else:
        if offset + length > len(data):
            return '', offset + length
        s = data[offset:offset + length].decode('utf-8', errors='replace').rstrip('\0')
        return s, offset + length


def read_pak_entry_v8(data, offset, version):
    """Read a single FPakEntry (v8+ format). Returns (entry_dict, new_offset)."""
    start = offset
    entry = {}

    entry['data_offset'] = struct.unpack_from('<q', data, offset)[0]; offset += 8
    entry['compressed_size'] = struct.unpack_from('<q', data, offset)[0]; offset += 8
    entry['uncompressed_size'] = struct.unpack_from('<q', data, offset)[0]; offset += 8
    entry['compression_method'] = struct.unpack_from('<I', data, offset)[0]; offset += 4

    if version < 10:  # older versions had timestamp
        offset += 8  # timestamp

    offset += 20  # SHA1 hash

    if entry['compression_method'] != COMPRESS_NONE:
        num_blocks = struct.unpack_from('<I', data, offset)[0]; offset += 4
        blocks = []
        for _ in range(num_blocks):
            block_start = struct.unpack_from('<q', data, offset)[0]; offset += 8
            block_end = struct.unpack_from('<q', data, offset)[0]; offset += 8
            blocks.append((block_start, block_end))
        entry['blocks'] = blocks
    else:
        entry['blocks'] = []

    entry['flags'] = struct.unpack_from('<B', data, offset)[0]; offset += 1
    entry['block_size'] = struct.unpack_from('<I', data, offset)[0]; offset += 4

    return entry, offset


def read_pak_index_simple(f, index_offset, index_size, version):
    """Read PAK index (simple/legacy format, v1-v10). Returns dict {path: entry}."""
    f.seek(index_offset)
    index_data = f.read(index_size)
    offset = 0

    mount_point, offset = read_fstring(index_data, offset)

    num_entries = struct.unpack_from('<i', index_data, offset)[0]; offset += 4
    entries = {}

    for _ in range(num_entries):
        if offset >= len(index_data):
            break
        filename, offset = read_fstring(index_data, offset)
        entry, offset = read_pak_entry_v8(index_data, offset, version)
        # Clean up the filename
        filename = filename.replace('\\', '/').lstrip('/')
        if mount_point and mount_point != '/':
            clean_mount = mount_point.replace('\\', '/').strip('/')
            if clean_mount.startswith('../../../'):
                clean_mount = clean_mount[len('../../../'):]
            filename = clean_mount + '/' + filename if clean_mount else filename
        entries[filename] = entry

    return entries


def read_pak_index_encoded(f, index_offset, index_size, version, file_size):
    """Read PAK v11+ encoded index. Returns dict {path: entry} or None on failure."""
    f.seek(index_offset)
    index_data = f.read(index_size)
    offset = 0

    mount_point, offset = read_fstring(index_data, offset)

    num_entries = struct.unpack_from('<i', index_data, offset)[0]; offset += 4

    # v11: PathHashSeed (uint64)
    path_hash_seed = struct.unpack_from('<Q', index_data, offset)[0]; offset += 8

    # bHasPathHashIndex (int32)
    has_path_hash = struct.unpack_from('<i', index_data, offset)[0]; offset += 4
    if has_path_hash:
        # Skip path hash index: offset(8) + size(8) + hash(20)
        offset += 8 + 8 + 20

    # bHasFullDirectoryIndex (int32)
    has_full_dir = struct.unpack_from('<i', index_data, offset)[0]; offset += 4
    if has_full_dir:
        dir_index_offset = struct.unpack_from('<q', index_data, offset)[0]; offset += 8
        dir_index_size = struct.unpack_from('<q', index_data, offset)[0]; offset += 8
        offset += 20  # dir index hash

    # Encoded entries follow — these are the actual file records
    encoded_size = struct.unpack_from('<i', index_data, offset)[0]; offset += 4
    encoded_data = index_data[offset:offset + encoded_size]
    offset += encoded_size

    # File count from encoded data
    if len(encoded_data) < 4:
        return None
    enc_offset = 0
    file_count = struct.unpack_from('<i', encoded_data, enc_offset)[0]; enc_offset += 4

    # Try to read directory index to get filenames
    if has_full_dir and dir_index_offset > 0 and dir_index_size > 0:
        f.seek(dir_index_offset)
        dir_data = f.read(dir_index_size)
        return _parse_directory_index(dir_data, encoded_data, enc_offset,
                                       file_count, mount_point, version)

    return None


def _parse_directory_index(dir_data, encoded_data, enc_offset, file_count,
                           mount_point, version):
    """Parse the full directory index to get filenames and pair with encoded entries."""
    entries = {}
    d_offset = 0

    try:
        num_dirs = struct.unpack_from('<i', dir_data, d_offset)[0]; d_offset += 4

        # Build list of (directory, [(filename, encoded_entry_index)])
        all_files = []
        for _ in range(num_dirs):
            dir_name, d_offset = read_fstring(dir_data, d_offset)
            num_files = struct.unpack_from('<i', dir_data, d_offset)[0]; d_offset += 4
            for _ in range(num_files):
                file_name, d_offset = read_fstring(dir_data, d_offset)
                entry_idx = struct.unpack_from('<i', dir_data, d_offset)[0]; d_offset += 4
                full_path = (dir_name + file_name).replace('\\', '/').lstrip('/')
                # Clean mount point
                if mount_point and mount_point != '/':
                    clean_mount = mount_point.replace('\\', '/').strip('/')
                    if clean_mount.startswith('../../../'):
                        clean_mount = clean_mount[len('../../../'):]
                    full_path = clean_mount + '/' + full_path if clean_mount else full_path
                all_files.append((full_path, entry_idx))

        # Now decode the encoded entries — v11 uses a compact format
        # Each entry is 53 bytes in the encoded block (after the file count)
        ENCODED_ENTRY_SIZE = 53  # Most common size for v11

        for full_path, entry_idx in all_files:
            entry_off = 4 + entry_idx * ENCODED_ENTRY_SIZE
            if entry_off + ENCODED_ENTRY_SIZE > len(encoded_data):
                continue

            # Decode: flags(4) + offset(4or8) + uncompressed(4or8) +
            #         compression(1) + compressed(4or8) + ... varies
            # Use simplified approach: read the raw fields
            flags = struct.unpack_from('<I', encoded_data, entry_off)[0]

            # Bit-packed fields — try common layout
            e_off = entry_off + 4
            data_offset = struct.unpack_from('<I', encoded_data, e_off)[0]; e_off += 4
            uncompressed = struct.unpack_from('<I', encoded_data, e_off)[0]; e_off += 4
            compression = struct.unpack_from('<I', encoded_data, e_off)[0]; e_off += 4
            compressed = struct.unpack_from('<I', encoded_data, e_off)[0]; e_off += 4

            entries[full_path] = {
                'data_offset': data_offset,
                'compressed_size': compressed if compression else uncompressed,
                'uncompressed_size': uncompressed,
                'compression_method': compression,
                'blocks': [],
                'flags': 0,
                'block_size': 0,
            }
    except Exception:
        pass

    return entries if entries else None


def read_pak_file(pak_path):
    """Read a PAK file and return all entries. Returns dict {path: entry} or None."""
    file_size = os.path.getsize(pak_path)
    if file_size < 64:
        return None

    with open(pak_path, 'rb') as f:
        version, index_offset, index_size = read_pak_footer(f, file_size)
        if version is None:
            return None

        # Try v11 encoded index first, fall back to simple
        if version >= 11:
            entries = read_pak_index_encoded(f, index_offset, index_size, version, file_size)
            if entries:
                return entries

        # Simple/legacy index
        try:
            return read_pak_index_simple(f, index_offset, index_size, version)
        except Exception:
            return None


def extract_pak_entry(pak_path, entry):
    """Extract a single file from a PAK. Returns raw bytes or None."""
    try:
        with open(pak_path, 'rb') as f:
            # PAK entries have a small header before the actual data
            f.seek(entry['data_offset'])

            if entry['compression_method'] == COMPRESS_NONE:
                # Uncompressed — skip the entry header (variable size)
                # Try reading with and without the inline header
                raw = f.read(entry['uncompressed_size'] + 256)

                # Look for the actual data start by checking magic bytes or size
                # The FPakEntry is re-serialized before the data, skip it
                # Simple approach: the data is at the end of what we read
                size = entry['uncompressed_size']
                if len(raw) >= size:
                    return raw[:size]
                return None

            elif entry['compression_method'] == COMPRESS_ZLIB:
                if entry.get('blocks'):
                    # Block-compressed
                    decompressed = bytearray()
                    for block_start, block_end in entry['blocks']:
                        block_size = block_end - block_start
                        f.seek(block_start)
                        compressed = f.read(block_size)
                        try:
                            decompressed.extend(zlib.decompress(compressed))
                        except zlib.error:
                            decompressed.extend(compressed)  # May not actually be compressed
                    return bytes(decompressed[:entry['uncompressed_size']])
                else:
                    # Single zlib stream
                    compressed = f.read(entry['compressed_size'])
                    try:
                        return zlib.decompress(compressed)[:entry['uncompressed_size']]
                    except zlib.error:
                        return compressed  # Fallback
            else:
                # Oodle or unknown compression — try loading oodle DLL
                return _try_oodle_decompress(pak_path, f, entry)

    except Exception:
        return None


def _try_oodle_decompress(pak_path, f, entry):
    """Try to decompress using Oodle DLL from game folder."""
    try:
        import ctypes
        # Look for oo2core DLL near the game
        game_dir = os.path.dirname(os.path.dirname(os.path.dirname(pak_path)))
        for dll_name in ['oo2core_9_win64.dll', 'oo2core_8_win64.dll',
                         'oo2core_7_win64.dll', 'oo2core_win64.dll']:
            dll_path = os.path.join(game_dir, 'Binaries', 'Win64', dll_name)
            if os.path.exists(dll_path):
                oodle = ctypes.cdll.LoadLibrary(dll_path)
                decompress = oodle.OodleLZ_Decompress

                compressed = f.read(entry['compressed_size'])
                output = ctypes.create_string_buffer(entry['uncompressed_size'])
                result = decompress(compressed, len(compressed), output,
                                    entry['uncompressed_size'], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                if result == entry['uncompressed_size']:
                    return output.raw
    except Exception:
        pass
    return None


def unpack_paks_to_temp(paks_dir, search_paths, temp_dir, name_filter=None, extract_all=False):
    """Extract texture files from PAK files into a temp directory structure.
    If extract_all=True, extracts ALL .uexp/.uasset/.ubulk files (for --all mode).
    Returns the temp base path (equivalent to an exports Content folder)."""
    print('[*] Reading PAK files...')
    pak_files = sorted(glob.glob(os.path.join(paks_dir, '*.pak')))
    if not pak_files:
        return None

    # Build a set of path prefixes we're interested in
    search_prefixes_alt = set()
    if not extract_all:
        for sp in search_paths:
            prefix = sp.replace('\\', '/')
            search_prefixes_alt.add(prefix.lower())
            # PAK paths often start with "Icarus/Content/" or just the asset path
            search_prefixes_alt.add(('Icarus/Content/' + prefix).lower())

    all_entries = {}  # path -> (pak_path, entry)
    total_entries = 0

    for pak_path in pak_files:
        pak_name = os.path.basename(pak_path)
        entries = read_pak_file(pak_path)
        if not entries:
            continue

        texture_count = 0
        for path, entry in entries.items():
            path_lower = path.lower().replace('\\', '/')

            if extract_all:
                # --all mode: grab every potential texture file from every path
                matched = True
            else:
                # Filtered mode: only extract from requested directories
                matched = False
                for prefix in search_prefixes_alt:
                    if prefix in path_lower:
                        matched = True
                        break

                if not matched:
                    # Also check for any 2DArt or Textures path
                    if '/2dart/' in path_lower or '/textures/' in path_lower or '/ui/' in path_lower:
                        matched = True

            if not matched:
                continue

            # Want .uasset, .uexp, and .ubulk files (ubulk has large texture mip data)
            if not (path_lower.endswith('.uasset') or path_lower.endswith('.uexp') or path_lower.endswith('.ubulk')):
                continue

            if name_filter and name_filter.lower() not in path_lower:
                continue

            # Later PAK files (patches) override earlier ones
            all_entries[path] = (pak_path, entry)
            texture_count += 1

        if texture_count > 0:
            total_entries += texture_count
            print(f'    {pak_name}: {texture_count} asset files found')

    if not all_entries:
        print('    No matching texture files found in PAK files.')
        return None

    print(f'[*] Extracting {len(all_entries)} files from PAK to temp directory...')

    # Extract matching files to temp directory
    extracted = 0
    for path, (pak_path, entry) in sorted(all_entries.items()):
        # Build output path
        # Strip common prefixes like "Icarus/Content/"
        clean_path = path.replace('\\', '/')
        for prefix in ['Icarus/Content/', 'icarus/content/', 'Content/']:
            if clean_path.lower().startswith(prefix.lower()):
                clean_path = clean_path[len(prefix):]
                break

        out_path = os.path.join(temp_dir, clean_path.replace('/', os.sep))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        data = extract_pak_entry(pak_path, entry)
        if data:
            with open(out_path, 'wb') as f:
                f.write(data)
            extracted += 1

    print(f'    Extracted {extracted} files to temp directory')
    return temp_dir


# ===================================================================
#  BINARY TEXTURE METADATA PARSER (no JSON/FModel needed)
# ===================================================================

def parse_texture_from_binary(uexp_data, uexp_path=None):
    """Heuristically parse texture metadata directly from .uexp binary data.
    If uexp_path is provided, can read .ubulk companion files for external mip data.
    Returns dict with width, height, format, mip info, or None on failure."""

    # Strategy: scan for known pixel format strings (stored as FString in platform data)
    # The FTexturePlatformData layout after tagged properties is:
    #   SizeX(i32) + SizeY(i32) + PackedData/NumSlices(u32) + PixelFormat(FString)
    #   + FirstMipToSerialize(i32) + NumMips(i32) + [mip data...]

    for fmt in KNOWN_PIXEL_FORMATS:
        fmt_bytes = fmt.encode('ascii') + b'\x00'
        length_prefix = struct.pack('<i', len(fmt) + 1)
        needle = length_prefix + fmt_bytes

        idx = uexp_data.find(needle)
        if idx < 0:
            continue

        # Found a pixel format string. Width and height are 12 bytes before it.
        if idx < 12:
            continue

        w = struct.unpack_from('<i', uexp_data, idx - 12)[0]
        h = struct.unpack_from('<i', uexp_data, idx - 8)[0]

        # Sanity check dimensions
        if not (1 <= w <= 16384 and 1 <= h <= 16384):
            continue

        # Read mip count after pixel format string
        after_fmt = idx + 4 + len(fmt) + 1  # skip length_prefix + string + null
        if after_fmt + 8 > len(uexp_data):
            continue

        first_mip = struct.unpack_from('<i', uexp_data, after_fmt)[0]
        num_mips = struct.unpack_from('<i', uexp_data, after_fmt + 4)[0]

        if not (0 <= first_mip < 20 and 1 <= num_mips <= 20):
            continue

        # Now find the mip0 data
        # After NumMips, each mip has: bCooked(i32) + BulkData header + pixel data + footer
        mip_start = after_fmt + 8
        return _extract_mips_from_binary(uexp_data, mip_start, w, h, fmt, num_mips, uexp_path)

    return None


def _extract_mips_from_binary(uexp_data, mip_start, width, height, pixel_format, num_mips, uexp_path=None):
    """Extract mip0 texture data from binary uexp starting at mip_start offset.
    If uexp_path is provided, reads .ubulk companion files for external mip data."""
    offset = mip_start
    best_inline = None  # Track best inline mip as fallback when mip0 is in .ubulk

    for mip_idx in range(num_mips):
        if offset + 4 > len(uexp_data):
            break

        # bCooked (int32, should be 1 for cooked assets)
        cooked = struct.unpack_from('<i', uexp_data, offset)[0]
        offset += 4

        if cooked != 1:
            break

        # FBulkData header
        if offset + 20 > len(uexp_data):
            break

        bulk_flags = struct.unpack_from('<I', uexp_data, offset)[0]; offset += 4
        element_count = struct.unpack_from('<i', uexp_data, offset)[0]; offset += 4
        size_on_disk = struct.unpack_from('<i', uexp_data, offset)[0]; offset += 4
        offset_in_file = struct.unpack_from('<q', uexp_data, offset)[0]; offset += 8

        if size_on_disk < 0 or element_count < 0:
            break

        # Determine where the pixel data is
        pixel_data = None
        data_size = size_on_disk if size_on_disk > 0 else element_count

        if data_size > MAX_MIP_READ_SIZE:
            break  # Safety cap — reject absurdly large mips

        if bulk_flags & BULKDATA_PayloadInSeperateFile:
            # Data is in .ubulk file — read it if we have the path
            if uexp_path and data_size > 0:
                ubulk_path = os.path.splitext(uexp_path)[0] + '.ubulk'
                try:
                    ubulk_size = os.path.getsize(ubulk_path)
                    # offset_in_file may be absolute or relative; try as-is first
                    read_offset = offset_in_file if (0 <= offset_in_file < ubulk_size) else 0
                    if read_offset + data_size <= ubulk_size:
                        with open(ubulk_path, 'rb') as uf:
                            uf.seek(read_offset)
                            pixel_data = uf.read(data_size)
                        if len(pixel_data) != data_size:
                            pixel_data = None
                except (OSError, IOError):
                    pixel_data = None
        elif bulk_flags & BULKDATA_PayloadAtEndOfFile:
            # Data is at offset_in_file within the uexp (or appended)
            if 0 <= offset_in_file < len(uexp_data) and offset_in_file + data_size <= len(uexp_data):
                pixel_data = uexp_data[offset_in_file:offset_in_file + data_size]
        else:
            # Inline data — immediately follows the header
            if offset + data_size <= len(uexp_data):
                pixel_data = uexp_data[offset:offset + data_size]
                offset += data_size

        # Mip footer: SizeX(4) + SizeY(4) + SizeZ(4)
        mip_w = width >> mip_idx
        mip_h = height >> mip_idx
        if offset + 12 <= len(uexp_data):
            mip_w = struct.unpack_from('<i', uexp_data, offset)[0]
            mip_h = struct.unpack_from('<i', uexp_data, offset + 4)[0]
            offset += 12

        # We want mip0 (the full-resolution texture)
        if mip_idx == 0 and pixel_data and len(pixel_data) >= data_size > 0:
            return {
                'data': pixel_data,
                'width': width,
                'height': height,
                'format': pixel_format,
                'size': data_size,
            }

        # Track best inline mip as fallback (for when mip0 is in .ubulk but file missing)
        if pixel_data and len(pixel_data) >= data_size > 0 and mip_w > 0 and mip_h > 0:
            if best_inline is None or (mip_w * mip_h) > (best_inline['width'] * best_inline['height']):
                best_inline = {
                    'data': pixel_data,
                    'width': mip_w,
                    'height': mip_h,
                    'format': pixel_format,
                    'size': data_size,
                }

    # If mip0 was in .ubulk and we couldn't read it, return best inline mip
    return best_inline


# ===================================================================
#  UE4 .uexp TEXTURE EXTRACTION (supports both JSON and binary mode)
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


def _read_ubulk_mip0(uexp_path, mip0_bd):
    """Read mip0 data from a .ubulk companion file.
    Returns bytes or None if .ubulk doesn't exist or read fails."""
    ubulk_path = os.path.splitext(uexp_path)[0] + '.ubulk'
    if not os.path.exists(ubulk_path):
        return None
    try:
        size = mip0_bd.get('SizeOnDisk', mip0_bd.get('ElementCount', 0))
        if size <= 0 or size > MAX_MIP_READ_SIZE:
            return None

        # Parse offset — FModel JSON stores it as hex string like "0x0"
        off_raw = mip0_bd.get('OffsetInFile', 0)
        try:
            if isinstance(off_raw, str):
                offset = int(off_raw, 16) if off_raw.startswith('0x') else int(off_raw)
            else:
                offset = int(off_raw)
        except (ValueError, TypeError):
            offset = 0

        ubulk_size = os.path.getsize(ubulk_path)

        # Try the parsed offset first; if it's out of range, fall back to file start
        # (some UE4 versions store uexp-relative offsets that don't apply to .ubulk)
        if offset < 0 or offset + size > ubulk_size:
            offset = 0
        if offset + size > ubulk_size:
            return None

        with open(ubulk_path, 'rb') as f:
            f.seek(offset)
            raw = f.read(size)
        return raw if len(raw) == size else None
    except (OSError, IOError):
        return None


def _is_ubulk_mip(mip_bd):
    """Check if a mip's BulkData flags indicate the payload is in a separate .ubulk file."""
    flags_str = mip_bd.get('BulkDataFlags', '')
    if isinstance(flags_str, str):
        return 'PayloadInSeperateFile' in flags_str
    if isinstance(flags_str, (int, float)):
        return bool(int(flags_str) & BULKDATA_PayloadInSeperateFile)
    return False


def extract_texture_data_json(uexp_path, json_path):
    """Extract raw texture data from a .uexp file using its .json metadata (FModel exports).
    Supports .ubulk companion files for textures with external mip storage."""
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
        mip0_bd = mips[0]['BulkData']
        mip0_size = mip0_bd.get('SizeOnDisk', mip0_bd.get('ElementCount', 0))

        # --- .ubulk path: mip0 stored in separate file ---
        if _is_ubulk_mip(mip0_bd):
            raw = _read_ubulk_mip0(uexp_path, mip0_bd)
            if raw:
                return {
                    'data': raw, 'width': w, 'height': h,
                    'format': fmt, 'size': len(raw),
                }, f'{fmt} {w}x{h} ({num_mips} mips, ubulk)'

            # .ubulk not available — try to find the largest inline mip as fallback
            inline_mips = [m for m in mips if not _is_ubulk_mip(m['BulkData'])]
            if inline_mips:
                # Pick the first (largest) inline mip
                fb = inline_mips[0]
                fb_bd = fb['BulkData']
                fb_size = fb_bd.get('SizeOnDisk', fb_bd.get('ElementCount', 0))
                fb_w = fb.get('SizeX', w)
                fb_h = fb.get('SizeY', h)
                if fb_size > 0 and fb_w > 0 and fb_h > 0 and fb_size <= MAX_MIP_READ_SIZE:
                    # Recalculate offsets using only inline mips
                    num_inline = len(inline_mips)
                    total_inline = sum(
                        m['BulkData'].get('SizeOnDisk', m['BulkData'].get('ElementCount', 0))
                        for m in inline_mips)
                    detected = detect_inter_mip_gap(inline_mips)
                    bh_size, mf_size = detected if detected else (BULK_HEADER_SIZE, MIP_FOOTER_SIZE)
                    per_mip_overhead = bh_size + mf_size
                    uexp_size = os.path.getsize(uexp_path)
                    total_bulk = num_inline * per_mip_overhead + total_inline + UEXP_TRAILER_SIZE
                    first_inline_offset = uexp_size - total_bulk + bh_size
                    if 0 <= first_inline_offset < uexp_size and first_inline_offset + fb_size <= uexp_size:
                        with open(uexp_path, 'rb') as f:
                            f.seek(first_inline_offset)
                            raw = f.read(fb_size)
                        if len(raw) == fb_size:
                            return {
                                'data': raw, 'width': fb_w, 'height': fb_h,
                                'format': fmt, 'size': fb_size,
                            }, f'{fmt} {fb_w}x{fb_h} (inline fallback)'

            return None, 'ubulk mip0 but .ubulk file missing/unreadable'

        # --- Standard path: all mip data inline in .uexp ---
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


def extract_texture_data_binary(uexp_path):
    """Extract raw texture data from a .uexp file using binary parsing (no JSON needed).
    Supports .ubulk companion files for textures with external mip storage."""
    if not os.path.exists(uexp_path):
        return None, 'missing file'
    try:
        with open(uexp_path, 'rb') as f:
            uexp_data = f.read()

        result = parse_texture_from_binary(uexp_data, uexp_path)
        if result:
            src = 'ubulk' if os.path.exists(os.path.splitext(uexp_path)[0] + '.ubulk') else 'uexp'
            return result, f"{result['format']} {result['width']}x{result['height']} ({src})"
        return None, 'no texture data found'
    except Exception as e:
        return None, str(e)


def extract_icon(uexp_path, out_png_path):
    """Extract a single icon from .uexp to .png. Tries JSON metadata first, falls back to binary."""
    json_path = uexp_path.replace('.uexp', '.json')

    # Try JSON metadata first (FModel exports)
    result, msg = extract_texture_data_json(uexp_path, json_path)

    # Fall back to binary parsing (direct PAK extraction or non-FModel exports)
    if result is None:
        result, msg = extract_texture_data_binary(uexp_path)

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


def _quick_texture_check(uexp_path):
    """Quick binary scan to determine if a .uexp is likely a texture file.
    Reads the entire file in 16KB chunks looking for pixel format strings."""
    try:
        size = os.path.getsize(uexp_path)
        if size < 128:
            return False

        # Build search set of encoded format bytes
        fmt_needles = [fmt.encode('ascii') for fmt in KNOWN_PIXEL_FORMATS]

        # For small files, just read the whole thing
        if size <= 65536:
            with open(uexp_path, 'rb') as f:
                data = f.read()
            return any(needle in data for needle in fmt_needles)

        # For larger files, sample multiple 16KB chunks across the file
        chunk_size = 16384
        offsets = [0]  # Always check start
        # Sample middle sections (texture metadata is often in first 64KB)
        for off in range(chunk_size, min(size, 65536), chunk_size):
            offsets.append(off)
        # Also check the end (mip metadata can be near end)
        if size > chunk_size:
            offsets.append(max(0, size - chunk_size))

        with open(uexp_path, 'rb') as f:
            for off in offsets:
                f.seek(off)
                data = f.read(chunk_size)
                if any(needle in data for needle in fmt_needles):
                    return True

        return False
    except Exception:
        return False


# ===================================================================
#  IMAGE SCANNING (supports exports, unpacked PAKs, and deep scan)
# ===================================================================

def find_all_images(base_path, search_paths, name_filter=None, require_json=False):
    """
    Recursively scan directories for .uexp texture files.
    If require_json=True, only finds files with matching .json metadata (FModel exports).
    If require_json=False, finds all .uexp files and validates them with binary parsing.
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

                has_json = os.path.exists(json_path)

                if require_json and not has_json:
                    continue

                # Validate it's actually a texture file
                if has_json:
                    try:
                        with open(json_path, encoding='utf-8') as f:
                            meta = json.load(f)
                        if isinstance(meta, list):
                            meta = meta[0]
                        if 'Mips' not in meta or not meta['Mips']:
                            continue
                    except Exception:
                        continue
                else:
                    # Quick check: file must be at least 128 bytes and contain a
                    # known pixel format string somewhere in the file
                    if not _quick_texture_check(uexp_path):
                        continue

                # Build output name from relative path
                rel = os.path.relpath(uexp_path, base_path)
                parts = rel.replace('\\', '/').split('/')
                clean_parts = []
                skip = {'Assets', '2DArt', 'UI', 'Items', 'Item_Icons',
                        'Textures', 'Materials', 'Environment'}
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


def find_all_deep(base_path, name_filter=None):
    """Deep scan: find ALL .uexp texture files anywhere under base_path.
    Used with --all flag to extract everything."""
    icons = {}
    scanned_dirs = set()
    checked = 0
    textures = 0
    print('[*] Deep scanning entire Content directory...')

    for root, dirs, files in os.walk(base_path):
        real_root = os.path.realpath(root)
        if real_root in scanned_dirs:
            continue
        scanned_dirs.add(real_root)

        uexp_files = [f for f in files if f.lower().endswith('.uexp')]
        if not uexp_files:
            continue

        # Show which directory we're scanning
        rel_dir = os.path.relpath(root, base_path)
        if rel_dir == '.':
            rel_dir = '(root)'
        print(f'\r    Scanning: {rel_dir[:80]:<80}  [{textures} textures found]', end='', flush=True)

        for filename in uexp_files:
            checked += 1
            uexp_path = os.path.join(root, filename)
            json_path = uexp_path.replace('.uexp', '.json')
            has_json = os.path.exists(json_path)

            # Validate it's a texture
            if has_json:
                try:
                    with open(json_path, encoding='utf-8') as f:
                        meta = json.load(f)
                    if isinstance(meta, list):
                        meta = meta[0]
                    if 'Mips' not in meta or not meta['Mips']:
                        continue
                except Exception:
                    continue
            else:
                if not _quick_texture_check(uexp_path):
                    continue

            textures += 1

            # Build output name preserving directory structure
            rel = os.path.relpath(uexp_path, base_path)
            parts = rel.replace('\\', '/').split('/')
            clean_parts = [p for p in parts if p not in {'Assets'}]

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

    # Clear the progress line
    print(f'\r    Scanned {checked} files, found {textures} textures' + ' ' * 40)
    return icons


# Legacy alias
def find_all_icons(base_path, search_paths, name_filter=None):
    return find_all_images(base_path, search_paths, name_filter, require_json=True)


# ===================================================================
#  MAIN
# ===================================================================

def build_search_paths(args):
    """Build the list of search paths based on CLI flags."""
    paths = []

    # Check which categories are requested
    any_category = (args.loading_screens or args.backgrounds or args.cinematics or
                    args.marketing or args.environment or args.creatures or
                    args.vfx or args.materials or args.misc_art)

    if args.all:
        # --all means everything
        for _, (_, p) in IMAGE_CATEGORIES.items():
            paths.extend(p)
        return paths, True  # True = also do deep scan

    if not any_category and not args.icons:
        # Default: extract ALL textures (deep scan everything)
        for _, (_, p) in IMAGE_CATEGORIES.items():
            paths.extend(p)
        return paths, True

    # Specific categories requested
    if args.icons:
        paths.extend(UI_ICON_PATHS)
    if args.loading_screens:
        paths.extend(LOADING_SCREEN_PATHS)
    if args.backgrounds:
        paths.extend(BACKGROUND_PATHS)
    if args.cinematics:
        paths.extend(CINEMATIC_PATHS)
    if args.marketing:
        paths.extend(MARKETING_PATHS)
    if args.environment:
        paths.extend(ENVIRONMENT_PATHS)
    if args.creatures:
        paths.extend(CREATURE_PATHS)
    if args.vfx:
        paths.extend(VFX_PATHS)
    if args.materials:
        paths.extend(MATERIAL_PATHS)
    if args.misc_art:
        paths.extend(MISC_ART_PATHS)

    return paths, False


def main():
    parser = argparse.ArgumentParser(
        description='Icarus Image Extractor v8 — Extracts ALL images from game files. '
                    'No external tools needed! Works directly from game install or FModel exports.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='MODES:\n'
               '  Default:    Extract UI icons only (from FModel exports)\n'
               '  --game:     Extract directly from game PAK files (no FModel needed!)\n'
               '  --all:      Extract ALL images (icons, loading screens, backgrounds, etc.)\n'
               '\n'
               'CATEGORY FLAGS (combine as many as you want):\n'
               '  --icons             UI icons (items, achievements, talents, HUD)\n'
               '  --loading-screens   Full-screen biome/mission splash art\n'
               '  --backgrounds       Menu backgrounds, title screen art\n'
               '  --cinematics        Cutscene frames, story art\n'
               '  --marketing         Promotional/marketing art\n'
               '  --environment       Biome & terrain textures\n'
               '  --creatures         Creature & animal textures\n'
               '  --vfx               VFX & particle textures\n'
               '  --materials         Surface textures (wood, stone, metal)\n'
               '  --misc-art          Concept art, portraits, renders\n'
               '\n'
               'Only requires Python 3.8+ and Pillow (auto-installed).')

    # Source options
    parser.add_argument('--base', default=None,
                        help='Path to Icarus exports Content folder (auto-detected if omitted)')
    parser.add_argument('--game', action='store_true',
                        help='Extract directly from game PAK files (no FModel/exports needed)')
    parser.add_argument('--paks', default=None,
                        help='Path to Icarus Paks directory (auto-detected if omitted)')

    # Output options
    parser.add_argument('--out', default=None,
                        help='Output directory for PNG files (default: Desktop/icarus_icons)')
    parser.add_argument('--filter', default=None,
                        help='Only extract images matching this keyword (e.g. "Lithium", "Loading")')
    parser.add_argument('--dry-run', action='store_true',
                        help='List images that would be extracted without actually extracting')
    parser.add_argument('--force', action='store_true',
                        help='Re-extract images even if they already exist (overwrite)')
    parser.add_argument('--organize', action='store_true', default=True,
                        help='Organize output into subdirectories by category (default: on)')

    # Category flags
    parser.add_argument('--all', action='store_true',
                        help='Extract ALL textures (this is now the default!)')
    parser.add_argument('--icons', action='store_true', default=False,
                        help='Extract ONLY UI icons (items, achievements, talents, HUD)')
    parser.add_argument('--loading-screens', action='store_true',
                        help='Extract loading screen art')
    parser.add_argument('--backgrounds', action='store_true',
                        help='Extract menu/title backgrounds')
    parser.add_argument('--cinematics', action='store_true',
                        help='Extract cinematic/cutscene art')
    parser.add_argument('--marketing', action='store_true',
                        help='Extract marketing/promotional art')
    parser.add_argument('--environment', action='store_true',
                        help='Extract environment & biome textures')
    parser.add_argument('--creatures', action='store_true',
                        help='Extract creature & animal textures')
    parser.add_argument('--vfx', action='store_true',
                        help='Extract VFX & particle textures')
    parser.add_argument('--materials', action='store_true',
                        help='Extract material/surface textures')
    parser.add_argument('--misc-art', action='store_true',
                        help='Extract concept art, renders, misc 2D art')

    args = parser.parse_args()

    print(f'=== Icarus Image Extractor v8 ===\n')

    # Ensure Pillow is available
    if not args.dry_run:
        if not ensure_pillow():
            sys.exit(1)

    # Build search paths from flags
    search_paths, do_deep_scan = build_search_paths(args)

    # Print what we're extracting
    if do_deep_scan:
        print('[*] Mode: Extract ALL textures (deep scan)')
    elif args.game:
        print('[*] Mode: Direct game extraction (PAK files)')
    else:
        active = []
        for cat_key, (cat_name, _) in IMAGE_CATEGORIES.items():
            if getattr(args, cat_key.replace('-', '_'), False):
                active.append(cat_name)
        if active:
            print(f'[*] Categories: {", ".join(active)}')
        else:
            print('[*] Mode: Extract ALL textures')

    # --- Resolve source path ---
    temp_dir = None

    if args.game or args.paks:
        # PAK mode — extract from game files
        paks_dir = args.paks
        if not paks_dir:
            print('[*] Looking for Icarus game PAK files...')
            paks_dir = find_game_paks_dir()
            if paks_dir:
                print(f'    Found: {paks_dir}')
            else:
                print('    Could not auto-detect Icarus Paks directory.')
                paks_dir = prompt_path('    Enter path to Icarus/Content/Paks: ')
                if not paks_dir:
                    print('ERROR: No Paks path provided. Exiting.')
                    sys.exit(1)

        if not os.path.isdir(paks_dir):
            print(f'ERROR: Directory not found: {paks_dir}')
            sys.exit(1)

        # Create temp directory for extracted files
        temp_dir = tempfile.mkdtemp(prefix='icarus_extract_')
        print(f'[*] Temp directory: {temp_dir}')

        base_path = unpack_paks_to_temp(paks_dir, search_paths, temp_dir, args.filter, extract_all=do_deep_scan)
        if not base_path:
            print('ERROR: Could not extract any files from PAK files.')
            print('       The PAK files may use unsupported compression (Oodle).')
            print('       Try using FModel to export the game files first.')
            sys.exit(1)
    else:
        # Smart mode: try exports first, auto-switch to game PAKs if not found
        base_path = args.base
        if not base_path:
            print('[*] Looking for Icarus game data...')

            # Check for FModel exports first (they have JSON metadata = better results)
            base_path = find_icarus_exports()
            if base_path:
                print(f'    Found exports: {base_path}')
            else:
                # No exports — auto-switch to game PAK extraction
                print('    No FModel exports found — extracting from game files directly...')
                paks_dir = find_game_paks_dir()
                if not paks_dir:
                    paks_dir = prompt_path('    Could not auto-detect game. Enter path to Icarus/Content/Paks: ')
                if paks_dir and os.path.isdir(paks_dir):
                    print(f'    Found game: {paks_dir}')
                    temp_dir = tempfile.mkdtemp(prefix='icarus_extract_')
                    print(f'[*] Temp directory: {temp_dir}')
                    base_path = unpack_paks_to_temp(paks_dir, search_paths, temp_dir, args.filter, extract_all=do_deep_scan)
                    if not base_path:
                        print('ERROR: Could not extract from PAK files.')
                        sys.exit(1)
                else:
                    print('ERROR: Could not find Icarus game data.')
                    print('  Options:')
                    print('    python extract_all_icons.py --game            (extract from PAK files)')
                    print('    python extract_all_icons.py --base "path"     (use FModel exports)')
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

    # Find all image textures
    if do_deep_scan:
        images = find_all_deep(base_path, args.filter)
    else:
        # Use both JSON-validated and binary-validated scanning
        has_json_files = any(
            os.path.exists(os.path.join(base_path, sp))
            for sp in search_paths
            if os.path.isdir(os.path.join(base_path, sp))
        )
        images = find_all_images(base_path, search_paths, args.filter, require_json=False)

    if not images:
        print('No images found!')
        print(f'  Searched: {base_path}')
        if args.game:
            print('  The PAK extraction may not have found matching texture files.')
            print('  Try: python extract_all_icons.py --game --all')
        else:
            print('  Looking for .uexp texture files.')
            print('  Try: python extract_all_icons.py --game   (to extract from game PAKs)')
        sys.exit(1)

    print(f'Found {len(images)} textures to extract\n')

    if args.dry_run:
        for name in sorted(images.keys()):
            print(f'  {name}')
        print(f'\nTotal: {len(images)} images (dry run, nothing extracted)')
        # Cleanup temp dir
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        return

    # Extract all images
    good, bad, skipped = [], [], []
    for i, (out_name, src) in enumerate(sorted(images.items()), 1):
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
        total = len(images)
        pct = int(i / total * 100)
        status = 'OK  ' if ok else 'FAIL'
        bar = f'[{"#" * (pct // 5)}{"." * (20 - pct // 5)}]'
        print(f'  {bar} {pct:3d}% [{i}/{total}] {status}  {out_name} ({msg})')
        (good if ok else bad).append(out_name if ok else (out_name, msg))

    # Cleanup temp dir
    if temp_dir:
        import shutil
        print(f'\n[*] Cleaning up temp files...')
        shutil.rmtree(temp_dir, ignore_errors=True)

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
    print(f'Total images: {len(images)}')
    print(f'\nOutput: {out_dir}')


if __name__ == '__main__':
    main()
