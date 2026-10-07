#!/usr/bin/env python3
"""Totallympics LA28 상세 랭킹을 정적 JSON으로 갱신한다.

GitHub Actions와 로컬 PC에서 같은 방식으로 실행된다. 외부 패키지가 필요 없다.
"""
from __future__ import annotations

import concurrent.futures
import datetime as dt
import html
import json
import re
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "la28-ranking-details.json"
OVERVIEW = "https://totallympics.com/qualification-tracker/los-angeles-2028/qualification-rankings/"
UA = "koreaolympics-la28-ranking-updater/1.0 (+https://koreaolympics.github.io/)"

SPORTS = {
    "archery": ("양궁", "🏹", "olarchery.html"), "badminton": ("배드민턴", "🏸", "olbadminton.html"),
    "basketball": ("농구", "🏀", "olbasketball.html"), "basketball-3x3": ("3x3 농구", "🏀", "olbasketball.html"),
    "beach-volleyball": ("비치발리볼", "🏐", "olvolleyball.html"), "climbing": ("스포츠클라이밍", "🧗", "olclimbing.html"),
    "cricket": ("크리켓", "🏏", "olcricket.html"), "cycling-bmx": ("BMX", "🚴", "olcycling.html"),
    "cycling-mountain-bike": ("산악자전거", "🚴", "olcycling.html"), "cycling-road": ("도로사이클", "🚴", "olcycling.html"),
    "cycling-track": ("트랙사이클", "🚴", "olcycling.html"), "diving": ("다이빙", "🤿", "oldiving.html"),
    "equestrian": ("승마", "🏇", "olequestrian.html"), "fencing": ("펜싱", "🤺", "olfencing.html"),
    "golf": ("골프", "⛳", "olgolf.html"), "gymnastics-artistic": ("기계체조", "🤸", "olgymnastics.html"),
    "gymnastics-rhythmic": ("리듬체조", "🤸", "olgymnastics.html"), "gymnastics-trampoline": ("트램펄린", "🤸", "olgymnastics.html"),
    "hockey": ("필드하키", "🏑", "olhockey.html"), "judo": ("유도", "👘", "oljudo.html"),
    "modern-pentathlon": ("근대5종", "🎽", "olmodernpentathlon.html"), "rugby-sevens": ("럭비", "🏉", "olrugby.html"),
    "shooting": ("사격", "🎯", "olshooting.html"), "skateboarding": ("스케이트보딩", "🛹", "olskateboard.html"),
    "slalom-paddle": ("카누 슬라럼", "🛶", "olcanoe.html"), "sprint-paddle": ("카누 스프린트", "🛶", "olcanoe.html"),
    "squash": ("스쿼시", "⚫", "olsquash.html"), "surfing": ("서핑", "🏄", "olsurfing.html"),
    "swimming": ("마라톤 수영", "🌊", "olmarathonswim.html"), "table-tennis": ("탁구", "🏓", "oltabletennis.html"),
    "taekwondo": ("태권도", "🥋", "oltaekwondo.html"), "tennis": ("테니스", "🎾", "oltennis.html"),
    "triathlon": ("트라이애슬론", "🏅", "oltriathlon.html"), "volleyball": ("배구", "🏐", "olvolleyball.html"),
    "weightlifting": ("역도", "🏋️", "olweightlifting.html"), "wrestling": ("레슬링", "🤼", "olwrestling.html"),
}

COUNTRIES = {
 "KOR":"대한민국","JPN":"일본","CHN":"중국","TPE":"대만","HKG":"홍콩","USA":"미국","CAN":"캐나다","MEX":"멕시코","BRA":"브라질","ARG":"아르헨티나","COL":"콜롬비아","CHI":"칠레","PER":"페루","VEN":"베네수엘라","PUR":"푸에르토리코","DOM":"도미니카공화국","ITA":"이탈리아","FRA":"프랑스","GER":"독일","GBR":"영국","ESP":"스페인","POR":"포르투갈","NED":"네덜란드","BEL":"벨기에","SUI":"스위스","AUT":"오스트리아","POL":"폴란드","CZE":"체코","SVK":"슬로바키아","SLO":"슬로베니아","CRO":"크로아티아","SRB":"세르비아","GRE":"그리스","TUR":"튀르키예","UKR":"우크라이나","BUL":"불가리아","ROU":"루마니아","HUN":"헝가리","SWE":"스웨덴","NOR":"노르웨이","DEN":"덴마크","FIN":"핀란드","IRL":"아일랜드","ISR":"이스라엘","AZE":"아제르바이잔","GEO":"조지아","KAZ":"카자흐스탄","UZB":"우즈베키스탄","KGZ":"키르기스스탄","TJK":"타지키스탄","MGL":"몽골","IRI":"이란","IRQ":"이라크","JOR":"요르단","KSA":"사우디아라비아","QAT":"카타르","UAE":"아랍에미리트","IND":"인도","INA":"인도네시아","MAS":"말레이시아","THA":"태국","VIE":"베트남","PHI":"필리핀","SGP":"싱가포르","AUS":"호주","NZL":"뉴질랜드","EGY":"이집트","MAR":"모로코","TUN":"튀니지","ALG":"알제리","RSA":"남아프리카공화국","NGR":"나이지리아","KEN":"케냐","ETH":"에티오피아","IOC":"IOC 비승인"
}
STATUS = {"Ranking Quota":"랭킹 쿼터","Ranking quota":"랭킹 쿼터","NOC Limit":"NOC 제한","Outside Cutoff":"커트라인 밖","Currently Not Eligible":"출전자격 없음","Not Eligible":"출전자격 없음","Currently Qualified":"현재 쿼터권","Already Qualified":"타 경로 출전권 확보","Qualified":"출전권 확보","Ranking Limit":"랭킹 집계 한도 밖","No Athletes Qualified":"출전권 충족 선수 없음","One Gender Missing":"성별 구성 미충족","Continental Limit":"대륙별 제한","Reallocation":"재배분 대상","Host Country Quota":"개최국 쿼터","Continental Quota":"대륙 쿼터","Additional Quota":"추가 쿼터","Eligible to compete":"출전 가능"}
REPL = [("Men's","남자"),("Women's","여자"),("Mixed","혼성"),("Individual","개인"),("Team","단체"),("Singles","단식"),("Doubles","복식"),("World Ranking","세계랭킹"),("Olympic Ranking","올림픽 랭킹"),("Qualification Ranking","예선 랭킹"),("Freestyle","자유형"),("Greco-Roman","그레코로만형"),("Boulder","볼더"),("Lead","리드"),("Speed","스피드"),("Air Rifle","공기소총"),("Air Pistol","공기권총"),("Rapid Fire Pistol","속사권총"),("Pistol","권총"),("Rifle 3 Positions","소총 3자세"),("Road Race","도로경기"),("Time Trial","독주"),("Cross-country","크로스컨트리")]

