# Sort Later — Detailed Workflow

Phase-by-phase instructions with edge cases and gotchas. Read this when executing the skill.

## Phase 1: Understand the Input

The user may give you anything — browser exports (JSON, HTML), read-later service CSVs, plain text URL lists, markdown notes, or something unrecognizable.

**Your job is to figure out what it is and parse it.** Don't demand a specific format.

For each file, identify:
- What format is it? (JSON bookmark tree, CSV, HTML bookmark file, plain URLs, markdown notes, etc.)
- What fields are available? (url, title, date, folder/tag, content)
- Are there folder structures or tags that carry meaning?

If you can't determine what a file is, or there's no input:
- Ask what bookmark sources they want to organize
- Ask them to export and provide the files
- Give specific export instructions for their browser or service if they need help

## Phase 2: Parse & Deduplicate

Extract every bookmark into a working data store. Use whatever intermediate format makes sense — database, JSON, in-memory. This is throwaway pipeline data.

For each bookmark, capture: **url, title, date_saved, source** (where it came from), **original_folder** (folder/tag from the source).

### Missing Titles

Many export formats have bookmarks where the title is just the raw URL, or empty. This is common in Pocket exports, plain URL lists, and older browser exports. When you encounter these:

1. **During parsing**: Flag them but don't block on it. Use the URL as a temporary title.
2. **During scraping (Phase 6)**: Fetch the page's `<title>` tag as part of scraping. Update the bookmark's title with what the page actually says.
3. **If scraping is skipped or fails**: Derive a readable title from the URL path. `/blog/2024/async-python-guide` becomes "Async Python Guide". Strip file extensions, replace hyphens/underscores with spaces, title-case it.

A note titled "http://example.com/blog/some-post" is a bad reading experience. Fix it when you can.

### URL Normalization

- Strip `www.`, trailing slashes, lowercase hostname
- **Preserve query params** (`?id=...`, `?v=...`) — they distinguish different pages on the same domain
- Strip URL fragments (`#...`) UNLESS the domain uses them meaningfully (e.g., spreadsheet apps where fragments distinguish different tabs/sheets)
- `javascript:` URLs are valid bookmarklets — keep them
- Browser-internal URLs (`place:`, `chrome://`, `about:`) — skip them

### Gotcha: Query Params

This is the single most common deduplication bug. If you strip query params, every link to a news aggregator collapses to the same URL. Every video link becomes one video. Preserve them.

## Phase 3: Check Links

HTTP HEAD request every URL. Fall back to GET on failure. Run concurrently for speed.

### False Positives

Some sites block automated requests and return error codes despite being alive:
- **News aggregators** often return 403/405 to HEAD requests
- **Social media sites** may return 403 or redirect to login
- **CDNs and paywalled sites** often reject bot-like requests
- **`javascript:` bookmarklets** — always alive, don't HTTP-check them

**When in doubt, mark it alive.** It's better to include a working link than to wrongly kill it. The user can always delete a bookmark; they can't recover one you silently removed.

## Phase 4: Classify — Article vs. Functional

Every bookmark gets a bucket: **article** (something you read) or **functional** (something you use).

You do this yourself by reading the data. No external API calls needed.

### Signals to Use

- **URL patterns:** `javascript:` → functional. Online productivity tools (docs, sheets, project management) → functional. `localhost`, internal company domains → functional. Blog posts, news sites, tutorial pages → article.
- **Original folder names:** Strong signal. A folder called "Tools" or "Work Apps" → functional. "Articles" or "Read Later" → article.
- **Title + URL together:** A blog URL with a descriptive essay title → article. A URL to a dashboard or app → functional.
- **GitHub URLs need extra attention:** A GitHub repo that's a tool or library (something you `git clone` and use) → functional. A GitHub repo that's primarily a README/guide/tutorial (something you read) → article. A specific file in a repo (like a blog post, a YAML config, a code example) → judge by what the file actually is, not by the fact that it's on GitHub. Don't blindly classify all GitHub URLs the same way.
- **Source context matters:** If the input is from a read-later service (Pocket, Instapaper, Raindrop), expect almost everything to be articles — that's what those services are for. If it's a browser export, expect a more even mix. This doesn't change your classification logic, but it sets expectations for what the distribution should look like. A 97/3 article/functional split from Pocket is normal; the same split from a browser export would be suspicious.

### Process

1. Apply deterministic URL-pattern rules first (covers ~60-70%)
2. For the rest, group by original folder and classify folder-by-folder. You can reason about hundreds at once.
3. Show the user the breakdown
4. Let them review and override before proceeding

## Phase 5: Categorize into Folders

