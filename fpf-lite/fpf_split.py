#!/usr/bin/env python3

import re
import os

def normalize_text(text):
    """
    Normalizes text to handle non-standard hyphens used in FPF.
    """
    text = text.replace('\u2011', '-') # Non-breaking hyphen
    text = text.replace('\u2013', '-') # En dash
    text = text.replace('\u2014', '-') # Em dash
    text = text.replace('\u00A0', ' ') # Non-breaking space
    return text

def get_target_module(header_line):
    """
    Determines which module a section belongs to based on the Part letter.
    """
    # Normalize for easier matching
    clean_line = normalize_text(header_line).upper()

    # Regex to find "Part X"
    match = re.search(r'#\s*PART\s+([A-Z])', clean_line)
    
    if not match:
        return None

    part_letter = match.group(1)

    # --- ROUTING LOGIC ---
    
    # KERNEL: Ontology, Roles, Lexicon, Constitution
    # Part A: Kernel Architecture
    # Part E: Constitution & Authoring (contains E.10 LEX)
    if part_letter in ['A', 'E']:
        return 'kernel'

    # LOGIC: Reasoning, Unification, Trust
    # Part B: Reasoning Cluster
    # Part F: Unification Suite
    elif part_letter in ['B', 'F']:
        return 'logic'

    # DOMAIN: Specific Architheories, Implementation, Appendices
    # Part C: Architheories (CAL/CHR)
    # Part D: Ethics
    # Part G: SoTA Kit
    # Parts H, I, J, K: Appendices
    else:
        return 'domain'

def split_fpf(input_file):
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return

    # Output filenames
    filenames = {
        'kernel': 'FPF-Module-Kernel.md',
        'logic':  'FPF-Module-Logic.md',
        'domain': 'FPF-Module-Domain.md'
    }

    # Open handles for all output files
    files = {key: open(name, 'w', encoding='utf-8') for key, name in filenames.items()}

    # Default target (Preface goes to Kernel)
    current_target = 'kernel'
    
    print(f"Reading {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Check if this line is a Part header
            if line.strip().startswith('#'):
                new_target = get_target_module(line)
                if new_target:
                    current_target = new_target
                    print(f"--> Switching to [{current_target.upper()}] at: {line.strip()[:40]}...")

            # Write line to the currently active module
            files[current_target].write(line)

    # Close all files
    for f in files.values():
        f.close()

    print("-" * 30)
    print("Splitting complete. Created:")
    for name in filenames.values():
        size_kb = os.path.getsize(name) / 1024
        print(f"  - {name} ({round(size_kb, 1)} KB)")

if __name__ == "__main__":
    INPUT_FILE = "FPF-Spec.md"
    split_fpf(INPUT_FILE)