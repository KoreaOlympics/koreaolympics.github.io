/* npm install playwright; npx playwright install chromium
   node scripts/update-racket-rankings.cjs [--sport badminton|tabletennis] [--edge] */
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../..'),events={ms:'남자 단식',ws:'여자 단식',md:'남자 복식',wd:'여자 복식',xd:'혼합복식'};
const flash={ms:'bwf-singles-men',ws:'bwf-singles-women',md:'bwf-doubles-men',wd:'bwf-doubles-women',xd:'bwf-mixed-doubles'};
const noc={Bulgaria:'BUL',Thailand:'THA',France:'FRA',Taiwan:'TPE',Indonesia:'INA',China:'CHN',Denmark:'DEN',Japan:'JPN',Canada:'CAN',Singapore:'SGP',India:'IND','Hong Kong':'HKG','South Korea':'KOR',Malaysia:'MAS',USA:'USA',England:'ENG',Scotland:'SCO',Germany:'GER',Sweden:'SWE',Spain:'ESP',Vietnam:'VIE',Australia:'AUS',Brazil:'BRA',Belgium:'BEL',Finland:'FIN',Ireland:'IRL',Israel:'ISR','Sri Lanka':'SRI',Croatia:'CRO','El Salvador':'ESA',Poland:'POL',Guatemala:'GUA',Azerbaijan:'AZE',Italy:'ITA',Netherlands:'NED',Ukraine:'UKR',Russia:'RUS',Switzerland:'SUI','Czech Republic':'CZE',Slovakia:'SVK',Hungary:'HUN',Mexico:'MEX',Egypt:'EGY',Turkey:'TUR',Portugal:'POR',Romania:'ROU',Austria:'AUT'};
function validate(rows){if(rows.length!==20||rows.some((r,i)=>r.rank!==i+1||!r.names.length||!r.noc||!Number.isFinite(r.points)))throw Error('상위 20위 검증 실패');}
function save(sport,data){const dir=path.join(root,'data');fs.mkdirSync(dir,{recursive:true});const dest=path.join(dir,sport+'-rankings.json'),tmp=dest+'.tmp';fs.writeFileSync(tmp,JSON.stringify(data,null,2)+'\n');fs.renameSync(tmp,dest);}
async function run(){const ix=process.argv.indexOf('--sport'),sports=ix>=0?[process.argv[ix+1]]:['badminton','tabletennis'];let browser;let failures=0;
try{for(const sport of sports){try{const data={sport,fetchedAt:new Date().toISOString(),events:{}};
if(sport==='badminton'){
browser??=await chromium.launch({headless:true,...(process.argv.includes('--edge')?{executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'}:{})});
for(const [key,label] of Object.entries(events)){const page=await browser.newPage(),url='https://www.flashscore.com/badminton/rankings/'+flash[key]+'/';
try{await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});await page.locator('.rankingTable__row').nth(19).waitFor({timeout:30000});
const raw=await page.locator('.rankingTable__row').evaluateAll(rs=>rs.map(r=>({rank:parseInt(r.querySelector('[class*="--rank"]')?.textContent),names:[...r.querySelectorAll('.rankingTable__href')].map(x=>x.textContent.trim()),countries:[...r.querySelectorAll('.rankingTable__nationality')].map(x=>x.textContent.trim()),points:Number(r.querySelector('[class*="--points"]')?.textContent.replace(/[^\d]/g,''))})));
const date=await page.locator('body').innerText().then(t=>t.match(/\((\d{2}\.\d{2}\.\d{4})\)/)?.[1]);if(!date)throw Error('랭킹 발표일 없음');
const rows=raw.filter(r=>r.rank>=1&&r.rank<=20).map(r=>({...r,noc:[...new Set(r.countries.map(c=>noc[c]||c))].join('/')}));validate(rows);if(rows.some(r=>r.noc.length>7))throw Error('알 수 없는 국적: '+JSON.stringify(rows.filter(r=>r.noc.length>7))); 
data.events[key]={label,date,source:url,rows,koreaOutsideTop20:raw.filter(r=>r.rank>20&&r.countries.includes('South Korea')).map(r=>({...r,noc:'KOR'}))};
}finally{await page.close();}}
}else if(sport==='tabletennis'){
const base='https://wtt-mobile-app-services-api.azurewebsites.net';
const date=await fetch(base+'/api/cms/RankingDate/SEN').then(r=>{if(!r.ok)throw Error('WTT '+r.status);return r.json()});if(date.Status!=='Published')throw Error('미발표 랭킹');
for(const [key,label] of Object.entries(events)){const url=base+'/api/cms/GetRanking'+(['ms','ws'].includes(key)?'Individuals':'Pairs')+'?TopN=20&CategoryCode=SEN&SubEventCode='+key.toUpperCase()+'&RankingYear='+date.RankingYear+'&RankingMonth='+date.RankingMonth+'&RankingWeek='+date.RankingWeek;
const j=await fetch(url).then(r=>{if(!r.ok)throw Error('WTT '+r.status);return r.json()});if(j.StatusCode!==200)throw Error('WTT 응답 오류');
const rows=j.Result.map(r=>({rank:Number(r.RankingPosition),names:r.PlayerName?[r.PlayerName]:[r.PlayerName1,r.PlayerName1d],noc:r.AssociationCountryCode||[...new Set([r.AssociationCountryCode1,r.AssociationCountryCode1d])].join('/'),points:Number(r.Points||r.RankingPointsYTD)})).sort((a,b)=>a.rank-b.rank);validate(rows);
if(j.Result.some(r=>r.RankingYear!==date.RankingYear||r.RankingWeek!==date.RankingWeek))throw Error('종목별 발표 주차 불일치');
data.events[key]={label,date:date.RankingStatusDate,year:date.RankingYear,week:date.RankingWeek,source:url,rows};}
}else throw Error('지원하지 않는 종목');
save(sport,data);console.log(sport+': 5종목 × 20위 갱신 완료');
}catch(e){failures++;console.error(sport+': '+e.message+' — 기존 파일 유지');}}}finally{await browser?.close();}if(failures)process.exitCode=1;}
run();
