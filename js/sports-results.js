/* Apply the same Korean marker to legacy result tables. */
(()=>{document.querySelectorAll('.result-scroll').forEach(x=>{x.tabIndex=0;x.setAttribute('aria-label','결과표 · 가로로 스크롤 가능')});
document.querySelectorAll('table td,table th').forEach(cell=>{if(cell.closest('.ranking-table')||cell.querySelector('.athlete-entry'))return;
const text=cell.textContent.trim();const flag=cell.querySelector('[title*="South Korea"],[title*="Korea Republic"],img[alt="South Korea"],img[src*="KOR"],[data-noc="KOR"]');
if(/\bKOR\b|🇰🇷/.test(text)||flag)cell.classList.add('kor');
});})();
