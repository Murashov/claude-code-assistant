# Project: personal assistant workspace

## What this repo is

A personal assistant workspace. Claude Code runs inside a Docker container on a
Raspberry Pi with this repository mounted at `/workspace`. The repo is the
assistant's persistent storage: notes, documents, scripts, memories, and anything
else the owner asks to be created or kept.

The owner (Art Murashov) interacts with Claude remotely via Remote Control /
claude.ai. Files created here are committed and pushed to GitHub so they survive
container restarts and are reachable from anywhere.

## Repository layout

```
CLAUDE.md      Working rules plus the index of memories
README.md      Short human-facing description of the repo
memories/      One Markdown file per topic Claude should remember across sessions
notes/         Free-form notes, ideas, meeting notes (one Markdown file per topic)
docs/          Longer documents, drafts, reports
scripts/       Small utility scripts created on request
inbox/         Unsorted items to be processed later
repos/         Other git repositories cloned on request (gitignored, see below)
```

Create new top-level folders only when none of the above fits, and document them
here and in CLAUDE.md.

## Cloned repositories (set 2026-11-01)

- Other repos the owner asks for are cloned into `repos/<name>` inside this
  workspace. `repos/` is gitignored, so nested clones never land in this repo's
  history. Their state lives in their own remotes: commit and push there when
  asked and when access allows. The folder is ephemeral like everything else
  here; re-clone if it is missing after a container restart.
- `repos/manifest.txt` is the only tracked file under `repos/`. It lists every
  clone as `name  url  [branch]`. When cloning a new repo, add a line there and
  commit it. `scripts/repos-sync.sh` clones anything in the manifest that is
  missing, fetches, and prints branch / dirty / ahead / behind for each clone.
- Decision (2026-11-02): plain gitignored clones, not submodules or subtrees.
  Repos have different owners and permissions, and nothing here needs to pin a
  child version. One SSH key (the one this container already uses) is used for
  all remotes; the owner does not want per-repo credentials for now.

## Conventions

- File names: lowercase, words separated by hyphens, e.g. `notes/travel-ideas.md`.
- Date-stamped files use ISO format as a prefix: `2026-11-01-weekly-review.md`.
- Each Markdown file starts with a `# Title` line.
- Prefer Markdown for text. Do not add tooling, build systems, or dependencies
  unless a task actually needs them.
- Secrets, tokens, and passwords are never committed to this repo.

## Git

- Remote: `origin` = `git@github.com:Murashov/claude-code-assistant.git`
- Default branch: `main`
- Commit and push after each completed task so the owner can see results on GitHub.
- Use clear, descriptive commit messages.
