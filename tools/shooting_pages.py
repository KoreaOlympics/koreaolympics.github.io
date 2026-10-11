"""Render reviewed 2025 ISSF evidence and conditional LA28 projections."""
from pathlib import Path
import json,re,html
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'data/shooting-projection.json').read_text(encoding='utf-8'))
R=D['results'];E=D['events'];C=D['competitions']
H=lambda x:html.escape(str(x),quote=True)
def names(r):
    return ' · '.join(r['memberDisplay']) if r['members'] else r['display']
def medal(r):return r['stage'] in ['F','G','B'] and r['rank']<=3
def comp(r):return C[str(r['competition'])]
def kor(event=None,typ=None):return [r for r in R if r['country']=='KOR' and (event is None or r['event']==event) and (typ is None or comp(r)['type']==typ)]
ANALYSIS={
'ARW':('핵심 금 도전','반효진 · 권은지','반효진의 세계선수권 금과 파이널 은, 권은지의 월드컵 은 2개가 함께 뒷받침한다. 한국의 가장 두꺼운 우승 경쟁 종목이다.','같은 종목의 두 선수는 금메달 두 개로 합산하지 않는다. 반효진은 뮌헨 7위, 권은지는 세계선수권 7위·파이널 6위도 기록했다.','반효진·권은지·권유나 등의 국내 선발 경쟁 → 세계대회 결선 재현 → 중국 선수와 최종 2인 대결 승률 개선.'),
'SPW':('핵심 금 도전','양지인 · 오예진','양지인은 닝보 월드컵·세계선수권을 우승했고 뮌헨 동도 획득했다. 오예진은 뮌헨·닝보 은 2개로 강력한 경쟁 후보를 형성한다.','세계선수권에서 오예진은 본선 11위, 파이널에서 오예진 4위·양지인 5위였다. 우승 능력과 결선 진출 안정성은 따로 본다.','정밀·속사 본선 합계의 안정성 확보 → 2026/27 쿼터 → 결선 마지막 시리즈 명중률·슛오프 대응.'),
'APW':('추가 금 도전','오예진 · 추가은','오예진은 2024 올림픽 금메달리스트이며 2025 닝보 동·파이널 4위를 기록했다. 추가은은 부에노스아이레스 결선 5위였다.','2025 세계선수권 오예진 본선 12위·김보미 16위·양지인 20위. 이 시즌만으로 압도적 우승 후보라고 평가하지 않는다.','본선 8위권을 반복 확보하고 Suruchi Singh·Yao Qianxun 등 우승권과 결선 격차를 줄이면 핵심군으로 승격.'),
'ARM':('메달 확장','박하준','닝보 동메달로 개인전 세계 월드컵 포디엄 능력을 확인했다.','뮌헨 본선 17위·세계선수권 28위. 단 한 차례 동메달을 지속적 금메달 우세로 확대하지 않는다.','개인 본선 결선 진출 빈도 상승과 여자 공기소총 선수와의 혼성 합계 경쟁력 확인.'),
'R3PW':('결선 기반 확장','오세희 · 임하나','세계선수권 결선에서 오세희 5위·임하나 7위. 올림픽 종목의 실제 결선 경쟁력이 확인된다.','오세희의 복사 등 비올림픽 종목 메달은 이 종목 개인 금메달 근거에 더하지 않는다. 확인한 월드컵 시즌에는 한국 메달이 없다.','세 자세 간 점수 손실을 줄여 국제대회 포디엄을 반복하고 변경된 결선 자세 전환에 적응.'),
'APMT':('혼성 메달 확장','오예진 · 홍수현','카이로 세계선수권 혼성 동메달. 개인전 성적과 별개로 팀 조합의 메달 근거가 있다.','2025 별도 동·금메달 매치 성적은 LA28의 상위 4팀 동시 결선과 같지 않다. 파트너 조합도 확정되지 않았다.','남녀 모두 개인종목 출전자격 확보 → 본선 합계 상위 4팀 → 새 동시 결선 실전 경험.'),
'ARMT':('혼성 성장 관찰','박하준 + 여자 공기소총 후보','강한 여자 공기소총 선수층과 남자 개인전 포디엄 선수를 연결할 잠재력이 있다.','2025 뮌헨·닝보 최고 한국 팀은 본선 5위, 세계선수권은 7위. 이 표본의 혼성 메달은 0개다.','대표 조합의 본선 합계 상위 4팀 진입을 반복 확인한 뒤 금 도전군으로 올린다.'),
'RFPM':('결선 성장 관찰','홍석진 · 이재균 · 이건혁','홍석진이 뮌헨 결선 6위에 올랐다.','세계선수권은 이건혁 본선 10위·이재균 12위·홍석진 14위. 2025 국제 메달 증거가 없다.','2026부터 8인 결선 확대를 활용하되 실제 포디엄과 결선 명중률 개선을 확인.'),
'APM':('근거 보강','홍수현 · 임호진 · 이원호','홍수현 세계선수권 본선 14위, 임호진 뮌헨 13위. 혼성에서 남자 선수의 역할도 중요하다.','확인한 2025 시즌에 한국 개인 결선 메달이 없었다. 혼성 동을 남자 개인전 금 도전 근거로 바꾸지 않는다.','국제 개인 결선 진출과 포디엄 성적으로 재평가.'),
'R3PM':('근거 보강','정승우 · 모대성','세계선수권 한국 최고 기록은 정승우 본선 19위였다.','확인한 2025 시즌 국제 결선·포디엄 근거가 부족하다.','2026/27 국제 본선 8위권과 쿼터 경쟁 성과 확인.'),
'TRM':('쿼터·결선 우선','박준영 등','2025 니코시아 한국 최고는 본선 45위, 로나토 55위였다.','이번 표본에서 한국 국제 결선 메달이 없었다.','올림픽 쿼터 확보와 8인 결선 진입을 우선 과제로 둔다.'),
'TRW':('쿼터·결선 우선','이보나 · 조선아 등','로나토 이보나 본선 32위, 니코시아 조선아 46위 기록을 확인했다.','이번 표본에서 한국 국제 결선 메달이 없었다.','8인 결선 기준 국제 경쟁력과 대표 선발 결과 확인.'),
'SKM':('쿼터·결선 우선','이종준 등','이종준 니코시아 본선 30위·로나토 70위였다.','이번 표본에서 한국 국제 결선 메달이 없었다.','국제 본선 점수 개선과 8인 결선 진입 확인.'),
'SKW':('쿼터·결선 우선','장국희 등','장국희 니코시아 본선 22위·로나토 30위였다.','이번 표본에서 한국 국제 결선 메달이 없었다.','국제 본선 점수 개선과 8인 결선 진입 확인.'),
'TRMT':('새 올림픽 종목 관찰','한국 트랩 남녀 조합','니코시아·로나토에서 한국 최고 조합은 모두 본선 8위였다.','스키트 혼성 성적은 LA28 트랩 혼성의 성적으로 대신할 수 없다.','남녀 트랩 개인종목 출전자격과 혼성 본선 상위 4팀 경쟁력을 함께 확인.')}
SOURCES=[('2025 성인 월드컵 일정',4530),('2025 파이널 소총·권총 참가 경로',4844),('LA28 종목 구성',4610),('LA28 쿼터 체계',4880),('LA28 결선 변경',5086),('혼성 4팀 결선',5087),('2026 도하 첫 쿼터',5085),('오예진 2024 올림픽 금',4399)]
def source_list():
    return '<ol>'+''.join(f'<li><a href="{H(c["url"])}">ISSF · {H(c["name"])} 공식 결과</a></li>' for c in C.values())+''.join(f'<li><a href="https://www.issf-sports.org/news/{n}">ISSF · {H(t)}</a></li>' for t,n in SOURCES)+'</ol>'
