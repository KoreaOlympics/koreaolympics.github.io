"""Write short Korean columns about Korean athletes' results with Claude.

  python -m tools.winter.column

Runs after collect.py. For each (event, KST day) whose Korean results changed since the
last column, asks Claude for a factual column built only from the collected data, and
stores it in data/winter/columns/. Skips quietly when ANTHROPIC_API_KEY is not set.
"""
import datetime as dt, hashlib, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WINTER = ROOT / 'data' / 'winter'
OUT = WINTER / 'columns'
MODEL = 'claude-opus-5-5'
MAX_PER_RUN = 3
KST = dt.timezone(dt.timedelta(hours=9))

SYSTEM = """당신은 한국 동계스포츠 전문 기자입니다. 주어진 JSON 데이터만 근거로 한국 선수들의 경기 결과를 정리하는 짧은 칼럼을 씁니다.

원칙:
- 데이터에 없는 사실(부상, 인터뷰, 경기 장면 묘사, 과거 전적 등)은 절대 지어내지 않습니다.
- 기록·순위·라운드명은 데이터와 정확히 일치해야 합니다. 선수 이름은 korean_name이 있으면 한글로, 없으면 데이터의 로마자 표기 그대로 씁니다.
- Q는 순위로 진출, q는 기록으로 진출, ADV는 심판 판정으로 진출, PEN은 페널티입니다.
- projection(예상 대진)은 공식 발표 전 계산값이므로 '예상'임을 분명히 밝힙니다.
- 아직 끝나지 않은 라운드는 결과를 단정하지 않습니다.
- 분량은 본문 600~1000자, 독자는 일반 스포츠 팬입니다. 담백한 신문 칼럼 문체로 씁니다."""

SCHEMA = {
    'type': 'object',
    'properties': {
        'title': {'type': 'string', 'description': '30자 이내 제목'},
        'summary': {'type': 'string', 'description': '한 문장 요약'},
        'body': {'type': 'string', 'description': '본문. 문단은 빈 줄로 구분'},
    },
    'required': ['title', 'summary', 'body'],
    'additionalProperties': False,
}

def load(path, default):
    try: return json.loads(path.read_text())
    except Exception: return default

def kst_day(ts):
    return dt.datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(KST).date().isoformat()

def groups():
    """{(event_id, day): {'event': ..., 'rows': [...], 'projections': [...]}} for recent events."""
    names = load(WINTER / 'names-ko.json', {})
    cutoff = (dt.datetime.now(KST) - dt.timedelta(days=2)).date().isoformat()
    out = {}
    for f in sorted((WINTER / 'events').glob('*.json')):
        data = load(f, {})
        ev = data.get('event') or {}
        for r in data.get('korea') or []:
            if not r.get('start_utc'): continue
            day = kst_day(r['start_utc'])
            if day < cutoff: continue
            g = out.setdefault((ev['id'], day), {'event': {k: ev.get(k) for k in ('name', 'sport', 'city', 'country', 'start', 'end')},
                                                 'day': day, 'rows': [], 'projections': []})
            g['rows'].append({**{k: r.get(k) for k in ('distance', 'round', 'heat', 'name', 'rank', 'time', 'qual', 'status')},
                              'korean_name': names.get(r.get('name'), '')})
        for dist in (data.get('results') or {}).values():
            for rnd in dist.get('rounds') or []:
                p = rnd.get('projection')
                if p and not p['official_draw_published'] and any(c['noc'] == 'KOR' for c in p['qualified']) and rnd.get('start_utc'):
                    key = (ev['id'], kst_day(rnd['start_utc']))
                    if key in out:
                        out[key]['projections'].append({'distance': dist['title'], 'from_round': rnd['name'], 'next': p['next'],
                                                        'projected_races': p['races']})
    return out

def digest(g):
    return hashlib.sha256(json.dumps([g['rows'], g['projections']], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]

def write(client, g):
    import anthropic
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        betas=['server-side-fallback-2026-07-01'],
        fallbacks='default',
        output_config={'effort': 'medium', 'format': {'type': 'json_schema', 'schema': SCHEMA}},
        system=SYSTEM,
        messages=[{'role': 'user', 'content': '다음 데이터로 칼럼을 써 주세요.\n\n' + json.dumps(g, ensure_ascii=False, indent=1)}],
    )
    if response.stop_reason == 'refusal':
        raise RuntimeError(f'refused: {response.stop_details}')
    text = next(b.text for b in response.content if b.type == 'text')
    return json.loads(text), response.model

def main():
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print('column: ANTHROPIC_API_KEY not set, skipping'); return 0
    import anthropic
    client = anthropic.Anthropic()
    index = load(OUT / 'index.json', {'columns': []})
    known = {c['id']: c for c in index['columns']}
    todo = []
    for (event_id, day), g in groups().items():
        cid = f'{event_id}-{day}'
        h = digest(g)
        if known.get(cid, {}).get('source_hash') != h:
            todo.append((cid, h, g))
    failed = 0
    for cid, h, g in todo[:MAX_PER_RUN]:
        try:
            col, model = write(client, g)
        except (anthropic.APIError, RuntimeError, ValueError, StopIteration) as exc:
            failed += 1
            print(f'column {cid} failed: {type(exc).__name__}: {exc}', file=sys.stderr)
            continue
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        rec = {'id': cid, 'event_id': cid.rsplit('-', 3)[0], 'event': g['event']['name'], 'sport': g['event']['sport'],
               'day': g['day'], 'title': col['title'], 'summary': col['summary'], 'body': col['body'],
               'generated_at': now, 'model': model, 'source_hash': h, 'ai': True}
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f'{cid}.json').write_text(json.dumps(rec, ensure_ascii=False, indent=1) + '\n')
        known[cid] = {k: rec[k] for k in ('id', 'event_id', 'event', 'sport', 'day', 'title', 'summary', 'generated_at', 'source_hash')}
        print(f'column {cid}: {col["title"]}')
    index['columns'] = sorted(known.values(), key=lambda c: (c['day'], c['generated_at']), reverse=True)
    (OUT).mkdir(parents=True, exist_ok=True)
    (OUT / 'index.json').write_text(json.dumps(index, ensure_ascii=False, indent=1) + '\n')
    return 1 if failed and failed == len(todo[:MAX_PER_RUN]) else 0

if __name__ == '__main__':
    sys.exit(main())
