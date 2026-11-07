# Free demo hosting and local data

The project stays on Render Free. There is no paid hosting or disk configuration to apply.

## What is saved, and where

| Setup | Where records and uploads live | What survives |
| --- | --- | --- |
| Render Free website | Files inside a temporary server container | Not redeploys, restarts or idle spin-down; fresh synthetic data is seeded when the installation is empty |
| Existing Desktop app | The database selected by `.env` or process settings and its sibling `documents/` folder | Normal app restarts and Git branch switches, as long as the same paths and files are kept |

By default, local data is in `.runtime/dayone.db` and `.runtime/documents/`. A browser's session storage is only a sign-in token, not a backup of these records. Git shares code, not your `.env`, live database or uploads. Your laptop's database is separate from Render's database.

## No-cost recording workflow

Use the existing project folder, such as `Desktop/dayforce hackthon`; keep its `.env`, `.venv`, installed dependencies and data files. Stop your own running app before restarting changed code. In that folder run:

```powershell
npm.cmd run dev
```

Open http://127.0.0.1:5173. Use one prepared backend for the recording and separate browser profiles/sessions for each role. Different laptops' localhost addresses are different backends. Do not reseed a database that already has users; changing `DEMO_PASSWORD` does not change existing account passwords.

In another terminal in the same folder, `npm.cmd run check` runs isolated automated checks without using live AI or resetting your working data. `npm.cmd run smoke` checks the running app. A successful configuration check is not proof that the hosted AI key works.

## Back up local progress

Stop the backend, its worker and all other writers. Copy the database, any journal/WAL/SHM companions and the matching sibling documents folder to a private location outside the repository. Test a restore on disposable copies, never by overwriting your working files. An ordinary copy of a live SQLite database is unsafe.

The Free website is only a disposable demonstration. This app has no bulk database-export endpoint, and Render Free has no dashboard shell/SSH; do not assume its current progress can be downloaded or recovered after it disappears.

## Can hosted persistence be free?

Render Free cannot attach a persistent disk. Free external databases or object-storage tiers may exist, but they have their own quotas and retention limits. This app uses SQLite-specific SQL/FTS5 and local upload files: moving it to external storage requires a reviewed database, search and upload-storage migration, not just a connection URL. No such migration or new account is included in these fixes. Local recording is the smallest no-cost option for retaining demo progress now.

Reference: [Render Free limitations](https://render.com/docs/free), checked 7 November 2026.