def overview():
    blocks=''
    for typ,label in [('wc','2025 월드컵'),('world','2025 세계선수권'),('final','2025 파이널')]:
        ms=[r for r in kor(typ=typ) if medal(r)];counts=[sum(r['rank']==i for r in ms) for i in [1,2,3]]
        blocks+=f'<article class="shoot-card"><h3>{label}</h3><p class="shoot-tally">금 {counts[0]} · 은 {counts[1]} · 동 {counts[2]}</p><p>LA28 해당 성인 개인·혼성만 집계</p></article>'
    return '<section id="baseline"><h2>2025 실적 · 올림픽 종목만</h2><div class="shoot-grid">'+blocks+'</div><p>소총·권총과 산탄총은 각 4차례 월드컵을 치렀다. 부에노스아이레스·리마는 두 분야가 함께 열린 대회이므로 개최지는 6곳이다. 파이널은 정규 월드컵과 분리한다. 세계선수권의 3인 단체전·비올림픽 거리·주니어 메달은 위 집계에서 제외한다.</p></section>'
def projection(event):
    tier,n,proof,risk,nextstep=ANALYSIS[event]
    return f'<section id="projection"><h2>LA28 전망 · {H(tier)}</h2><div class="shoot-callout"><b>{H(n)}</b><p>{H(proof)}</p></div><h3>판정을 낮추는 근거</h3><p>{H(risk)}</p><h3>2028까지 확인할 조건</h3><p>{H(nextstep)}</p><p class="small">2025 실적에 근거한 편집 분석. LA28 대표·쿼터 확정, 현재 세계랭킹 또는 통계적 금메달 확률을 의미하지 않는다. 2026 전체 시즌·2027 결과는 이 성적 표본에 포함하지 않았다.</p></section>'
