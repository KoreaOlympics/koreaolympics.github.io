"""Render the eight Olympic weight pathways from reviewed WT result snapshots.

Run after athletes.py / weightpages.py. Network fetching is intentionally separate:
future medals and undated rankings must never be substituted for verified results.
"""
from pathlib import Path
import html,json,re
SITE=Path(__file__).resolve().parents[1]
D=json.loads((SITE/'data/taekwondo-pathways.json').read_text(encoding='utf-8'))
E={x['id']:x for x in D['events']}
H=lambda s:html.escape(str(s),quote=True)
KO={'KIM Jongmyeong':'김종명','BAE Jun-Seo':'배준서','JUNG Woo-Hyeok':'정우혁','JUNG Woo-hyeok':'정우혁','SEO Geon-woo':'서건우','MUN Jinho':'문진호','JANG Jun':'장준','KIM Woojin':'김우진','LEE Ye-Ji':'이예지','KWAK Minju':'곽민주','SEO Eunsu':'서은수','PARK Tae-Joon':'박태준','PARK Tae-joon':'박태준','PARK Woo hyeok':'박우혁','PARK Woo-Hyeok':'박우혁','KANG Jaegwon':'강재권','JUNSANG Park':'박준상','LEE Yumin':'이유민','KIM Gahyeon':'김가현','HONG Hyo rim':'홍효림','PARK Min kyu':'박민규','KANG Sanghyun':'강상현','KIM Yujin':'김유진','SONG Dabin':'송다빈'}
def link(key):
    s=D['sources'][key]; return f'<a href="{H(s["url"])}">{H(s["title"])}</a>'
def athlete(a):
    name=KO.get(a['name'],a['name']); name=H(name)
    if a.get('profile'): name=f'<a href="{H(a["profile"])}">{name}</a>'
    return name+f' <span class="tkd-country">{H(a["country"])}</span>'
def weightnav(group=None):
    return '<nav class="tkd-weights" aria-label="체급별 분석">'+''.join(f'<a href="./oltaekwondo-ev-{c}.html">{H(w["label"])}</a>' for c,w in D['weights'].items() if not group or c[0]==group)+'</nav>'
def cycles():
    return '''<section id="cycles"><h2>랭킹 1기에서 2기로</h2><div class="tkd-grid"><article class="tkd-card"><span class="tkd-kicker">1기 · 출전 경로 확보</span><h3>2024.06.01–2026.05.31</h3><p>2025 GP 챌린지 입상 → 2026 GP 초청. 2025 세계선수권 우승·GS 챌린지 결승 → 2026 GS 본선 경로.</p><p><b>1기 점수는 2026.07 랭킹에서 0점.</b> 그 점수로 확보한 대회 초청 경로는 별도로 판단한다.</p></article><article class="tkd-card"><span class="tkd-kicker">2기 · LA28 랭킹 경쟁</span><h3>2026.06.01–2028.05.31</h3><p>2026년 6월 대회부터 적립하고 7월 랭킹부터 반영한다. 2027 세계선수권·GP·GP 파이널이 중심이다.</p><p>올림픽 쿼터 판정용 <b>2028.01 랭킹</b>과 이후 올림픽 시드용 랭킹을 구분한다.</p></article></div><p class="small">근거: '''+link('rank')+''' · 2기는 2027년 시작이 아니다.</p></section>'''
