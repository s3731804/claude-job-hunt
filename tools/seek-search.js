// Run in the in-app browser on an au.seek.com page.
// Prepend the output of `python3 tools/ledger.py prefix seek` (DAYS, EXPECT, LOCATION, TERMS, BAD, MAX_PAY_K from me/config.json).
// The seen list lives in this site's localStorage ("jobLedger:v1", {id: "YYYY-MM-DD"}), so it never passes through messages.
// If the browser's count doesn't match the ledger, this returns "RESEED ..." and does nothing else; reseed with
//   localStorage.setItem('jobLedger:v1', '<output of ledger.py seen seek>')
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
const highPay = s => { const m = s.replace(/,/g, '').match(/\$?(\d{2,3})(?:k|\d{3})/i); return m && +m[1] >= MAX_PAY_K; };
const parser = new DOMParser();
const found = {};
for (const slug of TERMS) {
  for (const page of [1, 2]) {
    const html = await (await fetch(`/${slug}-jobs/${LOCATION}?daterange=${DAYS}${page > 1 ? '&page=' + page : ''}`)).text();
    parser.parseFromString(html, 'text/html').querySelectorAll('article').forEach(card => {
      const id = card.getAttribute('data-job-id') || (card.querySelector('a[href*="/job/"]')?.getAttribute('href').match(/job\/(\d+)/) || [])[1];
      if (!id || found[id] || seen[id]) return;
      const get = k => card.querySelector(`[data-automation="${k}"]`)?.textContent.trim() || '';
      found[id] = [get('jobTitle'), get('jobCompany'), get('jobSalary'), get('jobListingDate'), get('jobLocation')];
    });
  }
}
const keep = Object.fromEntries(Object.entries(found).filter(([, j]) => !BAD.test(j[0]) && !highPay(j[2])));
const filtered = Object.keys(found).filter(id => !keep[id]);
for (const id of [...Object.keys(keep), ...filtered]) seen[id] = today;
localStorage.setItem(KEY, JSON.stringify(seen));
result = JSON.stringify({ new: Object.entries(keep).map(([id, j]) => [id, ...j].join('|')), filtered });
}
}
result;