def record_name(r):
    return names(r) if r['members'] else r['display']
def result_tables(event=None,medals_only=False):
    blocks=''
    for cid,c in C.items():
        rows=[r for r in kor(event) if r['competition']==int(cid) and (not medals_only or medal(r))]
        if not rows:continue
        # One result per athlete/team: final/medal outcome supersedes qualification.
        selected={}
        for r in rows:
            key=(r['event'],tuple(r['members']) if r['members'] else r['name'])
            if r['stage'] in ['G','B']:
                # Q roster key matches the named medal-match pair.
                key=(r['event'],tuple(r['members']) if r['members'] else r['name'])
            if key not in selected or r['stage']!='Q':selected[key]=r
        trs=''
        for r in sorted(selected.values(),key=lambda x:(x['event'],x['rank'])):
            stage='결선' if r['stage'] in ['F','G','B'] else '본선'
            outcome={1:'금',2:'은',3:'동'}.get(r['rank']) if medal(r) else None
            result=f'{outcome} · {r["rank"]}위' if outcome else f'{stage} {r["rank"]}위'
            q=next((q for q in rows if q['stage']=='Q' and q['event']==r['event'] and ((q['members'] and q['members']==r['members']) or q['name']==r['name'])),None)
            detail= ('본선 '+q['score']+' · ') if q and q['score'] and r['stage']!='Q' else ''
            detail+= ('결선 ' if r['stage']!='Q' else '본선 ')+r['score'] if r['score'] else ''
            label=(E[r['event']]['label']+' · ') if not event else ''
            badge=' · RPO(순위 외)' if r['rpo'] else ''
            cls=' class="shoot-medal"' if outcome else ''
            trs+=f'<tr{cls}><th scope="row">{H(record_name(r))}</th><td><span>{H(label+result+badge)}</span><small>{H(detail)} · <a href="{H(r["url"])}">공식 결과</a></small></td></tr>'
        blocks+=f'<details class="shoot-meet"{" open" if medals_only else ""}><summary>{H(c["name"])} · {H(c["start"])}</summary><table class="shoot-table"><thead><tr><th scope="col">선수·팀</th><th scope="col">성적</th></tr></thead><tbody>{trs}</tbody></table></details>'
    if not blocks:blocks='<p>수집한 공식 성인 결과표에 한국 결과 행이 없습니다. 메달 0개와 참가 사실 미확인은 구분합니다.</p>'
    return blocks
def medal_section():
    return '<section id="medals"><h2>대회별 한국 메달</h2>'+result_tables(medals_only=True)+'</section>'
def rival_section(event):
    entries={}
    for r in R:
        if r['event']!=event or r['country']=='KOR' or not medal(r) or r['rank']!=1:continue
        k=(names(r),r['country']);entries.setdefault(k,[]).append(r)
    trs=''
    for (n,c),rs in sorted(entries.items(),key=lambda x:-len(x[1])):
        desc=' · '.join(comp(r)['name'] for r in rs)
        trs+=f'<tr><th scope="row">{H(n)} <span class="shoot-noc">{H(c)}</span></th><td>{H(desc)} 금 <small><a href="{H(rs[0]["url"])}">공식 결과</a></small></td></tr>'
    return '<details class="shoot-meet"><summary>2025 국제 우승권 · 비교 대상</summary><table class="shoot-table"><thead><tr><th scope="col">선수·팀</th><th scope="col">우승 대회</th></tr></thead><tbody>'+trs+'</tbody></table><p class="small">2025 우승 실적 목록이며 현재 세계랭킹 순서가 아니다.</p></details>'
