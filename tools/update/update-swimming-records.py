"""Fetch Korea Aquatics 50m-pool record tables; validate before atomic write."""
import argparse,datetime,html,json,re,time,urllib.request
from pathlib import Path
CATEGORIES={'free':'006001','back':'006002','breast':'006003','fly':'006007','im':'006005','relayfree':'006004','relaymedley':'006006'}
EXPECTED={g+s+str(d) for g in 'mw' for s,ds in [('free',[50,100,200,400,800,1500]),('back',[50,100,200]),('breast',[50,100,200]),('fly',[50,100,200]),('im',[200,400])] for d in ds}|{g+s for g in 'mw' for s in ['relay4x100free','relay4x200free','relay4x100medley']}|{'xrelay4x100medley'}
def clean(s):
    s=re.sub(r'<(?:br\b[^>]*|/h[1-6]|/p|/div)>','\n',s,flags=re.I)
    s=html.unescape(re.sub('<[^>]+>','',s))
    return '\n'.join(re.sub(r'\s+',' ',x).strip() for x in s.splitlines() if x.strip())
def seconds(t):
    parts=t.split(':');return sum(float(x)*60**i for i,x in enumerate(reversed(parts)))
def parse_document(raw,stroke,url):
    tables=re.findall(r'<table\b[^>]*>(.*?)</table>',raw,re.S|re.I)
    out={}; relevant=[]
    for table in tables:
        if '한국' in table and '신기록' in table:relevant.append(table)
    for gender,table in zip('mwx',relevant):
        for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',table,re.S|re.I):
            cells=re.findall(r'<(?:td|th)\b[^>]*>(.*?)</(?:td|th)>',row,re.S|re.I)
            if len(cells)!=5:continue
            distance=re.search(r'\d+',clean(cells[0]))
            if not distance:continue
            dist=int(distance.group()); key=gender+stroke+str(dist)
            if stroke=='relayfree':key=gender+({400:'relay4x100free',800:'relay4x200free'}.get(dist,'unsupported'))
            elif stroke=='relaymedley':key=gender+('relay4x100medley' if dist==400 else 'unsupported')
            if key not in EXPECTED:continue
            lines=clean(cells[-1]).splitlines(); record_time=re.search(r'\d{1,2}:\d{2}\.\d{2}',lines[0]) if lines else None
            date=re.search(r'(\d{4})\.(\d{2})\.(\d{2})',clean(cells[-1]))
            if not record_time or len(lines)<3 or not date:raise ValueError('Unrecognised record cell: '+key)
            value=record_time.group(); value=value[3:] if value.startswith('00:') else value.lstrip('0')
            if value.startswith(':'):value='0'+value
            out[key]={'time':value,'holder':re.sub(r'\s*\([^)]*\)','',lines[1]).strip(),'date':'-'.join(date.groups()),'meet':clean(cells[-1]).split('/',1)[-1].strip(),'source':url,'status':'연맹 게시'}
    return out
def update(output,local=None):
    fresh={}
    for stroke,cat in CATEGORIES.items():
        url='https://www.korswim.co.kr/page/14?cate='+cat+'&cor=021002'
        if local:
            name='korea-official' if stroke=='free' else 'official-'+stroke
            raw=(Path(local)/('swim-'+name+'.html')).read_text(encoding='utf8')
        else:
            req=urllib.request.Request(url,headers={'User-Agent':'KoreaOlympics-records/1.0 (public record comparison)'})
            for attempt in range(3):
                try:
                    with urllib.request.urlopen(req,timeout=45) as r:raw=r.read().decode('utf-8')
                    break
                except Exception:
                    if attempt==2:raise
                    time.sleep(2)
        fresh.update(parse_document(raw,stroke,url))
    if set(fresh)!=EXPECTED:raise ValueError('Incomplete source: missing '+str(sorted(EXPECTED-set(fresh))))
    path=Path(output); old=json.loads(path.read_text(encoding='utf8')) if path.exists() else {'records':{},'history':[]}
    records=old.get('records',{}); history=old.get('history',[])
    for key,new in fresh.items():
        previous=records.get(key)
        if previous and seconds(new['time'])>seconds(previous['time'])+.0001:raise ValueError('Source regression; manual review needed: '+key)
        if previous!=new:
            if previous:history.append({'event':key,'previous':previous,'next':new,'detected':datetime.date.today().isoformat()})
            records[key]=new
    result={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),'pool':'50m','records':records,'history':history}
    path.parent.mkdir(parents=True,exist_ok=True); temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');temporary.replace(path)
    print('Validated',len(records),'records')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='data/swimming-records.json');p.add_argument('--local');a=p.parse_args();update(a.output,a.local)
