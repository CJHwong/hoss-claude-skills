# Browser Database Schemas

How to read browsing history and bookmarks from different browsers. Each browser stores data in SQLite but with different schemas and profile paths.

## Browser Detection

Check these paths in order to find installed browsers:

| Browser | macOS Profile Path | DB File |
|---------|-------------------|---------|
| Zen | `~/Library/Application Support/zen/Profiles/*.Default*/` | `places.sqlite` |
| Firefox | `~/Library/Application Support/Firefox/Profiles/*.default-release*/` | `places.sqlite` |
| Chrome | `~/Library/Application Support/Google/Chrome/Default/` | `History` |
| Arc | `~/Library/Application Support/Arc/User Data/Default/` | `History` |
| Brave | `~/Library/Application Support/BraveSoftware/Brave-Browser/Default/` | `History` |
| Edge | `~/Library/Application Support/Microsoft Edge/Default/` | `History` |
| Safari | `~/Library/Safari/` | `History.db` |

On Linux, replace `~/Library/Application Support/` with `~/.config/` for Chromium browsers, `~/.mozilla/firefox/` for Firefox, `~/.zen/` for Zen.

## WAL Copy Strategy (all browsers)

All browser SQLite databases are locked while the browser runs. Copy before reading:

**Firefox/Zen:** Copy `places.sqlite`, `places.sqlite-wal`, `places.sqlite-shm`
**Chromium:** Copy `History`, `History-journal` (if exists)
**Safari:** Copy `History.db`, `History.db-wal`, `History.db-shm`

Copy all files in rapid succession to a temp directory. Query the copy.

---

## Firefox / Zen Schema

DB file: `places.sqlite`

### moz_places (URL registry)

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `url` | TEXT | Full URL |
| `title` | TEXT | Page title (may be NULL) |
| `visit_count` | INTEGER | Total visits |
| `frecency` | INTEGER | Frequency+recency score |
| `last_visit_date` | INTEGER | **Microseconds** since Unix epoch |
| `hidden` | INTEGER | 1 = redirect/frame. Skip these. |

### moz_bookmarks

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `type` | INTEGER | 1 = bookmark, 2 = folder, 3 = separator |
| `fk` | INTEGER | FK to `moz_places.id` |
| `parent` | INTEGER | FK to parent folder |
| `title` | TEXT | Bookmark name |
| `dateAdded` | INTEGER | **Microseconds** since epoch |

### moz_historyvisits

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `place_id` | INTEGER | FK to `moz_places.id` |
| `visit_date` | INTEGER | **Microseconds** since epoch |
| `visit_type` | INTEGER | 1=link, 2=typed, 3=bookmark, 4=embed, 5=redirect_perm, 6=redirect_temp, 7=download |

### Timestamps

**All Firefox/Zen timestamps are microseconds since Unix epoch.** `timestamp / 1_000_000 = Unix seconds`.

### Key Queries

```sql
-- All bookmarks (incremental by dateAdded)
SELECT b.id, COALESCE(b.title, p.title, p.url) as title, p.url, b.dateAdded,
       (SELECT pb.title FROM moz_bookmarks pb WHERE pb.id = b.parent) as folder
FROM moz_bookmarks b JOIN moz_places p ON b.fk = p.id
WHERE b.type = 1 AND b.dateAdded > :last_dateAdded
ORDER BY b.dateAdded ASC;

-- History (incremental by last_visit_date)
SELECT p.id, p.url, p.title, p.visit_count, p.frecency, p.last_visit_date
FROM moz_places p
WHERE p.last_visit_date > :last_timestamp
  AND p.visit_count >= 1 AND p.hidden = 0 AND p.url LIKE 'http%'
ORDER BY p.last_visit_date ASC;
```

### Zen-Specific

Zen adds `zen_workspaces` and `zen_pins` tables. The core `moz_*` tables are identical to Firefox. Ignore Zen-specific tables.

---

## Chromium Schema (Chrome, Arc, Brave, Edge)

DB file: `History`

