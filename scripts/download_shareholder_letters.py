#!/usr/bin/env python3
"""
Batch download Berkshire Hathaway shareholder letters from berkshirehathaway.com
and save them as text files for RAG ingestion.
"""
import os
import re
import time
from pathlib import Path
from html.parser import HTMLParser
import urllib.request
import ssl

CORPUS_DIR = "/workspace/corpus/buffett/shareholder_letters"
BASE_URL = "https://www.berkshirehathaway.com/letters/"

# SSL context for HTTPS
CTX = ssl.create_default_context()

class TextExtractor(HTMLParser):
    """Extract text content from HTML, stripping tags."""
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_tags = {'script', 'style', 'head', 'meta', 'link'}
        self.in_skip = False
    
    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.skip_tags:
            self.in_skip = True
        elif tag.lower() in ('br', 'p', 'div', 'h1', 'h2', 'h3', 'h4', 'tr'):
            self.text_parts.append('\n')
    
    def handle_endtag(self, tag):
        if tag.lower() in self.skip_tags:
            self.in_skip = False
        elif tag.lower() in ('p', 'div', 'h1', 'h2', 'h3', 'h4'):
            self.text_parts.append('\n\n')
    
    def handle_data(self, data):
        if not self.in_skip:
            self.text_parts.append(data)
    
    def get_text(self):
        text = ''.join(self.text_parts)
        # Clean up whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()


def download_letter(year: int) -> str | None:
    """Download and extract text from a shareholder letter."""
    # Try HTML format first (early years)
    url = f"{BASE_URL}{year}.html"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30, context=CTX) as response:
            html = response.read().decode('utf-8', errors='replace')
        
        extractor = TextExtractor()
        extractor.feed(html)
        text = extractor.get_text()
        
        if len(text) > 500:  # Minimum content check
            return text
    except Exception as e:
        print(f"  HTML fetch failed for {year}: {e}")
    
    # Try ltr.html format
    url = f"{BASE_URL}{year}ltr.html"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30, context=CTX) as response:
            html = response.read().decode('utf-8', errors='replace')
        
        extractor = TextExtractor()
        extractor.feed(html)
        text = extractor.get_text()
        
        if len(text) > 500:
            return text
    except Exception as e:
        print(f"  ltr.html fetch failed for {year}: {e}")
    
    return None


def main():
    os.makedirs(CORPUS_DIR, exist_ok=True)
    
    # Years to download (all available from berkshirehathaway.com)
    years = list(range(1977, 2025))  # 1977-2024
    
    print(f"📥 Downloading Berkshire Hathaway shareholder letters (1977-2024)")
    print(f"📂 Saving to: {CORPUS_DIR}")
    print()
    
    success_count = 0
    fail_count = 0
    
    for year in years:
        print(f"Downloading {year}...")
        text = download_letter(year)
        
        if text:
            filename = f"{year}_letter.txt"
            filepath = os.path.join(CORPUS_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"  ✅ Saved: {filename} ({len(text)} chars)")
            success_count += 1
        else:
            print(f"  ❌ Failed or too short")
            fail_count += 1
        
        # Be polite - don't hammer the server
        time.sleep(1)
    
    print(f"\n📊 Summary: {success_count} succeeded, {fail_count} failed")
    print(f"💾 Files saved to: {CORPUS_DIR}")


if __name__ == "__main__":
    main()
