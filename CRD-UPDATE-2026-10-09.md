# CRD 진단 개선 및 AI 인계 기록

- 작업일: 2026-10-09 (Asia/Seoul)
- 대상: `D:\LLM_Repositories\koreaolympics.github.io`
- 요청 근거: 사용자가 지정한 `CRD-diagnosis.txt`의 개선 항목. 첨부 문서에 포함된 도구 지시는 작업 범위 자료로 취급했으며 별도 게시·메시지·배포 권한으로 해석하지 않았다.
- 저장소의 기존 수정 사항 없음 확인 후 작업. 커밋·push·배포는 수행하지 않았다.

## 적용 내용

1. **홈페이지**: 쿼터 단위를 `장`에서 `명`으로 변경. 동적 종목별 카운터에도 반영. `index.html`, `index1.html`, `oldindex.html`은 바이트 단위 동일.
2. **라크로스**: 종목 소개와 필드/식스 비교, 한국 남녀 현황을 상단에 추가. 기존 예선 흐름을 대륙 16팀 → 세계선수권 직행 4팀/최종 예선 6팀 → 최종 우승 1팀의 3단계 구조와 표로 교체. 개최국 1팀을 별도로 설명. 남녀 상세 문서도 동기화. 팬암·아프리카 개최지 및 일정 보완.
3. **유도**: 14체급을 행, 직행/개최국/대륙/혼성 초청/보편성을 열로 한 구조표. 체급별 배정과 공용 풀을 구분하고 238+14+104+6+10=372명을 표시. 14개 체급 페이지에 공식 IJF 데이터로 NOC당 1명 상위 17명을 제공.
4. **역도**: 최상단에 12체급 × OQR8/대륙1/개최국 또는 보편성1 구조표. `olweightlifting-world-athletes.html`과 추가 탐색 링크 생성. 제공된 남녀 선수 분석 전문 보존, 검증 상태와 비교 한계를 표시.
5. **스케이트보딩**: 두 페이지 상단에 개최국 미사용 자리 재배정 시 **랭킹20+대륙1+보편성1=22명**을 설명. 기본 배정 20명 내부의 대륙 보장과 구분. 기존 WSR 자료로 종목별 추가 후보 표시. 이벤트 기록 페이지, 데이터, 필터, 갱신/검증 도구 추가.

## 공식 확인으로 보정한 내용

