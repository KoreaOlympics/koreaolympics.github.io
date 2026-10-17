"""Refresh ratified World Aquatics 50m-pool records; keep fixed LA28 standards."""
import datetime,json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE='https://api.worldaquatics.com/fina/records/SW?recordCode=WR&eventTypeId=&region=&countryId=&gender={}&pool=LCM'
def seconds(s):
 parts=s.split(':');return sum(float(v)*60**i for i,v in enumerate(reversed(parts)))
def key(r,g):
 t=r['eventDisciplineName'].lower();d=re.search(r'(\d+)m',t)
 if not d:return None
 if 'relay' in t:return g+('relay4x100medley' if 'medley' in t else 'relay4x'+d[1]+'free')
 stroke=next((code for word,code in [('freestyle','free'),('backstroke','back'),('breaststroke','breast'),('butterfly','fly'),('medley','im')] if word in t),None)
 return g+stroke+d[1] if stroke else None
def main():
 definitions=json.loads((ROOT/'data/swimming-la28-standards.json').read_text(encoding='utf-8'));events={}
 for api_g,g in [('M','m'),('F','w'),('X','x')]:
  url=BASE.format(api_g)
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'KoreaOlympics-records/1.0'}),timeout=35) as response:data=json.load(response)
  for r in data.get('records',[]):
   k=key(r,g)
   if k not in definitions['events'] or r['recordStatus']!=2:continue
   assert r['pool']==0 and seconds(r['timeFormatted'])>0
   if k in events and seconds(events[k]['world']['time'])<=seconds(r['timeFormatted']):continue
   events[k]={**definitions['events'][k],'world':{'time':r['timeFormatted'],'holder':r.get('fullName') or r['nationalityName'],'noc':r['nationalityCode'],'date':r['date'][:10],'source':url}}
 if len(events)!=41 or sum(bool(e['a']) for e in events.values())!=28:raise ValueError('41종목 / 28개 A기준 검증 실패')
 dest=ROOT/'data/swimming-benchmarks.json'
 if dest.exists():
  previous=json.loads(dest.read_text(encoding='utf-8'))
  for k,e in events.items():
   if seconds(e['world']['time'])>seconds(previous['events'][k]['world']['time']):raise ValueError(k+': 세계기록이 느려짐, 교체 중단')
 result={'pool':'50m','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),'world_source':'https://www.worldaquatics.com/swimming/records','standard_source':definitions['source'],'standard_version':definitions['version'],'events':events}
 temp=dest.with_suffix('.tmp');temp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(dest);print('41종목 세계기록 검증·갱신 완료')
if __name__=='__main__':
 try:main()
 except Exception as exc:print('기존 기준 자료 유지: '+str(exc),file=sys.stderr);sys.exit(1)