def fetch(url: str, attempts: int = 3) -> str:
    for n in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language":"en"})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if n + 1 == attempts: raise
            time.sleep(2 ** n)

class TableParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.tables=[]; self.table=None; self.row=None; self.cell=None; self.img_alt=""
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=="table": self.table=[]
        elif self.table is not None and tag=="tr": self.row=[]
        elif self.row is not None and tag in ("td","th"): self.cell=[]; self.img_alt=""
        elif self.cell is not None and tag=="img": self.img_alt=a.get("alt","")
    def handle_data(self,data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self,tag):
        if tag in ("td","th") and self.cell is not None:
            text=" ".join("".join(self.cell).split())
            self.row.append((text,self.img_alt.lstrip("."))); self.cell=None
        elif tag=="tr" and self.row is not None:
            if self.row: self.table.append(self.row)
            self.row=None
        elif tag=="table" and self.table is not None:
            self.tables.append(self.table); self.table=None

def ko_title(s):
    for a,b in REPL: s=s.replace(a,b)
    return s

def ko_status(s):
    for key, value in sorted(STATUS.items(), key=lambda item: len(item[0]), reverse=True):
        if s.startswith(key): return value + s[len(key):]
    s=re.sub(r'^(\d+) Athletes? Quota',r'선수 \1명 쿼터',s)
    return s

def detail(url):
    raw=fetch(url); p=TableParser(); p.feed(raw)
    title_m=re.search(r'<meta property="og:title" content="([^"]+)',raw)
    title=html.unescape(title_m.group(1)).split(" - Totallympics")[0] if title_m else url.rstrip('/').split('/')[-1]
    mod=re.search(r'"dateModified"\s*:\s*"([0-9-]+)',raw)
    rows=[]
    for table in p.tables:
        if not table: continue
        head=[x[0].upper() for x in table[0]]
        if len(head)>=4 and head[0]=="RANK" and ("PROJECTION" in head or "STATUS" in head):
            for row in table[1:]:
                if len(row)<4 or not row[0][0].strip().isdigit(): continue
                noc=next((x[1] for x in row if x[1]),"")
                vals=[x[0] for x in row]
                name="대한민국" if noc=="KOR" and vals[1] in ("Republic of Korea","Korea","South Korea") else vals[1]
                rows.append({"rank":vals[0],"name":name,"noc":noc,"country":COUNTRIES.get(noc,noc),"score":vals[3],"status":ko_status(vals[4]) if len(vals)>4 else ""})
            break
    parts=urlparse(url).path.split('/')
    slug=parts[parts.index('qualification-by-sport')+1]
    sport,icon,page=SPORTS.get(slug,(slug,"🏅","index1.html"))
    return {"sport":sport,"sportSlug":slug,"icon":icon,"page":page,"name":ko_title(title),"originalName":title,"source":url,"updated":mod.group(1) if mod else "","rows":rows,"korea":[r for r in rows if r["noc"]=="KOR"]}

def main():
    overview=fetch(OVERVIEW)
    paths=sorted(set(html.unescape(x) for x in re.findall(r'href="([^"]*qualification-by-sport/[^"]+-r\d+/)"',overview)))
    urls=[urljoin(OVERVIEW,p) for p in paths]
    print(f"상세 랭킹 {len(urls)}개 수집 시작")
    items=[]; errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        future={ex.submit(detail,u):u for u in urls}
        for i,f in enumerate(concurrent.futures.as_completed(future),1):
            try: items.append(f.result())
            except Exception as e: errors.append({"url":future[f],"error":str(e)})
            if i%20==0: print(f"  {i}/{len(urls)}")
    items.sort(key=lambda x:(x["sport"],x["name"]))
    payload={"generated":dt.datetime.now(dt.timezone.utc).isoformat(),"source":OVERVIEW,"rankingCount":len(items),"rowCount":sum(len(x["rows"]) for x in items),"koreaRowCount":sum(len(x["korea"]) for x in items),"rankings":items,"errors":errors}
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
    print(f"완료: {len(items)}개 랭킹, {payload['rowCount']}행, 한국 {payload['koreaRowCount']}행, 오류 {len(errors)}개")
    if len(items)<150: raise SystemExit("수집된 랭킹 수가 비정상적으로 적습니다.")

if __name__=="__main__": main()
