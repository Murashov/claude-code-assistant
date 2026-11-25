# Morning brief (07:00 Sao Paulo)

Goal: tell Art what Claude did overnight and get the answers Claude needs,
without flooding him. Agreed with Art on 2026-11-25. He reads it on the
phone: keep it short.

## When the cron fires

1. Gather:
   - Last night's report `docs/night-reports/YYYY-MM-DD.md`.
   - Today's planned task: the row in the current week plan and today's
     Managed calendar events (re-read). Add one prep line if useful: what
     to have ready, where it was left last time.
   - Today's questions from `automation/questions.md` (rules below).
   - Later, when the job search is active: curated open positions (see the
     backlog item; not ready yet).
2. If there is nothing at all (no night work, no question, no planned task),
   send nothing.
3. `PushNotification` (one line, under 200 chars), e.g.
   `Brief: 3 citizenship tasks done overnight, 1 question waiting.`
4. Write the brief as short text: Done overnight (one line each), Today
   (task plus prep), and links to longer results.
5. Ask today's question(s) with `AskUserQuestion` (tappable options plus
   Other for free text).
6. Run the cron sync from `automation/crons.md`.

## Question limit

- One question a day, or a few closely connected ones on the same topic
  (at most 3). Never a mix of topics.
- Pick by: deadlines first, then what unblocks the most Claude work, then
  oldest first.
- If yesterday's question is still unanswered, ask it again instead of a
  new one.
- Proposals for periodic jobs are questions too and follow the same limit.

## When Art answers

- Write the answer where it belongs (project file, memory, CV README) and
  move the question to "Answered" in `automation/questions.md` with the
  date. The next night shift picks up the work it unblocks.
- Approved periodic jobs go to "Approved periodic checks" in
  `automation/questions.md`, with what to check and how often. A job that
  needs its own cron also goes to the table in `automation/crons.md`.
- Commit and push (push as the standalone `git push -q origin main`).
