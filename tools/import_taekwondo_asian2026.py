import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
PODIUMS={
'Men -54kg':[('ALDAOUD Jafar','JOR'),('VALIZADEH Yasin','IRI'),('YENSEGENOV Yerkebulan','KAZ'),('KHUDAYBERDIEV Jakhongir','UZB')],
'Men -58kg':[('ZANDI Abolfazl','IRI'),('YANG Hui-chan','KOR'),('OTAJONOV Omonjon','UZB'),('KIM Jongmyeong','KOR')],
'Men -63kg':[('HAJIMOUSAEI Mehdi','IRI'),('JANG Jun','KOR'),('NAZAROV Nazarali','UZB'),('ABABAKIROV Samirkhon','KAZ')],
'Men -68kg':[('MUN Jinho','KOR'),('TUKHLIBOEV Diyorbek','UZB'),('CHEN Yufan','CHN'),('KAREEM Zaid','JOR')],
'Men -74kg':[('BAKHTIARI Amir Sina','IRI'),('CAI Zhaoxun','CHN'),('KOSIMKHOJIEV Najmiddin','UZB'),('BIRIMBAY Eldar','KAZ')],
'Men -80kg':[('SEO Geon-woo','KOR'),('JAYSUNOV Jasurbek','UZB'),('SADEGHIAN Amir Reza','IRI'),('ALADARBI Mohammad','JOR')],
'Men -87kg':[('PARK Woo hyeok','KOR'),('ZHURABOEV Yodgorbek','UZB'),('CHEN Liang-hsi','TPE'),('MENG Mingkuan','CHN')],
'Men +87kg':[('SALIMI Arian','IRI'),('MAVLONOV Marat','UZB'),('KANG Sanghyun','KOR'),('TANG Hao','CHN')],
'Women -46kg':[('WANG Chieh-ling','TPE'),('POOLKERD Patcharakan','THA'),('SARZA Clarence','PHI'),('LEE Yumin','KOR')],
'Women -49kg':[('KIM Hyanggi','KOR'),('LIU You-yun','TPE'),('FU Xiaolu','CHN'),('MA Jingyue','CHN')],
'Women -53kg':[('ZUO JU','CHN'),('ABUTALEB Dunya','KSA'),('MALIK Kashish','IND'),('SEO Yeo-won','KOR')],
'Women -57kg':[('KIANI Nahid','IRI'),('MIRABZALOVA Madina','UZB'),('KIM Yujin','KOR'),('LIN Wei-chun','TPE')],
'Women -62kg':[('CHANG Jui-en','TPE'),('LUO Zongshi','CHN'),('VALINEJAD Yalda','IRI'),('LEE Ga-eun','KOR')],
'Women -67kg':[('SOBIRJONOVA Ozoda','UZB'),('KWAK Minju','KOR'),('ALRAWASHDEH Razan','JOR'),('XING Jiani','CHN')],
'Women -73kg':[('XIAO Shunan','CHN'),('SONG Jie','CHN'),('MAKHMUTOVA Nazym','KAZ'),('DAS Etisha','IND')],
'Women +73kg':[('OSIPOVA Svetlana','UZB'),('SONG Dabin','KOR'),('ZHOU Zeqi','CHN'),('XU Lei','CHN')]}
def main():
 p=R/'data/taekwondo-pathways.json';d=json.loads(p.read_text(encoding='utf-8'));e=next(e for e in d['events'] if e['id']=='cu26')
 e.update(title='2026 아시아선수권',start='2026-05-21',end='2026-05-24',status='완료',weightSystem='world',resultUrl='https://en.wikipedia.org/wiki/2026_Asian_Taekwondo_Championships',route='G4 · 세계체급 16개 · 1기 성적, 2기 점수 이월 없음',sources=['asian26','rank'])
 e.pop('dayByWeight',None);e['medals']=[dict(weight=w,medal=medal,name=name,country=noc) for w,people in PODIUMS.items() for medal,(name,noc) in zip(['Gold','Silver','Bronze','Bronze'],people)]
 d['sources']['asian26']=dict(title='Wikipedia · 2026 아시아선수권 · 16체급 입상자',url=e['resultUrl']);d['asOf']='2026-10-13'
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print('Added Asian Championships: 16 weights, 64 medals')
if __name__=='__main__':main()
