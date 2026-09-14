"""English -> Korean for event/phase/unit names. Proper nouns (game titles, venues, countries) are left as-is."""
import re

N = r"(\d+)"

NOC_KO = {
    "AFG": "아프가니스탄", "BRN": "바레인", "BAN": "방글라데시", "BHU": "부탄", "BRU": "브루나이", "CAM": "캄보디아",
    "CHN": "중국", "PRK": "북한", "HKG": "홍콩", "IND": "인도", "INA": "인도네시아", "IRI": "이란", "IRQ": "이라크",
    "JPN": "일본", "JOR": "요르단", "KAZ": "카자흐스탄", "KOR": "대한민국", "KUW": "쿠웨이트", "KGZ": "키르기스스탄",
    "LAO": "라오스", "LBN": "레바논", "MAC": "마카오", "MAS": "말레이시아", "MDV": "몰디브", "MGL": "몽골",
    "MYA": "미얀마", "NEP": "네팔", "OMA": "오만", "PAK": "파키스탄", "PLE": "팔레스타인", "PHI": "필리핀",
    "QAT": "카타르", "KSA": "사우디아라비아", "SGP": "싱가포르", "SRI": "스리랑카", "SYR": "시리아", "TPE": "대만",
    "TJK": "타지키스탄", "THA": "태국", "TLS": "동티모르", "TKM": "투르크메니스탄", "UAE": "아랍에미리트",
    "UZB": "우즈베키스탄", "VIE": "베트남", "YEM": "예멘", "ART": "아시아 난민팀",
}

