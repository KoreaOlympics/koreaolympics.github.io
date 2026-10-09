"""Fetch official IJF rankings; publish only after all 14 categories validate."""
import datetime as dt, json, re, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CATEGORIES=dict(zip(['m60','m66','m73','m81','m90','m100','mo100','w48','w52','w57','w63','w70','w78','wo78'],range(1,15)))
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json,text/html'})
 with urllib.request.urlopen(req,timeout=30) as r: return r.read().decode('utf-8')
def get_category(category,action):
 rows=[]
 for page in range(10):
  url=f'https://www.ijf.org/internal_api/{action}?category={category}&limit=100&page={page}'
  feed=json.loads(fetch(url))['feed']
  if not isinstance(feed,list): raise ValueError('Unexpected IJF feed')
  rows.extend(feed)
  if len(feed)<100: break
 else: raise ValueError('IJF pagination exceeded safety limit')
 return rows

def select(rows):
 seen=set(); selected=[]
 for x in sorted(rows,key=lambda x:(int(x['place']),-float(x['sum_points']))):
  if str(x.get('strike_through','0'))=='1' or str(x.get('personal_strike_through','0'))=='1': continue
  noc=x['country_ioc_code'].upper()
  if not re.fullmatch('[A-Z]{3}',noc): raise ValueError('Invalid NOC')
  if noc in seen: continue
  seen.add(noc)
  selected.append({'rank':int(x['place']),'previousRank':int(x['place_prev']),'name':x['given_name']+' '+x['family_name'],'noc':noc,'points':float(x['sum_points'])})
  if len(selected)==17: break
 if len(selected)!=17: raise ValueError('Fewer than 17 distinct NOCs')
 return selected

def main():
 now=dt.datetime.now(dt.timezone.utc).isoformat(); out={}
 for key,category in CATEGORIES.items():
  rows=get_category(category,'wrl_olympic'); kind='olympic'
  if not rows: rows=get_category(category,'wrl');kind='world-reference'
  out[key]={'kind':kind,'source':f'https://www.ijf.org/{"wrl_olympic" if kind=="olympic" else "wrl"}?category={category}','athletes':select(rows)}
  print(key,kind,len(rows))
 raw=fetch('https://www.ijf.org/wrl');version=re.search(r'Seniors:\s*([0-9A-Za-z-]+)',raw)
 payload={'checkedAt':now,'worldRankingVersion':version.group(1) if version else None,'categories':out}
 path=ROOT/'data/ijf-ranking.json'; data=json.dumps(payload,ensure_ascii=False,indent=2)
 history=ROOT/'data/ijf-history';history.mkdir(exist_ok=True)
 # Archive distinct data, retaining the ranking history without empty overwrites.
 previous=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
 if previous.get('categories')!=out:
  (history/(now[:19].replace(':','-')+'.json')).write_text(data,encoding='utf-8')
 temp=path.with_suffix('.tmp');temp.write_text(data,encoding='utf-8');temp.replace(path)
if __name__=='__main__': main()
