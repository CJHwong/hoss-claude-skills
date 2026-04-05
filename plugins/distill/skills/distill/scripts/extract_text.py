#!/usr/bin/env python3
"""
Extract text from scraped HTML files and prepare classification batches.
No LLM tokens. Pure Python HTML parsing.

Usage:
    python3 extract_text.py <scrape-results.json> <candidates.json> [--batch-size 20] [--min-text 200] [--preview-chars 3000]

Input:
    scrape-results.json: output from scrape.py (status per URL)
    candidates.json: original candidates with title metadata

Output:
    classify-batch-{N}.json files in the same directory as scrape-results.json
    Each batch has up to 20 articles with: url, title, text_preview, full_text
"""

import json
import os
import argparse
from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    SKIP_TAGS = {'script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript'}

    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self.skip = True

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            stripped = data.strip()
            if stripped:
                self.text.append(stripped)

    def get_text(self):
        return '\n'.join(self.text)


def html_to_text(html, max_chars=15000):
    try:
        extractor = TextExtractor()
        extractor.feed(html)
        return extractor.get_text()[:max_chars]
    except Exception:
        return html[:max_chars]


def main():
    parser = argparse.ArgumentParser(description="Extract text from scraped HTML")
    parser.add_argument("scrape_results", help="scrape-results.json from scrape.py")
    parser.add_argument("candidates", help="Original candidates JSON with title metadata")
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--min-text", type=int, default=200)
    parser.add_argument("--preview-chars", type=int, default=3000)
    args = parser.parse_args()

    with open(args.scrape_results) as f:
        scrape_results = json.load(f)

    with open(args.candidates) as f:
        candidates = {c["url"]: c for c in json.load(f)}

    classifiable = []
    for sr in scrape_results:
        if sr["status"] not in ("ok", "cached"):
            continue

        filepath = sr.get("file", "")
        if not filepath or not os.path.exists(filepath):
            continue

        with open(filepath, 'r', errors='replace') as f:
            raw = f.read()

        text = html_to_text(raw)
        if len(text) < args.min_text:
            continue

        candidate = candidates.get(sr["url"], {})
        classifiable.append({
            "url": sr["url"],
            "title": candidate.get("title", ""),
            "text_preview": text[:args.preview_chars],
            "full_text": text,
        })

    output_dir = os.path.dirname(args.scrape_results)

    for i in range(0, len(classifiable), args.batch_size):
        batch = classifiable[i:i + args.batch_size]
        batch_num = i // args.batch_size + 1
        batch_path = os.path.join(output_dir, f"classify-batch-{batch_num}.json")
        with open(batch_path, 'w') as f:
            json.dump(batch, f)

    total_batches = (len(classifiable) + args.batch_size - 1) // args.batch_size
    print(f"Classifiable articles: {len(classifiable)}")
    print(f"Batches written: {total_batches}")
    print(f"Output: {output_dir}/classify-batch-{{1..{total_batches}}}.json")


if __name__ == "__main__":
    main()
