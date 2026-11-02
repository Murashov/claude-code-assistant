# CLAUDE.md

This repo is Claude's personal assistant workspace and persistent storage.
This file is deliberately short: it explains how to work here and indexes the
memories in `memories/`. Read only the memories a task needs.

## How to work

1. Scan the memory index below. Read the memory files relevant to the task.
2. Do the task directly in this repo (notes, docs, scripts, etc.).
3. Commit and push to `origin main` with a descriptive message.
4. Memory upkeep: when the owner says something important (preferences, facts
   about them, ongoing projects, how they want things done), save it. Append to
   an existing memory if it fits the topic; otherwise create a new file in
   `memories/` and add one line to the index below. Before changing a memory,
   read it first. Never store secrets. Every memory change is committed and
   pushed to `origin main` immediately, even if no other task is finished, so
   nothing is lost when the container restarts.

## Memory index

| File | What is there |
|------|---------------|
| `memories/project.md` | What this repo is, folder layout, naming conventions, git remote and push rules |
| `memories/identity.md` | Claude's role as personal assistant and how it should behave here |
| `memories/owner.md` | Facts about Art: time zone (Sao Paulo), calendar structure, works from phone, Managed calendar ID and the write-only-to-Managed rule |
| `memories/project.md` (Cloned repositories section) | `repos/` holds other repos cloned on request, gitignored, pushed to their own remotes; `repos/manifest.txt` lists them and `scripts/repos-sync.sh` restores them |
| `memories/environment.md` | Container facts: OS, hardware, installed tools, what can and cannot be installed, network, session tools and connectors |
