(async()=>{
 const box=document.querySelector('[data-ijf-category]');if(!box)return;
 const p=document.createElement('p');box.replaceChildren(box.querySelector('h2'),p);
 try{const res=await fetch('data/ijf-ranking.json');if(!res.ok)throw Error(res.status);const data=await res.json(),c=data.categories[box.dataset.ijfCategory];if(!c)throw Error('missing category');
 p.textContent=(c.kind==='olympic'?'올림픽 랭킹 참고 명단':'세계랭킹 참고 명단 · 올림픽 전용 랭킹 미공개')+' | 세계랭킹 버전 '+(data.worldRankingVersion||'미확인')+' | 수집 '+data.checkedAt+' · 참가 자격·국가 선택·동점 규정에 따라 최종 선발은 달라집니다.';
 const wrap=document.createElement('div');wrap.style.overflowX='auto';const table=document.createElement('table');table.className='data ijf-compact';
 const cols=document.createElement('colgroup');['18%','18%','48%','16%'].forEach(width=>{const col=document.createElement('col');col.style.width=width;cols.append(col)});table.append(cols);
 const head=table.createTHead().insertRow();['NOC 순번','IJF 순위','선수 · 성','NOC'].forEach(t=>{const th=document.createElement('th');th.scope='col';th.textContent=t;head.append(th)});
 const surname=name=>{const words=String(name||'').trim().split(/\s+/);const upper=words.filter(w=>/\p{L}/u.test(w)&&w===w.toLocaleUpperCase()&&w!==w.toLocaleLowerCase());return upper.length?upper.join(' '):words[words.length-1]||''};
 const body=table.createTBody();c.athletes.forEach((a,i)=>{const tr=body.insertRow();[i+1,a.rank,surname(a.name),a.noc].forEach((v,j)=>{const td=tr.insertCell();td.textContent=v;if(j===2){td.title=a.name;td.setAttribute('aria-label',a.name);td.tabIndex=0}})});wrap.append(table);box.append(wrap);
 const note=document.createElement('p');note.className='small';note.textContent='NOC 순번은 국가별 제한 적용 후 순서입니다. 선수는 성만 표시하며, 이름에 마우스를 올리면 전체 이름을 확인할 수 있습니다.';box.append(note);
 const a=document.createElement('a');a.href=c.source;a.textContent='IJF 공식 원문';box.append(a);
 }catch(e){p.textContent='랭킹 수집 자료를 불러오지 못했습니다. IJF 공식 랭킹을 확인해 주세요.';const a=document.createElement('a');a.href='https://www.ijf.org/wrl';a.textContent='공식 랭킹';box.append(a)}
})();
