# Task system (agreed 2026-11-23)

- Source of truth is git, not an app. `projects/areas.md` lists the buckets
  (Family, Health, Money, Emigration, Friends, Hobby, with sub-areas). One
  file per project in `projects/` holds goal, context, tasks with owner
  labels ([art] / [claude] / [claude?]), open questions and a log.
- Google Calendar (Managed) is only the output: scheduled work lands there.
- Art keeps a Miro mind map for himself; Claude does not use it.
- Board (built 2026-11-23): `board/index.html`, published as a private
  claude.ai artifact at https://claude.ai/artifact/YCdJpnxrrkR1d7TZeST4r7 .
  Its data is hand-copied from the project files into the JS arrays at the
  bottom. After any project change, update those arrays and republish the
  same file path (or pass that URL from another conversation).
- Loose tasks live in `projects/backlog.md`.
- Weekly plans live in `plans/YYYY-MM-DD-week.md` (Monday date), with an
  outcome column filled at the daily check-in.
- Planned, not built yet:
  weekly plan files recording done / missed / moved, and a daily check-in plus
  weekly planning via scheduled routines with push notifications.
  **Why:** plans were put on the calendar while Art was sick and nothing
  tracked that they were missed.
- Art is describing projects one at a time. Collect them all before building
  the board and routines.

## Backlog intake (2026-11-23): seeding done

- Art seeded all projects on 2026-11-23 and said that is everything for now.
  When he adds items, record them as described. Do not research, propose
  solutions, or schedule anything unless he asks.
  **Why:** he wants the full picture first and will come back to solving.
- Art asked to be reminded about the driver's license project
  (projects/drivers-license.md). Include it in check-ins once they exist.

## Check-in automation (built 2026-11-24)

- Daily check-in runs as a session cron defined in `automation/crons.md`,
  procedure in `automation/checkin.md`. Crons are session-only and expire
  after 7 days, so every session syncs them from that file at start.
- Notifications go via PushNotification (Remote Control pushes to phone).
- Next steps Art discussed: morning brief, Monday week-plan nudge, and
  Claude researching `[claude]` tasks on its own. Not built yet.
