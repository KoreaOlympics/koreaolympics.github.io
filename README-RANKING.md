# LA28 실제 예선 랭킹 자동 갱신

이 폴더의 내용물을 GitHub Pages 저장소 루트에 합칩니다. `index.html`과 `index1.html`에는 `la28-qualifier-ranking.html` 진입 링크가 이미 포함되어 있습니다.

## 자동 갱신

- `.github/workflows/update-la28-rankings.yml`이 매일 18:20 UTC(한국시간 다음 날 03:20)에 실행됩니다.
- `update_rankings.py`가 Totallympics의 LA28 전체 목록에서 상세 랭킹 URL을 다시 찾습니다.
- 각 상세 페이지에서 순위, 선수·팀, NOC, 점수, 예상 쿼터 상태를 읽습니다.
- 종목명, 국가명과 쿼터 상태를 한국어로 바꾸어 `data/la28-ranking-details.json`을 생성합니다.
- 데이터가 달라졌을 때만 GitHub Actions 봇이 새 JSON을 커밋합니다.
- GitHub 저장소의 **Settings → Actions → General → Workflow permissions**에서 `Read and write permissions`가 허용되어야 자동 커밋됩니다.

수동 갱신은 저장소 루트에서 `python update_rankings.py`를 실행합니다. 외부 Python 패키지는 필요하지 않습니다.

선수 고유명은 오역을 막기 위해 원문의 로마자 표기를 유지합니다. 대한민국 국가대표팀 이름과 국가명, 표 제목 및 쿼터 판정은 한국어로 표시합니다.
