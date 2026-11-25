# Scheduled jobs (session crons)

Claude Code crons live only inside a session and expire after 7 days. This
file is the source of truth; the live session mirrors it.

## Sync procedure

Run at the start of every session, and at the end of every job run:

1. `CronList`.
2. For each job below, look for a registered cron whose prompt starts with
   the job's tag (e.g. `[cron:checkin]`).
   - Missing: `CronCreate` it with the cron and prompt from the table.
   - Present but cron or prompt differs from the table: delete and re-create.
3. Delete registered crons with a `[cron:...]` tag that is not in the table.
4. If a job's next run is more than 7 days away or it is about to expire,
   re-create it (recurring crons auto-expire after 7 days).

Cron times are container time, which is **UTC**. Sao Paulo = UTC-3.
Daily crons can fire up to 30 minutes late (scheduler jitter), so times
are set a bit early.

## Jobs

| Tag | Cron (UTC) | Sao Paulo time | Prompt |
|-----|------------|----------------|--------|
| `[cron:checkin]` | `47 21 * * *` | daily ~18:47-19:17 | `[cron:checkin] Daily check-in. Read automation/checkin.md and follow it.` |
| `[cron:night]` | `7 3 * * *` | daily ~00:37 | `[cron:night] Night shift. Read automation/night.md and follow it.` |
| `[cron:brief]` | `27 9 * * *` | daily ~06:57 (fixed +30 min offset) | `[cron:brief] Morning brief. Read automation/brief.md and follow it.` |

Job procedures live in their own files so they can change without
re-creating the cron.
