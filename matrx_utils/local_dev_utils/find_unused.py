import subprocess
import os
import re

# Path to the directory to check
TARGET_DIR = "/Users/armanisadeghi/code/matrx-admin/features/agents"
PROJECT_ROOT = "/Users/armanisadeghi/code/matrx-admin"

def get_exports(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Regex for exports (functions, consts, types, interfaces, etc.)
    # This captures named exports.
    exports = re.findall(r'export (?:const|function|class|type|interface|enum) (\w+)', content)
    
    # Check for default exports
    default_export_match = re.search(r'export default (?:function|class|) (\w+)', content)
    if default_export_match:
        exports.append(default_export_match.group(1))
    
    # Check for default export without name (e.g. export default function() ...)
    # This is harder to track but usually there's a name.
    return set(exports)

def is_used(symbol, defining_file):
    # Ripgrep for usage
    try:
        result = subprocess.run(
            ['grep', '-r', '-l', symbol, PROJECT_ROOT],
            capture_output=True, text=True, check=False
        )
        files = result.stdout.splitlines()
        
        # Filter out the defining file and index.ts files in the same or lower hierarchy
        other_files = []
        for file in files:
            if file == defining_file:
                continue
            if '/node_modules/' in file or '/.git/' in file:
                continue
            if file.endswith('index.ts') or file.endswith('index.tsx'):
                # Still check if it's truly used or just re-exported
                # For now let's see if there are any *other* files
                continue
            other_files.append(file)
            
        return len(other_files) > 0
    except Exception as e:
        print(f"Error checking {symbol}: {e}")
        return True # Assume used on error

def main():
    unused_items = []
    
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(('.ts', '.tsx')) and file != 'index.ts' and file != 'index.tsx':
                file_path = os.path.join(root, file)
                exports = get_exports(file_path)
                
                for symbol in exports:
                    if not is_used(symbol, file_path):
                        unused_items.append((symbol, file_path))
    
    print("\n--- Potential Unused Items ---")
    for symbol, path in unused_items:
        print(f"File: {path}\nSymbol: {symbol}\n")

if __name__ == "__main__":
    main()
