# LA28 골프·근대5종 통합 업로드 파일

## 업로드
1. ZIP을 풉니다.
2. 이 폴더 자체가 아니라 **안의 HTML 7개와 css 폴더**를 GitHub Pages 저장소 최상위에 올립니다.
3. 같은 이름의 HTML·CSS는 이 통합본으로 교체합니다. 다른 종목 파일과 기존 목차는 그대로 둡니다.
4. `https://koreaolympics.github.io/olmodernpentathlon.html` 또는 `https://koreaolympics.github.io/olgolf.html`로 접속합니다.

골프 묶음을 이미 올렸다면 이번 통합본을 마지막으로 올리세요. 골프 6개 페이지는 기존 제작본의 내용을 가져오고 공통 내비게이션·위키 CSS 연결을 맞췄습니다. 이전 묶음의 HTML을 나중에 다시 덮어쓰면 공통 내비게이션 변경이 되돌아갑니다.

## 업로드할 파일
- olmodernpentathlon.html — 근대5종 전체 안내, 남녀 예선·랭킹·한국 전망
- olgolf.html — 골프 전체 안내
- olgolf-men.html / olgolf-women.html / olgolf-mixed.html
- olgolf-ogr.html / olgolf-omtr.html
- css/olympic-wiki.css — **공통 위키 스타일**, 기본 골프 CSS를 불러옵니다.
- css/olympic-golf.css — 기존 골프 묶음의 기본 스타일, 반드시 함께 올립니다.
- css/olympic-pentathlon.css — 근대5종 표·모바일 보정

설치·빌드·JavaScript가 필요 없습니다. 모든 내용, 접기/펼치기, 목차·주석 이동은 HTML/CSS만으로 작동합니다. 같은 URL에서 화면 너비에 맞춰 바뀝니다.

## 링크 범위
7개 문서와 CSS, 문서 내 주석은 상대경로입니다. 로컬에서도 같은 폴더에 두면 연결됩니다. 별도의 프로젝트 하위 경로에 올려도 이 문서 간 링크는 유지됩니다.

기존 전체 종목 목차(index1.html)와 농구(olbasketball.html)는 이 묶음에 포함하지 않았습니다. 원래 사이트의 공개 URL로 연결하므로 인터넷 연결이 필요하며, 해당 페이지를 복제하거나 덮어쓰지 않습니다. 공식 규정·랭킹 출처도 외부 링크입니다.

## 디자인·내용
기존 사이트의 흰 배경, 파란 링크, 얇은 테두리, 문서형 제목·목차와 오른쪽 정보상자를 유지했습니다. 근대5종의 불필요한 요약 카드는 제거했습니다. 남녀는 제목과 얇은 색상선으로 구분합니다. 모바일에서 5열 쿼터표는 종목별 4열 표로 전환하며, 나머지 표는 2~4열입니다.

UIPM Olympic Games 페이지가 연결하는 2026.05.12 영문 규정과 2026.10.01 확인한 공개 시니어 세계랭킹을 사용했습니다. 미정 날짜를 확정하지 않았으며, 현재 세계랭킹과 LA28 올림픽 랭킹을 구분했습니다. 한국 전망은 예선 전 평가입니다.

## 안내·검증 자료 (업로드 선택)
- PENTATHLON-SOURCES.md — 근대5종 근거와 해석상 주의점
- GOLF-SOURCES.md — 앞서 제작한 골프 문서의 근거
- ranking-snapshot.json — 확인일의 주요 한국 선수 수치
- LINK-VALIDATION.json — 파일·앵커·공통 내비게이션 검사
- browser-validation.json — 실제 브라우저 반응형 및 동작 검사

이 패키지는 업로드할 파일입니다. 공개 GitHub Pages 사이트에 직접 게시한 상태는 아닙니다.
