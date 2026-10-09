"""Validate records; --update accepts one complete event revision, preserving history."""
import argparse,datetime as dt,json,re
from urllib.parse import urlparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];FILE=ROOT/'data/skateboard-events.json'
STATES={'scheduled','in_progress','awaiting_results','results_confirmed','wsr_confirmed'}
def official(url):
 if not url:return False
 u=urlparse(url);return u.scheme=='https' and (u.hostname=='worldskate.org' or u.hostname.endswith('.worldskate.org') or u.hostname=='worldskate.tv' or u.hostname.endswith('.worldskate.tv'))
def validate(data):
 seen=set()
 for e in data['events']:
  assert e['event_id'] not in seen,'Duplicate event';seen.add(e['event_id'])
  assert e['discipline'] in {'park','street'} and e['gender'] in {'men','women'}
  assert e['status'] in STATES
  start,end=[dt.date.fromisoformat(e[k]) for k in ['start_date','end_date']];assert start<=end
  for k in ['checked_at','updated_at']:dt.date.fromisoformat(e[k])
  assert official(e['official_event_url']) and official(e['wsr_url']),'Missing official source'
  assert e['history'],'Missing history'
  assert e['la28_points_eligible'] is None or type(e['la28_points_eligible']) is bool
  if e['la28_points_eligible'] is True:
   assert start>=dt.date(2026,6,11) and end<=dt.date(2028,6,11)
   assert e['eligibility_basis'] and official(e.get('eligibility_source_url')),'Eligibility needs official rule source'
  if e['status'] in {'results_confirmed','wsr_confirmed'}:
   assert official(e['official_results_url']) and e['results'],'Confirmed results need official source and rows'
  ids=set();positions=set()
  for a in e['results']:
   assert a['athlete_id'] not in ids;ids.add(a['athlete_id'])
   assert type(a['position']) is int and a['position']>0
   assert a['position'] not in positions;positions.add(a['position'])
   assert a['name'] and re.fullmatch('[A-Z]{3}',a['noc'])
   assert a['wsr_points'] is None or isinstance(a['wsr_points'],(int,float)) and a['wsr_points']>=0
  change_ids=set()
  for c in e['wsr_changes']:
   assert c['athlete_id'] in ids and c['athlete_id'] not in change_ids;change_ids.add(c['athlete_id'])
   for k in ['previous_rank','current_rank']:assert type(c[k]) is int and c[k]>0
   assert c['delta']==c['previous_rank']-c['current_rank'],'Incorrect rank delta'
   assert official(c['previous_source_url']) and official(c['current_source_url'])
   dt.date.fromisoformat(c['checked_at'])
  if e['status']=='wsr_confirmed':assert e['wsr_changes'],'Missing confirmed WSR changes'
 return data

def main():
 p=argparse.ArgumentParser();p.add_argument('--update',type=Path);a=p.parse_args();data=json.loads(FILE.read_text(encoding='utf-8'))
 if a.update:
  event=json.loads(a.update.read_text(encoding='utf-8'));old=next((x for x in data['events'] if x['event_id']==event['event_id']),None)
  stamp=dt.datetime.now(dt.timezone.utc).isoformat();today=stamp[:10]
  event['history']=(old['history'] if old else [])+[{'at':stamp,'note':'Event revision saved after validation','previous_record':{k:v for k,v in old.items() if k!='history'} if old else None}]
  event['updated_at']=today;data['updated_at']=today
  data['events']=[x for x in data['events'] if x['event_id']!=event['event_id']]+[event]
 validate(data)
 if a.update:
  tmp=FILE.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(FILE)
 print(f"Validated {len(data['events'])} events")
if __name__=='__main__':main()
