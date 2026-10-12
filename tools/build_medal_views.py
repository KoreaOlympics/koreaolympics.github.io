"""Build reviewed result data for integration into existing wiki documents."""
import json,re,html,subprocess
from pathlib import Path
import boxing_pages as B,tour_pages as T,shooting_pages as S
from podium_tables import Table,plain
R=Path(__file__).resolve().parents[1]
LABELS={'judo':'유도','wrestling':'레슬링','boxing':'복싱','fencing':'펜싱','badminton':'배드민턴','tabletennis':'탁구','shooting':'사격','archery':'양궁','golf':'골프','taekwondo':'태권도'}
CHINESE={'CHEN Ximin':'천시민','CHEN Xuyan':'천쉬옌','FU Xiaolu':'푸샤오루','HUANG Kefen':'황커펀','LI Mixue':'리미쉐','LI Yawen':'리야원','LIU Zixuan':'류쯔쉬안','LUO Zongshi':'뤄쭝스','MA Jingyue':'마징웨','MU Wenzhe':'무원저','SHEN Zinuo':'선쯔눠','WANG Shiyi':'왕스이','WANG Xiaolu':'왕샤오루','WU Shanshan':'우산산','XIANG Qizhang':'샹치장','XING Jiani':'싱자니','XU Lei':'쉬레이','YE Xiaoting':'예샤오팅','ZHANG Chuling':'장추링','ZHOU Zeqi':'저우쩌치','ZUO JU':'쭤주'}
CHINESE.update({'CHEN Yufan':'천위판','CAI Zhaoxun':'차이자오쉰','MENG Mingkuan':'멍밍콴','TANG Hao':'탕하오','XIAO Shunan':'샤오수난','SONG Jie':'쑹제'})
DATA={s:dict(label=l,weights={},meets=[],records=[]) for s,l in LABELS.items()}
def person(name,noc='',url='',family=''):
 full=name;name=T.KOR.get(name,CHINESE.get(name,name))
 if noc not in ['KOR','CHN','TPE','HKG'] and not re.search('[가-힣]',name):name=family or (name.split()[0].title() if name.split()[0].isupper() and len(name.split())>1 else name.split()[-1])
 return dict(name=name,fullName=full,country=noc,url=url)
def add(s,w,label,meet,name,date,rank,p,source='',note=''):
 d=DATA[s];d['weights'][w]=label
 if not any(m['id']==meet for m in d['meets']):d['meets'].append(dict(id=meet,name=name,date=str(date),url=source,note=note))
 row=next((r for r in d['records'] if r['meet']==meet and r['weight']==w),None)
 if row is None:row=dict(meet=meet,weight=w,event=label,date=str(date),state='수록 기록',source=source,medals={'gold':[],'silver':[],'bronze':[]});d['records'].append(row)
 if rank:
  bucket=row['medals'][rank]
  if not any(x['fullName']==p['fullName'] and x['country']==p['country'] for x in bucket):bucket.append(p)
