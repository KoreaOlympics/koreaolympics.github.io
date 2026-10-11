# 배드민턴·탁구 랭킹 갱신

배드민턴은 사용자가 지정한 Flashscore의 BWF 단식·복식 5종목 랭킹을 읽습니다. 탁구는 WTT의 공개 API에서 같은 5종목을 읽습니다. 각 종목에서 1~20위 연속 순위, 선수 이름, 국적, 점수, 발표일을 검증한 후 종목 전체 파일을 원자적으로 교체합니다. 실패한 종목은 기존 파일을 유지합니다. 배드민턴은 최초 100위 내 한국 선수 중 20위 밖의 선수도 별도 참고 항목으로 저장합니다.

```sh
npm install --no-save playwright
npx playwright install chromium
node scripts/update-racket-rankings.cjs
```

Windows에 Edge가 설치되어 있으면 `--edge`, 한 종목만 갱신하려면 `--sport badminton` 또는 `--sport tabletennis`를 사용합니다.

`olbadminton-ranking.html`과 `oltabletennis-ranking.html`은 초기 자료를 HTML에 내장하여 로컬 파일에서도 보입니다. 웹에 게시하면 페이지를 열 때 최신 JSON을 읽고, ‘갱신 자료 불러오기’로 `data/*-rankings.json`을 다시 읽습니다. 이 버튼은 외부 사이트를 직접 스크래핑하지 않습니다. 상위 20위 표에는 순위·성·NOC만 표시합니다.

`.github/workflows/racket-rankings.yml`은 수요일 한국시간 07:35에 갱신하고 기존 사이트 전체를 GitHub Pages에 배포하도록 준비한 파일입니다. 저장소에 올리기 전에는 자동화가 실행되지 않습니다. GitHub Pages 소스를 Actions로 설정하고 다른 Pages 워크플로와 함께 같은 `pages` 동시 실행 그룹을 사용합니다. 한 종목 갱신이 실패하면 그 종목의 기존 자료를 보존하고 성공한 종목만 갱신합니다. 이후 워크플로 실패 상태로 해당 문제를 알립니다.
