#!/usr/bin/env python3
"""
Batch extract text from Berkshire Hathaway PDF shareholder letters (1998-2024).

Handles common PDF artifacts: page headers, footers, page numbers, broken lines.
Usage:
    python3 scripts/pdf_extract_letters.py --pdf_dir /path/to/pdfs --output_dir /workspace/corpus/buffett/shareholder_letters

Requirements:
    pip install pdfplumber
"""

import os
import re
import argparse
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Error: pdfplumber is required. Install with: pip install pdfplumber")
    exit(1)


# Common PDF noise patterns
HEADER_PATTERNS = [
    r'^\s*BERKSHIRE HATHAWAY INC\.\s*$',
    r'^\s*\d+\s+Farnam Street.*$',
    r'^\s*WARREN E\. BUFFETT\s*$',
    r'^\s*Chairman and Chief Executive Officer\s*$',
]

FOOTER_PATTERNS = [
    r'^\s*February \d{1,2}, \d{4}\s*$',
    r'^\s*To the Shareholders of Berkshire Hathaway Inc\.\s*$',
]

PAGE_NUMBER_PATTERNS = [
    r'^\s*-?\s*\d+\s*-$',
    r'^\s*\d+\s*$',
]

TABLE_NOISE_PATTERNS = [
    r'^\s*\(?\d\)?\s*$',
    r'^\s*Year-by-Year.*$',
    r'^\s*Comparative.*$',
    r'^\s*Per-Book.*$',
]


def clean_pdf_text(raw_text: str) -> str:
    """Remove common PDF extraction artifacts."""
    lines = raw_text.split('\n')
    cleaned = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Skip headers/footers/page numbers/table artifacts
        if any(re.match(p, stripped, re.IGNORECASE) for p in 
               HEADER_PATTERNS + FOOTER_PATTERNS + PAGE_NUMBER_PATTERNS + TABLE_NOISE_PATTERNS):
            continue
        cleaned.append(stripped)
    
    text = '\n'.join(cleaned)
    
    # Fix broken lines (lines ending without punctuation likely continued on next line)
    # Join short broken lines back together
    text = re.sub(r'([a-z,;])\n([a-z])', r'\1 \2', text)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract and clean text from a PDF file."""
    text_parts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    
    full_text = '\n\n'.join(text_parts)
    return clean_pdf_text(full_text)


def main():
    parser = argparse.ArgumentParser(description='Extract text from PDF shareholder letters')
    parser.add_argument('--pdf_dir', required=True, help='Directory containing PDF files')
    parser.add_argument('--output_dir', required=True, help='Directory to save extracted text')
    parser.add_argument('--min_length', type=int, default=500, help='Minimum text length to save')
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    pdf_dir = Path(args.pdf_dir)
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {args.pdf_dir}")
        return
    
    print(f"📄 Found {len(pdf_files)} PDF files")
    print(f"📂 Output directory: {args.output_dir}")
    print()
    
    success_count = 0
    fail_count = 0
    
    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path.name}...")
        
        try:
            text = extract_text_from_pdf(str(pdf_path))
            
            if len(text) < args.min_length:
                print(f"  ⚠️  Text too short ({len(text)} chars), skipping")
                fail_count += 1
                continue
            
            year_match = re.search(r'(\d{4})', pdf_path.stem)
            output_filename = f"{year_match.group(1)}_letter.txt" if year_match else f"{pdf_path.stem}.txt"
            
            output_path = Path(args.output_dir) / output_filename
            if output_path.exists():
                output_path = Path(args.output_dir) / f"{pdf_path.stem}_extracted.txt"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"  ✅ Saved: {output_path.name} ({len(text)} chars, {len(text.split())} words)")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            fail_count += 1
    
    print(f"\n📊 Summary: {success_count} succeeded, {fail_count} failed")


if __name__ == "__main__":
    main()
