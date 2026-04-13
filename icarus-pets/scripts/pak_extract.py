"""Simple UE4 Pak v11 file lister and extractor."""
import struct
import zlib
import os

def read_string(data, pos):
    length = struct.unpack_from('<i', data, pos)[0]
    pos += 4
    if length <= 0:
        return "", pos
    s = data[pos:pos+length-1].decode('utf-8', errors='replace')
    pos += length
    return s, pos

def parse_pak(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find footer magic
    magic_pos = data.rfind(b'\xe1\x12\x6f\x5a')
    if magic_pos < 0:
        print("Not a valid UE4 pak file")
        return None
    
    pos = magic_pos + 4
    version = struct.unpack_from('<I', data, pos)[0]; pos += 4
    index_offset = struct.unpack_from('<q', data, pos)[0]; pos += 8
    index_size = struct.unpack_from('<q', data, pos)[0]; pos += 8
    
    print(f"Pak version: {version}")
    print(f"Index at: {index_offset}, size: {index_size}")
    
    # Parse index
    pos = index_offset
    mount_point, pos = read_string(data, pos)
    print(f"Mount point: {mount_point}")
    
    file_count = struct.unpack_from('<i', data, pos)[0]; pos += 4
    print(f"File count: {file_count}")
    
    path_hash_seed = struct.unpack_from('<q', data, pos)[0]; pos += 8
    
    # bHasPathHashIndex
    has_path_hash = struct.unpack_from('<i', data, pos)[0]; pos += 4
    if has_path_hash:
        path_hash_offset = struct.unpack_from('<q', data, pos)[0]; pos += 8
        path_hash_size = struct.unpack_from('<q', data, pos)[0]; pos += 8
        pos += 20  # hash
    
    # bHasFullDirectoryIndex
    has_full_dir = struct.unpack_from('<i', data, pos)[0]; pos += 4
    full_dir_offset = 0
    full_dir_size = 0
    if has_full_dir:
        full_dir_offset = struct.unpack_from('<q', data, pos)[0]; pos += 8
        full_dir_size = struct.unpack_from('<q', data, pos)[0]; pos += 8
        pos += 20  # hash
    
    # Encoded entries
    encoded_count = struct.unpack_from('<i', data, pos)[0]; pos += 4
    encoded_data_start = pos
    # Each encoded entry is 12 bytes (flags+offset compressed)
    encoded_entries_size = encoded_count * 12  # approximate
    
    print(f"Has path hash: {has_path_hash}, Has full dir: {has_full_dir}")
    print(f"Full dir index at: {full_dir_offset}, size: {full_dir_size}")
    print(f"Encoded entries: {encoded_count}")
    
    # Parse full directory index to get filenames
    files = []
    if has_full_dir and full_dir_size > 0:
        dpos = full_dir_offset
        dir_count = struct.unpack_from('<i', data, dpos)[0]; dpos += 4
        
        for _ in range(dir_count):
            dir_name, dpos = read_string(data, dpos)
            file_in_dir_count = struct.unpack_from('<i', data, dpos)[0]; dpos += 4
            
            for _ in range(file_in_dir_count):
                filename, dpos = read_string(data, dpos)
                encoded_idx = struct.unpack_from('<i', data, dpos)[0]; dpos += 4
                full_path = dir_name + filename
                files.append((full_path, encoded_idx))
    
    print(f"\nFound {len(files)} files:")
    for path, idx in files:
        print(f"  [{idx:3d}] {path}")
    
    # Now decode encoded entries to get file offsets/sizes
    # v11 encoded entry format: variable length bit-packed
    # For simplicity, let's try to read unencoded entry info
    # The encoded entries use a compact format - let me try reading them
    
    return data, files, encoded_data_start, encoded_count, version

def decode_entry(data, encoded_start, idx):
    """Try to decode a pak v11 entry. Entries are bit-packed."""
    # This is complex - v11 uses variable-length encoding
    # Let's try a simpler approach: look for the file data directly
    pass

def try_extract_by_search(data, filename_fragment):
    """Try to find and decompress data associated with a filename."""
    # Search for the filename in the data
    search = filename_fragment.encode('utf-8')
    positions = []
    start = 0
    while True:
        idx = data.find(search, start)
        if idx < 0:
            break
        positions.append(idx)
        start = idx + 1
    return positions

def cleanup_old_extracts():
    """Remove old extracted chunks to prevent stale data contamination."""
    import glob
    pak_dir = "pak-files"
    patterns = [
        os.path.join(pak_dir, "extracted_*.bin"),
        os.path.join(pak_dir, "found_*.json"),
    ]
    removed = 0
    for pattern in patterns:
        for f in glob.glob(pattern):
            os.remove(f)
            removed += 1
    if removed:
        print(f"Cleaned up {removed} old extracted file(s)")


if __name__ == "__main__":
    cleanup_old_extracts()
    result = parse_pak(os.path.join("pak-files", "data.pak"))
    if result:
        data, files, enc_start, enc_count, version = result
        
        # Try to decompress file data for interesting files
        print("\n\nSearching for zlib streams...")
        # The file data is before the index, try decompressing from start
        # Each file entry has: offset, compressed size, uncompressed size
        # The actual data starts at offset 0 of the pak
        
        # Try brute-force finding zlib streams
        found = 0
        for i in range(0, min(len(data), 2500000), 1):
            if data[i:i+2] == b'\x78\x9c' or data[i:i+2] == b'\x78\x01' or data[i:i+2] == b'\x78\xda':
                try:
                    decompressed = zlib.decompress(data[i:i+65536])
                    if len(decompressed) > 100:
                        # Check if it contains mount/talent related data
                        if any(kw in decompressed for kw in [b'Talent', b'Mount', b'Genetic', b'Buffalo', b'Boar', b'Wolf']):
                            found += 1
                            outname = f"pak-files/extracted_{i}.bin"
                            with open(outname, 'wb') as f:
                                f.write(decompressed)
                            # Show some strings
                            import re
                            strings = re.findall(b'[\x20-\x7e]{6,}', decompressed[:2000])
                            preview = [s.decode() for s in strings[:10]]
                            print(f"  Found at {i}: {len(decompressed)} bytes decompressed")
                            print(f"    Preview: {preview[:5]}")
                except:
                    pass
        print(f"\nExtracted {found} relevant chunks")
