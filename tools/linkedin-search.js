// Run in the in-app browser on a www.linkedin.com page (the public job feed needs no login).
// Prepend the output of `python3 tools/ledger.py prefix linkedin` (DAYS, EXPECT, LOCATIONS, TERMS, ENTRY_TERMS, BAD from me/config.json).
// The seen list lives in this site's localStorage ("jobLedger:v1", {id: "YYYY-MM-DD"}), so it never passes through messages.
// If the browser's count doesn't match the ledger, this returns "RESEED ..." and does nothing else; reseed with
//   localStorage.setItem('jobLedger:v1', '<output of ledger.py seen linkedin>')
// then run it again. Every ID it returns (new and filtered) is added to the browser list, so add them all to the ledger afterwards.
var result;
{
const KEY = 'jobLedger:v1';
const today = new Date().toLocaleDateString('en-CA');
const cutoff = new Date(Date.now() - 35 * 86400000).toLocaleDateString('en-CA');
let seen = {};
try { seen = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) {}
for (const [id, d] of Object.entries(seen)) if (d < cutoff) delete seen[id];
if (Object.keys(seen).length !== EXPECT) {
  result = `RESEED: browser has ${Object.keys(seen).length}, ledger has ${EXPECT}`;
} else {
const parser = new DOMParser();
const sleep = ms => new Promise(r => setTimeout(r, ms));
const found = {};
for (const loc of LOCATIONS) for (const kw of TERMS) {
  for (const start of [0, 25]) {
    try {
      const url = `/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=${encodeURIComponent(kw)}&location=${encodeURIComponent(loc)}&f_TPR=r${DAYS * 86400}${ENTRY_TERMS.includes(kw) ? '&f_E=1%2C2' : ''}&start=${start}`;
      const html = await (await fetch(url)).text();
      parser.parseFromString(html, 'text/html').querySelectorAll('li').forEach(li => {
        const urn = li.querySelector('[data-entity-urn]')?.getAttribute('data-entity-urn') || '';
        const id = (urn.match(/(\d{8,})/) || (li.querySelector('a[href*="/jobs/view/"]')?.href.match(/(\d{8,})/)) || [])[1];
        if (!id || found[id] || seen[id]) return;
        const get = s => li.querySelector(s)?.textContent.trim().replace(/\s+/g, ' ') || '';
        found[id] = [get('.base-search-card__title'), get('.base-search-card__subtitle'), get('.job-search-card__location'), get('time')];
      });
    } catch (e) {}
    await sleep(400);
  }
}
const keep = Object.fromEntries(Object.entries(found).filter(([, j]) => !BAD.test(j[0])));
const filtered = Object.keys(found).filter(id => !keep[id]);
for (const id of [...Object.keys(keep), ...filtered]) seen[id] = today;
localStorage.setItem(KEY, JSON.stringify(seen));
result = JSON.stringify({ new: Object.entries(keep).map(([id, j]) => [id, ...j].join('|')), filtered });
}
}
result;
