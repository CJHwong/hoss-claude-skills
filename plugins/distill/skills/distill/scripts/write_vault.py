#!/usr/bin/env python3
"""
Write classification results to the Obsidian vault.
Merges multiple result JSON files, deduplicates, and writes insight notes.

Usage:
    python3 write_vault.py <vault-path> <results-json> [<results-json> ...]

Input: One or more JSON files, each an array of:
    {"url", "title", "topic_folder", "filename", "note_content"}

Output: Markdown files written to vault/{topic_folder}/{filename}
        Never overwrites existing files.
"""

import json
import os
import sys
import re
from urllib.parse import urlparse


def get_vault_urls(vault_path):
    """Get all URLs already in the vault from frontmatter."""
    urls = set()
    for root, dirs, files in os.walk(vault_path):
        for fname in files:
            if not fname.endswith('.md') or fname.startswith('_'):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath) as f:
                content = f.read(2000)
            match = re.search(r'^url:\s*["\']?(https?://[^\s"\']+)', content, re.MULTILINE)
            if match:
                parsed = urlparse(match.group(1).strip().rstrip('/'))
                urls.add((parsed.netloc.replace('www.', '') + parsed.path.rstrip('/')).lower())
    return urls


def normalize_url(url):
    parsed = urlparse(url)
    return (parsed.netloc.replace('www.', '') + parsed.path.rstrip('/')).lower()


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <vault-path> <results.json> [results.json ...]")
        sys.exit(1)

    vault_path = sys.argv[1]
    result_files = sys.argv[2:]

    # Load existing vault URLs
    existing = get_vault_urls(vault_path)
    print(f"Existing vault notes: {len(existing)}")

    # Load and merge all results
    all_insights = []
    for rf in result_files:
        if not os.path.exists(rf):
            print(f"Warning: {rf} not found, skipping")
            continue
        with open(rf) as f:
            data = json.load(f)
        print(f"  {os.path.basename(rf)}: {len(data)} insights")
        all_insights.extend(data)

    # Deduplicate
    seen = set()
    unique = []
    for item in all_insights:
        norm = normalize_url(item.get("url", ""))
        if norm not in seen and norm not in existing:
            seen.add(norm)
            unique.append(item)

    print(f"Total after dedup: {len(unique)} new insights")

    # Write to vault
    written = 0
    skipped = 0
    for item in unique:
        topic = item.get("topic_folder", "uncategorized")
        filename = item.get("filename", "untitled.md")
        content = item.get("note_content", "")

        if not content:
            skipped += 1
            continue

        topic_dir = os.path.join(vault_path, topic)
        os.makedirs(topic_dir, exist_ok=True)

        filepath = os.path.join(topic_dir, filename)
        if os.path.exists(filepath):
            skipped += 1
            continue

        with open(filepath, 'w') as f:
            f.write(content)
        written += 1

    print(f"Written: {written}")
    print(f"Skipped: {skipped}")

    # Count total
    total = sum(
        1 for r, d, fs in os.walk(vault_path)
        for f in fs if f.endswith('.md') and not f.startswith('_')
    )
    print(f"Total vault notes: {total}")


if __name__ == "__main__":
    main()