### urls

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `url` | TEXT | Full URL |
| `title` | TEXT | Page title |
| `visit_count` | INTEGER | Total visits |
| `last_visit_time` | INTEGER | **Microseconds** since Jan 1, 1601 (Windows epoch) |
| `hidden` | INTEGER | 0 = visible |

### visits

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `url` | INTEGER | FK to `urls.id` |
| `visit_time` | INTEGER | **Microseconds** since Jan 1, 1601 |
| `transition` | INTEGER | Bitfield. `transition & 0xFF` for core type: 0=link, 1=typed, 2=auto_bookmark, 3=auto_subframe, 5=generated, 6=start_page, 8=keyword |

### Timestamps

**Chromium uses microseconds since January 1, 1601 (Windows FILETIME epoch).** To convert to Unix seconds:

```
(chromium_timestamp - 11644473600000000) / 1000000 = Unix seconds
```

The magic number `11644473600000000` is the microsecond difference between 1601-01-01 and 1970-01-01.

### Key Queries

```sql
-- History (incremental)
SELECT u.id, u.url, u.title, u.visit_count, u.last_visit_time
FROM urls u
WHERE u.last_visit_time > :last_visit_time
  AND u.visit_count >= 1 AND u.hidden = 0 AND u.url LIKE 'http%'
ORDER BY u.last_visit_time ASC;
```

### Bookmarks

Chromium stores bookmarks in a JSON file, not SQLite:
- Path: `{profile}/Bookmarks`
- Format: JSON with `roots.bookmark_bar`, `roots.other`, `roots.synced` trees
- Each entry: `{"name": "...", "url": "...", "date_added": "...", "type": "url"}`
- `date_added` is microseconds since Jan 1, 1601 (same epoch as History DB)

```python
import json
with open(f"{profile}/Bookmarks") as f:
    data = json.load(f)
# Recursively walk roots.bookmark_bar.children, roots.other.children
```

---

## Safari Schema

DB file: `History.db`

### history_items

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `url` | TEXT | Full URL |
| `visit_count` | INTEGER | Total visits |

### history_visits

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key |
| `history_item` | INTEGER | FK to `history_items.id` |
| `visit_time` | REAL | **Seconds** since Jan 1, 2001 (Core Data epoch) |
| `title` | TEXT | Page title at visit time |

### Timestamps

**Safari uses seconds (float) since January 1, 2001 (Core Data / NSDate epoch).** To convert to Unix seconds:

```
safari_timestamp + 978307200 = Unix seconds
```

### Key Queries

```sql
SELECT hi.id, hi.url, hv.title, hi.visit_count, hv.visit_time
FROM history_items hi
JOIN history_visits hv ON hi.id = hv.history_item
WHERE hv.visit_time > :last_visit_time
ORDER BY hv.visit_time ASC;
```

### Bookmarks

Safari bookmarks are in `~/Library/Safari/Bookmarks.plist` (binary plist format). Use `plutil -convert json` to read:

```bash
plutil -convert json -o /tmp/bookmarks.json ~/Library/Safari/Bookmarks.plist
```

---

## File-Based Sources (no DB)

### Netscape Bookmark HTML

Standard export format from all browsers. Parse `<DT><A HREF="...">Title</A>` within `<DL>` folder trees.

### Pocket Export

CSV with columns: `title`, `url`, `time_added`, `tags`, `status` (unread/archived).

### Raindrop Export

CSV with columns: `title`, `url`, `folder`, `tags`, `created`, `note`.

### Plain URL List

One URL per line. Title will be fetched during scraping from `<title>` tag.

---

## Normalized Output

Regardless of source, Phase 1 produces a JSON array:

```json
[
  {
    "url": "https://...",
    "title": "Page Title",
    "source": "zen-bookmark",
    "date": "2026-04-01",
    "folder": "Engineering"
  }
]
```

Source values: `{browser}-bookmark`, `{browser}-history`, `pocket-export`, `raindrop-export`, `url-list`, `manual`.

Everything after Phase 1 is source-agnostic.
