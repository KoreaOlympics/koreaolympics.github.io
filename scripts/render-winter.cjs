const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const {render}=require('../js/winter-live.js');
const data=JSON.parse(fs.readFileSync(path.join(root,'data/winter-live.json'),'utf8'));
for(const [file,key] of Object.entries({'wishorttrack.html':'short-track','wifigure.html':'figure-skating','wispeedskating.html':'speed-skating','wicurling.html':'curling'})){
  const p=path.join(root,file);let s=fs.readFileSync(p,'utf8');
  const panel=`<!-- winter-live:start --><section id="season-live"><h2>2026–27 일정 · 최신 성적</h2><p id="winter-fetch-state" class="note" aria-live="polite"></p><div data-winter-sport="${key}">${render(data,key)}</div></section><!-- winter-live:end -->`;
  if(s.includes('<!-- winter-live:start -->'))s=s.replace(/<!-- winter-live:start -->[\s\S]*?<!-- winter-live:end -->/,panel);
  else s=s.replace('<section id="overview">',panel+'\n<section id="overview">');
  if(!s.includes('href="#season-live"'))s=s.replace('<strong>목차</strong><ol>','<strong>목차</strong><ol><li><a href="#season-live">2026–27 일정 · 최신 성적</a></li>');
  if(!s.includes('js/winter-live.js'))s=s.replace('</body>','<script src="./js/winter-live.js" defer></script></body>');
  s=s.replaceAll('기준 2026.10.15','기준 2026.10.16');
  if(key==='figure-skating')s=s.replace('2026 대회는 네벨호른 트로피','2026 대회는 베이징 Skate to Milano 예선');
  fs.writeFileSync(p,s);
}
let p=path.join(root,'index.html');fs.writeFileSync(p,fs.readFileSync(p,'utf8').replaceAll('롱트랙(스피드스케이팅)','스피드스케이팅'));
console.log('Rendered 4 winter pages and index label');
