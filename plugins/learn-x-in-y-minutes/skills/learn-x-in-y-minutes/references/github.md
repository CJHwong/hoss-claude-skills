# GitHub Repository Analysis

Reference for analyzing GitHub repositories using `gh` CLI.

## Fetch Repository Info

```bash
# Get basic repo info as JSON
gh repo view {owner}/{repo} --json name,description,primaryLanguage,stargazerCount,url,homepageUrl,licenseInfo

# Get topics
gh repo view {owner}/{repo} --json repositoryTopics

# Get languages breakdown
gh api repos/{owner}/{repo}/languages
```

## Fetch Repository Structure

```bash
# Get root contents
gh api repos/{owner}/{repo}/contents

# Get specific directory
gh api repos/{owner}/{repo}/contents/{path}

# Get file content (raw)
gh api repos/{owner}/{repo}/contents/{path} --jq '.content' | base64 -d

# Or use raw URL
gh api /repos/{owner}/{repo}/readme --jq '.content' | base64 -d
```

## Fetch Key Files

```bash
# README
gh api repos/{owner}/{repo}/readme

# Package manifests
gh api repos/{owner}/{repo}/contents/package.json
gh api repos/{owner}/{repo}/contents/pyproject.toml
gh api repos/{owner}/{repo}/contents/Cargo.toml
gh api repos/{owner}/{repo}/contents/go.mod

# Main entry points (try common ones)
gh api repos/{owner}/{repo}/contents/main.py
gh api repos/{owner}/{repo}/contents/index.js
gh api repos/{owner}/{repo}/contents/src/main.rs
gh api repos/{owner}/{repo}/contents/cmd/main.go
```

## Parse GitHub URL

From a URL like `https://github.com/owner/repo`:
- Owner: `owner`
- Repo: `repo`

```bash
# Example extraction
echo "https://github.com/anthropics/anthropic-sdk-python" | sed 's|https://github.com/||' | cut -d'/' -f1,2
# Output: anthropics/anthropic-sdk-python
```

## Detect Project Type

Check for indicators:

**Web Framework:**
- `package.json` with `express`, `fastify`, `hapi`, `koa`
- `requirements.txt` with `fastapi`, `flask`, `django`, `starlette`
- `Cargo.toml` with `actix-web`, `rocket`, `axum`
- `go.mod` with `gin`, `echo`, `fiber`

**Library:**
- `pyproject.toml` with `[project]` section
- `package.json` without `main` pointing to CLI
- `Cargo.toml` with `[lib]` section

**CLI Tool:**
- `package.json` with `bin` field
- `pyproject.toml` with `scripts` entry
- Files in `bin/` or `cmd/` directories
- `main.rs` or `main.go` pattern

**Data Science:**
- `requirements.txt` with `pandas`, `numpy`, `scikit-learn`, `torch`
- `.ipynb` files (Jupyter notebooks)
- `data/` directory

## Language Detection

From GitHub API:
```json
{
  "primaryLanguage": {
    "name": "Python",
    "color": "#3572A5"
  }
}
```

From file extensions in contents:
- `.py` → Python
- `.js` → JavaScript
- `.ts` → TypeScript
- `.go` → Go
- `.rs` → Rust
- `.java` → Java
- `.rb` → Ruby
- `.php` → PHP