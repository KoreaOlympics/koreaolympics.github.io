실행 순서 (사이트 루트에서):
  python3 tools/athletes.py     # 선수·세부종목·체급 문서 재생성 + 공통 CSS + index 한국 선수 탭
  python3 tools/weightpages.py  # 유도·태권도·역도·레슬링·복싱 규정 문서에 체급별 블록 삽입
  python3 tools/gympages.py     # 기계체조 세부 문서 15개 + 체조 문서 2행 탭
  python3 tools/archery_live.py # 양궁 라이브 현황 (필요 시)
  python3 tools/ttpages.py      # 탁구 전체 안내 + 세부종목 6 + 쿼터 트래킹 (tools/tt/live.json)
선수 정보 수정: tools/research/*.json 편집 후 위 순서로 재실행.
경로는 스크립트 위치 기준(tools/의 상위 폴더 = 사이트 루트)으로 자동 계산됩니다.
공통 CSS는 css/olympic-wiki.css 입니다 (사이트 루트의 olympic-wiki.css 는 쓰이지 않음).
