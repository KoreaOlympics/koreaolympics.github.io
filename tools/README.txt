실행 순서 (사이트 루트에서):
  python3 tools/athletes.py     # 선수·세부종목·체급 문서 재생성 + 공통 CSS + index 한국 선수 탭
  python3 tools/weightpages.py  # 유도·태권도·역도·레슬링·복싱 규정 문서에 체급별 블록 삽입
  python3 tools/gympages.py     # 기계체조 세부 문서 15개 + 체조 문서 2행 탭
  python3 tools/archery_live.py # 양궁 라이브 현황 (필요 시)
선수 정보 수정: tools/research/*.json 편집 후 위 순서로 재실행.
스크립트 안의 경로(/root/site/, scratchpad)는 작업 환경 기준이므로 로컬에서 쓰려면 SITE·RS 값을 바꾸세요.
