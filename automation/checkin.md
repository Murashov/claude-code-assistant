# Daily check-in (19:00 Sao Paulo)

Goal: nothing planned gets silently missed. Art usually answers from his
phone, so keep everything short.

## When the cron fires

1. Gather today's items (Sao Paulo date):
   - The row(s) for today in the current week plan
     (`plans/YYYY-MM-DD-week.md`, Monday date) with an empty Outcome.
   - Earlier rows this week still without an Outcome (unanswered before).
   - Today's events on the Managed calendar (re-read; they may have moved).
   - Open items waiting on someone (investor, Dad, etc.) only if they are
     worth a nudge.
2. `PushNotification` (one line, under 200 chars), e.g.
   `Check-in: Book a haircut (07:00). Done, missed or moved?`
   If nothing was planned today, say so and ask if anything got done.
3. Ask in the session with `AskUserQuestion` so Art can tap answers on
   the phone:
   - One question per planned item (max 3 items; list the rest as text):
     options `Done`, `Missed`, `Moved` (he types the new date in Other).
   - Always a last question "Anything else on your mind?" with options
     `Nothing else` and `Did more than listed`; the Other field is free
     text for new tasks, extra things completed, or thoughts.
   If AskUserQuestion is not available, write a short numbered list and
   end with "Anything else: new tasks, or things you did that are not on
   the list?".
4. Run the cron sync from `automation/crons.md`.

Do not change any files before Art answers.

## When Art answers

- Fill the Outcome column in the week plan: `done`, `missed`, `moved (to X)`.
- done: mark the task done in its project file or backlog, add a log line.
- moved: move the Managed calendar event (scheduling rules in
  `memories/owner.md`) and note it in the project file.
- missed with no new date: put the task back to unscheduled and ask once
  whether to plan it.
- Free text: new tasks go to the right project file or the backlog,
  recorded as described (no research or scheduling unless he asks).
  Extra things completed get marked done (or added as done) with a log
  line. Facts and preferences go to memory as usual.
- Update the board arrays and republish the board artifact.
- Commit and push (push as the standalone `git push -q origin main`).

If Art does not answer, include the unanswered items in the next check-in.