def ledger(code,cycle):
    w=D['weights'][code]
    out=''
    for event in D['events']:
        if event['cycle']!=cycle: continue
        if event.get('gender') and event['gender']!=code[0]:continue
        rows=[a for a in event['medals'] if a['weight']==w['olympic'] or ((event['id'].startswith('wc') or event['id']=='women26') and a['weight'] in w['worldWeights'])]
        date=event['start']+((' – '+event['end']) if event['start']!=event['end'] else '')
        body=f'<p class="tkd-date">{H(date)} · {H(event["status"])}</p><p>{H(event["route"])}</p>'
        if event.get('partialResults'):body+='<p class="small">부분 결과 · 2026.10.09 공식 1일차 메달표, 8개 중 3개 체급만 공표. 다른 체급 결과를 추정하지 않는다.</p>'
        if rows:
            body+=medals(rows)
            body+=ticket_note(event,rows)
        elif event['medals']: body+='<p>이 체급 결과는 현재 수집한 공식 부분 결과에 아직 없습니다.</p>'
        else: body+='<p class="small">'+H(event['resultNote'])+'</p>' if event.get('resultNote') else '<p class="small">입상자: '+('대회 진행 중 · 전체 체급 확정 결과를 기다리는 중' if event['status']=='진행 중' else '예정 대회는 결과 확정 후 반영' if event['start']>D['asOf'] else '대륙·체급별 대회요강 및 결과 확인 필요')+'</p>'
        refs=' · '.join(link(k) for k in event['sources'])
        if event.get('resultUrl'): refs=f'<a href="{H(event["resultUrl"])}">WT 공식 결과</a> · '+refs
        out+=f'<details class="tkd-meet" id="meet-{event["id"]}"><summary><b>{H(event["title"])}</b> <span class="tkd-grade">{H(event["grade"])}</span><span class="tkd-date">{H(date)} · {H(event["status"])}</span></summary>{body}<p class="small">{refs}</p></details>'
    return f'<section id="cycle{cycle}"><h2>{cycle}기 주요 대회 · 시간순</h2>'+('<p>동일한 연도만 확인된 2027 대회는 계획 항목으로 묶었습니다. 대회 간 실제 선후관계는 최종 날짜 공표 후 확정합니다.</p>' if cycle==2 else '<p>1기 점수를 2기에 더하지 않습니다. 아래 결과는 이후 대회의 초청권을 판단하는 기록입니다.</p>')+out+'</section>'
def medals(rows):
    out=''; cats=list(dict.fromkeys(a['weight'] for a in rows))
    for cat in cats:
        if len(cats)>1: out+=f'<h4>{H(cat.replace("Men","남자").replace("Women","여자"))}</h4>'
        out+='<ul class="tkd-podium">'
        for a in rows:
            medal={'Gold':'금','Silver':'은','Bronze':'동'}[a['medal']]
            out+=f'<li class="{("tkd-kor" if a["country"]=="KOR" else "")}"><span class="tkd-medal tkd-{a["medal"].lower()}">{medal}</span><span>{athlete(a)}</span></li>'
        out+='</ul>'
    return out
def ticket_note(event,rows):
    if event['id'].startswith('gpc'):
        seen=set(); eligible=[]; duplicates=[]
        candidates=event.get('placements',{}).get(rows[0]['weight'],rows)
        for a in candidates:
            if a['country'] in seen: duplicates.append(a)
            else: seen.add(a['country']); eligible.append(a)
            if len(eligible)==3:break
        text='<b>챌린지 초청 후보 3명:</b> '+', '.join(athlete(a)+(f' ({a["place"]}위)' if a.get('place') else '') for a in eligible)+'.'
        if duplicates: text+=' '+', '.join(athlete(a) for a in duplicates)+'은 같은 국가의 상위 선수가 있어 중복 초청으로 계산하지 않는다.'
        text+=' 공식 메달표와 준결승·8강 경기 결과에서 요강 순위를 적용한 후보다. 실제 등록·계체·기권·교체를 반영한 최종 참가 명단은 별도로 확인한다.'
        if event.get('matchResultUrl'):text+=f' <a href="{H(event["matchResultUrl"])}">차순위 경기 근거</a>'
    elif event['id']=='gsc25':
        countries=[]; selected=[]
        for a in rows:
            if a['country'] not in countries: countries.append(a['country']); selected.append(a)
            if len(selected)==2: break
        text='<b>2026 GS 초청 경로:</b> '+', '.join(athlete(a) for a in selected)+'.'
        if rows[0]['country']==rows[1]['country']:
            text+=' 동일국가 결승이므로 은메달 선수에게 두 번째 초청권을 자동 배정하지 않는다.'
            if len(selected)<2: text+=' 상위 3명 모두 동일국가로, 두 번째 초청 후보는 4위 이하 결과·WT 초청 명단의 추가 확인이 필요하다.'
        text+=' 최종 초청·등록 공지가 우선한다. 챌린지의 G2 점수를 본선 메리트로 합산하지 않는다.'
    elif event['id']=='wc25':
        text='<b>2026 GS의 세계선수권 경로:</b> '+', '.join(athlete(a) for a in rows if a['medal']=='Gold')+'. 은·동은 이 경로의 초청 대상이 아니다. 2025 G14 점수는 2기에 이월되지 않는다.'
    elif event['id']=='women26':
        text='<b>랭킹 점수 경로:</b> 여자 오픈 G4 성적이다. 세계선수권·GP 금메달에 부여하는 GS 초청권으로 바꾸어 계산하지 않는다.'
    else:
        text='<b>2026 GS의 GP 우승 경로:</b> '+', '.join(athlete(a) for a in rows if a['medal']=='Gold')+'. GP 은메달은 GS 직행 경로가 아니라 GP 파이널 진출 경로다.'
    return '<div class="tkd-callout">'+text+'</div>'
