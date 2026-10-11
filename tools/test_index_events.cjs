const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new vm.Script(m[1]);
const source=html.match(/<script id="featured-events-script">([\s\S]*?)<\/script>/)[1];
function render(day){const box={innerHTML:''};class TestDate extends Date{constructor(...a){super(...(a.length?a:[day+'T12:00:00']));}}vm.runInNewContext(source,{Date:TestDate,document:{getElementById:()=>box,addEventListener:()=>{}},setInterval:()=>{}});return box.innerHTML;}
let x=render('2026-10-11');assert(x.includes('상하이'));assert(x.includes('로테르담'));assert(!x.includes('라크로스'));assert(!x.includes('바쿠'));assert.equal((x.match(/class="event-card"/g)||[]).length,4);
x=render('2026-10-18');assert(!x.includes('상하이'));assert(!x.includes('로테르담'));assert(x.includes('닝보'));
assert(render('2027-01-01').includes('확인 대기'));
assert(html.includes('&&a>today;'));assert(html.includes('id="featured-events"'));
console.log('PASS: JS syntax, future-only featured cards, automatic expiry, empty state');
