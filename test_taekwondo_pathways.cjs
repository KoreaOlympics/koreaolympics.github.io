const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const api=require('../js/taekwondo-pathways.js');
const data=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/taekwondo-pathways.json'),'utf8'));
assert.equal(api.rankingPoints(140,'2025-10','2026-06'),140);
assert.equal(api.rankingPoints(140,'2025-10','2026-07'),0);
assert.equal(api.rankingPoints(60,'2026-06','2026-06'),0);
assert.equal(api.rankingPoints(60,'2026-06','2027-06'),60);
assert.equal(api.rankingPoints(60,'2026-06','2027-07'),30);
assert.equal(api.rankingPoints(60,'2026-06','2028-01'),30);
assert.equal(api.rankingPoints(140,'2027-07','2028-01'),140);
assert.equal(api.rankingPoints(140,'2027-07','2028-07'),0);
assert.equal(api.meritAfterDeduction(151),75.5);
assert.throws(()=>api.rankingPoints(-1,'2027-07','2028-01'));
const event=id=>data.events.find(e=>e.id===id);
assert.equal(Object.keys(data.weights).length,8);
assert.equal(event('wc25').medals.length,64);
assert.equal(event('gsc25').medals.length,24);
assert.equal(event('women26').medals.length,32);
assert.equal(data.events.reduce((n,e)=>n+e.medals.length,0),268);
assert.equal(data.events.length,22);
for(const id of ['gp26a','gp26b']){
  const entrants=event(id).participants;
  assert.equal(Object.keys(entrants).length,8);
  for(const [weight,names] of Object.entries(entrants)){
    assert.ok(names.length>=16&&names.length<=32);
    assert.equal(new Set(names.map(a=>a.name.toLowerCase())).size,names.length);
    for(const medallist of event(id).medals.filter(a=>a.weight===weight)){
      const key=s=>s.toLowerCase().replace(/[^a-z0-9]/g,'');
      assert.ok(names.some(a=>key(a.name)===key(medallist.name)),`${id}: missing medallist ${medallist.name}`);
    }
  }
}
assert.equal(event('gp26c').partialResults,true);
assert.equal(new Set(event('gp26c').medals.map(x=>x.weight)).size,3);
for(const e of data.events){
  if(e.start>data.asOf)assert.equal(e.medals.length,0,'Future medals must remain empty');
  if(!e.placements)continue;
  for(const rows of Object.values(e.placements)){
    assert.equal(rows.length,8);
    assert.deepEqual(rows.map(x=>x.place),[1,2,3,4,5,6,7,8]);
    const seen=new Set();const invite=rows.filter(x=>{if(seen.has(x.country))return false;seen.add(x.country);return true;}).slice(0,3);
    assert.equal(invite.length,3);assert.equal(new Set(invite.map(x=>x.country)).size,3);
  }
}
// Two Korean medals at Charlotte M-58 are one Challenge invitation, with Italy moving up.
const m58=event('gpc1').placements['Men -58kg'];
assert.equal(m58[0].country,'KOR');assert.equal(m58[1].country,'KOR');
assert.equal(m58[3].country,'ITA');
for(const w of Object.values(data.weights)){
  assert.equal(event('wc25').medals.filter(a=>w.worldWeights.includes(a.weight)).length,8);
  for(const id of ['gpc1','gpc2','gpc3','gsc25'])assert.equal(event(id).medals.filter(a=>a.weight===w.olympic).length,3);
}
console.log('Passed: ranking reset/decay, 8 weights, 268 medals, 192 top-8 placements, invitation country limits, future/partial states.');
