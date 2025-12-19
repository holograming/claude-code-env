# Code Documentation Skill

코드베이스를 분석하여 **MD / PDF / PPT** 형식의 기술 문서를 생성하는 Claude 스킬입니다.

### 1. 스킬 사용
Claude에게 문서 작성을 요청하면 자동으로 스킬이 적용됩니다.

## 스킬 구조

```
code2doc/
├── SKILL.md                          # 메인 스킬 정의
├── references/
│   ├── analysis_template.md          # 코드 분석 체크리스트
│   └── mermaid_patterns.md           # 다이어그램 패턴
└── scripts/
    ├── generate_doc_md.py            # Markdown 생성
    ├── generate_doc_pdf.py           # PDF 생성
    └── generate_doc_pptx.py          # PowerPoint 생성
```

## 출력 형식

| 형식 | 확장자 | 용도 |
|------|--------|------|
| **Markdown** | `.md` | GitHub README, 버전 관리 |
| **PDF** | `.pdf` | 정식 문서, 인쇄물, 공유 |
| **PowerPoint** | `.pptx` | 발표, 교육 자료 |

## 사용 예시

### PDF 문서 요청
```
"이 프로젝트를 분석해서 PDF 문서로 만들어줘"
"주니어 개발자를 위한 기술 문서를 PDF로 작성해줘"
```

### Markdown 문서 요청
```
"README 문서 작성해줘"
"GitHub용 문서 만들어줘"
```

### PowerPoint 요청
```
"발표 자료 만들어줘"
"PPT로 정리해줘"
```

## 의존성

스크립트 실행에 필요한 Python 패키지:

```bash
# PDF 생성
pip install reportlab --break-system-packages

# PowerPoint 생성
pip install python-pptx --break-system-packages
```

## 주요 기능

### PDF 생성 개선사항
- ✅ 테이블 컬럼 너비 명시적 지정 (텍스트 겹침 방지)
- ✅ 페이지 번호/헤더 자동 추가
- ✅ 본문 + 부록 분리 구조
- ✅ 가독성 최적화 (여백, 줄간격)

### 다이어그램 지원
- Markdown: Mermaid 문법
- PDF: ASCII Art (호환성)
- PowerPoint: 텍스트 박스 또는 이미지

## 문서 구조 권장

```
1. 개요 (Overview)
2. 시스템 구조 (Architecture)
3. 워크플로우 (Workflow)
4. 주요 컴포넌트 (Key Components)
5. 빌드 & 실행 (Build & Run)
6. 트러블슈팅 (Troubleshooting)

[부록]
A. 알고리즘 상세
B. 데이터 구조
C. 용어집
```

## 라이선스

MIT License
