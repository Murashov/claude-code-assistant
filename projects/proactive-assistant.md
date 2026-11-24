# Proactive assistant

- Area: Assistant
- Status: active (check-in notifications done; research autonomy next)
- Updated: 2026-11-24

## Goal

Make Claude a proactive assistant: regular reminders and check-ins instead of
waiting to be asked.

## Context (as Art described it)

- Design the system to be proactive, for example scheduled jobs that remind
  Art of things.
- It is not trivial, so Art cannot do it right away and needs to think it
  through.
- Ideas already noted in memories/task-system.md: daily check-in, weekly
  planning, done / missed / moved tracking, a visual board.
- Related: voice and Pi bridge RFC in
  documents/rfc-pi-bridge-and-voice.md (not implemented).

## Art's plan (2026-11-23)

- Art added two blocks to his calendar: "Week plan" every Monday 07:00-08:00
  and a daily "Check-in" 19:00-19:30.
- Check-in: see what is done and what needs to be moved, usually together
  with Claude.
- Automation goal: Claude prepares the summary for these sessions, with
  checkboxes, so Art only confirms.

## Tasks

- [x] Notifications and interactive daily check-in (done 2026-11-24):
      session cron from automation/crons.md, procedure in
      automation/checkin.md, push and tappable questions tested on phone.
- [ ] [art] Make Claude research tasks on its own (scheduled Wed
      2026-11-25 07:00)
- [ ] [art] Implement the Pi bridge and voice RFC (later)

## Log

- 2026-11-23: Recorded at the end of backlog intake.
- 2026-11-24: Check-in notifications built and tested. Wed slot now for research autonomy.
