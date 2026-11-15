"""Fetch official IJF rankings; publish only after all 14 categories validate."""
import datetime as dt, json, re, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CATEGORIES=dict(zip(['m60','m66','m73','m81','m90','m100','mo100','w48','w52','w57','w63','w70','w78','wo78'],range(1,15)))
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json,text/html'})
 with urllib.request.urlopen(req,timeout=30) as r: return r.read().decode('utf-8')
API='https://ijf.org/api/v1/wrl?limit=2000'  # 2026-10 개편된 ijf.org의 랭킹 API (예전 www.ijf.org/internal_api는 없어졌다)
def get_all():
 """체급 번호(1~14) → 순위순 선수 목록. limit은 전체 합계에 걸리므로 넉넉히 준다."""
 cats=json.loads(fetch(API))['categories']
 if not isinstance(cats,dict) or len(cats)!=14: raise ValueError('Unexpected IJF feed')
 return {int(k):v['competitors'] for k,v in cats.items()}

def select(rows):
 seen=set(); selected=[]
 for x in sorted(rows,key=lambda x:(int(x['place']),-float(x['points']))):
  noc=x['country_short'].upper()
  if not re.fullmatch('[A-Z]{3}',noc): raise ValueError('Invalid NOC')
  if noc in seen: continue
  seen.add(noc)
  selected.append({'rank':int(x['place']),'previousRank':int(x['place_prev'] or 0),'name':x['given_name']+' '+x['family_name'],'noc':noc,'points':float(x['points'])})
  if len(selected)==17: break
 if len(selected)!=17: raise ValueError('Fewer than 17 distinct NOCs')
 return selected

def main():
 now=dt.datetime.now(dt.timezone.utc).isoformat(); out={}
 feed=get_all()
 for key,category in CATEGORIES.items():
  rows=feed[category]
  out[key]={'kind':'world-reference','source':'https://ijf.org/world-ranking','athletes':select(rows)}
  print(key,len(rows))
 # 새 사이트는 랭킹 버전 문자열을 내보내지 않는다 → 수집일을 적는다
 payload={'checkedAt':now,'worldRankingVersion':now[:10]+' 수집','categories':out}
 path=ROOT/'data/ijf-ranking.json'; data=json.dumps(payload,ensure_ascii=False,indent=2)
 history=ROOT/'data/ijf-history';history.mkdir(exist_ok=True)
 # Archive distinct data, retaining the ranking history without empty overwrites.
 previous=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
 if previous.get('categories')!=out:
  (history/(now[:19].replace(':','-')+'.json')).write_text(data,encoding='utf-8')
 temp=path.with_suffix('.tmp');temp.write_text(data,encoding='utf-8');temp.replace(path)
if __name__=='__main__': main()
