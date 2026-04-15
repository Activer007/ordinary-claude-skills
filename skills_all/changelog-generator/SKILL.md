---
name: changelog-generator
description: "Generate a user-facing changelog or release notes from git commit history. Use when updating CHANGELOG.md, preparing version notes, writing a release summary, or documenting what changed between tags or dates. Analyzes commits, categorizes by type, filters noise, and rewrites technical messages into customer-friendly language."
---

# Changelog Generator

Generate user-facing changelogs from git commit history by categorizing changes, filtering internal noise, and rewriting technical commits into clear release notes.

## Workflow

Follow these steps sequentially to produce a changelog.

### Step 1 — Determine the Commit Range

Identify the range of commits to include. Use tags, dates, or SHAs.

```bash
# Between two tags
git log --oneline v1.2.0..v1.3.0

# Since a specific date
git log --oneline --since='2024-03-01'

# Since the last tag
git log --oneline $(git describe --tags --abbrev=0)..HEAD
```

### Step 2 — Categorize Commits

Map each commit to a changelog section using conventional commit prefixes:

| Prefix | Section |
|--------|---------|
| `feat:` | New Features |
| `fix:` | Bug Fixes |
| `perf:` | Performance |
| `docs:` | Documentation |
| `BREAKING CHANGE` or `!:` | Breaking Changes |
| `security:` | Security |

For repositories not using conventional commits, infer the category from the commit message content (e.g., "add" → New Features, "fix" / "resolve" → Bug Fixes, "improve" / "update" → Improvements).

### Step 3 — Filter Out Noise

Exclude commits that are not user-facing:

- Prefixes: `chore:`, `ci:`, `test:`, `refactor:`, `style:`, `build:`
- Merge commits (`Merge branch ...`, `Merge pull request ...`)
- Dependency-bot commits (dependabot, renovate)
- Release-only commits (`chore: release v1.2.3`)

### Step 4 — Rewrite for Users

Transform each remaining commit from developer language to user-facing language:

- Remove file paths, function names, and implementation details
- Explain the impact or benefit to the user
- Start each entry with a bold feature name when possible

Example transformation:

```
# Raw commit
feat(sync): implement delta-sync algorithm using rsync protocol for FileStore

# User-facing entry
- **Faster Sync**: Files now sync 2x faster across devices using incremental updates
```

### Step 5 — Format and Output

Assemble entries into sections. Use this structure:

```markdown
# Changelog — v1.3.0 (March 15, 2024)

## Breaking Changes
- ...

## New Features
- ...

## Improvements
- ...

## Bug Fixes
- ...

## Performance
- ...
```

Omit any section that has no entries. If the project has a `CHANGELOG_STYLE.md`, follow its formatting conventions instead.

## Worked Example

**Input** — raw git log for the past week:

```
a1b2c3d feat(workspace): add multi-team workspace support with RBAC
d4e5f6a feat(shortcuts): implement global keyboard shortcut system
b7c8d9e fix(upload): handle files >50MB by chunking upload stream
f0a1b2c fix(tz): store all timestamps in UTC, convert on display
e3d4f5a fix(notifications): correct unread badge counter query
g6h7i8j perf(sync): implement delta-sync for 2x throughput
k9l0m1n chore: update eslint config
o2p3q4r ci: add nightly build workflow
s5t6u7v refactor(auth): extract token refresh into middleware
w8x9y0z docs: update API rate-limit table
```

**Output** — generated changelog:

```markdown
# Updates — Week of March 10, 2024

## New Features

- **Team Workspaces**: Create separate workspaces for different
  projects. Invite team members and control access with roles.

- **Keyboard Shortcuts**: Press `?` to see all available shortcuts.
  Navigate faster without touching your mouse.

## Improvements

- **Better Search**: Search now includes file contents, not just titles.

## Bug Fixes

- Fixed issue where large images would fail to upload.
- Resolved timezone confusion in scheduled posts.
- Corrected notification badge count.

## Performance

- **Faster Sync**: Files now sync 2x faster across devices.

## Documentation

- Updated API rate-limit reference.
```

Note: `chore:`, `ci:`, and `refactor:` commits were excluded automatically.

