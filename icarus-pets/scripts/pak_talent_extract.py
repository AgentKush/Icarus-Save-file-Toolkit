"""Extract mount/pet talent definitions from pak-extracted bin files.

Reads the zlib-decompressed chunks from pak-files/ that contain
the D_Talents data table, reassembles them, and parses out
complete talent entries with names, descriptions, stats, and values.
"""
import os
import re
import json

PAK_DIR = "pak-files"


def load_talent_chunks():
    """Load and concatenate the sequential chunks containing talent definitions."""
    chunks = []
    for fname in sorted(os.listdir(PAK_DIR)):
        if not fname.endswith('.bin'):
            continue
        offset = int(fname.replace('extracted_', '').replace('.bin', ''))
        # The talent definition chunks live in this offset range
        # Extended to 2300000 for DLC creature talents (Raptor, Slinker, Orka, Storca)
        if offset < 1615000 or offset > 2300000:
            continue
        fpath = os.path.join(PAK_DIR, fname)
        with open(fpath, 'rb') as f:
            chunks.append((offset, f.read()))
    chunks.sort()
    combined = b''.join(d for _, d in chunks)
    return combined.decode('utf-8', errors='replace')


def parse_talent_entries(text):
    """Parse complete talent entries from concatenated text."""
    # Match "Name": "Creature_...", "CombatPet_...", "NonCombatPet_...",
    # and DLC creature talents: Raptor_, RaptorDesert_, Slinker_, Orka_, Storca_
    # Note: Sotrca_ is a typo for Storca_ used by one in-game talent (Sotrca_Regeneration)
    pattern = r'"Name":\s*"((?:Creature_|CombatPet_|NonCombatPet_|Raptor_|RaptorDesert_|Slinker_|Orka_|Storca_|Sotrca_|Saddle_)[^"]+)"'
    matches = list(re.finditer(pattern, text))
    
    entries = []
    for i, m in enumerate(matches):
        name = m.group(1)
        start = m.start()
        # Block extends to next Name match or 5000 chars
        end = matches[i + 1].start() if i + 1 < len(matches) else start + 5000
        block = text[start:end]
        
        # Must have DisplayName to be a real definition (not just a reference)
        # Note: JSON has escaped quotes \" inside strings
        dn = re.search(
            r'"DisplayName":\s*"NSLOCTEXT\((?:[^"\\]|\\.)*,\s*(?:[^"\\]|\\.)*,\s*\\"([^\\]*(?:\\\\.[^\\]*)*)\\\"', block
        )
        if not dn:
            continue
        
        desc = re.search(
            r'"Description":\s*"NSLOCTEXT\((?:[^"\\]|\\.)*,\s*(?:[^"\\]|\\.)*,\s*\\"([^\\]*(?:\\\\.[^\\]*)*)\\\"', block
        )
        tree = re.search(
            r'"TalentTree":\s*\{\s*"RowName":\s*"([^"]*)"', block
        )
        
        # Extract Rewards — each Rewards array element = 1 rank
        # Each element has GrantedStats (one or more stat:value pairs)
        # and optionally GrantedFlags (boolean abilities like food slots)
        #
        # We count Rewards elements (not stat pairs) to get the real rank count.
        # A talent with 4 ranks granting 2 stats each has 4 elements, not 8.
        rewards_section = re.search(r'"Rewards":\s*\[', block)
        rank_rewards = []  # list of dicts, one per rank
        flags = []
        
        if rewards_section:
            # Find the closing ] of the Rewards array (bracket counting)
            arr_start = rewards_section.end()
            depth = 1
            arr_end = arr_start
            for ci, ch in enumerate(block[arr_start:], arr_start):
                if ch == '[':
                    depth += 1
                elif ch == ']':
                    depth -= 1
                if depth == 0:
                    arr_end = ci + 1
                    break
            rewards_text = block[rewards_section.start():arr_end]
            # Each reward element contains "GrantedStats": { ... }
            for gs_match in re.finditer(
                r'"GrantedStats":\s*\{([^}]*)\}', rewards_text
            ):
                stats_block = gs_match.group(1)
                rank_stats = {}
                for sv in re.finditer(
                    r'\(Value=\\"([^\\]+)\\"\)\s*"?\s*:\s*(-?[\d.]+)', stats_block
                ):
                    rank_stats[sv.group(1)] = float(sv.group(2))
                if rank_stats:
                    rank_rewards.append(rank_stats)
            
            # Check for GrantedFlags across all reward elements
            for fm in re.finditer(r'"GrantedFlags":\s*\[\s*"([^"]+)"', rewards_text):
                flags.append(fm.group(1))
        
        # Determine primary stat and values per rank
        if rank_rewards:
            primary_stat = list(rank_rewards[0].keys())[0]
            primary_values = [r.get(primary_stat, 0) for r in rank_rewards]
        else:
            primary_stat = ''
            primary_values = []
        
        # Clean up escaped apostrophes from pak data (e.g. \\' → ')
        display_text = dn.group(1).replace("\\\\'", "'")
        desc_text = (desc.group(1) if desc else '').replace("\\\\'", "'")
        
        entries.append({
            'name': name,
            'display': display_text,
            'desc': desc_text,
            'tree': tree.group(1) if tree else '',
            'max_rank': len(rank_rewards) if rank_rewards else (1 if flags else 0),
            'stat': primary_stat if primary_stat else (flags[0] if flags else ''),
            'values': primary_values if primary_values else [],
        })
    
    return entries


def group_by_tree(entries):
    """Group talent entries by their TalentTree reference."""
    trees = {}
    for e in entries:
        tree = e['tree']
        if tree:
            trees.setdefault(tree, []).append(e)
    return trees


def main():
    print("Loading talent definition chunks...")
    text = load_talent_chunks()
    print(f"  Total text: {len(text):,} chars")
    
    print("Parsing talent entries...")
    entries = parse_talent_entries(text)
    print(f"  Found {len(entries)} complete talent entries")
    
    print("\nGrouping by talent tree...")
    trees = group_by_tree(entries)
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"TALENT TREES ({len(trees)} trees)")
    print(f"{'='*80}")
    
    for tree_name in sorted(trees.keys()):
        tlist = trees[tree_name]
        print(f"\n--- {tree_name}: {len(tlist)} talents ---")
        for t in tlist:
            vals = [int(v) if v == int(v) else v for v in t['values']]
            stat_short = t['stat'][:35] if t['stat'] else '-'
            print(f"  {t['name']}")
            print(f"    \"{t['display']}\" - {t['desc']}")
            print(f"    rank={t['max_rank']} stat={stat_short} vals={vals}")
    
    # Save JSON
    output = {
        'tree_count': len(trees),
        'entry_count': len(entries),
        'trees': trees,
    }
    with open('pak_talents_extracted.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to pak_talents_extracted.json")


if __name__ == "__main__":
    main()
