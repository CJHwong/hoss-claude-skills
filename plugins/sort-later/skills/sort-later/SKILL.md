---
name: sort-later
description: Organize messy bookmarks into two clean outputs — markdown notes for articles (things to read) and browser-importable HTML for functional sites (things to use). Use this skill whenever a user mentions organizing bookmarks, sorting saved links, cleaning up browser exports, triaging a reading list, importing/exporting bookmarks, or dealing with a pile of URLs from any source. Also trigger when users mention Pocket, Raindrop, Instapaper, read-later lists, or browser bookmark exports.
---

# Sort Later

Take a user's unorganized bookmarks and saved links from any source and split them into two outputs:

1. **Markdown notes** — articles (things to READ): one `.md` file per article with scraped content, YAML frontmatter, tags, and a reading queue index
2. **Browser-importable HTML** — functional sites (things to USE): nested Netscape bookmark format that any browser can import

Dead links go to neither output.

## How This Works

The process is collaborative and iterative. You work through 8 phases with the user, pausing after each one so they can review and course-correct. Never blast through the whole pipeline silently.

Read `references/workflow.md` for the detailed phase-by-phase instructions. Here's the summary:

| Phase | What Happens | User Reviews |
|-------|-------------|--------------|
| 1. Understand Input | Figure out what the user gave you — any format | Confirm sources identified |
| 2. Parse & Deduplicate | Extract all URLs, fix missing titles | Check count, spot duplicates |
| 3. Check Links | HTTP check every URL, flag dead ones | Review dead link list |
| 4. Classify | Split into "article" vs "functional" buckets | Approve the split |
| 5. Categorize | Assign folder paths collaboratively | Iterate on taxonomy |
| 6. Scrape | Fetch article content as markdown | Spot-check quality |
| 7. Export | Generate `.md` notes + `.html` bookmark file | Check both outputs |
| 8. Verify | Full integrity audit — nothing missing | Approve before deleting old bookmarks |

## Key Decisions You Make (Not the User)

**Classification (Phase 4):** You read titles, URLs, and folder names and decide what's an article vs. what's functional. This is reasoning work — no external API calls needed. URL patterns get you 60-70%. Folder names and title context handle the rest. Pay extra attention to GitHub URLs — a tool repo is functional, a README tutorial is an article, a specific file depends on what the file is. Also factor in source context: a Pocket export will be almost all articles (that's what Pocket is for), while a browser export will be more mixed.

**Categorization (Phase 5):** You propose a folder taxonomy based on the user's actual data. Don't use a template. A photographer's bookmarks need different categories than a chef's. Start from original folder names, group by topic not source, and iterate with the user until they're happy with the structure. When splitting large topics, prefer 2-3 broad subcategories over 5-6 narrow ones — the user should be able to predict where a new bookmark would go without thinking hard.

## Key Decisions the User Makes (Not You)

- **Where to put the outputs** — ask where they want the markdown notes and the HTML file
- **Final taxonomy** — you propose, they approve and refine
- **Reading status mapping** — if they have "Read Later" or priority folders, ask how those map to `unread` / `actionable` / `read`
- **Overrides** — any classification or categorization they disagree with

## Output Formats

### Markdown Notes (Articles)

```markdown
---
url: "https://example.com/article"
title: "Article Title"
date_saved: 2024-03-15
source: browser-name
link_alive: true
reading_status: read
tags:
  - "topic-a"
  - "topic-b"
---

# Article Title

> [Original article](https://example.com/article) | Saved: 2024-03-15

---

{scraped content or fallback link}
```

Tags come from the category path and original folder — derived mechanically, not from an expensive tagging step.

Also generate:
- **Reading Queue** — all `unread` articles grouped by category
- **Followup Tasks** — all `actionable` articles

Never overwrite existing `.md` files — the user may have hand-edited them.

### Browser HTML (Functional)

Netscape bookmark format with nested `<DL>` blocks:

```html
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3>Folder Name</H3>
    <DL><p>
        <DT><A HREF="https://..." ADD_DATE="...">Site Title</A>
    </DL><p>
</DL><p>
```

Only alive links. Importable by every major browser.

## Principles

These aren't guidelines — they're load-bearing constraints learned from real usage:

1. **You are the categorizer.** Classification and categorization are your reasoning work. No external API calls needed.
2. **Each step is reviewable.** Pause after each phase. The user's mental model matters more than any algorithm.
3. **Intermediate data is disposable.** Use whatever working format you want (database, JSON, in-memory). The deliverables are the markdown notes and HTML file.
4. **Folder size matters.** 5-7 items per browser bookmark folder. 10-15 per markdown folder. Split anything over 20. Merge anything under 3. But don't over-split — 2-3 subcategories beats 5-6 tiny ones.
5. **Dead links are gone.** Never export them. They clutter outputs with things that can't be opened.
6. **Bookmarklets are real.** `javascript:` URLs are functional bookmarks, not garbage to filter.
7. **Preserve user content.** Never overwrite hand-edited notes.
8. **The taxonomy is the user's.** Propose categories from the data, but the user decides the final structure.
9. **Iterate fast.** Rough cut first, refine based on feedback. Three rounds of "split this folder" beats one hour of perfecting it silently.

## References

- `references/workflow.md` — Detailed phase-by-phase instructions with edge cases and gotchas