def recipients(code):
    """Qualification tables: destination is the caption, source event and names only."""
    w=D['weights'][code]
    groups={x:[] for x in ['2026 로마 GP1','2026 무주 GP2','2026 파리 GP3','2026 GP 파이널','2026 GS 본선']}
    for event in D['events']:
        rows=[a for a in event['medals'] if a['weight']==w['olympic'] or (event['id']=='wc25' and a['weight'] in w['worldWeights'])]
        if not rows:continue
        source=event['title']+' '+event['start'][:4]
        if event['id'].startswith('gpc'):
            seen=set();names=[]
            for a in event['placements'][w['olympic']]:
                if a['country'] in seen:continue
                seen.add(a['country']);names.append(a)
                if len(names)==3:break
            target={'gpc1':'2026 로마 GP1','gpc2':'2026 무주 GP2','gpc3':'2026 파리 GP3'}[event['id']]
            groups[target].append((source,names,event['id']))
        elif event['id']=='gsc25':
            seen=set();names=[]
            for a in rows:
                if a['country'] in seen:continue
                seen.add(a['country']);names.append(a)
                if len(names)==2:break
            groups['2026 GS 본선'].append((source,names,event['id']))
        elif event['id']=='wc25':
            groups['2026 GS 본선'].append((source,[a for a in rows if a['medal']=='Gold'],event['id']))
        elif event['id'].startswith('gp26'):
            groups['2026 GS 본선'].append((source,[a for a in rows if a['medal']=='Gold'],event['id']))
            groups['2026 GP 파이널'].append((source,[a for a in rows if a['medal'] in ['Gold','Silver']],event['id']))
    groups['2026 GS 본선'].append(('GS 챌린지 2024',[],'grand-slam'))
    groups['2026 GS 본선'].append(('GP 파이널 2026',[],'meet-gpf26'))
    groups['2027 GS 본선']=[(title,[],event_id) for title,event_id in [('세계선수권 2027','wc27'),('로마 GP1 2027','gp27a'),('파리 GP2 2027','gp27b'),('맨체스터 GP3 2027','gp27c'),('GP 파이널 2027','gpf27'),('GS 챌린지 2026','gsc26'),('GS 챌린지 2027','gsc27')]]
    groups['2027 GP 파이널']=[(title,[],event_id) for title,event_id in [('로마 GP1 2027','gp27a'),('파리 GP2 2027','gp27b'),('맨체스터 GP3 2027','gp27c')]]
    blocks=''
    for target,entries in groups.items():
        table=f'<table class="tkd-recipients"><caption>{H(target)} · 출전 경로 명단</caption><thead><tr><th scope="col">대회명</th><th scope="col">선수명</th></tr></thead><tbody>'
        for source,names,event_id in entries:
            anchor=event_id if event_id in ['grand-slam','meet-gpf26'] else 'meet-'+event_id
            table+=f'<tr><th scope="row"><a href="#{anchor}">{H(source)}</a></th><td>'+(recipient_names(names) if names else '—')+'</td></tr>'
        table+='</tbody></table>'
        blocks+='<div class="tkd-recipient-block">'+table+'</div>'
    return '<section id="recipients"><h2>대회별 참가 경로 명단</h2><p class="small">성적에 따른 초청 경로 후보 · 최종 참가 확정 별도 · — 미확인/미정 · 한국 선수는 노란색</p>'+blocks+'</section>'

