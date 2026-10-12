"""Podiums transcribed from the named Wikipedia tournament articles, 2026-10-13."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
W=[
('fs57','Aman Sehrawat|IND','Han Chong-song|PRK','Zou Wanhao|CHN','Aiaal Belolyubskii|TJK'),
('fs65','Sujeet Kalkal|IND','Abdulmazhid Kudiev|TJK','Kotaro Kiyooka|JPN','Nachyn Kuular|KAZ'),
('fs74','Younes Emami|IRI','Yoshinosuke Aoyagi|JPN','Viktor Rassadin|TJK','Nurkozha Kaipanov|KAZ'),
('fs86','Mohammad Nokhodi|IRI','Hayato Ishiguro|JPN','Malik Shavaev|KGZ','Olonbayaryn Süldkhüü|MGL'),
('fs97','Amir Ali Azarpira|IRI','Sherzod Poyonov|UZB','Deepak Punia|IND','Arash Yoshida|JPN'),
('fs125','Amir Hossein Zare|IRI','Buheeerdun|CHN','Shamil Sharipov|BRN','Yedige Kassimbek|KAZ'),
('gr60','Zholaman Sharshenbekov|KGZ','Alisher Ganiev|UZB','Sajjad Ali|IRQ','Ayata Suzuki|JPN'),
('gr67','Aytjan Khalmakhanov|UZB','Kyotaro Sogabe|JPN','Razzak Beishekeev|KGZ','Meirzhan Shermakhanbet|KAZ'),
('gr77','Alireza Abdevali|IRI','Nao Kusaka|JPN','Akzhol Makhmudov|KGZ','Shahin Badaghi|QAT'),
('gr87','Taizo Yoshida|JPN','Asan Zhanyshov|KGZ','Jalgasbay Berdimuratov|UZB','Sunil Kumar|IND'),
('gr97','Yuri Nakazato|JPN','Nitesh Siwach|IND','Ganbaataryn Gankhuyag|MGL','Mehdi Bali|IRI'),
('gr130','Amin Mirzazadeh|IRI','Rafael Tsitsuashvili|UZB','Meng Lingzhe|CHN','김민석|KOR'),
('ww50','Yui Susaki|JPN','Kim Son-hyang|PRK','Feng Ziqi|CHN','Zeinep Bayanova|KAZ'),
('ww53','Moe Kiyooka|JPN','Antim Panghal|IND','Zhang Jin|CHN','Bayanmönkhiin Otgontuyaa|MGL'),
('ww57','Hong Kexin|CHN','Son Il-sim|PRK','Nilufar Raimova|KAZ','Akari Fujinami|JPN'),
('ww62','Nonoka Ozaki|JPN','Kim Ok-ju|PRK','Togtokhyn Altjin|MGL','Zhang Qi|CHN'),
('ww68','Ami Ishii|JPN','Pak Sol-gum|PRK','Meerim Zhumanazarova|KGZ','Long Jia|CHN'),
('ww76','Yuka Kagami|JPN','Elmira Syzdykova|KAZ','Aiperi Medet Kyzy|KGZ','Li Wenji|CHN')]
URL='https://en.wikipedia.org/wiki/Wrestling_at_the_2026_Asian_Games'
def p(raw,url):
 name,noc=raw.rsplit('|',1)
 display=name if noc in ['KOR','CHN','TPE','HKG'] else name.split()[-1]
 return dict(name=display,fullName=name,country=noc,url=url)
def update():
 path=R/'data/medal-views.json';data=json.loads(path.read_text(encoding='utf-8'));d=data['wrestling']
 for code,g,s,b1,b2 in W:
  row=next(x for x in d['records'] if x['weight']==code)
  row.update(date='2026-09-30',source=URL,state='확인된 결과',medals={'gold':[p(g,URL)],'silver':[p(s,URL)],'bronze':[p(b1,URL),p(b2,URL)]})
 d['meets'][0]['url']=URL
 url='https://en.wikipedia.org/wiki/2026_All_England_Open'
 bronze={'ms':['Victor Lai|CAN','Kunlavut Vitidsarn|THA'],'ws':['Chen Yufei|CHN','Akane Yamaguchi|JPN'],'wd':['Pearly Tan / Thinaah Muralitharan|MAS','Jia Yifan / Zhang Shuxian|CHN'],'xd':['Guo Xinwa / Chen Fanghui|CHN','Tang Chun Man / Tse Ying Suet|HKG']}
 for code,names in bronze.items():
  row=next(x for x in data['badminton']['records'] if x['weight']==code and x['meet']=='2026-All England Open')
  people=[]
  for raw in names:
   x=p(raw,url)
   if ' / ' in x['fullName']:x['name']=' / '.join(n if x['country'] in ['CHN','TPE','HKG'] else n.split()[-1] for n in x['fullName'].split(' / '))
   people.append(x)
  row['medals']['bronze']=people
 path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 print('Imported 72 wrestling medals and 8 badminton semifinalists')
if __name__=='__main__':update()
