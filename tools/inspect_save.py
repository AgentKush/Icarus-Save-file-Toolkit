import os, struct

base = r'C:\Users\finla\AppData\Local\Icarus\Saved\PlayerData\76561198094828289'

# Confirm fog file structure
print('=== FOG FILE ANALYSIS ===')
fog_dir = os.path.join(base, 'MapData')
for fn in sorted(os.listdir(fog_dir)):
    fp = os.path.join(fog_dir, fn)
    with open(fp, 'rb') as f:
        data = f.read()
    count = struct.unpack('<i', data[:4])[0]
    remaining = len(data) - 4
    per_entry = remaining / count if count > 0 else 0
    print(f'{fn}: count={count}, remaining={remaining} bytes, per_entry={per_entry:.1f} bytes')
    # Read first 5 triplets
    offset = 4
    for i in range(min(5, count)):
        x, y, state = struct.unpack('<3i', data[offset:offset+12])
        offset += 12
        print(f'  [{i}] x={x}, y={y}, state={state}')
    if count > 5:
        print(f'  ... and {count-5} more entries')

# Confirm flags structure
print('\n=== FLAGS .DAT DECODED ===')
dat_path = os.path.join(base, 'flags_76561198094828289.dat')
with open(dat_path, 'rb') as f:
    data = f.read()

offset = 0
str_len = struct.unpack('<i', data[offset:offset+4])[0]
offset += 4
steam_id = data[offset:offset+str_len].decode('ascii').rstrip('\0')
offset += str_len
flag_count = struct.unpack('<i', data[offset:offset+4])[0]
offset += 4
flags = []
for i in range(flag_count):
    flag_id = struct.unpack('<i', data[offset:offset+4])[0]
    offset += 4
    flags.append(flag_id)

print(f'SteamID: {steam_id}')
print(f'Flag count: {flag_count}')
print(f'Flags: {flags}')
print(f'Bytes consumed: {offset} / {len(data)} (remaining: {len(data)-offset})')
