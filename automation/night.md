# Night shift (from 00:00 Sao Paulo)

Goal: do every task Claude can do alone while Art sleeps, so the morning
brief can report finished work. Agreed with Art on 2026-11-25.

Art's rules:

- No artificial limit on the amount of work. Keep going until nothing is
  left that can be done without asking Art first. That is the stopping
  point.
- A night with nothing to do is fine. Do not invent work to fill it.
- Do not assume. Anything Claude does not know for sure (a fact about Art,
  a preference, a choice between options) becomes a question in
  `automation/questions.md`, not a guess.
- Questions are what gets limited (see `automation/brief.md`), not research.

## When the cron fires

1. Run the cron sync from `automation/crons.md`.
2. Collect the work list:
   - Every open `[claude]` task in `projects/*.md` and `projects/backlog.md`.
   - `[claude?]` tasks whose blocking question is answered in
     `automation/questions.md`.
   - Follow-up work from questions Art answered since the last night.
   - Approved periodic jobs listed in `automation/questions.md` under
     "Approved periodic checks" that are due.
3. For each task, in the order that unblocks the most:
   - Do it fully: web research (WebSearch, WebFetch), drafting, checklists.
     Prefer official sources; write the source link next to every fact.
     Mark anything not confirmed by a reliable source as "to verify".
   - Write the result where it belongs: into the project file, or a longer
     document in `docs/` linked from the project file.
   - Tick the task or, if partly done, note what is left. Add a log line.
   - Every point where Art has to answer or decide: add it to
     `automation/questions.md` (grouped by topic, with why it matters and
     what it unblocks). If a task cannot go further without the answer,
     leave it and move on.
   - Commit after each task (push as the standalone
     `git push -q origin main`).
4. Write the report `docs/night-reports/YYYY-MM-DD.md` (Sao Paulo date of
   the morning): what was done (one line each, with the file), what was
   found that matters, which new questions were added, and anything that
   failed (for example a denied push). If nothing was done, one line saying
   so. Commit and push.

## Not allowed unattended

Only research and writing inside this repo. Everything else is a question
for Art:

- No calendar writes, no emails or messages to anyone, no purchases, no
  sign-ups, no contacting people.
- No new crons or periodic jobs: propose them as questions; they run only
  after Art approves them.
- No changes to Art's plans, priorities or memories about his preferences.
- No PushNotification at night. Art hears about it in the morning brief.
