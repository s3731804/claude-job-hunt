# Job application workspace: working rules for Claude

This workspace finds job listings, ranks them, and builds a tailored application for each role: resume, cover letter and paste-ready form answers. It's driven by short keywords (see Keywords).

Everything about the user (who they are, what's true about their history, what they're targeting) lives in `me/`. The rules here are generic. Before doing anything for the user, read `me/personal-profile.md`. Call the user by the name it gives, and treat its "what's true and what to avoid claiming" notes as hard limits.

## Folder layout
- **Shared (in git):** `CLAUDE.md`, `README.md`, `tools/`, `templates/`.
- **Personal (gitignored):**
  - `me/`:
    - `personal-profile.md`: facts, targets, application defaults
    - `config.json`: name, contact line, search terms
    - `resume.html`: the master resume, plus its PDF and any transcript
  - `applications/<Company> - <Role>/`:
    - `resume-<company>.html` and its PDF
    - the cover letter HTML and PDF, if there is one
    - `application.md`
  - `data/`:
    - `seen-jobs.tsv`: ledger of every listing looked at
    - `job-queue.md`: the rolling shortlist
    - `skipped.md`
    - `last-search.txt`

## First run / setup
If `me/personal-profile.md` doesn't exist, or the user says **setup**, run setup before anything else. Ask in small batches, not one long questionnaire.
1. **Start with the resume.** First create `me/` if it doesn't exist. Then open by asking for their current resume (PDF, DOCX or an image), and nothing else in that first message. Offer two ways:
   - drag and drop it into the chat (desktop app), or paste the text;
   - save it into `me/` (e.g. `me/resume-original.pdf`) and say "done". This is easier from the terminal CLI, and it keeps the original with the rest of their personal files.

   Either way, keep a copy of the original in `me/`.
   - Extract everything you can: name, contact line, location, education (dates, grades), work history, projects and stacks, skills, and any hints about work rights or availability.
   - Then show a short "here's what I picked up" summary, grouped by profile section, and mark anything you inferred rather than read (for example "Melbourne, from your phone number and suburb").
   - Ask only for what's missing or uncertain, in small batches: work rights and citizenship, clearance, which cities they're looking in (just where they live, or other cities they'd relocate to) and how far they'd commute, on-site/hybrid/remote preference, availability and notice, salary expectations, roles they want and roles they won't do. Skip any question the resume already answers.
2. **Confirm the truth about their history.** Walk through what you extracted and confirm it:
   - education (degree, dates, grades)
   - work history: what they did and didn't do
   - each project and their actual part in it
   - years of experience in the terms forms use (professional dev, customer-facing, support)
   
   If they share repo paths, check authorship and claims against the repos. Record anything they didn't do or haven't confirmed under "what's true and what to avoid claiming".
3. **Write `me/personal-profile.md`** using the same sections as `templates/personal-profile.md`.
4. **Build the master resume:**
   - Copy `templates/resume.html` to `me/resume.html` and fill it from their resume and profile.
   - Render it and run the render check.
   - Name the PDF `<file_prefix>-Resume.pdf`.
5. **Search research.** Spend real effort here, because it decides what every future search finds.
   - From their skills and target roles, list good-fit titles, adjacent stretch titles (roles their skills transfer to with a 1–3 year ask) and backup titles. Look at real listings in their area to see which titles employers actually use.
   - Search every city they named: `seek_locations` and `linkedin_locations` in config are lists, and the scripts loop over them.
   - For SEEK, test candidate keyword slugs in the in-app browser: fetch `https://au.seek.com/<slug>-jobs/<location>?daterange=14` and count the results. Keep slugs that return relevant listings and drop ones that return noise.
   - Do the same for LinkedIn keywords through `/jobs-guest/jobs/api/seeMoreJobPostings/search`.
   - Draft a `title_exclude` regex covering seniority and unrelated fields they'd never apply for, and a salary ceiling above which roles are clearly too senior.
   - Show the user the proposed Targets (good / stretch / backup / avoid) and the keyword lists, and confirm them.
6. **Offer a LinkedIn and SEEK profile review** (optional; ask, don't assume).
   - **LinkedIn:** public profiles are mostly behind a login wall, so ask the user to export theirs (Profile → More → Save to PDF) and drop it in, or paste it, or send screenshots.
     - Review it against their Targets: headline, About, experience and project entries, skills (top 3 pinned), education, custom URL, photo and banner, and Open to Work settings (titles, locations, start date, recruiters-only or public).
     - Write `me/linkedin-profile.md` with paste-ready replacements, in the same fenced-block format as application.md, plus a short "quick wins" list.
     - Keep every claim within the profile's "what's true" notes.
   - **SEEK:** worth a lighter pass. Recruiters search SEEK Profiles, and Quick Apply sends the profile along with the resume.
     - Check the headline and summary, career history, skills, right to work, availability, salary expectation and the "let employers find you" visibility setting.
     - Add the suggestions to `me/seek-profile.md` in the same format.
7. **Write `me/config.json`** in the shape of `templates/config.json`.
8. **Create `data/`:**
   - `seen-jobs.tsv`, holding only its header line
   - `job-queue.md` and `skipped.md`, copied from `templates/`
9. **Offer the first `search`.** With an empty ledger it covers the full 14 days, so that first run is the expensive one.

To update the profile later, the user can say **profile**: show the Targets and defaults, ask what's changed, and edit them. If targets change, redo step 5 for the keywords, and offer to redo the LinkedIn and SEEK review (step 6) so those profiles match.

## Don't touch submitted applications
- Never re-edit or regenerate a tailored resume, cover letter or PDF in an application folder after it's been generated, unless the user explicitly asks to revise that specific application.
- Assume a generated application may already have been submitted. Its folder is the record of what was sent, so changing it afterwards breaks that record.
- That includes improvements and corrections. Make them in `me/resume.html` only, so future applications inherit them.
- If a factual error turns up in an existing application, tell the user and let them decide. Don't fix it silently or in bulk.

## When revising is fine
- The application currently being worked on, before the user says it's submitted.
- Anything the user explicitly asks to change.
- The master resume in `me/`.

## Every edit gets a render check
After any change to a resume or cover letter, re-render the PDF with headless Chrome:

`google-chrome --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=<out.pdf> <in.html>`

Then confirm there are no formatting problems before reporting it done:
- `pdfinfo` shows exactly 1 page.
- `pdftotext -layout <pdf> - | awk 'NF>0 && NF<=3'` shows no single-line items wrapping onto a second line, and no orphaned words on their own line.
- A `pdftoppm -png -r 70` preview shows nothing visually off: spacing, cramped sections, stray bullets, text running into the margin.

Tell the user the result of the check, or what was fixed. Fix orphans by rewording, never by shrinking the font.

## Building an application
- **Folder:** `applications/<Company> - <Role>/`.
- **Resume:**
  - Copy `me/resume.html` to `resume-<company>.html`, then tailor it with small, exact string replacements: summary, skill-row order and wording, project order. Use a scratch Python script with an assert that each replacement matches exactly once.
  - Only use facts from the profile, and keep them true. Don't add claims the profile flags.
  - Render to `<file_prefix>-Resume-<Company>.pdf`.
- **Cover letter:**
  - Only if the ad wants one, or a form will take one.
  - Write the body as plain paragraphs (greeting through sign-off) in a scratch file.
  - Run `python3 tools/make_letter.py <body.txt> <out.html> "<Company, Suburb STATE>"`. It adds the name, contact line and today's date from config.
  - Render to `<file_prefix>-Cover-Letter-<Company>.pdf`.
- **application.md:** follow "application.md format".
- **Read every claim back** against the profile before rendering. Use the user's own wording where they've given it (for example "helped build" rather than "built").

## When the user links a listing
- First check whether it's already handled: search `data/seen-jobs.tsv` and `applications/` for the job ID. Then do a quick fit evaluation against the profile's Targets.
- If it looks worth applying for, go straight ahead and build the application. Don't stop to ask.
- Pause and confirm only if it's unlikely to succeed: a big skills or seniority gap, eligibility problems, not a real opening, and so on. Say why, and ask whether they want to bother.

## Running a job search
- The sweep goes to a Haiku subagent: the Agent tool with model "haiku", run in the background, with the prompt "Follow <absolute path to this folder>/tools/search-brief.md exactly." The brief has the steps, the tier rules and the report format.
- `data/seen-jobs.tsv` is the ledger of every listing already looked at (job_id, site, first_seen, status). Use `tools/ledger.py` instead of reading it: `days`, `count`, `seen`, `add`, `set`, `counts`, `stamp`, `since`, `prefix`.
- The search scripts take their terms from `me/config.json` through `ledger.py prefix <site>`. They keep the seen list in each site's browser localStorage, so the IDs never pass through messages, and they ask for a reseed if the browser and ledger counts don't match.
- When the report comes back, review the tier calls, because Haiku over-rates stretches. Also check for duplicates of listings already in the queue or ruled out. Then:
  - pipe its ledger lines into `python3 tools/ledger.py add`, changing any statuses you corrected;
  - add new A/B/C rows to the bottom of each tier in `data/job-queue.md`, plus any Couldn't-read rows;
  - log the search under "Searches".
- As the user decides:
  - **Build:** the application folder, then `ledger.py set <id> application`.
  - **Skip:** add it to `data/skipped.md`, then `ledger.py set <id> skipped`.

## Keywords
When the user's whole message is one of these words, it means the following:

- **search**:
  1. Run `python3 tools/ledger.py since`. If the last search was under 24 hours ago, say how long ago and what it found, and only run another once the user confirms.
  2. Run the search as in "Running a job search". The window is the days since the last ledger date.
  3. Add the new listings to `data/job-queue.md` without changing Mode or Current, so you carry on where you were rather than jumping back to new good fits.
  4. Run `ledger.py stamp "<one-line result>"`.
  5. Report the counts and the top new picks. If a new Worth-applying listing closes within a few days, flag it.
- **next**: move to the next listing in `data/job-queue.md`.
  - **Previous listing:** treat it as done. If its application was built, set its application.md status to "assumed submitted (moved on with next, <date>)". If it wasn't built, mark its Decision as "Passed". Update its ledger status either way.
  - **Order:** stay in the current Mode (tier) and take the next undecided row, top to bottom. When the tier is empty, move to the next one (A → B → C → back to A) and update Mode.
  - **Worth applying:** before building, open the ad and confirm it's still live and still a good fit. Then build the full package without asking (see "Building an application"), and mark Decision "Built".
  - **Stretch / Backup:** give a short fit summary and recommendation, and wait. The user replies **build** to make it, or **next** to pass.
  - **Pause:** if the ad has changed, closed, or turns out to be a poor fit, say so and wait.
- **build**: after a Stretch or Backup summary, build that application in full, then mark Decision "Built".
- **status**: show the Mode and Current listing, then a line per tier: how many are undecided, what's next in it, and the oldest undecided Added date. Also show totals for Built, Passed, Skipped and Closed, plus the last search time (`ledger.py since`). Read-only, so nothing is fetched.
- **where**: restate where we are, e.g. after a tangent. In two or three lines: the Mode and Current listing (posting link first, then folder link), where it stands (built and waiting to be submitted, or waiting on build/next, and any open question), and exactly what **next** will do. Also reopen the current listing's application.md in the Files pane (show_pane, no `line`), if it has one. Read-only otherwise.
- **refresh**: re-check every listing in the current tier that isn't decided yet. Confirm each is still live: SEEK says "no longer advertised" when it's gone, and LinkedIn says "No longer accepting applications". Mark closed ones "Closed", note any changes, and say which listing is up next.
- **setup**: run first-run setup (see above).
- **profile**: review and update `me/personal-profile.md` and, if targets change, the search terms in `me/config.json`.
- **help**: list these keywords with one line on what each does. Read them from this section so the list stays current.

Start every listing summary (from next, build, or a linked listing) with the posting link on its own line, followed by the folder link, so the user can open the ad straight away. When an application is built, also open its application.md in the app's Files pane. Use show_pane with no `line`, because passing a line forces the raw source view instead of the preview. The preview's code blocks have copy buttons.

`data/job-queue.md` keeps `Mode:` and `Current:` lines at the top, so a new session can pick up where the last one left off.

## application.md format
- Under the title, add a `## Quick links` heading with one line of links: Posting · Apply form (once known) · Paste-ready · each paste-ready field · Resume PDF · Cover letter PDF. Section links use heading anchors (e.g. `#why-appliers`).
- Notes go next, as normal markdown: ad link, status, fit notes.
- Anything the user will paste into a form goes under `## Paste-ready`.
  - Each field is a `### <field label as the form words it>` heading, followed by its value alone in a plain ``` fence. Nothing else goes inside the fence: no bullets, bold or quotes. Use one fence per field, even for short values.
  - Put advice about a field (which option to pick, what to check) on a line above the fence, never inside it.
  - Put `[↑ Top](#quick-links)` on its own line after every paste-ready block.
  - Include the cover letter body as a fenced block (no letterhead or date) whenever there's a cover letter, for forms that want it pasted.
  - Use the profile's "Application defaults" for standard answers (availability, notice, salary, police check and so on).
  - Before the form is known, include the likely fields. Once the user shares the real form, trim Paste-ready to exactly its fields, in its order and with its labels.

## Ground rules
- Never ask for ID documents or passwords in chat. The user uploads those themselves.
- Draft outgoing emails and messages for the user to send. Never send them.
- Report what was and wasn't checked honestly, and flag any claim you couldn't verify.
