# PDP 추출 작업 보고서

## 필요한 추출 작업

### 방법 1: Claude Code로 자동 추출 (권장)
각 제품별로:
1. WebFetch 또는 Chrome Extension으로 PDP 콘텐츠 읽기
2. geo_markdown_guide.md에 맞춰 마크다운 작성
3. 분석 문서 업데이트

### 방법 2: 수동 PDP 방문
각 제품 URL을 직접 방문하여:
- 제품 설명 복사
- 스펙 정보 수집
- 주요 기능 확인

## 우선순위 제품 목록

### Phase 1: OLED C5 시리즈 (4개)
필수 정보:
- 화면 크기 (인치)
- 패널 기술 (OLED, evo, 등)
- 프로세서 (Alpha 9 AI Processor Gen8)
- 주사율 (120Hz native, VRR up to 144Hz)
- 스피커 (40W, 2.2ch, Dolby Atmos)
- 가격 (CAD)

URL 예: https://www.lg.com/ca_en/tv-soundbars/oled-evo/oled55c5pua/

### Phase 2: 프리미엄 냉장고 (5개)
필수 정보:
- 크기 (mm)
- 용량 (L)
- 기술 (InstaView, Craft Ice, 등)
- 냉동실 위치
- 에너지 등급
- 가격 (CAD)

### Phase 3: 인기 세탁기 (3개)
필수 정보:
- 타입 (Front-load/Top-load)
- 용량 (cu.ft)
- AI DD 기술 여부
- 사이클 개수
- 에너지 등급
- 가격 (CAD)

## 다음 단계
1. 각 PDP에서 위 정보 수집
2. geo_markdown_guide.md 섹션에 맞춰 작성
3. 수량화된 수치 포함 (%, dB, W, 등)
4. LLM 인용 최적화 (간단하고 명확한 문장)

## 자동화 진행 상황
- ✅ 템플릿 생성: 12개
- ✅ 분석 파일 생성: 12개
- ⏳ PDP 콘텐츠 추출: 준비 중
- ⏳ 마크다운 채우기: 준비 중