def recipient_names(names):
    return '<ul class="tkd-name-list">'+''.join(f'<li class="{"tkd-name-kor" if a["country"]=="KOR" else ""}">{athlete(a)}</li>' for a in names)+'</ul>'

def participants(code):
    weight=D['weights'][code]['olympic'];blocks=''
    for event in D['events']:
        names=event.get('participants',{}).get(weight,[])
        if not names:continue
        blocks+=f'<details class="tkd-meet"><summary><b>{H(event["title"])} {H(event["start"][:4])} · 참가 {len(names)}명</b></summary><table class="tkd-recipients"><thead><tr><th scope="col">대회명</th><th scope="col">선수명</th></tr></thead><tbody><tr><th scope="row">{H(event["title"])} {H(event["start"][:4])}</th><td>'+recipient_names(names)+f'</td></tr></tbody></table><p class="small"><a href="{H(event["matchResultUrl"])}">WT 공식 경기 기록</a></p></details>'
    return '<section id="participants"><h2>완료 대회 참가 명단</h2><p class="small">공식 경기 기록에 등장하는 선수 전원. 예정 대회의 참가자는 확정 공표 후 반영.</p>'+blocks+'</section>'


def strategy(code):
    w=D['weights'][code]
    golds=[a for key in ['gp26a','gp26b','gp26c'] for a in E[key]['medals'] if a['weight']==w['olympic'] and a['medal']=='Gold']
    kor=[a for a in golds if a['country']=='KOR']
    world=', '.join(x.replace('Men','남자').replace('Women','여자') for x in w['worldWeights'])
    return f'''<section id="strategy"><h2>이 체급에서 볼 핵심 판정</h2><div class="tkd-callout"><b>{H(w['label'])}의 세계선수권 연결 체급: {H(world)}</b><p>2027 세계선수권의 두 체급 우승자는 이 올림픽 체급의 GS 출전 경로로 모인다. 일반 올림픽 랭킹 점수는 선수의 신고 체급·WT 변환 규정을 따르므로, GS 통합 체급표만으로 점수를 자동 합산하면 안 된다.</p></div><p>확인된 2026 GP 우승 경로(로마·무주 및 파리 부분 결과)는 {', '.join(athlete(a) for a in golds)}. {('한국의 GP 우승 경로 후보는 '+', '.join(athlete(a) for a in kor)+'.') if kor else '이 수집 결과에서 한국 GP 우승 경로는 확인되지 않았다.'} 다른 GS 경로 및 11월 랭킹 재배정 가능성은 별도로 남는다.</p><ol><li><b>2027 G14 세계선수권:</b> 금 140점은 G6 GP 금 60점의 약 2.33배다. 높은 점수와 GS 초청 경로를 동시에 노릴 수 있다.</li><li><b>2027 G6 GP:</b> 랭킹 점수 + GP 파이널 출전 경로 + 금메달의 GS 초청 경로를 함께 확인한다.</li><li><b>2027 G10 파이널:</b> 금 100점과 GS 초청 경로. 2028년 1월 판정에 앞선 중요한 대회다.</li><li><b>GS 본선:</b> 보통의 올림픽 랭킹 점수와 별도인 메리트 순위를 본다. 초청권 확보만으로 올림픽 출전권을 획득한 것은 아니다.</li></ol><p class="small">위 비교는 공식 배점에 따른 분석이다. 현재 월별 WT 올림픽 랭킹 원본·총점은 재확인하지 못해 개인의 LA28 합격 순위를 제시하지 않는다.</p></section>'''