# Sport-specific terms: applied only to that discipline, before the generic rules.
SPORT = {
    "ARC": [(r"Qualification Round", "랭킹라운드"), (r"Compound", "컴파운드"), (r"Recurve", "리커브")],
    "ATH": [
        (r"Half Marathon Race Walk", "하프마라톤 경보"), (r"Marathon Race Walk", "마라톤 경보"), (r"Marathon", "마라톤"),
        (r"Hurdles", "허들"), (r"Steeplechase", "장애물"), (r"Decathlon", "10종경기"), (r"Heptathlon", "7종경기"),
        (r"High Jump", "높이뛰기"), (r"Long Jump", "멀리뛰기"), (r"Triple Jump", "세단뛰기"), (r"Pole Vault", "장대높이뛰기"),
        (r"Shot Put", "포환던지기"), (r"Discus Throw", "원반던지기"), (r"Hammer Throw", "해머던지기"),
        (r"Javelin Throw", "창던지기"), (r"Relay", "계주"),
    ],
    "BBL": [(r"Baseball", "야구")],
    "SBL": [(r"Softball", "소프트볼")],
    "BKG": [(r"B-Boys", "비보이"), (r"B-Girls", "비걸"), (r"Pre-Selection", "사전 선발전")],
    "BMF": [(r"Park", "파크"), (r"Seeding", "시딩")],
    "BMX": [(r"Motos Run " + N, r"모토 \1차"), (r"Motos", "모토")],
    "SKB": [(r"Park", "파크"), (r"Street", "스트리트")],
    "CLB": [(r"Boulder", "볼더"), (r"Lead", "리드"), (r"Speed", "스피드"), (r"Final Round", "결승")],
    "CRD": [(r"Ind\. Time Trial", "개인 독주"), (r"Individual Time Trial", "개인 독주"), (r"Road Race", "도로경기")],
    "MTB": [(r"Cross-country", "크로스컨트리")],
    "CTR": [
        (r"Keirin", "경륜"), (r"Madison", "매디슨"), (r"Omnium", "옴니엄"), (r"Team Pursuit", "단체추발"),
        (r"Team Sprint", "단체스프린트"), (r"Sprint", "스프린트"),
        (r"Elimination Race", "제외경기"), (r"Points Race", "포인트레이스"), (r"Scratch Race", "스크래치"), (r"Tempo Race", "템포레이스"),
        (r"Final for Gold", "금메달 결정전"), (r"Final for " + N + r"th-" + N + r"th Places", r"\1–\2위 결정전"),
        (r"Final for places " + N + "-" + N, r"\1–\2위 결정전"),
    ],
    "TRI": [(r"Relay", "계주")],
    "CSL": [(r"Kayak Cross", "카약 크로스"), (r"Kayak Single", "카약 1인승"), (r"Canoe Single", "카누 1인승")],
    "CSP": [
        (r"Kayak Single", "카약 1인승"), (r"Kayak Double", "카약 2인승"), (r"Kayak Four", "카약 4인승"),
        (r"Canoe Single", "카누 1인승"), (r"Canoe Double", "카누 2인승"),
    ],
    "ROW": [
        (r"(?:Sculls)+", "스컬"), (r"Single 스컬", "싱글스컬"), (r"Double 스컬", "더블스컬"), (r"Quadruple 스컬", "쿼드러플스컬"),
        (r"Lightweight", "경량급"), (r"\bFour\b", "무타포어"), (r"\bPair\b", "무타페어"),
    ],
    "SPK": [(r"Regu", "레구"), (r"Quadrant", "쿼드런트"), (r"\bDouble\b", "더블")],
    "PDL": [(r"Pairs", "복식")],
    "DIV": [(r"Synchronised", "싱크로"), (r"Platform", "플랫폼"), (r"Springboard", "스프링보드")],
    "GAR": [
        (r"All-Around", "개인종합"), (r"Floor Exercise", "마루운동"), (r"Horizontal Bar", "철봉"), (r"Parallel Bars", "평행봉"),
        (r"Pommel Horse", "안마"), (r"Rings", "링"), (r"Vault", "도마"), (r"Balance Beam", "평균대"), (r"Uneven Bars", "이단평행봉"),
    ],
    "GRY": [(r"Group All-Around", "단체전"), (r"Individual All-Around", "개인종합")],
    "GLF": [(r"Stroke Play", "스트로크플레이")],
    "SHO": [
        (r"Air Pistol", "공기권총"), (r"Air Rifle", "공기소총"), (r"Rapid Fire Pistol", "속사권총"),
        (r"Rifle " + N + r" Positions", r"소총 \1자세"), (r"Pistol", "권총"), (r"Precision", "정밀"), (r"Rapid", "속사"),
        (r"Skeet", "스키트"), (r"Trap", "트랩"),
    ],
    "FEN": [(r"Foil", "플뢰레"), (r"Épée", "에페"), (r"Sabre", "사브르"), (r"Pools", "조별리그")],
    "KTE": [(r"Kata", "가타"), (r"Kumite", "구미테")],
    "MMA": [(r"Modern", "모던"), (r"Traditional", "전통")],
    "TKW": [(r"Poomsae", "품새"), (r"Virtual Taekwondo", "버추얼 태권도")],
    "WRE": [(r"Greco-Roman", "그레코로만형"), (r"Freestyle", "자유형"), (r"Wrestling", "레슬링")],
    "WSU": [
        (r"Changquan", "장권"), (r"Nanquan", "남권"), (r"Nangun", "남곤"), (r"Nandao", "남도"), (r"Taijiquan", "태극권"),
        (r"Taijijian", "태극검"), (r"Daoshu", "도술"), (r"Gunshu", "곤술"), (r"Jianshu", "검술"), (r"Qiangshu", "창술"),
    ],
    "WLF": [(r"All Groups", "전체 조")],
    "SWM": [
        (r"Freestyle-Timed Final\s*" + N, r"자유형 타임결승 \1"), (r"Individual Medley", "개인혼영"), (r"Medley Relay", "혼계영"),
        (r"Freestyle Relay", "계영"), (r"Freestyle", "자유형"), (r"Backstroke", "배영"), (r"Breaststroke", "평영"), (r"Butterfly", "접영"),
    ],
    "MPN": [
        (r"Fencing Seeding Round", "펜싱 랭킹라운드"), (r"Fencing Direct Elimination", "펜싱 토너먼트"), (r"Laser Run", "레이저런"),
        (r"Obstacle", "장애물"), (r"Swimming", "수영"), (r"Freestyle", "자유형"),
    ],
    "SWA": [
        (r"Duet", "듀엣"), (r"Technical Routine", "테크니컬 루틴"), (r"Free Routine", "프리 루틴"), (r"Acrobatic Routine", "아크로바틱 루틴"),
    ],
    "SAL": [
        (r"Boys'", "남자 청소년"), (r"Girls'", "여자 청소년"), (r"Youth", "청소년"), (r"Dinghy", "딩기"), (r"Skiff", "스키프"),
        (r"Windsurfing", "윈드서핑"), (r"Opening Series", "예선 시리즈"),
    ],
    "SRF": [(r"Shortboard", "숏보드")],
    "EQU": [
        (r"Dressage", "마장마술"), (r"Eventing", "종합마술"), (r"Cross Country", "크로스컨트리"), (r"Grand Prix", "그랑프리"),
        (r"Team and Individual", "단체·개인"),
    ],
    "ELS": [
        (r"League of Legends", "리그 오브 레전드"), (r"Honor of Kings", "아너 오브 킹즈"),
        (r"Mobile Legends: Bang Bang", "모바일 레전드: 뱅뱅"), (r"Pokémon UNITE", "포켓몬 유나이트"),
        (r"PUBG MOBILE", "배틀그라운드 모바일"), (r"NARAKA\s*:\s*BLADEPOINT", "나라카: 블레이드포인트"),
        (r"Identity V", "제5인격"), (r"Asian Games Version", "아시안게임 버전"), (r"Gran Turismo", "그란 투리스모"),
        (r"eFootball™?", "e풋볼"), (r"Puyo Puyo Champions", "뿌요뿌요 챔피언스"), (r"Street Fighter", "스트리트 파이터"),
        (r"TEKKEN™?", "철권"), (r"THE KING OF FIGHTERS", "더 킹 오브 파이터즈"),
        (r"(\d+)v(\d+) asymmetrical survival game", r"\1v\2 비대칭 생존 게임"), (r"Action-adventure", "액션 어드벤처"),
        (r"Battle Royale", "배틀로얄"), (r"Auto Racing", "레이싱"), (r"Fighting Games", "격투 게임"),
        (r"^Football \[", "축구 ["), (r"^Puzzle \[", "퍼즐 ["), (r"Time Attack", "타임어택"),
    ],
    "SQU": [(r"(\d+)/(\d+) play off", r"\1/\2위 결정전")],
}