def paths():
    rows=[('반효진','세계선수권 · 여자 공기소총 금'),('권은지','뮌헨 월드컵 · 여자 공기소총 은 / 중복 우승에 따른 차순위 경로'),('양지인','닝보 월드컵 · 여자 25m 권총 금 + 세계선수권 금'),('오예진','뮌헨 월드컵 · 여자 25m 권총 은 / 차순위 경로 + 공기권총 시즌 랭킹')]
    return '<section id="paths"><h2>2025 파이널 참가 경로</h2><table class="shoot-table"><thead><tr><th scope="col">선수명</th><th scope="col">경로 대회·성적</th></tr></thead><tbody>'+''.join(f'<tr><th scope="row">{H(n)}</th><td>{H(d)}</td></tr>' for n,d in rows)+'</tbody></table><p>ISSF는 권은지와 오예진의 뮌헨 성적을 파이널 진출 경로로 공표했다. 두 선수는 뮌헨 금메달리스트가 아니다. 기존 진출자의 중복 우승 시 차순위가 진출권을 받는 규칙이다. 파이널 진출권은 LA28 출전권과 별개다.</p><p class="small"><a href="https://www.issf-sports.org/news/4844">ISSF 참가 경로 공지</a> · 최종 출전·순위는 도하 공식 결과로 대조.</p></section>'
def milestones():
    return '''<section id="road"><h2>2026–2028 · 전망을 갱신할 관문</h2><ol class="shoot-road"><li><b>2026 도하 세계선수권</b><span>첫 LA28 쿼터 대회. 2025 금메달은 이 쿼터를 확보한 성적이 아니다.</span></li><li><b>2027 세계선수권·월드컵</b><span>소총·권총 대구, 산탄총 카이로 세계선수권과 2027 월드컵에서 쿼터 및 세계 우승권의 재현을 확인한다.</span></li><li><b>2028년 5월 1일</b><span>예선 기간 종료·올림픽 랭킹 경로 판정. 종목별 NOC 최대 2명과 선수의 참가 자격을 점검한다.</span></li><li><b>2028 LA 결선</b><span>여자 공기소총·25m 권총의 핵심 금 도전, 공기권총·혼성의 추가 우승 시나리오를 갱신한다.</span></li></ol><p>혼성은 해당 개인종목에 출전할 자격을 갖춘 남녀로 구성한다. 개인 선수층이 강해도 조합의 올림픽 출전과 메달을 자동 보장하지 않는다.</p><p class="small">근거: <a href="https://www.issf-sports.org/news/4880">ISSF LA28 쿼터 체계</a> · <a href="https://www.issf-sports.org/news/5085">도하 첫 쿼터</a>. 상세 배정은 기존 <a href="./olshooting.html">전체 안내</a>의 규정 원문을 따른다.</p></section>'''
def formats():
    return '''<section id="format"><h2>2025 실적을 LA28에 옮길 때</h2><ul><li><b>혼성은 공기소총·공기권총·트랩.</b> 파리의 스키트 혼성 실적은 트랩 혼성으로 이전하지 않는다.</li><li><b>혼성 상위 4팀이 한 결선에서 경쟁.</b> 2025 금·동메달 매치의 승패와 새 형식의 메달 재현은 별도 검증이 필요하다.</li><li><b>속사권총·트랩·스키트는 결선 6명 → 8명.</b> 2025 본선 7·8위를 과거 결선 출전으로 표시하지 않는다.</li><li><b>소총3자세 결선은 자세 전환 시간 운영이 변경.</b> 본선 합계와 별개로 결선 적응을 관찰한다.</li><li><b>공기소총·공기권총 개인, 여자 25m 권총의 결선 기본 형식은 유지.</b> 핵심 한국 후보의 기존 결선 성적 비교가 상대적으로 직접적이다.</li></ul><p class="small"><a href="https://www.issf-sports.org/news/5086">ISSF · LA28 결선 형식</a></p></section>'''
