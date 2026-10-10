const assert = require('node:assert/strict');
const {qualify} = require('../js/fencing-quota.js');
function ranking() {
  return Array.from({length:30},(_,i)=>({code:'T'+(i+1),rank:i+1,points:300-i,zone:i<4?'Europe':['Asia-Oceania','Africa','America','Europe'][(i-4)%4]}));
}
let teams=ranking();teams[1].code='KOR';
assert.equal(qualify(teams).selected.find(t=>t.code==='KOR').route,'세계 상위 4팀');
assert.equal(qualify(teams).selected.length,8);
teams=ranking();teams[4].code='KOR';
assert.equal(qualify(teams).selected.find(t=>t.code==='KOR').route,'아시아·오세아니아 존 몫');
teams[4].code='JPN';teams[8].code='KOR';
assert.equal(qualify(teams).selected.some(t=>t.code==='KOR'),false);
teams=ranking();teams.filter(t=>t.zone==='Africa').forEach(t=>t.zone='Europe');
assert.equal(qualify(teams).selected.length,8);
assert.equal(qualify(teams).selected.find(t=>t.route==='빈 존 차순위 배정').rank,8);
teams=ranking();teams.filter(t=>t.zone==='Asia-Oceania').forEach(t=>t.zone='Europe');teams[23].zone='Asia-Oceania';teams[23].code='KOR';
assert.equal(qualify(teams).selected.some(t=>t.code==='KOR'),true);
teams[23].zone='Europe';teams[23].code='T24';teams[24].zone='Asia-Oceania';teams[24].code='KOR';
assert.equal(qualify(teams).selected.some(t=>t.code==='KOR'),false);
teams=ranking();teams[4].rank=4;
assert.equal(qualify(teams).unresolved,true);
teams=ranking();teams[8].rank=5;
assert.equal(qualify(teams).unresolved,true);
assert.throws(()=>qualify(ranking().slice(0,10)));
teams=ranking();teams[5].zone='Unknown';assert.throws(()=>qualify(teams));
const data=require('../data/fie-team-ranking.json');
for(const event of data.events) {const r=qualify(event.teams);assert.equal(r.unresolved,false);assert.equal(r.selected.length,8);assert.equal(new Set(r.selected.map(t=>t.code)).size,8);console.log(event.label, event.teams.find(t=>t.code==='KOR').rank, r.selected.find(t=>t.code==='KOR')?.route);}
console.log('Quota tests passed: top four, zones, vacant zone, 24th/25th boundary, ties, incomplete input, six official snapshots');
