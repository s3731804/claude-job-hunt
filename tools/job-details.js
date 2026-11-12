// Pulls the requirement lines from each ad so they can be screened without opening every page.
// SEEK: run on au.seek.com with SITE = 'seek'. LinkedIn: run on www.linkedin.com with SITE = 'linkedin'.
// Prepend: var SITE = 'seek' | 'linkedin', IDS = ['...'];
// Fetches one at a time with a pause, because parallel requests get rate-limited.
var result;
{
const parser = new DOMParser();
const sleep = ms => new Promise(r => setTimeout(r, ms));
const out = [];
for (const id of IDS) {
  let text = '', meta = '';
  for (let attempt = 0; attempt < 2 && !text; attempt++) {
    try {
      const url = SITE === 'seek' ? '/job/' + id : '/jobs-guest/jobs/api/jobPosting/' + id;
      const doc = parser.parseFromString(await (await fetch(url)).text(), 'text/html');
      if (SITE === 'seek') {
        text = doc.querySelector('[data-automation="jobAdDetails"]')?.textContent || '';
        meta = ['job-detail-title', 'job-detail-salary', 'job-detail-location', 'job-detail-work-type']
          .map(k => doc.querySelector(`[data-automation="${k}"]`)?.textContent || '').join(' · ');
      } else {
        text = doc.querySelector('.show-more-less-html__markup')?.textContent || '';
        meta = [...doc.querySelectorAll('.description__job-criteria-item')].map(x => x.textContent.replace(/\s+/g, ' ').trim()).join('; ');
      }
      text = text.replace(/\s+/g, ' ');
    } catch (e) {}
    if (!text) await sleep(2500);
  }
  const reqs = [...text.matchAll(/[^.]{0,40}(\d+\s*(?:\+|–|-|to)?\s*\d*\+?\s*years?|graduate|junior|entry[- ]level|early.career|no experience|clearance|citizen|degree)[^.]{0,80}/gi)]
    .map(m => m[0].trim()).filter(x => !/founded|since|over \d+ years|more than \d+ years|in business/i.test(x)).slice(0, 4);
  out.push(`${id} | ${meta.slice(0, 140)} | ${reqs.join(' // ').slice(0, 400) || (text ? text.slice(0, 200) : 'COULD NOT READ')}`);
  await sleep(SITE === 'seek' ? 300 : 1200);
}
result = out.join('\n');
}
result;