def points():
    return '''<section id="points"><h2>배점·상한·감점의 구분</h2><div class="tkd-grid"><article class="tkd-card"><h3>G14 · 세계선수권</h3><p>금 <b>140</b> · 은 84 · 동 50.4</p></article><article class="tkd-card"><h3>G10 · GP 파이널</h3><p>금 <b>100</b> · 은 60 · 동 36</p></article><article class="tkd-card"><h3>G6 · GP 시리즈</h3><p>금 <b>60</b> · 은 36 · 동 21.6</p></article><article class="tkd-card"><h3>G2 · 챌린지</h3><p>금 <b>20</b> · 은 12 · 동 7.2</p></article></div><p>일반 G1·G2·G3·G4의 합산 상한은 2025년 40점, 2026.01–05 20점, 2026.06–12 20점, 2027년 40점, 2028.01–05 20점이다. <b>GP 챌린지는 상한 예외, GS 챌린지는 상한에 포함</b>된다. G4 대륙선수권·4년 주기 대륙종합대회·여자 오픈·세계주니어 등 규정에 열거된 예외는 별도로 적용한다.</p><p>점수는 다음 달 랭킹에 반영되고 12개월 후 원점수의 50%를 감점한다. 예컨대 2026.06 GP 금 60점은 2027.07 랭킹부터 30점, 2027년 대회 금 60점은 2028.01 판정 시점에 아직 60점이다. 2025년 점수는 감점 잔액과 관계없이 2026.07에 초기화한다.</p><p>5월 1–25일 올림픽 체급 신고/변경 → 6월 1일부터 다음 해 5월 31일까지 적용 → 7월 랭킹에 반영. 세계체급 점수를 두 올림픽 체급에 중복 더하지 않는다.</p><p class="small">배점은 기본값이다. 소수 참가·실제 승리 요건·상한·신고 체급 등을 적용한 실제 공표 총점과 다를 수 있다. '''+link('rank')+'''</p></section>'''
def grand_slam():
    return '''<section id="grand-slam"><h2>GS 초청과 올림픽 메리트 판정</h2><div class="tkd-grid"><article class="tkd-card"><h3>2026 GS · 10명 구조</h3><p>2026 GP 금 3 + GP 파이널 금 1 + 2025 세계선수권 금 2 + 2024/25 GS 챌린지 결승 각 2.</p></article><article class="tkd-card"><h3>2027 GS · 10명 구조</h3><p>2027 GP 금 3 + GP 파이널 금 1 + 2027 세계선수권 금 2 + 2026/27 GS 챌린지 결승 각 2.</p></article></div><p>같은 선수가 여러 경로에서 겹치면 해당 체급 <b>11월 올림픽 랭킹 차순위</b>로 보충한다. 개최국 자동 초청은 없다. 연도별 최종 초청 공지로 재확인한다.</p><dl class="tkd-facts"><dt>본선 메리트</dt><dd>금 1000 · 은 600 · 동 360 · 4위 216 · 5위 151 · 9위 106</dd><dt>50% 감점 후</dt><dd>500 · 300 · 180 · 108 · 75.5 · 53</dd><dt>올림픽 쿼터</dt><dd>2028.01 메리트 1위. 그 선수가 올림픽 랭킹 상위 5위이면 2위까지 재배정 가능. 3위에게 자동 승계하지 않는다.</dd><dt>별도 제한</dt><dd>체급 이동 시 메리트 이전 불가. 동점은 GS 본선·챌린지 참여 대회 수로 판단. 연도 완료 후 원점수 50% 감점 및 다음 주기 초기화 규정을 적용한다.</dd></dl><p>2026 성적도 다음 해 감점 이후 잔액이 남을 수 있으므로 2027 한 대회의 메달만으로 메리트 1위를 판정하면 안 된다. 최종 공표 메리트표와 해당 연도 감점 적용 시점을 확인해야 한다.</p><details><summary>메리트 감점 전·후 배점 비교</summary><div class="tkd-calculator"><label>성적 <select id="merit-place"><option value="1000">금</option><option value="600">은</option><option value="360">동</option><option value="216">4위</option><option value="151">5위</option><option value="106">9위</option></select></label><output id="merit-result" aria-live="polite">감점 전 1000 · 50% 감점 후 500</output></div><p class="small">규정 배점 비교용이며 현재 메리트 순위나 올림픽 합격 예측값이 아니다.</p></details><p class="small">근거: '''+link('gs')+' · '+link('council')+'''</p></section>'''