This is the most important phase. Assign each bookmark a **category** — a folder path for the output.

You do this yourself. Read every bookmark's title, URL, and original folder. Group them into logical categories through pure reasoning.

### Strategy

1. **Start from original folder names** — they reflect how the user thinks
2. **Group by topic, not source** — all bookmarks on the same subject go together regardless of which browser or service they came from
3. **Resolve ambiguity with titles and URLs** — a bookmark with a clear topic in a vague folder like "General" should move to the right topic folder
4. **Propose a taxonomy to the user** — show top-level areas and subfolders before applying. The taxonomy must emerge from the user's actual data. Every person's collection is different.

### Iteration Loop

1. Generate initial categories, show distribution (items per folder)
2. User says "too big" → split using title/URL signals
3. User says "too small" → merge into parent or sibling
4. User says "wrong place" → move it, check if siblings need moving too
5. Repeat until satisfied

### Folder Size Guidelines

| Context | Target Size | Why |
|---------|------------|-----|
| Browser bookmarks (functional) | 5-7 per leaf folder | Visual scanning in a dropdown menu |
| Markdown notes (articles) | 10-15 per folder | Search and tags compensate |
| Over 20 in one folder | Propose a split | Too many to scan |
| Under 3 in a folder | Merge upward | Fragment, not a real category |

### Gotcha: Over-Splitting

When a topic has 25-30 items, it's tempting to split it into 5-6 tiny subcategories. Resist this. Splitting "python" (29 items) into 6 folders of 4-7 items each creates cognitive overhead — the user now has to remember which subfolder to look in. A 2-3 way split is almost always better:

- **Good:** `python/core` (internals + stdlib), `python/patterns` (design patterns + best practices), `python/applied` (specific libraries + use cases)
- **Bad:** `python/internals`, `python/patterns`, `python/stdlib`, `python/applied`, `python/ecosystem`, `python/general` — too many buckets, the distinctions blur

The test is: can the user predict which subfolder a new bookmark would go into without thinking hard? If the categories require domain expertise to distinguish, you've split too fine.

### Gotcha: Reading Status from Source Metadata

Different sources encode reading intent differently. Check for these before asking the user:
- **Pocket**: `status` field — "unread" maps to `unread`, "archive" maps to `read`
- **Instapaper**: "Archive" folder → `read`, everything else → `unread`
- **Browser exports**: "Read Later" or "Reading List" folders → `unread`, toolbar/bookmarks bar → consider `actionable`
- **Raindrop**: has explicit "unsorted" and collection-based organization

Map what you can from the data, then confirm with the user. "I see Pocket marks 164 as unread and 26 as archived. I'll map those to `unread` and `read`. Does that match how you use Pocket?"

## Phase 6: Scrape Article Content

For alive articles, scrape the page content and convert to markdown.

- Run concurrently but respect per-domain rate limits
- Truncate excessively long content (50K+ chars)
- Failures happen — mark them and move on. A note with just metadata and a link is still useful.

## Phase 7: Export

### Markdown Notes (Articles)

Each article becomes a `.md` file in its category folder with YAML frontmatter:

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

**Tags** come from category path and original folder. If the bookmark is in a category about a specific topic, derive tags from that name. Keep it mechanical and simple.

**Reading status** — if the user's bookmarks carry reading intent (e.g., "Read Later" folders, priority folders, toolbar pins), ask how they map to:

| Value | Meaning |
|---|---|
| `unread` | Saved to read but hasn't yet |
| `actionable` | Read it, has followup tasks |
| `read` | Already consumed, kept for reference |

Don't assume the mapping — ask.

**Also generate:**
- **Reading Queue** — all `unread` articles grouped by category
- **Followup Tasks** — all `actionable` articles (if any)

**Never overwrite existing `.md` files** — the user may have hand-edited them.

Ask the user where they want the notes.

### Browser HTML (Functional)

Netscape bookmark format with nested `<DL>` blocks so folders actually nest on import:

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

Only alive links. This format is universally importable by all major browsers.

## Phase 8: Verify

Before the user deletes their old bookmarks, run a full integrity audit:

1. Every URL from the original input is accounted for
2. Every alive article has a markdown note
3. Every alive functional bookmark is in the HTML
4. Zero dead links in either output
5. No URLs fell through the cracks

Report clearly:
```
Original URLs:      {total}
In notes:           {n} articles (alive)
In HTML:            {n} functional (alive)
Dead (excluded):    {n}
Missing:            0
```

If anything is missing, investigate and fix before giving the all-clear. The user is about to delete their old bookmarks based on your audit — don't let them lose data.