- 역도는 진단서의 '14체급' 대신 **남녀 각 6, 합계 12체급**이다. [IWF 최신 공지](https://iwf.sport/2026/10/07/updated-la28-olympic-qualification-system-published/), [AWF 예선 안내](https://awf.sport/official-qualification-system-announced-for-la28-olympic-weightlifting/).
- 라크로스 아프리카 일정은 진단서의 12.1~4 대신 **12.3~5**, 요하네스버그. 유럽 살루 11.2~18. [공식 일정](https://worldlacrosse.sport/sanctioned-event-calendar/).
- 팬암은 오샤와 9.29~10.4, 성별 5팀 진출. [World Lacrosse](https://worldlacrosse.sport/2026-pan-american-sixes-lacrosse-championships/).
- 한국 남자부는 공식 연결 Pointbench 대진의 7위 결정전, 여자부는 준결승 진출 확인. **남자 세계선수권 진출 탈락 / 여자 4위 이내 확보**. 여자 최종 순위는 대회 종료 후 확인. [남자 공식 결과](https://worldlacrosse.sport/apslc26-men/), [여자 공식 결과](https://worldlacrosse.sport/apslc26-women/). 조회 경로: `https://stats.pointbench.com/ap/apslcm/2026/?embed=main&fmt=compact`, 여자 `apslcw`.
- 유도 대륙 배정은 남녀 모두 아프리카12/유럽13/아시아12/오세아니아4/아메리카11=52명. IJF 공식 문서의 2026.05.12판 확인. [IJF 문서 목록](https://www.ijf.org/ijf/documents/1?sort=a-).
- Asunción 파크는 진단서의 10.8~11 대신 공식 중계의 **10.6~11**을 기록. [World Skate TV](https://worldskate.tv/world-skate-games/wsg-2026/).
- 로마 스트리트는 행사 6.14~21, 공식 결승 결과표상 경기 6.16~21. 남녀 결승 각 8명의 순위·경기 점수 확인. WSR 반영은 미확정. [World Skate 공식 대회 안내](https://www.worldskate.org/news/3901-all-you-need-to-know-about-wst-world-cup-rome-2026.html).

## 유도 갱신 운영

```shell
python tools/update_ijf_rankings.py
```

- Python 3.11+ 표준 라이브러리만 사용. IJF 공식 프런트엔드가 호출하는 `https://www.ijf.org/internal_api/wrl_olympic` / `wrl`을 사용. 체급 1~14, `limit=100`, **page=0부터** 페이지 순회.
- 올림픽 전용 데이터가 비어 있으면 세계랭킹을 참고 자료로 사용하고 화면·JSON에 `world-reference`를 명시한다. 이번 수집은 14체급 모두 세계랭킹이며 공식 버전은 JSON의 `worldRankingVersion` 참조. **올림픽 확정 선발 명단이 아니다.**
- 취소선 선수 제외, 순위순 정렬, NOC별 첫 선수 선택, 각 17명 검증. NOC 선택·국적/참가 자격·동점 규정은 최종 선발 시 추가 확인.
- 14체급 모두 정상 수집해야 새 파일을 원자적으로 저장. 오류 발생 시 기존 파일 보존. API 구조 변경 시 실패 처리하며 데이터를 임의 생성하지 않는다.
- 현재 자료: `data/ijf-ranking.json`. 순위/점수 변경 이력: `data/ijf-history/`.
- `.github/workflows/ijf-ranking-update.yml`: 매일 UTC22:15, **한국시간 다음날 07:15**, 수동 실행 지원. 저장소에 push된 뒤 GitHub Actions가 활성화되어야 실행된다. 현재는 로컬 파일 추가와 실제 수집 검증까지만 완료했다.

## WSR 이벤트 기록 운영

- 데이터: `data/skateboard-events.json`, 표시: `olskateboard-events.html`, JS: `js/skateboard-events.js`.
- 이벤트별 ID/공식 명칭/기관/종목/성별/장소/기간/상태/결과/WSR 변동/LA28 인정 근거/출처/확인일/갱신일/변경 이력 저장.
- 상태: `scheduled`, `in_progress`, `awaiting_results`, `results_confirmed`, `wsr_confirmed`. 종료일 경과만으로 결과 확정을 자동 추정하지 않는다.
- 현재 4기록: Asunción 파크 남녀(진행 중), 로마 스트리트 남녀(결과 확정). **로마 남녀 결승 각 8명만 수록**했으며 `results_scope=finalists`로 범위를 명시. 공식 대회 안내에서 LA28 예선임을 확인하여 인정 여부 true와 출처 입력. 검증된 WSR 포인트·변동은 확보하지 못해 null/빈 배열로 두었다.
- `results` 행: `athlete_id`, `position`, `name`, `noc`, `event_score`(경기 점수), `wsr_points`(미확인 null).
- `wsr_changes` 행: 같은 `athlete_id`, `previous_rank`, `current_rank`, `delta`(이전-현재), `previous_source_url`, `current_source_url`, `checked_at`.
- 대회 결과 확인 → `results_confirmed` 및 공식 결과 URL/행 입력 → 공식 WSR 이전/현재 원문 대조 → `wsr_confirmed`와 연결된 변동 입력.
- LA28 포인트 인정 true에는 기간 내 개최뿐 아니라 공식 지정/규정 근거인 `eligibility_source_url`과 설명을 입력해야 한다.

```shell
python tools/manage_skateboard_events.py
python tools/manage_skateboard_events.py --update work/event-revision.json
```

`--update` 파일은 위 스키마의 **이벤트 1개 전체 객체**. 기존 이벤트 수정 시 ID를 유지. 이전 레코드를 history에 보존하고 검증 후 원자적으로 저장한다. 중복 ID, 역전된 날짜, 누락 출처, 조기 결과 확정, 잘못된 순위 변동을 거부한다. 공식 첨부가 다른 도메인에서 제공된다면 공식 페이지와의 연결을 검증한 후 허용 도메인 로직을 보완할 것.

공식 로마 결과: [결승 결과 기사](https://www.skateboarding.worldskate.org/news/1851-wst-world-cup-rome-street-2026-final-results.html), 기사에 연결된 남녀 결과표를 직접 확인. 강준이 4위(167.70), 신지율 6위(126.89). 포인트와 경기 점수를 혼동하지 말 것.

## 검증 결과

- IJF 실제 네트워크 수집: 14체급 × 17명 = 238명, 체급별 NOC 중복 없음.
- JSON 스키마와 4개 이벤트 정상 검증. 잘못된 날짜/출처/결과 확정/중복 이벤트 입력 거부 확인.
- 변경 페이지 로컬 링크 및 중복 ID 검사 통과. Python 구문, 신규 JS 구문 검사 통과.
- Chromium에서 8개 대표 페이지 × PC1280px/모바일390px, 16개 화면 확인. JavaScript 오류 없음, 문서 가로 넘침 없음. 유도 17명 렌더링 및 파크 필터 2개 기록 확인. 로컬 파일 응답을 Playwright route로 제공하여 검사했으며 실서비스 배포 검사는 수행하지 않았다.
- 세 index 파일 바이트 동일 검증. Git whitespace 검사 통과.

## 인계 시 주의할 사항

- 선수 분석은 **사용자 제공 원문**이다. 기록 전체와 세계기록 표시는 공식 결과로 독립 검증하지 않았다. 페이지에서 이를 명시했다. 미나시얀 447/457kg을 460kg대로 묶는 원문의 수치 불일치도 안내했다. 이 분석을 OQR 확정 기록으로 옮기지 말 것.
- IWF는 10.7 최신 예선 문서 공지를 게시했다. 이번 체급 구조는 확인했지만 기존 예선 페이지의 모든 5.12판 조항을 최신 문서로 재감사하는 작업은 포함하지 않았다.
- 스케이트보딩 후보는 기존 2026.10.01 WSR 자료를 단순 적용한 시나리오이며 LA28 인정 기간 점수로 재구성한 확정 명단이 아니다.
- 기존 `tools/skbpages.py`, `tools/weightpages.py`, `tools/weightrules.py` 등의 전체 페이지 재생성은 이번 HTML 변경을 덮어쓸 수 있다. 실행 전에 이번 섹션을 생성기에 이식하거나 변경 diff를 보존해야 한다. 신규 IJF/이벤트 갱신 도구는 HTML을 재생성하지 않는다.
- 자동 갱신 활성화를 위해서는 사용자의 기존 배포 절차에 따라 변경 파일과 workflow를 저장소에 push해야 한다.

## 변경 파일

- `.github/workflows/ijf-ranking-update.yml`
- `data/ijf-history/2026-10-09T08-20-36.json`
- `data/ijf-ranking.json`
- `data/skateboard-events.json`
- `index.html`
- `index1.html`
- `js/ijf-ranking.js`
- `js/skateboard-events.js`
- `oldindex.html`
- `oljudo-ev-m100.html`
- `oljudo-ev-m60.html`
- `oljudo-ev-m66.html`
- `oljudo-ev-m73.html`
- `oljudo-ev-m81.html`
- `oljudo-ev-m90.html`
- `oljudo-ev-mo100.html`
- `oljudo-ev-w48.html`
- `oljudo-ev-w52.html`
- `oljudo-ev-w57.html`
- `oljudo-ev-w63.html`
- `oljudo-ev-w70.html`
- `oljudo-ev-w78.html`
- `oljudo-ev-wo78.html`
- `oljudo.html`
- `ollacrosse-men.html`
- `ollacrosse-women.html`
- `ollacrosse.html`
- `olskateboard-events.html`
- `olskateboard-sim.html`
- `olskateboard.html`
- `olweightlifting-world-athletes.html`
- `olweightlifting.html`
- `tools/__pycache__/manage_skateboard_events.cpython-312.pyc`
- `tools/manage_skateboard_events.py`
- `tools/update_ijf_rankings.py`
