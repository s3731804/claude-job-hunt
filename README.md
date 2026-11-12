# claude-job-hunt

A small system that turns Claude Code into a job-search assistant. It finds new listings on SEEK and LinkedIn, ranks them against your goals, and builds a tailored application for each one: a one-page resume, a cover letter, and form answers ready to copy. Then it works through them with you one at a time.

It runs on short keywords, so a session mostly looks like `search`, `next`, `next`, `status`.

## What you need
- **[Claude Code](https://claude.com/claude-code) desktop app**, with the built-in browser enabled (Settings → Claude Code → Browser). Searches run in that browser, and LinkedIn is read through its public job feed, so no login is needed.
- **Google Chrome**, for rendering the PDFs.
- **`poppler-utils`**, for the `pdfinfo`, `pdftotext` and `pdftoppm` render checks.
- **Python 3.**

## Getting started
1. Clone this repo and open the folder in Claude Code.
2. Say **setup**. Claude will:
   - **ask for your resume** (drop it into the chat, or save it into `me/` if you're using the terminal), pull out everything it can, and then only ask about what's missing (work rights, location, availability, salary and the roles you want);
   - **record your history,** including what you did *not* do, so applications never overclaim;
   - **build your master resume** from `templates/resume.html` and check it renders to one clean page;
   - **research search terms:** it tests SEEK and LinkedIn keywords against real listings near you, works out good-fit, stretch and backup roles from your skills, and confirms them with you;
   - **offer to review your LinkedIn and SEEK profiles** and write paste-ready improvements (headline, About, skills, Open to Work settings);
   - **create your private folders** (`me/`, `applications/`, `data/`). These are gitignored, so your details never end up in the repo.
3. Say **search** for your first sweep, then **next** to start working through the results.

## Keywords
Each keyword only triggers when it's your whole message.

| Keyword | What it does |
|---|---|
| `search` | Finds listings posted since your last search, screens them with a cheaper background model, and adds the good ones to your queue. It asks first if you searched in the last 24 hours. |
| `next` | Moves on from the current listing (assumed applied, or passed) to the next one. Good fits are checked and built automatically. Stretches and backups get a summary first. |
| `build` | Builds the stretch or backup listing you're looking at. |
| `status` | Where you are in the queue, and what's left in each tier. |
| `back` | After a tangent: where you are, what's pending on the current listing, and what `next` will do. |
| `refresh` | Re-checks the current tier for closed or changed ads. |
| `profile` | Reviews and updates your profile and search terms. |
| `setup` | Runs onboarding (again). |
| `help` | Lists the keywords. |

You can also paste any job link. Claude checks whether it's already handled, judges the fit, and builds the application, or tells you why it isn't worth it.

## How it fits together
```
CLAUDE.md          the rules Claude follows (generic, so no personal data)
tools/
  ledger.py        ledger of every listing seen, so nothing is screened twice
  seek-search.js   search scripts that run in the built-in browser;
  linkedin-search.js  their seen list lives in browser storage, which keeps runs cheap
  job-details.js   pulls the requirement lines out of each ad
  search-brief.md  instructions for the background screening agent
  make_letter.py   cover letter builder (reads your name and contact details from me/config.json)
templates/         blank profile, config, resume, queue and skipped list
me/                your profile, config and master resume          (gitignored)
applications/      one folder per role: resume, letter, application.md  (gitignored)
data/              ledger, queue, skipped list, last search time    (gitignored)
```

## Ground rules it follows
- **Every resume and letter is render-checked:** one page, no orphan words, and a clean preview.
- **Submitted applications are never edited afterwards.** Improvements go into the master resume instead.
- **Claims are checked against your profile,** and anything unconfirmed is flagged rather than included.
- **It never sends messages for you, and never asks for ID documents in chat.**