def matrix():
    rows=''
    order=['ARW','SPW','APW','ARM','APMT','R3PW','ARMT','RFPM','APM','R3PM','TRM','TRW','SKM','SKW','TRMT']
    for e in order:
        v=E[e]
        tier,n,*_=ANALYSIS[e]
        ms=[r for r in kor(e) if medal(r)]
        summaries=[]
        for typ,short in [('world','세계선수권'),('wc','WC'),('final','파이널')]:
            subset=[r for r in ms if comp(r)['type']==typ]
            text=[]
            for rank,label in [(1,'금'),(2,'은'),(3,'동')]:
                count=sum(r['rank']==rank for r in subset)
                if count:text.append(label+(str(count) if count>1 else ''))
            if text:summaries.append(short+' '+'·'.join(text))
        if not summaries:
            for typ,short in [('world','세계선수권'),('wc','WC')]:
                finals=sorted({r['rank'] for r in kor(e,typ) if r['stage']=='F'})
                if finals:summaries.append(short+' 결선 '+'·'.join(map(str,finals))+'위')
        result=' / '.join(summaries) or '2025 표본 메달 없음'
        rows+=f'<tr><th scope="row"><a href="./olshooting-ev-{v["code"]}.html">{H(v["label"])}</a></th><td><b>{H(tier)}</b><span>{H(n)}</span><small>{H(result)}</small></td></tr>'
    return '<section id="events"><h2>15종목 · 금메달 도전 우선순위</h2><table class="shoot-table"><thead><tr><th scope="col">종목</th><th scope="col">한국 후보·근거</th></tr></thead><tbody>'+rows+'</tbody></table></section>'
def scenarios():
    return '''<section id="scenario"><h2>조건부 금메달 시나리오</h2><div class="shoot-grid"><article class="shoot-card"><h3>하방 · 금 0</h3><p>쿼터·대표 선발·본선·결선 어느 단계에서도 탈락할 수 있다. 과거 세계 우승도 올림픽 금을 보장하지 않는다.</p></article><article class="shoot-card"><h3>핵심 성공 · 금 1–2</h3><p>여자 공기소총과 여자 25m 권총 중 한 종목 또는 두 종목을 우승하는 가정. 반효진·권은지 또는 양지인·오예진을 선수 수대로 더하지 않는다.</p></article><article class="shoot-card"><h3>확장 성공 · 금 3 이상</h3><p>핵심 두 종목 외 공기권총·혼성·남자 공기소총 등에서 추가 우승이 필요하다. 해당 종목의 2026/27 포디엄 재현이 먼저다.</p></article></div><p class="small">실적을 읽기 위한 시나리오이며 기대 금메달 수·확률 예측·통계적 신뢰구간이 아니다. 현재 데이터만으로 금메달 확률을 숫자로 산출하지 않는다.</p></section>'''
def nav():
    return '<nav class="golf-nav" aria-label="사격 문서"><a href="./olshooting.html">전체 안내</a><a href="./olshooting-projection.html" aria-current="page">LA28 전망</a><a href="./olshooting-rifle.html">소총</a><a href="./olshooting-pistol.html">권총</a><a href="./olshooting-shotgun.html">산탄총</a><a href="./olshooting-athletes.html">한국 선수</a></nav>'
def hub():
    content=overview()+matrix()+scenarios()+medal_section()+paths()+milestones()+formats()+f'<section id="sources"><h2>공식 출처·분석 범위</h2><p>확인일 2026.10.11 · 성적 표본은 2025 성인 시즌. 세계선수권 2개, 정규 월드컵 6개 개최지, 파이널의 한국 본선·결선 기록을 대조했다. 2026 전체 시즌 성적과 실시간 랭킹은 포함하지 않았다. 선수 이름은 ISSF 영문 식별명과 함께 데이터에 보존한다.</p>{source_list()}</section>'
    return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>사격 LA28 전망 | 한국 2025 세계선수권·월드컵</title><meta name="description" content="한국 사격 2025 ISSF 성인 올림픽 종목 실적과 조건부 LA28 금메달 후보 분석"><link rel="stylesheet" href="./css/olympic-wiki.css"><link rel="stylesheet" href="./css/shooting-projection.css"></head><body><a class="skip" href="#main">본문 바로가기</a><header class="topbar"><div class="topbar-inner"><a href="./index.html">← 올림픽예선 목차</a><span>LA28 · 사격</span></div></header><div class="shell"><h1 class="title">사격 · LA28 금메달 후보</h1><p class="intro">2025 세계선수권·ISSF 월드컵의 한국 실적에서 출발하는 2028 전망. 핵심은 여자 공기소총과 여자 25m 권총, 확장은 공기권총과 혼성이다.</p>'+nav()+'<main id="main"><nav class="toc"><strong>목차</strong><ol>'+''.join(f'<li><a href="#{id}">{H(label)}</a></li>' for id,label in [('baseline','2025 올림픽 종목 실적'),('events','15종목 후보'),('scenario','조건부 금메달 시나리오'),('medals','한국 메달'),('paths','파이널 참가 경로'),('road','2026–2028 관문'),('format','LA28 결선 변경'),('sources','출처')])+'</ol></nav>'+content+'</main><footer class="footer"><a href="./olshooting.html">사격 전체 안내</a> · <a href="#main">위로</a><p>분석 확인 2026.10.11 · 2025 실적 표본 · 비공식 분석</p></footer></div></body></html>\n'
