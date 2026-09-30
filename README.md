# LA28 골프 페이지 묶음

1. ZIP을 풉니다.
2. ZIP 안의 HTML 6개와 css 폴더를 기존 GitHub Pages 저장소 루트에 함께 업로드합니다.
3. 기존 olgolf.html을 새 파일로 교체합니다. 다른 종목 파일은 덮어쓰지 않습니다.
4. https://koreaolympics.github.io/olgolf.html 에서 확인합니다.

빌드·설치·서버·JavaScript 없이 작동합니다. 로컬에서는 olgolf.html을 열면 됩니다.
모든 골프 문서와 CSS는 상대경로입니다. 기존 목차(index1.html)와 근대5종은 묶음 밖의 실제 공개 문서이므로 원래 사이트의 절대 URL로 연결했습니다. 두 주소는 HTTP 200 응답을 확인했습니다. 이 방식은 ZIP을 로컬에서 열어도 없는 파일로 이동하지 않으며 기존 문서를 복제하거나 덮어쓰지 않습니다.

## 파일
- olgolf.html: 골프 허브
- olgolf-men.html / olgolf-women.html: 개인전
- olgolf-mixed.html: 혼성 단체전
- olgolf-ogr.html / olgolf-omtr.html: 공식 랭킹 규정 설명
- css/olympic-golf.css: 공통 반응형 스타일
- SOURCES.md: 근거와 확인 한계
- VALIDATION.json: 링크·모바일 검증 결과

## 표시 원칙
데스크톱 쿼터표는 5열, 900px 이하에서는 종목 이름을 표 제목으로 옮겨 4열입니다. 나머지 표는 최대 4열입니다. 동일 HTML 주소에서 전환됩니다. 선발 설명은 각 표 바로 아래 번호 주석으로 연결됩니다.

한국 전망은 2026-09-30을 기준일로 삼습니다. 2026-09-28 공식 IGF 남녀 랭킹 트래커와 여자 WWGR 주간표를 반영했습니다. 2028년 확정 전망으로 제시하지 않습니다.
