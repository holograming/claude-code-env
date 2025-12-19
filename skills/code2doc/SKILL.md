---
name: code-documentation
description: "코드베이스를 분석하여 기술 문서를 생성하는 스킬. MD/PDF/PPT 출력 형식 선택 가능. 워크플로우 다이어그램, 주요 함수 설명을 포함한 문서를 생성한다. 사용 시점: (1) 코드 인수인계 문서 필요시, (2) 주니어 개발자/기획자를 위한 시스템 설명 문서 필요시, (3) 프로젝트 온보딩 문서 작성시"
---

# Code Documentation Skill

코드를 분석하여 비개발자도 이해할 수 있는 기술 문서를 생성한다.

## 출력 형식 옵션

| 형식 | 확장자 | 용도 | 스크립트 |
|------|--------|------|----------|
| **Markdown** | `.md` | GitHub README, 버전 관리 | `scripts/generate_doc_md.py` |
| **PDF** | `.pdf` | 정식 문서, 인쇄물, 공유 | `scripts/generate_doc_pdf.py` |
| **PowerPoint** | `.pptx` | 발표, 교육 자료 | `scripts/generate_doc_pptx.py` |

### 형식 선택 가이드

```
사용자 요청 분석:
+-- "문서 작성" / "README" / "기록용" --> Markdown
+-- "PDF로" / "인쇄" / "공유 문서" --> PDF  
+-- "발표 자료" / "PPT" / "교육용" --> PowerPoint
+-- 명시적 요청 없음 --> 용도 확인 후 추천
```

## 대상 독자

- 주니어 개발자
- 기획자 / 이해관계자
- 인수인계 대상자
- 리버스 엔지니어링 수행자

## 문서 구조

```
1. 개요 (Overview)
   - 프로젝트 목적과 역할
   - 핵심 기능 요약

2. 시스템 구조 (Architecture)
   - 디렉토리 구조
   - 모듈 간 관계

3. 워크플로우 (Workflow)
   - 데이터 처리 흐름
   - 단계별 설명

4. 주요 컴포넌트 (Key Components)
   - 클래스/함수 설명
   - 입출력 정의

5. 빌드 & 실행 (Build & Run)
   - 필수 요구사항
   - 실행 명령어

6. 트러블슈팅 (Troubleshooting)
   - 자주 발생하는 문제
   - 해결 방법

[부록] 기술 상세 (선택)
   - 알고리즘 상세
   - 데이터 구조
   - 용어집
```

---

## 실행 프로세스

### Step 1: 코드베이스 분석

```bash
# 프로젝트 구조 파악
find . -type f \( -name "*.py" -o -name "*.cpp" -o -name "*.h" \) | head -50

# 디렉토리 트리
tree -L 3 -I 'node_modules|__pycache__|.git|venv|build'
```

### Step 2: 진입점 식별

1. `main.cpp`, `main.py`, `index.js` 등 진입점 확인
2. 핵심 비즈니스 로직 모듈 식별
3. 의존성 관계 파악

### Step 3: 모듈별 분석

`references/analysis_template.md` 참조:
1. 클래스/함수 목록 추출
2. import/include 분석으로 의존성 파악
3. 주요 로직 흐름 파악

### Step 4: 다이어그램 작성

`references/mermaid_patterns.md` 참조:
1. 워크플로우 플로우차트
2. 시스템 구조도
3. 시퀀스 다이어그램 (필요시)

### Step 5: 문서 생성

출력 형식에 따라 적절한 스크립트 사용

---

## 형식별 생성 가이드

### Option A: Markdown

**적합한 상황**: GitHub 저장소, 개발자 문서, 버전 관리 필요

**특징**:
- Mermaid 다이어그램 지원 (GitHub 렌더링)
- 코드 블록 문법 하이라이팅
- 목차 자동 생성 가능

```bash
python scripts/generate_doc_md.py --project "ProjectName"
```

---

### Option B: PDF

**적합한 상황**: 공식 문서, 인쇄물, 외부 공유, 인수인계

**특징**:
- 페이지 번호/헤더 자동 추가
- 테이블 컬럼 너비 최적화 (텍스트 겹침 방지)
- 본문 + 부록 분리 구조
- ASCII 다이어그램 (호환성)

**PDF 작성 시 주의사항**:
1. 테이블 컬럼 너비를 명시적으로 지정 (cm 단위)
2. 한글 폰트 등록 필요 (NanumGothic 또는 DejaVu)
3. 긴 텍스트는 줄바꿈 처리

```bash
python scripts/generate_doc_pdf.py --project "ProjectName"
```

---

### Option C: PowerPoint

**적합한 상황**: 발표, 팀 교육, 경영진 보고

**특징**:
- 슬라이드별 구성
- 시각적 레이아웃
- 2열 레이아웃 지원

**권장 슬라이드 구성**:
```
Slide 1:  표지
Slide 2:  목차
Slide 3:  개요 & 목적
Slide 4:  시스템 아키텍처
Slide 5:  워크플로우
Slide 6-8: 주요 컴포넌트
Slide 9:  빌드 & 실행
Slide 10: Q&A
```

```bash
python scripts/generate_doc_pptx.py --project "ProjectName"
```

---

## 문서 작성 원칙

### 주니어 친화적 작성

1. **전문 용어 최소화**: 기술 용어 사용 시 괄호 안에 설명
2. **비유 활용**: 복잡한 개념은 일상적인 비유로 설명
3. **시각 자료 우선**: 텍스트보다 다이어그램으로 먼저 설명
4. **What-Why-How**: 무엇을 → 왜 필요한지 → 어떻게 동작하는지

### 함수 설명 템플릿

```markdown
### function_name()

**목적**: 한 문장으로 이 함수가 하는 일

**비유**: (선택) 일상적인 비유로 설명

**입력**:
- `param1`: 설명
- `param2`: 설명

**출력**: 반환값 설명

**코드 위치**: file.cpp, line 100-150
```

### 다이어그램 작성

**Markdown용 (Mermaid)**:
```
flowchart TD
    A[Start] --> B{Condition}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
```

**PDF용 (ASCII)**:
```
+-------+     +-------+
| Start |---->| Check |
+-------+     +---+---+
                  |
        +---------+---------+
        v                   v
  +-----------+       +-----------+
  | Action 1  |       | Action 2  |
  +-----------+       +-----------+
```

---

## 파일 명명 규칙

```
{프로젝트명}_{내용}.{확장자}

예시:
- phasemap_documentation.md
- phasemap_documentation.pdf
- phasemap_presentation.pptx
```

## 산출물 위치

```
/mnt/user-data/outputs/
+-- {프로젝트명}_documentation.md
+-- {프로젝트명}_documentation.pdf
+-- {프로젝트명}_presentation.pptx
```

---

## 참조 문서

- `references/analysis_template.md`: 코드 분석 체크리스트
- `references/mermaid_patterns.md`: 다이어그램 패턴
- `scripts/generate_doc_md.py`: Markdown 생성
- `scripts/generate_doc_pdf.py`: PDF 생성
- `scripts/generate_doc_pptx.py`: PowerPoint 생성
