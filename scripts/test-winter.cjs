const assert=require('node:assert/strict');
const {render}=require('../js/winter-live.js');
const data={season:'2026/2027',sports:{curling:{checked_at:new Date().toISOString(),status:'ok',events:[
  {start:'2026-03-01',end:'2026-03-08',name:'OLD',url:'https://example.com',location:'A'},
  {start:'2026-10-29',end:'2026-11-03',name:'CROSS_MONTH',url:'https://example.com',location:'B'},
  {start:'2027-01-01',end:'2027-01-03',name:'FUTURE',url:'https://example.com',location:'C'}
],results:[{athlete:'Korean',country:'KOR',event:'E',source:'https://example.com',date:'2026-10-16'},
{athlete:'<script>alert(1)</script>',country:'USA',event:'E',source:'javascript:alert(1)',date:'2026-10-16'}]}}};
const all=render(data,'curling',{today:'2026-10-16'});
assert(!all.includes('>OLD'));
assert(all.includes('CROSS_MONTH')&&all.includes('FUTURE'));
assert(all.includes('&lt;script&gt;')&&!all.includes('href="javascript:'));
const filtered=render(data,'curling',{today:'2026-11-01',month:'2026-11',country:'KOR',upcoming:'yes'});
assert(filtered.includes('CROSS_MONTH')&&!filtered.includes('>FUTURE'));
assert(filtered.includes('Korean')&&!filtered.includes('&lt;script&gt;'));
assert(filtered.includes('value="KOR" selected'));
const empty=render(data,'curling',{today:'2028-01-01',upcoming:'yes',country:'JPN'});
assert(empty.includes('표시할 자료가 없습니다'));
data.sports.curling.status='error';
assert(render(data,'curling').includes('이전 자료 유지'));
data.sports['short-track']=data.sports.curling;
assert(render(data,'short-track').includes('2026 세계선수권 우승 기록'));
const fs=require('node:fs'),path=require('node:path');
for(const file of ['wishorttrack','wifigure','wispeedskating','wicurling','wisnowboard','wisliding','wiothers']){
 const html=fs.readFileSync(path.join(__dirname,'..',file+'.html'),'utf8');
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
 assert.equal(ids.length,new Set(ids).size,file+' duplicate IDs');
 for(const match of html.matchAll(/href="#([^"]+)"/g))assert(ids.includes(match[1]),file+' broken anchor');
}
console.log('PASS: seasonal dates, cross-month filters, Korean results, escaping, empty/error states and 7-page anchors');
