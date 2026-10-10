(function(root){
  'use strict';
  function rankingPoints(base,eventMonth,rankingMonth){
    if(!Number.isFinite(base)||base<0||!/^\d{4}-\d{2}$/.test(eventMonth)||!/^\d{4}-\d{2}$/.test(rankingMonth))throw new Error('Invalid points or month');
    const index=s=>Number(s.slice(0,4))*12+Number(s.slice(5))-1;
    const e=index(eventMonth),r=index(rankingMonth);
    if(r<=e)return 0;
    if(e<index('2026-06')&&r>=index('2026-07'))return 0;
    if(e>=index('2026-06')&&e<index('2028-06')&&r>=index('2028-07'))return 0;
    return r-e>=13?base*.5:base;
  }
  const api={rankingPoints,meritAfterDeduction:p=>Math.round(p*50)/100};
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(!root.document)return;
  const select=root.document.getElementById('merit-place'),output=root.document.getElementById('merit-result');
  if(select&&output){const render=()=>{const p=Number(select.value);output.textContent=`감점 전 ${p} · 50% 감점 후 ${api.meritAfterDeduction(p)}`;};select.addEventListener('change',render);render();}
})(typeof window==='object'?window:globalThis);
