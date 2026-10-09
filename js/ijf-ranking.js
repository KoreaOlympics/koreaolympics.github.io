(async()=>{
 const box=document.querySelector('[data-ijf-category]');if(!box)return;
 const p=document.createElement('p');box.replaceChildren(box.querySelector('h2'),p);
 try{const res=await fetch('data/ijf-ranking.json');if(!res.ok)throw Error(res.status);const data=await res.json(),c=data.categories[box.dataset.ijfCategory];if(!c)throw Error('missing category');
 p.textContent=(c.kind==='olympic'?'올림픽 랭킹 참고 명단':'세계랭킹 참고 명단 · 올림픽 전용 랭킹 미공개')+' | 세계랭킹 버전 '+(data.worldRankingVersion||'미확인')+' | 수집 '+data.checkedAt+' · 참가 자격·국가 선택·동점 규정에 따라 최종 선발은 달라집니다.';
 const wrap=document.createElement('div');wrap.style.overflowX='auto';const table=document.createElement('table');table.className='data';
 const head=table.createTHead().insertRow();['NOC 제한 후','IJF 순위','선수','NOC','점수','직전 대비'].forEach(t=>{const th=document.createElement('th');th.scope='col';th.textContent=t;head.append(th)});
 const body=table.createTBody();c.athletes.forEach((a,i)=>{const tr=body.insertRow();[i+1,a.rank,a.name,a.noc,a.points,a.previousRank-a.rank].forEach(v=>tr.insertCell().textContent=v)});wrap.append(table);box.append(wrap);
 const a=document.createElement('a');a.href=c.source;a.textContent='IJF 공식 원문';box.append(a);
 }catch(e){p.textContent='랭킹 수집 자료를 불러오지 못했습니다. IJF 공식 랭킹을 확인해 주세요.';const a=document.createElement('a');a.href='https://www.ijf.org/wrl';a.textContent='공식 랭킹';box.append(a)}
})();
