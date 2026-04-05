---
category: tool
name: Git
contributors:
    - ["Jake Prather", "http://github.com/JakeHP"]
    - ["Bruno Volcov", "http://github.com/volcov"]
filename: LearnGit.txt
---

Git is a distributed version control and source code management system.
It works through snapshots of your project, providing functionality to version
and manage your source code.

## Versioning Concepts

### What is version control?

Version control records changes to files over time so you can recall specific
versions later.

### Why Use Git?

* Works offline.
* Branching and merging are fast and cheap.
* Every developer has a full history of the repository.

## Git Architecture

### Repository

A set of files, directories, historical records, commits, and heads. Contains
a `.git/` directory (config, logs, refs) and a **working tree** (the files
you actually edit).

### Staging Area (Index)

A layer between your working tree and the repository. You explicitly stage
changes before committing — giving you fine-grained control over what goes
into each snapshot.

### Commits, Branches, Tags

* **Commit** — a snapshot of staged changes. Has an author, timestamp, and
  pointer to its parent.
* **Branch** — a movable pointer to the latest commit on a line of development.
* **Tag** — a fixed pointer to a specific commit, used for release markers.
* **HEAD** — points to the currently checked-out branch or commit.

## Commands

### init / clone

```bash
# Create an empty repo in the current directory
git init

# Clone an existing remote repository
git clone https://github.com/user/repo.git
git clone https://github.com/user/repo.git my-local-name  # custom folder name
```

### config

```bash
# Set global identity (stored in ~/.gitconfig)
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"

# Set repo-local config (overrides global)
git config user.email "work@company.com"

# View all config
git config --list
```

### status / log

```bash
# Show working tree status (staged, unstaged, untracked)
git status

# Show commit history
git log
git log --oneline --graph --decorate  # compact visual graph
git log -p                             # include diffs
git log --author="Alice"              # filter by author
```

### add / commit

```bash
# Stage a specific file
git add file.txt

# Stage all changes in the current directory
git add .

# Stage patches interactively (choose hunks)
git add -p

# Commit staged changes
git commit -m "Short imperative summary"

# Stage tracked files and commit in one step (skips new untracked files)
git commit -am "Fix typo in README"
```

### branch / checkout / merge

```bash
# List branches (* marks current)
git branch

# Create a new branch
git branch feature/my-feature

# Switch to a branch
git checkout feature/my-feature
git switch feature/my-feature     # modern alternative

# Create and switch in one step
git checkout -b feature/my-feature
git switch -c feature/my-feature  # modern alternative

# Merge a branch into the current branch
git merge feature/my-feature

# Delete a merged branch
git branch -d feature/my-feature
```

### remote / push / pull

```bash
# List remotes
git remote -v

# Add a remote
git remote add origin https://github.com/user/repo.git

# Push a branch to a remote
git push origin main
git push -u origin feature/my-feature  # set upstream tracking

# Pull (fetch + merge) from the tracked remote branch
git pull

# Fetch without merging
git fetch origin
```

### stash

```bash
# Save dirty working tree without committing
git stash

# List stashes
git stash list

# Apply the most recent stash and keep it in the stash list
git stash apply

# Apply and remove the most recent stash
git stash pop
```

<!-- Source: https://github.com/adambard/learnxinyminutes-docs/blob/master/git.md (truncated for reference) -->
