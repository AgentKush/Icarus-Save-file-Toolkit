"""Quick diagnostic: traces why BuildGuide extraction fails."""
import json, os, struct, sys

# Test file
BASE = r"E:\SteamLibrary\steamapps\common\Icarus\Exports\Icarus\Content\Assets\2DArt\UI\HUD"
TEST = "BuildGuide"

uexp_path = os.path.join(BASE, f"{TEST}.uexp")
json_path = os.path.join(BASE, f"{TEST}.json")
ubulk_path = os.path.join(BASE, f"{TEST}.ubulk")

print(f"=== Diagnosing {TEST} ===")
print(f"  uexp exists: {os.path.exists(uexp_path)} ({os.path.getsize(uexp_path) if os.path.exists(uexp_path) else 'N/A'} bytes)")
print(f"  json exists: {os.path.exists(json_path)} ({os.path.getsize(json_path) if os.path.exists(json_path) else 'N/A'} bytes)")
print(f"  ubulk exists: {os.path.exists(ubulk_path)} ({os.path.getsize(ubulk_path) if os.path.exists(ubulk_path) else 'N/A'} bytes)")

# Load JSON
print(f"\n--- JSON Analysis ---")
with open(json_path, encoding='utf-8') as f:
    meta = json.load(f)
print(f"  JSON type: {type(meta).__name__}")
if isinstance(meta, list):
    print(f"  Array length: {len(meta)}")
    meta = meta[0]

print(f"  Top-level keys: {list(meta.keys())}")
print(f"  SizeX: {meta.get('SizeX', 'MISSING')}")
print(f"  SizeY: {meta.get('SizeY', 'MISSING')}")
print(f"  PixelFormat: {meta.get('PixelFormat', 'MISSING')}")

mips = meta.get('Mips', [])
print(f"  Mips count: {len(mips)}")

if mips:
    mip0 = mips[0]
    bd = mip0.get('BulkData', {})
    print(f"\n  Mip0 BulkData:")
    print(f"    BulkDataFlags: {bd.get('BulkDataFlags', 'MISSING')}")
    print(f"    ElementCount: {bd.get('ElementCount', 'MISSING')}")
    print(f"    SizeOnDisk: {bd.get('SizeOnDisk', 'MISSING')}")
    print(f"    OffsetInFile: {bd.get('OffsetInFile', 'MISSING')}")

    flags = bd.get('BulkDataFlags', '')
    is_ubulk = 'PayloadInSeperateFile' in str(flags)
    print(f"    Is ubulk mip: {is_ubulk}")

    if is_ubulk and os.path.exists(ubulk_path):
        size = bd.get('SizeOnDisk', bd.get('ElementCount', 0))
        off_raw = bd.get('OffsetInFile', 0)
        if isinstance(off_raw, str):
            offset = int(off_raw, 16) if off_raw.startswith('0x') else int(off_raw)
        else:
            offset = int(off_raw)

        ubulk_size = os.path.getsize(ubulk_path)
        print(f"\n  ubulk read attempt:")
        print(f"    ubulk file size: {ubulk_size}")
        print(f"    mip0 data size: {size}")
        print(f"    parsed offset: {offset}")
        print(f"    offset+size <= ubulk_size: {offset + size <= ubulk_size}")

        if offset + size <= ubulk_size:
            with open(ubulk_path, 'rb') as f:
                f.seek(offset)
                raw = f.read(size)
            print(f"    Read {len(raw)} bytes successfully!")
            print(f"    First 16 bytes: {raw[:16].hex()}")
        else:
            # Try offset 0
            print(f"    Offset invalid, trying 0...")
            if size <= ubulk_size:
                with open(ubulk_path, 'rb') as f:
                    raw = f.read(size)
                print(f"    Read {len(raw)} bytes from offset 0!")
                print(f"    First 16 bytes: {raw[:16].hex()}")

    # Check inline mips
    print(f"\n  All mips flags:")
    for i, m in enumerate(mips):
        mbd = m.get('BulkData', {})
        sz = mbd.get('SizeOnDisk', mbd.get('ElementCount', 0))
        mw = m.get('SizeX', '?')
        mh = m.get('SizeY', '?')
        flags = mbd.get('BulkDataFlags', '')
        print(f"    Mip {i}: {mw}x{mh}, size={sz}, flags={flags}")

# Binary analysis
print(f"\n--- Binary Analysis ---")
with open(uexp_path, 'rb') as f:
    uexp_data = f.read()

print(f"  uexp size: {len(uexp_data)} bytes")

# Look for pixel format strings
KNOWN = ['PF_DXT1', 'PF_DXT5', 'PF_BC7', 'PF_B8G8R8A8', 'PF_BC1', 'PF_BC3',
         'PF_BC5', 'PF_G8', 'PF_FloatRGBA', 'PF_A8', 'PF_BC4']

for fmt in KNOWN:
    # Raw search
    raw_idx = uexp_data.find(fmt.encode('ascii'))
    # FString search
    fmt_bytes = fmt.encode('ascii') + b'\x00'
    length_prefix = struct.pack('<i', len(fmt) + 1)
    needle = length_prefix + fmt_bytes
    fstr_idx = uexp_data.find(needle)

    if raw_idx >= 0 or fstr_idx >= 0:
        print(f"  {fmt}: raw@{raw_idx}, FString@{fstr_idx}")

        if fstr_idx >= 0 and fstr_idx >= 12:
            w = struct.unpack_from('<i', uexp_data, fstr_idx - 12)[0]
            h = struct.unpack_from('<i', uexp_data, fstr_idx - 8)[0]
            packed = struct.unpack_from('<I', uexp_data, fstr_idx - 4)[0]
            after = fstr_idx + 4 + len(fmt) + 1
            if after + 8 <= len(uexp_data):
                first_mip = struct.unpack_from('<i', uexp_data, after)[0]
                num_mips = struct.unpack_from('<i', uexp_data, after + 4)[0]
                print(f"    → w={w}, h={h}, packed={packed}, first_mip={first_mip}, num_mips={num_mips}")

                # Check mip0 bulk flags
                mip_start = after + 8
                if mip_start + 4 <= len(uexp_data):
                    cooked = struct.unpack_from('<i', uexp_data, mip_start)[0]
                    if cooked == 1 and mip_start + 24 <= len(uexp_data):
                        bulk_flags = struct.unpack_from('<I', uexp_data, mip_start + 4)[0]
                        elem_count = struct.unpack_from('<i', uexp_data, mip_start + 8)[0]
                        size_disk = struct.unpack_from('<i', uexp_data, mip_start + 12)[0]
                        off_file = struct.unpack_from('<q', uexp_data, mip_start + 16)[0]
                        print(f"    → mip0: cooked={cooked}, flags=0x{bulk_flags:04X}, elem={elem_count}, sz={size_disk}, off={off_file}")
                        print(f"    → PayloadInSeperateFile: {bool(bulk_flags & 0x0200)}")

print("\n--- Script Version Check ---")
script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extract_all_icons.py')
if os.path.exists(script_path):
    with open(script_path, 'r') as f:
        first_line = f.readline()
        second_line = f.readline()
    print(f"  {second_line.strip()}")

    with open(script_path, 'r') as f:
        content = f.read()
    print(f"  Contains '_read_ubulk_mip0': {'_read_ubulk_mip0' in content}")
    print(f"  Contains '_is_ubulk_mip': {'_is_ubulk_mip' in content}")
    print(f"  Contains 'MAX_MIP_READ_SIZE': {'MAX_MIP_READ_SIZE' in content}")
else:
    print(f"  Script not found at {script_path}")

print("\nDone!")
