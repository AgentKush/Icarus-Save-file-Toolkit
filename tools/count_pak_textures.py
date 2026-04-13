"""Quick PAK scanner — counts how many potential Texture2D assets are in the game."""
import glob, os, sys

# Add parent so we can import the PAK reader
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_all_icons import find_game_paks_dir, read_pak_file

paks_dir = find_game_paks_dir()
if not paks_dir:
    paks_dir = input("Enter path to Icarus/Content/Paks: ").strip()

print(f"Scanning: {paks_dir}\n")
pak_files = sorted(glob.glob(os.path.join(paks_dir, '*.pak')))

total_files = 0
uexp_files = 0
ubulk_files = 0
texture_candidates = 0
by_ext = {}
by_toplevel = {}

for pak_path in pak_files:
    pak_name = os.path.basename(pak_path)
    entries = read_pak_file(pak_path)
    if not entries:
        print(f"  {pak_name}: could not read (Oodle/unsupported)")
        continue

    pak_uexp = 0
    pak_ubulk = 0
    for path in entries:
        total_files += 1
        p = path.lower().replace('\\', '/')
        ext = os.path.splitext(p)[1]
        by_ext[ext] = by_ext.get(ext, 0) + 1

        # Track top-level directory
        parts = p.split('/')
        if len(parts) > 1:
            top = parts[0]
        else:
            top = '(root)'
        by_toplevel[top] = by_toplevel.get(top, 0) + 1

        if ext == '.uexp':
            uexp_files += 1
            pak_uexp += 1
        elif ext == '.ubulk':
            ubulk_files += 1
            pak_ubulk += 1

    print(f"  {pak_name}: {len(entries)} files ({pak_uexp} .uexp, {pak_ubulk} .ubulk)")

print(f"\n=== TOTALS ===")
print(f"Total files in all PAKs: {total_files}")
print(f"Total .uexp files: {uexp_files}")
print(f"Total .ubulk files: {ubulk_files}")
print(f"Total .uasset files: {by_ext.get('.uasset', 0)}")

print(f"\n=== FILE TYPES ===")
for ext, count in sorted(by_ext.items(), key=lambda x: -x[1]):
    print(f"  {ext or '(none)'}: {count}")

print(f"\n=== TOP DIRECTORIES ===")
for d, count in sorted(by_toplevel.items(), key=lambda x: -x[1])[:20]:
    print(f"  {d}: {count}")

print(f"\nNote: Not all .uexp are textures. Texture2D count is a subset of .uexp.")
print(f"The extractor validates each .uexp for texture data (Mips/pixel format).")
