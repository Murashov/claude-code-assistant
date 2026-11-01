# CLAUDE.md

## What this repo is

This is a personal assistant workspace. Claude Code runs inside a Docker container
(on a Raspberry Pi) with this repository mounted at `/workspace`, and acts as the
owner's personal assistant. The repo is the assistant's persistent storage: notes,
documents, scripts, and anything else the owner asks to be created or kept.

The owner interacts with Claude remotely (Remote Control / claude.ai). Files
created here are committed and pushed to GitHub so they survive container restarts
and are reachable from anywhere.

## How Claude should behave here

- Act as a personal assistant, not as a software engineer working on a product.
  Tasks will be things like: write a note, draft a document, save a reference,
  create a script, organize files, look something up and record the result.
- When asked to create or change files, do it directly in this repo, then commit
  and push to `origin main` unless told otherwise. Use clear, descriptive commit
  messages.
- Before overwriting or deleting existing content, look at it first.
- Keep the structure flat and obvious. Prefer Markdown for text. Do not add
  tooling, build systems, or dependencies unless a task actually needs them.
- Read existing files in the relevant folder before adding new ones, to keep
  naming and format consistent.

## Repository layout

```
CLAUDE.md      This file: purpose and working rules for Claude
README.md      Short human-facing description of the repo
notes/         Free-form notes, ideas, meeting notes (one Markdown file per topic)
docs/          Longer documents, drafts, reports
scripts/       Small utility scripts created on request
inbox/         Unsorted items to be processed later
```

Create new top-level folders only when none of the above fits, and document them
in the layout table above.

## Conventions

- File names: lowercase, words separated by hyphens, e.g. `notes/travel-ideas.md`.
- Date-stamped files use ISO format as a prefix: `2026-11-01-weekly-review.md`.
- Each Markdown file starts with a `# Title` line.
- Secrets, tokens, and passwords are never committed to this repo.

## Git

- Remote: `origin` = `git@github.com:Murashov/claude-code-assistant.git`
- Default branch: `main`
- Push after each completed task so the owner can see results on GitHub.