def build():
 for r in B.load_data()['results']:
  rank={'금':'gold','은':'silver','동':'bronze'}.get(r['result'])
  if not rank:continue
  label=dict(B.WEIGHTS).get(r['weight'],('남자 ' if r['weight'].startswith('m') else '여자 ')+r['weight'][1:].replace('o','+')+'kg');year=r['axis'][:4];meet=r['axis']+'-'+r['competition']
  noc=r.get('noc') or B.NOC.get(r.get('country',''),r.get('country','')) or ('KOR' if re.search('[가-힣]',r['athlete']) else '')
  add('boxing',r['weight'],label,meet,r['competition'],year,rank,person(r['athlete'],noc,r['source'],r.get('family_name','')),B.page(r['axis'])+'#weight-'+r['weight'])
 for sport in ['badminton','tabletennis']:
  labels=T.SPORTS[sport]['events']|{'mt':'남자 단체','wt':'여자 단체'}
  for r in T.data(sport)['results']:
   rank={'우승':'gold','금':'gold','준우승':'silver','은':'silver','동':'bronze','4강':'bronze','준결승':'bronze','준결승 탈락':'bronze'}.get(r['result'])
   if not rank:continue
   noc=T.NOC.get(r['country'],r['country']);full=' / '.join(r['members']);p=person(full,noc,r['source'])
   p['name']=' / '.join(person(n,noc)['name'] for n in r['members']) if len(r['members'])<=2 else noc+' 팀'
   add(sport,r['event'],labels.get(r['event'],r['event']),str(r['year'])+'-'+r['competition'],T.LABELS.get(r['competition'],r['competition']),r['year'],rank,p,'ol'+sport+'-'+str(r['year'])+'.html#event-'+r['event'])
 jd=json.loads((R/'data/judo-world-2026.json').read_text(encoding='utf-8'))
 for r in jd['results']:
  if r['rank'] not in [1,2,3]:continue
  w=r['event'];label=('남자 ' if w[0]=='m' else '여자 ')+w[1:].replace('o','+')+'kg'
  add('judo',w,label,'world2026','2026 세계선수권',2026,{1:'gold',2:'silver',3:'bronze'}[r['rank']],person(r['name'],r['noc'],jd['source']),'oljudo-2026-world.html')
 for r in S.R:
  if not S.medal(r):continue
  c=S.comp(r);event=r['event']
  if event not in S.E:continue
  add('shooting',event,S.E[event]['label'],str(r['competition']),c['name'],c['start'],{1:'gold',2:'silver',3:'bronze'}[r['rank']],person(S.names(r),r['country'],r['url']),r['url'])
 legacy=json.loads((R/'data/sports-results-2026.json').read_text(encoding='utf-8'))
 for event,podium in legacy['fencing'].items():
  for rank,people in podium.items():
   for p in people:add('fencing',event,event,'world2026','2026 세계선수권',2026,{'1':'gold','2':'silver','3':'bronze'}[rank],person(' / '.join(p['names']),p['noc'],'olfencing-results.html'),'olfencing-results.html')
 archery=[]
 for key,value in legacy['archery'].items():
  if key=='worldcup':archery.extend((stage,events) for stage,events in value.items())
  else:archery.append(('2026 아시안게임',value))
 for meet,events in archery:
  for event,podium in events.items():
   if not isinstance(podium,dict):continue
   for rank,people in podium.items():
    if rank not in ['1','2','3']:continue
    for p in people:add('archery',event,event,meet,meet,2026,{'1':'gold','2':'silver','3':'bronze'}[rank],person(' / '.join(p['names']),p['noc'],'olarchery-results.html'),'olarchery-results.html')
 for p in R.glob('olwrestling-ev-*.html'):
  old=subprocess.check_output(['git','show','HEAD:'+p.name]).decode('utf-8');w=p.stem.removeprefix('olwrestling-ev-');label=re.search(r'<h1[^>]*>(.*?)</h1>',old,re.S)
  for table in re.findall(r'<table\b.*?</table>',old,re.S):
   t=Table(table)
   if not t.rows or len(t.rows[0]['cells'])!=2 or plain(t.rows[0]['cells'][0]['html'])!='대회':continue
   for row in t.rows[1:]:
    if len(row['cells'])!=2:continue
    comp,value=[plain(c['html']) for c in row['cells']];m=re.search(r'^(.*?) · (금|은|동)(?:메달)?$',value)
    if not m:continue
    href=re.search('href="([^"]+)"',row['cells'][1]['html']);src=href[1] if href else p.name
    add('wrestling',w,plain(label[1]) if label else w,comp,comp,re.search(r'20\d\d',comp)[0] if re.search(r'20\d\d',comp) else '2026',{'금':'gold','은':'silver','동':'bronze'}[m[2]],person(m[1],'KOR',src),p.name)
 previous=R/'data/medal-views.json'
 if not DATA['wrestling']['records'] and previous.exists():DATA['wrestling']=json.loads(previous.read_text(encoding='utf-8'))['wrestling']
 for prefix,title,weights in [('fs','남자 자유형',[57,65,74,86,97,125]),('gr','그레코로만',[60,67,77,87,97,130]),('ww','여자 자유형',[50,53,57,62,68,76])]:
  for w in weights:add('wrestling',prefix+str(w),title+' '+str(w)+'kg','2026 아시안게임','2026 아시안게임','2026',None,None,'olwrestling-2026-ag.html#'+prefix+str(w))
 tk=json.loads((R/'data/taekwondo-pathways.json').read_text(encoding='utf-8'))
 import taekwondo_rules as K
 K.KO.update({'KIM Hyanggi':'김향기','KWAK Min Ju':'곽민주','YANG Hui-chan':'양희찬','SEO Yeo-won':'서여원','LEE Ga-eun':'이가은','HONG Hyo Rim':'홍효림'})
 for m in tk['events']:
  for r in m['medals']:
   w=r['weight'];label=w.replace('Men','남자').replace('Women','여자');name=K.KO.get(r['name'],r['name'])
   add('taekwondo',w,label,m['id'],m['title'],m['start'],{'Gold':'gold','Silver':'silver','Bronze':'bronze'}[r['medal']],person(name,r['country'],m.get('resultUrl','oltaekwondo.html')),m.get('resultUrl','oltaekwondo.html'))
 golf=json.loads((R/'data/golf-majors.json').read_text(encoding='utf-8'))
 for r in golf:
  add('golf',r['event'],r['label'],r['id'],r['name'],r['year'],None,None,r['source'])
  for rank,people in r.get('medals',{}).items():
   for p in people:add('golf',r['event'],r['label'],r['id'],r['name'],r['year'],rank,person(p['name'],p.get('country',''),r['source']),r['source'])
 (R/'data/medal-views.json').write_text(json.dumps(DATA,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 from import_wikipedia_podiums import update
 update()
 from integrate_wiki_results import run
 run()
 print({s:len(d['records']) for s,d in DATA.items()})
if __name__=='__main__':build()
