#!/usr/bin/env python3
"""
Convert JSONL OCR results from warren-buffett-letters-from-1998-2024 repo to plain text files.

Usage:
    python3 scripts/convert_jsonl_to_txt.py --jsonl_dir /tmp/buffett_1998_2024/docs/mistral_ocr_results --output_dir corpus/buffett/shareholder_letters
"""

import json
import argparse
import re
from pathlib import Path

# Year mapping from index (see docs/README.md)
YEAR_MAP = {
    0: 2024, 1: 2023, 2: 2022, 3: 2021, 4: 2020,
    5: 2019, 6: 2018, 7: 2017, 8: 2016, 9: 2015,
    10: 2014, 11: 2013, 12: 2012, 13: 2011, 14: 2010,
    15: 2009, 16: 2008, 17: 2007, 18: 2006, 19: 2005,
    20: 2004, 21: 2003, 22: 2002, 23: 2001, 24: 2000,
    25: 1999, 26: 1998
}

def clean_markdown_text(markdown: str) -> str:
    """Convert markdown OCR output to clean plain text."""
    text = markdown
    
    # Remove LaTeX math delimiters but keep content
    text = re.sub(r'\\\((.*?)\\\)', r'\1', text)
    text = re.sub(r'\\\[(.*?)\\\]', r'\1', text)
    text = re.sub(r'\$(.*?)\$', r'\1', text)
    
    # Remove markdown headers but keep text
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove bold/italic markers
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    
    # Convert markdown table rows to simple text
    lines = text.split('\n')
    cleaned_lines = []
    in_table = False
    for line in lines:
        if line.strip().startswith('|') and '---' in line:
            in_table = True
            continue
        if line.strip().startswith('|'):
            # Extract text from table cells
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                cleaned_lines.append(' '.join(cells))
            in_table = True
            continue
        else:
            in_table = False
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Remove common OCR artifacts
    text = re.sub(r'\$\\text\{(.*?)\}', r'\1', text)
    text = re.sub(r'\\text\{(.*?)\}', r'\1', text)
    
    return text.strip()

def convert_jsonl_to_txt(jsonl_path: str, output_path: str):
    """Convert a single JSONL file to plain text."""
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        pages = [json.loads(line) for line in f if line.strip()]
    
    # Sort by index and concatenate markdown
    pages.sort(key=lambda p: p.get('index', 0))
    full_text = '\n\n'.join(clean_markdown_text(p.get('markdown', '')) for p in pages)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    return len(full_text)

def main():
    parser = argparse.ArgumentParser(description='Convert JSONL OCR results to plain text')
    parser.add_argument('--jsonl_dir', required=True, help='Directory containing JSONL files')
    parser.add_argument('--output_dir', required=True, help='Directory to save text files')
    args = parser.parse_args()
    
    jsonl_dir = Path(args.jsonl_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    jsonl_files = sorted(jsonl_dir.glob('*.jsonl'))
    
    if not jsonl_files:
        print(f"No JSONL files found in {jsonl_dir}")
        return
    
    print(f"📄 Found {len(jsonl_files)} JSONL files")
    print(f"📂 Output directory: {output_dir}")
    print()
    
    total_chars = 0
    success_count = 0
    
    for jsonl_path in jsonl_files:
        # Extract year from filename (wb_letters_N.jsonl)
        match = re.search(r'wb_letters_(\d+)', jsonl_path.stem)
        if not match:
            print(f"⚠️  Could not extract index from {jsonl_path.name}, skipping")
            continue
        
        idx = int(match.group(1))
        year = YEAR_MAP.get(idx)
        
        if year is None:
            print(f"⚠️  Unknown index {idx} in {jsonl_path.name}, skipping")
            continue
        
        output_filename = f"{year}_letter.txt"
        output_path = output_dir / output_filename
        
        # Skip if file already exists (from earlier HTML extraction)
        if output_path.exists():
            print(f"⏭️  {output_filename} already exists, overwriting with OCR version")
        
        try:
            char_count = convert_jsonl_to_txt(str(jsonl_path), str(output_path))
            total_chars += char_count
            words = char_count // 5  # rough estimate
            print(f"✅ {output_filename}: {char_count:,} chars, ~{words:,} words")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to convert {jsonl_path.name}: {e}")
    
    print(f"\n📊 Summary: {success_count}/{len(jsonl_files)} files converted, {total_chars:,} total chars")

if __name__ == "__main__":
    main()
