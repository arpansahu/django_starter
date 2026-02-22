#!/usr/bin/env python3
import re

# Check all test_ui.py files
files = [
    'file_manager/test_ui.py',
    'user_account/test_ui.py',
    'notes_app/test_ui.py',
    'elasticsearch_app/test_ui.py',
    'api_app/test_ui.py',
    'event_streaming/test_ui.py',
    'commands_app/test_ui.py',
    'messaging_system/test_ui.py'
]

print("=" * 80)
print("FINAL VERIFICATION - goto() MODIFICATIONS IN test_ui.py FILES")
print("=" * 80)

total_with_timeout = 0
total_with_wait_for_load = 0
total_goto_calls = 0

for filepath in files:
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Count goto calls
        goto_matches = re.findall(r'(?:page|authenticated_page)\.goto\([^)]+\)', content)
        goto_with_timeout = len([m for m in goto_matches if 'timeout=' in m])
        
        # Count wait_for_load_state calls  
        wait_for_load_matches = len(re.findall(r'\.wait_for_load_state\("networkidle"\)', content))
        
        total_goto_calls += len(goto_matches)
        total_with_timeout += goto_with_timeout
        total_with_wait_for_load += wait_for_load_matches
        
        print(f"\n[{filepath}]")
        print(f"  • Total goto() calls: {len(goto_matches)}")
        print(f"  • With timeout=60000: {goto_with_timeout} ({100*goto_with_timeout//len(goto_matches) if len(goto_matches) > 0 else 0}%)")
        print(f"  • wait_for_load_state calls: {wait_for_load_matches}")
        
        # Identify any remaining without timeout
        remaining = len(goto_matches) - goto_with_timeout
        if remaining > 0:
            print(f"  ⚠️  Still missing timeout: {remaining} calls")
        else:
            print(f"  ✓ All goto() calls have timeout parameter")
    
    except Exception as e:
        print(f"\n[{filepath}]")
        print(f"  ✗ Error: {e}")

print("\n" + "=" * 80)
print(f"SUMMARY:")
print(f"  • Total goto() calls found: {total_goto_calls}")
print(f"  • With timeout=60000: {total_with_timeout} ({100*total_with_timeout//total_goto_calls if total_goto_calls > 0 else 0}%)")
print(f"  • wait_for_load_state calls added: {total_with_wait_for_load}")
print("=" * 80)
