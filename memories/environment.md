# Environment: the container Claude runs in

Surveyed 2026-11-01. Re-check if something below stops working.

## Host and container

- Ubuntu 26.04 LTS, aarch64 (Raspberry Pi 5, 4 cores, 8 GB RAM), overlay root
  with roughly 22 GB free. Clock is UTC.
- Runs as unprivileged user `claude` (uid 1000). No sudo, so no apt installs.
- No systemd, no crontab, no Docker socket. Recurring work must go through the
  Claude Code `/schedule` or `/loop` skills, not OS cron.
- `/home/claude/.claude` is a persistent mount on the Pi's SD card (ext4), so
  Claude Code settings, sessions, and plugins survive container restarts.
  Everything else outside `/workspace` is ephemeral.

## Languages and tools

- Python 3.14 with pip. System site-packages are locked (PEP 668); use
  `python3 -m venv` and install inside it. No third-party packages preinstalled.
- Node 26 with npm 11. Global npm prefix is not writable; use `npx` or local
  `npm install` in a project folder.
- Perl, gcc are absent (no compiler toolchain).
- CLI: git, curl, jq, ripgrep (`rg`), nano, ssh, tar, zip/unzip, gpg, openssl.
- Not installed: gh, wget, pandoc, ffmpeg, ImageMagick, sqlite3, libreoffice,
  make, go, rust, java.

## Network

- Outbound HTTPS works (github.com, pypi.org, npmjs.org, generic sites).
- Git push to `origin main` works over SSH.

## Claude Code session tools

- Core: Bash, Read/Write/Edit, Agent (subagents), Artifact (publish HTML
  pages), WebSearch/WebFetch, SendUserFile, scheduling (CronCreate, /schedule,
  /loop), Monitor.
- Connectors present in the session: Claude Docs (ready), Gmail, Google
  Calendar, Google Drive (the Google ones need the owner to authenticate first).
- Skills available: docs, docx, xlsx, pptx, pdf, google-workspace, dataviz,
  artifact-design, schedule, loop, claude-in-chrome, and others.
- Auto mode is on: a permission classifier blocks commands that read
  credentials or environment secrets. Keep surveys and scripts free of env
  dumps and `~/.ssh` reads.
