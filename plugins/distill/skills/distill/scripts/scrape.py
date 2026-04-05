#!/usr/bin/env python3
"""
Scrape URLs with parallel curl workers.
No LLM tokens. No WebFetch. Just HTTP requests.

Usage:
    python3 scrape.py <candidates.json> [--output-dir /tmp/scraped] [--workers 20] [--timeout 10]

Input: JSON array of objects with at least {"url": "..."}
Output: One file per URL in output-dir, named by MD5 hash of URL.
        Also writes scrape-results.json with status of each URL.
"""

import json
import subprocess
import os
import hashlib
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed


def scrape_url(url, output_dir, timeout):
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    outfile = os.path.join(output_dir, f"{url_hash}.txt")

    # Skip if already scraped
    if os.path.exists(outfile) and os.path.getsize(outfile) > 100:
        return {"url": url, "status": "cached", "file": outfile}

    try:
        result = subprocess.run(
            ["curl", "-sL", f"-m{timeout}", "-A", "Mozilla/5.0",
             "-o", outfile, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        code = result.stdout.strip()
        size = os.path.getsize(outfile) if os.path.exists(outfile) else 0

        if code in ("200", "301", "302") and size > 500:
            # Truncate to 50K
            if size > 50000:
                with open(outfile, 'r', errors='replace') as f:
                    content = f.read(50000)
                with open(outfile, 'w') as f:
                    f.write(content)
            return {"url": url, "status": "ok", "code": code, "size": size, "file": outfile}
        else:
            if os.path.exists(outfile):
                os.remove(outfile)
            return {"url": url, "status": "failed", "code": code, "size": size}
    except Exception as e:
        if os.path.exists(outfile):
            os.remove(outfile)
        return {"url": url, "status": "error", "error": str(e)[:80]}


def main():
    parser = argparse.ArgumentParser(description="Scrape URLs with parallel curl")
    parser.add_argument("candidates", help="JSON file with URL candidates")
    parser.add_argument("--output-dir", default="/tmp/distill-workdir/scraped")
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--timeout", type=int, default=10)
    args = parser.parse_args()

    with open(args.candidates) as f:
        candidates = json.load(f)

    os.makedirs(args.output_dir, exist_ok=True)

    urls = [c["url"] for c in candidates if "url" in c]
    print(f"Scraping {len(urls)} URLs with {args.workers} workers, {args.timeout}s timeout...")

    results = []
    ok = failed = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(scrape_url, url, args.output_dir, args.timeout): url for url in urls}
        for future in as_completed(futures):
            r = future.result()
            results.append(r)
            if r["status"] in ("ok", "cached"):
                ok += 1
            else:
                failed += 1
            total = ok + failed
            if total % 100 == 0:
                print(f"  {total}/{len(urls)} ({ok} ok, {failed} failed)")

    print(f"\nDone: {ok} ok, {failed} failed")

    results_path = os.path.join(os.path.dirname(args.output_dir), "scrape-results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results: {results_path}")


if __name__ == "__main__":
    main()
