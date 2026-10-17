# tools

모든 명령은 사이트 루트에서 실행한다. 원칙은 `PRINCIPLES.md`.

| 경로 | 용도 |
|---|---|
| `olympic.py` | 새 구조 관리 툴: `build` · `check` · `todo` |
| `update/` | 실시간 자료 갱신기. `data/*.json`만 쓴다. 갱신 후 `python tools/olympic.py build` |
| `legacy/` | 구 구조 생성기·테스트·조사 자료. 실행하지 않는다 (종목 문서를 덮어쓸 수 있음) |

## update/

| 파일 | 출력 | 실행 |
|---|---|---|
| `update_ijf_rankings.py` | `data/ijf-ranking.json`, `data/ijf-history/` | 워크플로 `ijf-ranking-update.yml` (매일) |
| `update_fie_rankings.py` | `data/fie-team-ranking.json`, `data/fie-team-history/` | 워크플로 `fie-ranking-update.yml` (6시간마다) |
| `update-swimming-records.py` | `data/swimming-records.json` | `python tools/update/update-swimming-records.py` |
| `update-swimming-benchmarks.py` | `data/swimming-benchmarks.json` | `python tools/update/update-swimming-benchmarks.py` |
| `update-racket-rankings.cjs` | `data/badminton-rankings.json`, `data/tabletennis-rankings.json` | `npm install playwright` 후 `node tools/update/update-racket-rankings.cjs` |
