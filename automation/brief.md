# Morning brief (07:00 Sao Paulo)

Goal: tell Art what Claude did overnight, then let him answer as many
open questions as he wants. Agreed with Art on 2026-11-25. He reads it on
the phone: keep it short.

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
5. Question loop (if any question is open), see below.
6. Run the cron sync from `automation/crons.md`.

## Question loop (changed by Art 2026-11-25)

No daily limit: Art decides how many to answer. Some days none, some days
ten.

1. After the brief, ask ONE question as plain text in the message. Do not
   use `AskUserQuestion` for the question itself: it has no voice
   dictation and long answers are awkward to type. Then stop and wait for
   his reply.
2. When he replies, record the answer (see below), then use
   `AskUserQuestion` with two options: "One more" / "Stop".
3. "One more": ask the next question the same way and repeat. "Stop" (or
   no reply): end. Unanswered questions just stay open; that is fine.
- Ask one question per message. If a backlog item holds several asks,
  split it and ask them one by one.
- Order: deadlines first, then what unblocks the most Claude work, then
  oldest first.
- Proposals for periodic jobs are questions too.

## When Art answers

- Write the answer where it belongs (project file, memory, CV README) and
  move the question to "Answered" in `automation/questions.md` with the
  date. The next night shift picks up the work it unblocks.
- Approved periodic jobs go to "Approved periodic checks" in
  `automation/questions.md`, with what to check and how often. A job that
  needs its own cron also goes to the table in `automation/crons.md`.
- Commit and push (push as the standalone `git push -q origin main`).
