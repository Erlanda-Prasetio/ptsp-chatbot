"""Remove all emojis from Python files"""
import os
import re
from pathlib import Path

# Emoji pattern - matches most common emojis
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U00002600-\U000026FF"  # misc symbols
    "]+",
    flags=re.UNICODE
)

# Emoji replacements for common ones
EMOJI_REPLACEMENTS = {
    '[OK]': '[OK]',
    '[FAIL]': '[FAIL]',
    '[WARN]': '[WARN]',
    '[INFO]': '[INFO]',
    '[STATS]': '[STATS]',
    '[SEARCH]': '[SEARCH]',
    '[FILE]': '[FILE]',
    '[DIR]': '[DIR]',
    '[CONNECT]': '[CONNECT]',
    '[TIME]': '[TIME]',
    '[SAVE]': '[SAVE]',
    '[DELETE]': '[DELETE]',
    '[TEST]': '[TEST]',
    '[START]': '[START]',
    '[TARGET]': '[TARGET]',
    '[METRIC]': '[METRIC]',
    '[TOOL]': '[TOOL]',
    '[CONFIG]': '[CONFIG]',
}

def remove_emojis_from_file(filepath):
    """Remove emojis from a Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # First, replace known emojis with text equivalents
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            content = content.replace(emoji, replacement)
        
        # Then remove any remaining emojis
        content = EMOJI_PATTERN.sub('', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Process all Python files"""
    root = Path(__file__).parent
    
    # Find all Python files
    python_files = list(root.glob('**/*.py'))
    
    print(f"Found {len(python_files)} Python files")
    print("Removing emojis...\n")
    
    modified_count = 0
    for py_file in python_files:
        # Skip virtual environment and cache directories
        if any(part in py_file.parts for part in ['venv', 'env', '__pycache__', '.git']):
            continue
        
        if remove_emojis_from_file(py_file):
            print(f"[OK] {py_file.relative_to(root)}")
            modified_count += 1
    
    print(f"\n{modified_count} files modified")
    print("Done!")

if __name__ == "__main__":
    main()
