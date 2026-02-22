#!/usr/bin/env python3
"""
Script to add timeout=60000 and wait_for_load_state("networkidle") to goto() calls
"""
import re

def fix_file(filepath):
    """Fix goto() calls in a single file"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    modified_lines = []
    i = 0
    changes_made = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line has a goto() without timeout
        if '.goto(f"{base_url}' in line and 'timeout=' not in line:
            # Add timeout parameter - replace closing ')' with ', timeout=60000)'
            modified_line = re.sub(r'\.goto\(f"\{base_url\}([^"]+)"\)', r'.goto(f"{base_url}\1", timeout=60000)', line)
            modified_lines.append(modified_line)
            changes_made += 1
            
            # Check if next line already has wait_for_load_state
            if i + 1 < len(lines) and 'wait_for_load_state' not in lines[i + 1]:
                # Add wait_for_load_state on the next line with proper indentation
                indent = len(line) - len(line.lstrip())
                page_var = 'authenticated_page' if 'authenticated_page' in line else 'page'
                modified_lines.append(' ' * indent + f'{page_var}.wait_for_load_state("networkidle")\n')
        else:
            modified_lines.append(line)
        
        i += 1
    
    if changes_made > 0:
        with open(filepath, 'w') as f:
            f.writelines(modified_lines)
        print(f"✓ {filepath}: Modified {changes_made} goto() calls")
    else:
        print(f"• {filepath}: No changes needed")
    
    return changes_made

# Fix all remaining files
files_to_fix = [
    'notes_app/test_ui.py',
    'commands_app/test_ui.py',
    'messaging_system/test_ui.py'
]

total_changes = 0
for file in files_to_fix:
    try:
        changes = fix_file(file)
        total_changes += changes
    except Exception as e:
        print(f"✗ {file}: Error - {e}")

print(f"\n✓ Total: Modified {total_changes} goto() calls across {len(files_to_fix)} files")