def entry():
    return '''<section id="entry"><h2>그랑프리에 들어가는 두 경로</h2><p><b>랭킹 경로:</b> GP 시리즈 체급당 31명은 올림픽 랭킹과 챌린지 성적으로 선발하고 개최국 1명을 더한다. 랭킹 상위 70명에게 사전등록을 열며, 기준 월과 마감은 해당 대회요강을 따른다. MNA는 랭킹 선발 선수 중 체급당 최대 2명, 챌린지 초청 선수는 이 제한에서 제외한다.</p><p><b>챌린지 경로:</b> 2025 세 대회의 상위 3명은 각각 2026의 대응 시리즈로 연결한다. 이 초청 경로 자체는 국가당 체급별 1명 제한이다. 한국 입상자가 두 명 이상이면 4위 이하의 타국 선수로 재배정될 수 있다.</p><p>2024 계획자료의 2026 초청 기준월은 2·4·6월, 2027은 2·4·8월이다. <b>이는 기준월 계획이며 실제 2026/27 각 GP의 최종 요강이 우선</b>한다. 2026년 6월 공표 랭킹은 아직 1기 마지막 5월 성적을 반영한다.</p><p><b>파이널:</b> 세 시리즈 결승 진출자 6명 + 11월 랭킹 상위 10명 구조, 체급당 국가 최대 2명. 중복 및 개최국 보장 초청을 조정한다. 사전등록은 랭킹 상위 30명에게 열린다.</p><p class="small">''' +link('gp')+' · '+link('cycle')+'''</p></section>'''
def evidence():
    return '<section id="evidence"><h2>자료 기준과 미확정 항목</h2><p>결과 확인일 2026.10.11. 완료 대회와 예정 대회를 구분했다. 2026 성인 세계선수권 우승자는 기재하지 않는다. 2026 주니어 세계선수권·품새 세계선수권·여자 오픈은 서로 다른 대회이며 2025/27 성인 세계선수권 GS 우승 초청 경로를 대신하지 않는다.</p><p>2024 GS 챌린지도 2026 본선의 초청 경로이나 해당 결과는 이번 수상자 수집 범위에 포함하지 않았다. 따라서 2026 GS 최종 10명 전원을 확정한 명단으로 읽으면 안 된다.</p><p>현재 월별 랭킹 총점·최종 초청 명단 및 2027 세부 날짜는 미확정/미확인이다. 2026년 말 예정 일정은 WT 2025.12.28 달력 보관본 기준이며 후속 요강에 따라 변경 가능하다. IOC 쿼터 표는 기존 페이지의 2026.05.12판 요약을 유지했으며 이번 접속에서 원문 재확인에 실패했다.</p></section>'
def quota():
    return '<section id="rules"><h2>LA28 체급별 쿼터 구조</h2><dl class="tkd-facts"><dt>올림픽 랭킹</dt><dd>5명 · 2028.01 공표 랭킹</dd><dt>GS 메리트</dt><dd>1명 · 메리트 1위, 랭킹 중복 시 2위까지</dd><dt>대륙 예선</dt><dd>9명 · 아시아·아프리카·유럽·팬암 각 2, 오세아니아 1</dd><dt>개최국/보편성</dt><dd>1명 · 체급별 총 16명 구조</dd></dl><p>쿼터는 NOC에 배정되고 체급당 1명을 출전시킨다. 랭킹·GS로 성별 2장 이상 확보한 NOC는 해당 성별 대륙 예선에 참가하지 못하는 구조다. 순위와 실제 한국 대표 선발은 구분한다.</p><p class="small">기존 IOC 규정 요약. '+link('ioc')+'</p></section>'
def calendar(group=None):
    out='<section id="timeline"><h2>주요 대회 정렬 · 1기와 2기</h2><p>정확한 개최일을 확인한 대회는 날짜순, 2027년만 확인한 대회는 연간 계획으로 묶었다. 체급별 입상자와 초청 후보는 해당 체급 문서에서 확인한다.</p>'
    for cycle in [1,2]:
        out+=f'<h3>랭킹 {cycle}기</h3>'
        for x in D['events']:
            if x['cycle']!=cycle or (group and x.get('gender') and x['gender']!=group):continue
            date=x['start']+(' – '+x['end'] if x['start']!=x['end'] else '')
            anchors=' · '.join(f'<a href="./oltaekwondo-ev-{c}.html#meet-{x["id"]}">{H(w["label"])}</a>' for c,w in D['weights'].items() if (not group or c[0]==group) and (not x.get('gender') or x['gender']==c[0]))
            out+=f'<details class="tkd-meet"><summary><b>{H(x["title"])}</b> <span class="tkd-grade">{H(x["grade"])}</span><span class="tkd-date">{H(date)} · {H(x["status"])}</span></summary><p>{H(x["route"])}</p><p>{anchors}</p></details>'
    return out+'</section>'