def update_pages():
    (ROOT/'olshooting-projection.html').write_text(hub(),encoding='utf-8',newline='\n')
    for path in ROOT.glob('olshooting*.html'):
        if path.name=='olshooting-projection.html':continue
        t=path.read_text(encoding='utf-8')
        t=re.sub(r'<!-- shooting-projection:start -->.*?<!-- shooting-projection:end -->','',t,flags=re.S)
        if 'css/shooting-projection.css' not in t:t=t.replace('</head>','<link rel="stylesheet" href="./css/shooting-projection.css"></head>')
        # Insert navigation once in each existing navigation group.
        t=re.sub(r'(<nav[^>]*>)(.*?)(</nav>)',lambda m:m[1]+(m[2].replace('<a href="./olshooting.html"','<a href="./olshooting-projection.html">LA28 전망</a><a href="./olshooting.html"',1) if 'olshooting.html' in m[2] and 'olshooting-projection.html' not in m[2] else m[2])+m[3],t,flags=re.S)
        code=path.stem.removeprefix('olshooting-ev-')
        event=next((e for e,v in E.items() if v['code']==code),None)
        if event:
            section=projection(event)+f'<section id="season2025"><h2>2025 공식 한국 성적</h2><p class="small">본선과 결선을 구분. 결선 진출 시 최종 순위를 표시. 노란색은 메달 성적. RPO는 순위 외 출전.</p>{result_tables(event)}{rival_section(event)}</section>'
            if event in ['ARMT','APMT','TRMT']:section+=formats()
            section+='<p><a href="./olshooting-projection.html">전체 종목 비교·LA28 분석 →</a></p>'
        else:
            section='<section id="la28-projection"><h2>세계선수권·2025 월드컵에서 보는 LA28</h2><div class="shoot-callout"><b>핵심 금 도전: 여자 공기소총 · 여자 25m 권총</b><p>반효진·양지인의 세계선수권 금, 권은지·오예진의 월드컵 은을 올림픽 종목별로 비교합니다. 3인 단체전과 비올림픽 메달은 별도로 취급합니다.</p><a href="./olshooting-projection.html">15종목 실적·금메달 후보 분석 →</a></div></section>'
        marker='<!-- shooting-projection:start -->'+section+'<!-- shooting-projection:end -->'
        # Place the analysis after the original contents navigation.
        match=re.search(r'(<main[^>]*>)(\s*<nav class="toc".*?</nav>)?',t,flags=re.S)
        if match:t=t[:match.end()]+marker+t[match.end():]
        if event:
            t=re.sub(r'<p class="intro">.*?</p>',f'<p class="intro">{H(E[event]["label"])} · 2025 ISSF 세계선수권·월드컵 실적과 LA28 후보 분석 · 확인 2026.10.11</p>',t,count=1,flags=re.S)
            t=re.sub(r'<p[^>]*>본문은 추후 작성 예정입니다\..*?</p>','',t,flags=re.S)
            # Keep historical biographical results available without a wide table dominating mobile.
            t=re.sub(r'(?<!<details class="shoot-history">)(<table class="data ath-res">.*?</table>)',r'<details class="shoot-history"><summary>기존 주요 성적 펼치기</summary>\1</details>',t,flags=re.S) if 'class="shoot-history"' not in t else t
            t=t.replace('<ol><li><a href="#athletes">','<ol><li><a href="#projection">LA28 전망</a></li><li><a href="#season2025">2025 공식 성적</a></li><li><a href="#athletes">',1)
        path.write_text(t.replace('\r\n','\n'),encoding='utf-8',newline='\n')
    print('Updated shooting projection hub and 22 existing shooting pages.')
if __name__=='__main__':update_pages()
