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
- Driver's license (projects/drivers-license.md): stays on the list, but no
  reminders in check-ins. Art cancelled them on 2026-11-24: he knows it needs
  doing and does not care about it right now.

## Check-in automation (built 2026-11-24)

- Daily check-in runs as a session cron defined in `automation/crons.md`,
  procedure in `automation/checkin.md`. Crons are session-only and expire
  after 7 days, so every session syncs them from that file at start.
- Notifications go via PushNotification (Remote Control pushes to phone).
- Next step Art discussed: Monday week-plan nudge. Not built yet.

## Night shift, morning brief, question backlog (built 2026-11-25)

- Night shift (`automation/night.md`, from 00:00 Sao Paulo): Claude does
  all `[claude]` work it can, with no limit, until it needs Art. A night
  with nothing to do is fine.
- Do not assume: anything uncertain becomes a question in
  `automation/questions.md`. **Why:** Art wants no guessed facts; he
  controls how many questions he answers.
- Morning brief (`automation/brief.md`, 07:00): what was done overnight,
  today's task with prep, then a question loop: one question as plain
  text, wait for the answer, then AskUserQuestion "One more" / "Stop".
  No daily limit; Art chooses how many (0 to 10+).
  **Why:** answers via AskUserQuestion have no voice dictation and long
  typing on the phone is awkward; his energy varies by day.
- Periodic jobs (watchers etc.) need Art's approval first; propose them
  as questions.
- Job search monitoring is planned as a brief section, not ready yet
  (backlog).
- Phone test (2026-11-24, cron-fired): PushNotification reported "not sent"
  (session counted as active), yet Art got a push on his phone, likely
  Remote Control's own alert when a question waits for him.
  AskUserQuestion shows as tappable on the phone. So cron-fired check-ins
  reach him even when PushNotification is skipped.

## Do not repeat the cron caveat (Art, 2026-11-25)

- Do not tell Art that crons are session-only or expire after 7 days. The
  sync step in `automation/crons.md` already handles it.
  **Why:** he finds the repeated warning pointless, since this was fixed.