def toc(items): return '<nav class="toc" aria-label="목차"><strong>목차</strong><ol>'+''.join(f'<li><a href="#{i}">{t}</a></li>' for i,t in items)+'</ol></nav>'
def sources(): return '<section id="sources"><h2>공식 규정과 결과 근거</h2><ol class="sources">'+''.join('<li>'+link(k)+'</li>' for k in D['sources'])+'</ol><p class="small"><a href="./data/taekwondo-pathways.json">체급별 결과·출처 데이터</a> · 비공식 한국어 분석. 후속 WT 규정과 최종 초청 공지가 우선한다.</p></section>'
def normalise(t):
    if './css/taekwondo.css' not in t: t=t.replace('</head>','<link rel="stylesheet" href="./css/taekwondo.css"><script src="./js/taekwondo-pathways.js" defer></script></head>')
    t=t.replace('2026.07부터 WT 올림픽 랭킹 포인트가 쌓이고 있다.','2026.06 대회부터 2기 점수가 적립되고 2026.07 랭킹부터 반영된다.')
    if './oltaekwondo-ranking.html' not in t:
        t=re.sub(r'(<nav class="golf-nav"[^>]*>.*?)(</nav>)',r'\1<a href="./oltaekwondo-ranking.html">랭킹·대회 경로</a>\2',t,count=1,flags=re.S)
    return '\n'.join(line.rstrip() for line in t.splitlines())+'\n'
def replace_main(t,body):
    old=re.search(r'<main id="main">(.*?)</main>',t,re.S); assert old
    old_ids=set(re.findall(r'id="([^"]+)"',old[1])); new_ids=set(re.findall(r'id="([^"]+)"',body))
    legacy=''.join(f'<span id="{H(i)}" class="tkd-legacy"></span>' for i in sorted(old_ids-new_ids))
    return t[:old.start()]+f'<main id="main">{legacy}{body}</main>'+t[old.end():]
def event_page(code):
    p=SITE/f'oltaekwondo-ev-{code}.html'; t=p.read_text(encoding='utf-8')
    original=re.search(r'<section id="athletes">.*?</section>',t,re.S)
    athletes=original[0] if original else ''
    # Undated third-party ranks cannot stand in for the current WT monthly table.
    athletes=re.sub(r'<dt>랭킹</dt><dd>.*?</dd>','',athletes,flags=re.S)
    athletes=re.sub(r'<table class="data ath-res">.*?</table>','',athletes,flags=re.S)
    player_data=json.loads((SITE/'tools/research/tkd_judo.json').read_text(encoding='utf-8'))['taekwondo']['events'].get(code,{})
    for a in player_data.get('athletes',[]):
        heading=f'<h3>{H(a["name"])}</h3>'
        results='<details class="tkd-ath-history"><summary>기존 주요 성적</summary><ul>'+''.join(f'<li>{H(r.get("year",""))} · {H(r.get("comp",""))} · {H(r.get("event",""))} · <b>{H(r.get("result",""))}</b></li>' for r in a.get('results',[]))+'</ul><p class="small">기존 선수 자료 기준 2026.10.05. 새 공식 대회 결과는 위 시간순 기록에서 확인.</p></details>'
        if heading in athletes and '기존 주요 성적' not in athletes.split(heading,1)[1].split('</div>',1)[0]:athletes=athletes.replace(heading,heading+results,1)
    if 'id="tkd-legacy-sources"' not in athletes:
        refs={s['url']:s['title'] for s in player_data.get('sources',[])}
        for a in player_data.get('athletes',[]):refs.update({s['url']:s['title'] for s in a.get('sources',[])})
        athletes=athletes.replace('</section>','<details id="tkd-legacy-sources"><summary>기존 선수 자료 출처</summary><ul>'+''.join(f'<li><a href="{H(u)}">{H(title)}</a></li>' for u,title in refs.items())+'</ul></details></section>')
    overview=re.search(r'<section id="overview">.*?</section>',t,re.S)
    overview=re.sub(r'<p class="stub">.*?</p>','',overview[0],flags=re.S) if overview else ''
    body=toc([('recipients','대회별 참가 경로'),('participants','완료 대회 참가 명단'),('strategy','체급별 핵심 판정'),('cycle1','1기 결과·초청 경로'),('cycle2','2기 대회·배점'),('grand-slam','GS 초청·메리트'),('rules','올림픽 쿼터'),('athletes','한국 주요 선수'),('sources','근거')])+weightnav(code[0])+recipients(code)+participants(code)+strategy(code)+cycles()+ledger(code,1)+ledger(code,2)+entry()+points()+grand_slam()+quota()+athletes+overview+evidence()+sources()
    t=replace_main(t,body)
    t=re.sub(r'<p class="intro">.*?</p>',f'<p class="intro">{H(D["weights"][code]["label"])} · 대회별 출전 경로와 참가 명단 · 2026.10.11 기준</p>',t,count=1,flags=re.S)
    p.write_text(normalise(t),encoding='utf-8',newline='\n')
