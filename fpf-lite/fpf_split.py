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

def get_header_part_letter(line):
    """
    Detects if a line is a 'Part X' header and returns the letter (A, B, C...).
    Returns None if it's not a Part header.
    """
    clean_line = normalize_text(line).strip()
    
    # Regex to find "# Part X" or "## Part X" (case insensitive)
    # We look for the pattern: Start of line -> hashes -> whitespace -> "Part" -> whitespace -> Single Letter
    match = re.search(r'^#+\s*Part\s+([A-Z])', clean_line, re.IGNORECASE)
    
    if match:
        return match.group(1).upper()
    return None

def write_module(filename, parts_content, parts_list):
    """
    Writes a list of Part contents into a single module file.
    """
    if not parts_list:
        return

    print(f"  Building {filename} from: {', '.join(parts_list)}")
    
    with open(filename, 'w', encoding='utf-8') as f:
        for part_id in parts_list:
            if part_id in parts_content:
                # Add a separator between parts for clarity (optional)
                if f.tell() > 0: 
                    f.write("\n\n<!-- MODULE SEPARATOR: End of Part " + part_id + " -->\n\n")
                
                f.writelines(parts_content[part_id])
    
    size_kb = os.path.getsize(filename) / 1024
    print(f"    -> Created {filename} ({round(size_kb, 1)} KB)")

def split_and_assemble_fpf(input_file):
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        return

    # 1. READ & PARSE
    # We store content in a dict: { 'PREFACE': [...], 'A': [...], 'B': [...] }
    parts_content = {}
    current_part = 'PREFACE' # Default container for content before the first "Part A"
    parts_content[current_part] = []

    print(f"Reading {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Check for new Part header
            new_part_letter = get_header_part_letter(line)
            
            if new_part_letter:
                current_part = new_part_letter
                if current_part not in parts_content:
                    parts_content[current_part] = []
                print(f"  -> Found start of Part {current_part}")
            
            # Append line to the currently active part bucket
            parts_content[current_part].append(line)

    # 2. DEFINE ASSEMBLY RULES ("Split by Layers")
    # Kernel: Preface + A (Ontology) + E (Constitution)
    kernel_parts = ['PREFACE', 'A', 'E']
    
    # Logic: B (Reasoning) + F (Unification)
    logic_parts = ['B', 'F']
    
    # Domain: C (Architheories) + D (Ethics) + G (SoTA) + Appendices (H, I, J, K...)
    # We dynamically grab all other found parts (C, D, G, H, I, J, K, etc.)
    all_found_keys = set(parts_content.keys())
    used_keys = set(kernel_parts + logic_parts)
    domain_parts = sorted(list(all_found_keys - used_keys))

    print("-" * 30)
    print("Assembling Modules...")

    # 3. WRITE MODULES
    write_module('FPF-Module-Kernel.md', parts_content, kernel_parts)
    write_module('FPF-Module-Logic.md', parts_content, logic_parts)
    write_module('FPF-Module-Domain.md', parts_content, domain_parts)

    print("-" * 30)
    print("Done.")

if __name__ == "__main__":
    INPUT_FILE = "FPF-Spec.md"
    split_and_assemble_fpf(INPUT_FILE)