# Generic tournament vocabulary, in order (longer phrases first).
GENERIC = [
    (r"\b(Men|Women)(?:['’�]+s)?(?=\W|$)", lambda m: "남자" if m.group(1) == "Men" else "여자"),
    (r"\bMixed\b|\bMix\b", "혼성"),
    (r"Victory Cer(?:emony|\.)|\bCeremony\b", "시상식"),
    # medal contests
    (r"(?:Contests?|Matches) for Bronze Medals?", "동메달 결정전"),
    (r"Final - Gold Medal(?: Contest)*", "금메달 결정전"),
    (r"Gold Medal (?:Team )?(?:Match|Game|Bout|Battle|Contest)(?: Contest)*", "금메달 결정전"),
    (r"Bronze Medal (?:Match(?:es)?|Game|Bout|Battle|Contest)", "동메달 결정전"),
    (r"Finals - For Gold", "결승 - 금메달 결정전"), (r"Finals - For Bronze", "결승 - 동메달 결정전"),
    (r"\bGold Medal\b", "금메달 결정전"), (r"\bBronze Medal\b", "동메달 결정전"),
    (r"\bGold\b", "금메달"), (r"\bBronze\b", "동메달"),
    # placings
    (r"\b" + N + r"(?:st|nd|rd|th) Place Match", r"\1위 결정전"),
    (r"Placing " + N + r"th-" + N + r"th", r"\1–\2위 결정전"),
    (r"\b" + N + r"th-" + N + r"th\b", r"\1–\2위"),
    (r"Placing " + N + "-" + N + r"\b", r"\1–\2위 결정전"), (r"Classification Match", "순위결정전"), (r"Classification", "순위결정전"), (r"Placement Round", "순위결정전"), (r"Playoff", "플레이오프"),
    # rounds
    (r"\b1/" + N + r" (?:Finals?|Eliminations?)", lambda m: f"{2 * int(m.group(1))}강"),
    (r"(?:Elimination )?Round of " + N, r"\1강"), (r"Table of " + N, r"\1강"),
    (r"Semi-?final of Table ([A-Z])", r"준결승 \1"),
    (r"Round Robin", "예선"), (r"Group Phase", "예선"), (r"Preliminary Round", "예선"), (r"First Stage", "1단계"),
    (r"Preliminar(?:y|ies)", "예선"), (r"Prelims", "예선"), (r"Qualifications?", "예선"), (r"Qualifying", "예선"),
    (r"\bHeats?\b(?! \d)", "예선"),
    (r"Opening Round", "오프닝라운드"), (r"Super Round", "슈퍼라운드"), (r"Play-in", "플레이인"),
    (r"\bFirst Round\b", "1라운드"), (r"\bSecond Round\b", "2라운드"), (r"\bThird Round\b", "3라운드"),
    (r"\b" + N + r"(?:st|nd|rd|th) Round\b", r"\1라운드"),
    (r"Repechages?(?: contest| Bout)?", "패자부활전"), (r"\bDecider\b", "결정전"),
    (r"Quarter[- ]?[Ff]inals?|Quaterfinal", "8강"),
    (r"Semi-?[Ff]inals?", "준결승"),
    (r"Super Final", "슈퍼결승"), (r"Small Final", "순위결정전"), (r"Timed Final", "타임결승"),
    (r"\bFinals?\b", "결승"),
    # numbered units
    (r"\s-Group ([A-Z])\b", r" - \1조"), (r"\bGroup ([A-Z])\b", r"\1조"),
    (r"\bPool ([A-Z])\b", r"\1조"), (r"\bPool " + N, r"\1조"), (r"\bHeat " + N, r"\1조"), (r"\bSubdivision " + N, r"\1조"),
    (r"\b(?:Match|Game|Bout) " + N, r"\1경기"), (r"\bRace " + N, r"\1레이스"), (r"\bRun " + N, r"\1차"),
    (r"\bRound " + N, r"\1라운드"), (r"\bDay " + N, r"\1일차"), (r"\bStage " + N, r"\1스테이지"),
    (r"\bRound\b", "라운드"), (r"\bMatch\b", "경기"), (r"\bContest\b", "경기"),
    # events
    (r"\bIndividual\b|\bInd\.", "개인"), (r"\bTeam\b", "단체"), (r"\bSingles\b", "단식"), (r"\bDoubles\b", "복식"),
    (r"\bAll-Around\b", "개인종합"), (r"\bElimination\b", "토너먼트"), (r"\b[Rr]ace\b", "레이스"), (r"\bSeries\b", "시리즈"),
    (r"\bPools\b", "조별리그"), (r"\bGroups\b", "조"),
]

_sport = {d: [(re.compile(p), r) for p, r in rules] for d, rules in SPORT.items()}
_generic = [(re.compile(p), r) for p, r in GENERIC]


def ko(text, disc):
    if not text:
        return text
    s = text
    for rx, rep in _sport.get(disc, []) + _generic:
        s = rx.sub(rep, s)
    s = re.sub(r"(?<=[가-힣])\s*,+\s*", " ", s)  # "경륜, 결승" -> "경륜 결승"; keeps "스트리트 파이터 6, 철권 8"
    s = re.sub(r"\s{2,}", " ", s).strip()
    s = re.sub(r"([가-힣]+)(?: \1(?![가-힣]))+", r"\1", s)  # "결승 결승" -> "결승"; Korean only so "Bang Bang" survives
    return s
