const KO = {
  ARC:"양궁", ATH:"육상", BDM:"배드민턴", BBL:"야구", SBL:"소프트볼", BKB:"농구", BK3:"3x3 농구", BKG:"브레이킹",
  BOX:"복싱", CSL:"카누 슬라럼", CSP:"카누 스프린트", CKT:"크리켓", CRD:"사이클 도로", CTR:"사이클 트랙",
  MTB:"사이클 산악자전거", BMX:"사이클 BMX 레이싱", BMF:"사이클 BMX 프리스타일", DIV:"다이빙", EQU:"승마",
  ELS:"e스포츠", FEN:"펜싱", FBL:"축구", GLF:"골프", GAR:"기계체조", GRY:"리듬체조", GTR:"트램펄린",
  HBL:"핸드볼", HOC:"하키", JJI:"주짓수", JUD:"유도", KAB:"카바디", KTE:"가라테", KUR:"쿠라시",
  MMA:"종합격투기", MPN:"근대5종", PDL:"파델", ROW:"조정", RU7:"7인제 럭비", SAL:"요트", SHO:"사격",
  SKB:"스케이트보드", CLB:"스포츠클라이밍", SQU:"스쿼시", SRF:"서핑", SWM:"경영", SWA:"아티스틱 스위밍",
  SPK:"세팍타크로", TTE:"탁구", TKW:"태권도", TEN:"테니스", TST:"정구", TEQ:"테크볼", TRI:"트라이애슬론",
  VVO:"배구", VBV:"비치발리볼", WPO:"수구", WLF:"역도", WRE:"레슬링", WSU:"우슈"
};
const STATUS_KO = { "Planned":"예정", "Scheduled":"예정", "Start List":"출전명단", "Getting Ready":"준비 중",
  "Running":"진행 중", "Live":"진행 중", "Unofficial":"비공식 결과", "Official":"종료", "Finished":"종료",
  "Postponed":"연기", "Cancelled":"취소", "Delayed":"지연", "Interrupted":"중단", "Rescheduled":"일정 변경" };
const WD = ["일","월","화","수","목","금","토"];

const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;" }[c]));

// Broadcaster badges from kor_manual.json "tv": {"SBS": "19:00", "KBS": "18:35 1TV"}
const tvBadges = tv => tv && Object.keys(tv).length ? `<span class="tv">${Object.entries(tv).map(([ch, t]) =>
  `<span class="tvb tv-${esc(ch)}" title="${esc(ch)} ${esc(t)} 중계">${esc(ch)}</span>`).join("")}</span>` : "";
const tvLine = tv => tv && Object.keys(tv).length ? `<div class="tvline">📺 ${Object.entries(tv).map(([ch, t]) =>
  `<span class="tvb tv-${esc(ch)}">${esc(ch)}</span> ${esc(t)}`).join(" · ")}</div>` : "";