def overview_page(p,group=None):
    t=p.read_text(encoding='utf-8')
    title='체급별 대회·출전 경로'
    body=toc([('classes','체급별 분석'),('cycles','랭킹 1기·2기'),('timeline','주요 대회 정렬'),('entry','GP 초청 경로'),('points','배점·감점'),('grand-slam','GS 초청·쿼터'),('rules','올림픽 쿼터'),('sources','공식 근거')])+f'<section id="classes"><h2>{title}</h2><p>체급을 선택하면 2025 샬럿·무주·방콕 GP 챌린지, 우시 세계선수권·GS 챌린지 입상자와 2026 GP 입상자를 시간순으로 볼 수 있습니다.</p>'+weightnav(group)+'</section>'+cycles()+calendar(group)+entry()+points()+grand_slam()+quota()+evidence()+sources()
    t=replace_main(t,body)
    t=re.sub(r'<p class="intro">.*?</p>','<p class="intro">LA28 태권도 예선의 핵심은 1기에서 출전 경로를 확보하고, 2026년 6월부터 시작된 2기에서 올림픽 랭킹과 GS 메리트를 따로 판정하는 것입니다. 2027 세계선수권·G6 그랑프리·G10 파이널의 연결을 체급별로 추적합니다.</p>',t,count=1,flags=re.S)
    p.write_text(normalise(t),encoding='utf-8',newline='\n')
def update_pages():
    for c in D['weights']: event_page(c)
    for name,group in [('oltaekwondo.html',None),('oltaekwondo-men.html','m'),('oltaekwondo-women.html','w')]: overview_page(SITE/name,group)
    ranking=SITE/'oltaekwondo-ranking.html'
    if not ranking.exists():
        t=(SITE/'oltaekwondo.html').read_text(encoding='utf-8')
        t=t.replace('<h1 class="title">태권도 (Taekwondo)</h1>','<h1 class="title">태권도 랭킹·대회 경로</h1>')
        t=re.sub(r'<title>.*?</title>','<title>랭킹·대회 경로 | LA28 태권도</title>',t,count=1)
        ranking.write_text(t,encoding='utf-8')
    overview_page(ranking)
    for name in ['oltaekwondo-continental.html','oltaekwondo-athletes.html','oltaekwondo-squad.html']:
        p=SITE/name; t=p.read_text(encoding='utf-8')
        block='<div class="tkd-callout" id="tkd-pathway-links"><b>체급별 랭킹·출전 경로 분석</b><p>2025 챌린지 초청권, 2026/27 GP 점수, 2027 세계선수권 및 GS 메리트는 각 체급 문서에서 함께 확인합니다. 2기 시작은 2026.06.01입니다.</p>'+weightnav()+'</div>'
        if 'id="tkd-pathway-links"' not in t: t=t.replace('<main id="main">','<main id="main">'+block,1)
        t=re.sub(r'<dt>랭킹</dt><dd>.*?기준일 미상.*?</dd>','',t,flags=re.S)
        p.write_text(normalise(t),encoding='utf-8',newline='\n')
    print('Updated 8 weight pages, 4 guides and 3 related pages')
if __name__=='__main__': update_pages()
