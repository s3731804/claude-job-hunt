# Job search sweep: subagent brief

You screen new job listings for the user. Their profile is `me/personal-profile.md`, but read only these parts:
- **Identity**
- **Education** (for units, grades and certs)
- **Targets**
- the **"Years of experience"** line under Work history
- the **"Doesn't have"** line under Projects

All paths below are relative to the folder containing `tools/` (the project root).

Don't write or edit any files. Only run the commands below, then report back.

## Use your own browser tab
The user and the main session may be using the browser pane while you work. A browser call without `tabId` goes to whichever tab is in front, which may not be yours.
- First, call `mcp__Claude_Browser__tabs_create` (no `foreground`, so it opens in the background and the main session's tab stays in front), and keep the `tabId` it returns. Never call `tabs_select` on it. If it says the Browser pane isn't open, call `mcp__Claude_Browser__navigate` with `{"url": "https://au.seek.com/"}` instead: that opens the pane, and the `tabId` in its result is your tab.
- Pass that `tabId` on **every** `mcp__Claude_Browser__navigate` and `mcp__Claude_Browser__javascript_tool` call, for example `{"url": "https://au.seek.com/", "tabId": "<your tabId>"}`. Never leave it out.
- When you're finished (or if you stop early), close it with `mcp__Claude_Browser__tabs_close` and that `tabId`.

## Steps
1. Run `python3 tools/ledger.py prefix seek` and `python3 tools/ledger.py prefix linkedin`. Each prints one `var …;` line, called a **prefix**.
2. Read `tools/seek-search.js`, `tools/linkedin-search.js` and `tools/job-details.js`.
3. Run the SEEK search:
   1. Open https://au.seek.com/ with `mcp__Claude_Browser__navigate` in your tab.
   2. Run the SEEK prefix plus `seek-search.js` with `mcp__Claude_Browser__javascript_tool`.
   3. If it returns `RESEED: …`:
      1. Run `python3 tools/ledger.py seen seek`.
      2. Run `localStorage.setItem('jobLedger:v1', '<that JSON>')` on the SEEK page.
      3. Run the search again.
4. Run the LinkedIn search the same way:
   1. Open https://www.linkedin.com/jobs/search/?keywords=developer in your tab.
   2. Run the LinkedIn prefix plus `linkedin-search.js`.
   3. Reseed the same way if it asks, using `ledger.py seen linkedin`.
5. Each search returns `{new: ["id|title|…"], filtered: [ids]}`. For the `new` IDs, run `job-details.js` on the matching site, starting it with `var SITE = 'seek', IDS = [...];` (or `'linkedin'`).
6. Put each new listing in a tier based on the ad text and the profile's Targets, not the title:
   - **A:** a good fit from Targets, and the ad asks for no more experience than the user has (or says projects count).
   - **B:** a Targets stretch, or asks for slightly more experience, or matches their stack only partly.
   - **C:** a Targets backup, or something under "Open to".
   - **C (off-target):** a genuine entry-level role that isn't in Targets or Avoid, but whose main requirements match skills the profile's Education backs up (units, grades, certs). Start the reason with "off-target:" and quote both the requirement and the matching unit or cert. If Targets says "Suggestions outside Targets: no", rule these out instead.
   - **Ruled out:** anything under Targets → Avoid, a firm experience requirement well above theirs, or a hard requirement from "Doesn't have".
   - **Unread:** you couldn't get the details.

   Be strict with B. If a listing would only be a reach, rule it out. But don't rule a listing out just for being outside Targets when it fits C (off-target).

## Report back (concisely)
- **Sanity line:**
  - DAYS
  - EXPECT for each site (from the prefixes)
  - whether a reseed was needed
  - that every browser call used your tabId, and the tab was closed
  - how many new and filtered IDs each site returned
- **Table:** job_id | site | company — role | link | tier | one-line reason that quotes the requirement you based it on.
- **Ledger lines:** every returned ID, in the form `<id> <site> <status>`, ready for `ledger.py add`:
  - status `shortlisted` for A, B and C
  - `unread` for Unread
  - `screened-out` for Ruled out
  - `title-filtered` for the IDs in `filtered`
