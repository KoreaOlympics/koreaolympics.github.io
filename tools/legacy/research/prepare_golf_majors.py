import json
from pathlib import Path
R=Path(__file__).resolve().parents[3]
names=[('m-masters','남자 마스터스','마스터스','https://www.masters.com/'),('m-pga','남자 PGA 챔피언십','PGA 챔피언십','https://www.pgatour.com/player/46414/Aaron-Rai/results'),('m-usopen','남자 US 오픈','US 오픈','https://www.usopen.com/'),('m-open','남자 디 오픈','디 오픈','https://www.theopen.com/latest/champion-golfers-list'),('w-chevron','여자 셰브론','셰브론 챔피언십','https://www.lpga.com/tournaments/chevron-championship/overview'),('w-usopen','여자 US 오픈','US 여자 오픈','https://www.lpga.com/tournaments/major-championship-records'),('w-pga','여자 PGA 챔피언십','KPMG 여자 PGA 챔피언십','https://www.lpga.com/tournaments/major-championship-records'),('w-evian','여자 에비앙','에비앙 챔피언십','https://www.lpga.com/tournaments/major-championship-records'),('w-open','여자 AIG 오픈','AIG 여자 오픈','https://www.aigwomensopen.com/')]
winners={2025:[('Rory McIlroy','GBR'),('Scottie Scheffler','USA'),('J.J. Spaun','USA'),('Scottie Scheffler','USA'),('Mao Saigo','JPN'),('Maja Stark','SWE'),('Minjee Lee','AUS'),('Grace Kim','AUS'),('Miyu Yamashita','JPN')],2026:[('Rory McIlroy','GBR'),('Aaron Rai','ENG'),('Wyndham Clark','USA'),('Ryan Fox','NZL'),('Nelly Korda','USA'),('Nelly Korda','USA'),('류해란','KOR'),('류해란','KOR'),('Shiho Kuwaki','JPN')]}
rows=[]
for year,people in winners.items():
 for (event,label,title,url),(winner,noc) in zip(names,people):rows.append(dict(id=str(year)+'-'+event,event=event,label=label,name=str(year)+' '+title,year=year,source=url,medals={'gold':[{'name':winner,'country':noc}]}))
rows[-1]['medals']['silver']=[{'name':'Esther Henseleit','country':'GER'}]
rows[-1]['source']='https://www.aigwomensopen.com/news/2026/08/shiho-kuwaki-wins-royal-lytham-50th-esther-henseleit'
rows[1]['source']='https://internationalmedia.pgatour.com/uploads/the_cut/2025/2025-pga-tour-the-cut-21-master-script.pdf'
(R/'data/golf-majors.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
