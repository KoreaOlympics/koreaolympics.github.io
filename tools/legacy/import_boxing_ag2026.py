"""Import the visible AINAGOC medal-list snapshot, preserving other tournaments."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 snapshot=json.loads((ROOT/'tools/legacy/research/boxing-ag2026-official.json').read_text(encoding='utf-8'))
 headings=re.findall(r"(?:Men|Women)'s \+?\d+kg",snapshot['text'])
 assert len(headings)==11 and len(snapshot['links'])==44
 country={'JPN':'Japan','PHI':'Philippines','MGL':'Mongolia','KAZ':'Kazakhstan','UZB':'Uzbekistan','KOR':'South Korea','TJK':'Tajikistan','JOR':'Jordan','IND':'India','CHN':'China','IRI':'Iran','VIE':'Vietnam','THA':'Thailand','PRK':'North Korea','TPE':'Chinese Taipei'}
 korean={'JANG Donghwan':'장동환','KIM Minseong':'김민성'}
 rows=[];weights=[]
 for i,heading in enumerate(headings):
  code=('m' if heading.startswith('Men') else 'w')+re.search(r'(\+?\d+)kg',heading)[1].replace('+','o');weights.append(code)
  for j,item in enumerate(snapshot['links'][i*4:i*4+4]):
   parts=item['text'].splitlines();name=' '.join(parts[1:]);noc=parts[0]
   rows.append(dict(id='ag2026-'+code+'-'+str(j),axis='2026-ag',weight=code,competition='2026 아시안게임',athlete=korean.get(name,name),country=country[noc],noc=noc,family_name=parts[1],result=['금','은','동','동'][j],source=item['href'],provenance='AINAGOC official medal list'))
 p=ROOT/'data/boxing-pathways.json';data=json.loads(p.read_text(encoding='utf-8'))
 data['results']=[r for r in data['results'] if r['axis']!='2026-ag']+rows
 data['as_of']=snapshot['checkedAt'];data['scope']='2025 medal tables; 2026 AINAGOC official Asian Games podiums; other existing Korean records'
 data.setdefault('competitions',{})['2026-ag']=dict(title='2026 아이치·나고야 아시안게임',start='2026-09-21',end='2026-10-02',venue='니시오시 종합체육관',weights=weights,status='완료',medals=44,koreanSummary='은 2 · 장동환(60kg), 김민성(80kg)',source=snapshot['source'],scheduleSource='https://www.aichi-nagoya2026.org/news-2003/')
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 print('Imported 44 official medal records across 11 Asian Games weights')
if __name__=='__main__':main()
