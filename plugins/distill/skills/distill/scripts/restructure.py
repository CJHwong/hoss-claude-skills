#!/usr/bin/env python3
"""
Audit and restructure vault folders.
Identifies singletons, oversized folders, and overlapping names.
Can propose merges and apply them.

Usage:
    python3 restructure.py <vault-path> --audit          # Just show problems
    python3 restructure.py <vault-path> --propose         # Show problems + proposed merges
    python3 restructure.py <vault-path> --apply <plan>    # Apply a move plan (JSON file)
"""

import os
import json
import shutil
import argparse
from collections import Counter


def audit_vault(vault_path):
    """Count notes per folder, find singletons and overlaps."""
    folders = Counter()
    for root, dirs, files in os.walk(vault_path):
        md_files = [f for f in files if f.endswith('.md') and not f.startswith('_')]
        if md_files:
            rel = os.path.relpath(root, vault_path)
            if rel != '.':
                folders[rel] = len(md_files)

    singletons = sorted([f for f, c in folders.items() if c == 1])
    oversized = sorted([(f, c) for f, c in folders.items() if c > 30], key=lambda x: -x[1])

    # Find overlapping folder names
    name_parts = {}
    for folder in folders:
        parts = set(os.path.basename(folder).replace('-', ' ').split())
        name_parts[folder] = parts

    overlaps = []
    folder_list = sorted(folders.keys())
    for i, a in enumerate(folder_list):
        for b in folder_list[i+1:]:
            shared = name_parts[a] & name_parts[b]
            meaningful = {w for w in shared if w not in ('and', 'the', 'of', 'in', 'a')}
            if meaningful:
                overlaps.append((a, folders[a], b, folders[b], meaningful))

    return folders, singletons, oversized, overlaps


def print_audit(folders, singletons, oversized, overlaps):
    total_notes = sum(folders.values())
    print(f"=== Vault Audit: {total_notes} notes in {len(folders)} folders ===\n")

    print("By size:")
    for folder, count in sorted(folders.items(), key=lambda x: -x[1]):
        flag = ""
        if count == 1: flag = " [singleton]"
        if count > 30: flag = " [oversized]"
        print(f"  {count:3d}  {folder}/{flag}")

    if singletons:
        print(f"\nSingletons ({len(singletons)}):")
        for s in singletons:
            print(f"  - {s}/")

    if oversized:
        print(f"\nOversized:")
        for f, c in oversized:
            print(f"  - {f}/ ({c} notes)")

    if overlaps:
        significant = [(a, ac, b, bc, s) for a, ac, b, bc, s in overlaps if ac + bc >= 4]
        if significant:
            print(f"\nSignificant overlaps:")
            for a, ac, b, bc, shared in significant[:20]:
                print(f"  - {a}/ ({ac}) vs {b}/ ({bc})")


def propose_merges(folders, singletons):
    """Propose merging singletons into nearby parent folders."""
    proposals = []

    for singleton in singletons:
        base_words = set(os.path.basename(singleton).replace('-', ' ').split())

        best_match = None
        best_score = 0
        for folder, count in folders.items():
            if folder == singleton or count <= 1:
                continue
            folder_words = set(os.path.basename(folder).replace('-', ' ').split())
            shared = base_words & folder_words
            meaningful = {w for w in shared if w not in ('and', 'the', 'of', 'in', 'a')}
            if len(meaningful) > best_score:
                best_score = len(meaningful)
                best_match = folder

        if best_match and best_score > 0:
            proposals.append({
                "from": singleton,
                "to": best_match,
                "reason": f"singleton, shares terms with {best_match}/ ({folders[best_match]} notes)"
            })
        else:
            proposals.append({
                "from": singleton,
                "to": None,
                "reason": "singleton, no obvious merge target"
            })

    return proposals


def apply_plan(vault_path, plan_path):
    """Apply a move plan from JSON file."""
    with open(plan_path) as f:
        moves = json.load(f)

    moved = 0
    for move in moves:
        src_rel = move["from"]
        dst_rel = move.get("to")
        if not dst_rel:
            continue

        src = os.path.join(vault_path, src_rel)
        dst = os.path.join(vault_path, dst_rel)

        if not os.path.exists(src):
            print(f"  Skip: {src_rel}/ not found")
            continue

        os.makedirs(dst, exist_ok=True)
        for fname in os.listdir(src):
            if fname.endswith('.md'):
                src_file = os.path.join(src, fname)
                dst_file = os.path.join(dst, fname)
                if not os.path.exists(dst_file):
                    shutil.move(src_file, dst_file)
                    moved += 1

        try:
            os.rmdir(src)
        except OSError:
            pass

    # Clean empty dirs recursively
    for root, dirs, files in os.walk(vault_path, topdown=False):
        for d in dirs:
            try:
                os.rmdir(os.path.join(root, d))
            except OSError:
                pass

    print(f"Moved {moved} files")


def main():
    parser = argparse.ArgumentParser(description="Audit and restructure vault folders")
    parser.add_argument("vault_path", help="Path to the Obsidian vault")
    parser.add_argument("--audit", action="store_true", help="Show problems only")
    parser.add_argument("--propose", action="store_true", help="Show problems + proposed merges")
    parser.add_argument("--apply", metavar="PLAN", help="Apply a move plan (JSON file)")
    args = parser.parse_args()

    if args.apply:
        apply_plan(args.vault_path, args.apply)
        return

    folders, singletons, oversized, overlaps = audit_vault(args.vault_path)
    print_audit(folders, singletons, oversized, overlaps)

    if args.propose and singletons:
        proposals = propose_merges(folders, singletons)
        print(f"\n=== Proposed Merges ===\n")
        for p in proposals:
            if p["to"]:
                print(f"  {p['from']}/ -> {p['to']}/  ({p['reason']})")
            else:
                print(f"  {p['from']}/  [no match]  ({p['reason']})")

        plan_path = os.path.join(args.vault_path, "_restructure-plan.json")
        actionable = [p for p in proposals if p["to"]]
        with open(plan_path, 'w') as f:
            json.dump(actionable, f, indent=2)
        print(f"\nPlan saved: {plan_path}")
        print(f"Review, then: python3 restructure.py {args.vault_path} --apply {plan_path}")


if __name__ == "__main__":
    main()
