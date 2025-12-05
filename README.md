# Holo Agent Skills

Claude skills 저장소입니다. 여러 개의 커스텀 스킬을 관리합니다.

---

## 📚 스킬 목록

### 1. splitting-pdf-chapters
PDF를 북마크 기반으로 개별 챕터로 분할합니다.

**위치**: `./skills/splitting-pdf-chapters`

### 2. cmake-skill
Modern CMake (3.15+) 프로젝트 구성 및 빌드 시스템 관리 스킬입니다. CMakeLists.txt 작성, 의존성 관리 (find_package, FetchContent), 빌드 설정, 컴파일러 플래그, 타겟 속성 설정, 문제 해결 등을 다룹니다.

**위치**: `./skills/cmake-skill`

---

## 🚀 빠른 시작

### 1단계: 마켓플레이스 등록 (한 번만)
\`\`\`bash
/plugin marketplace add hologramer/claude-code-env
\`\`\`

### 2단계: 스킬 설치

**문서 처리 스킬 (Document Skills):**
\`\`\`bash
/plugin install document-skills@lala-agent-skills
\`\`\`

**개발 도구 스킬 (Dev Tool):**
\`\`\`bash
/plugin install dev-tool@lala-agent-skills
\`\`\`

### 3단계: 사용

**splitting-pdf-chapters 예시:**
\`\`\`
"splitting-pdf-chapters 스킬로 이 PDF를 분할해줘: /path/to/file.pdf"
\`\`\`

**cmake-skill 예시:**
\`\`\`
"CMake 프로젝트 초기화를 도와줄 수 있어?"
"CMakeLists.txt에서 라이브러리를 링크하는 방법을 보여줘"
\`\`\`

---

## 📁 폴더 구조

\`\`\`
.
├── skills/                      # 스킬 저장소
│   ├── splitting-pdf-chapters/  # 스킬 1: 문서 처리
│   │   ├── SKILL.md             # 필수: 스킬 정의
│   │   ├── FORMS.md             # 선택: 사용 가이드
│   │   ├── REFERENCE.md         # 선택: 기술 참고
│   │   ├── scripts/             # 선택: 스크립트
│   │   └── requirements.txt     # 선택: 의존성
│   │
│   ├── cmake-skill/             # 스킬 2: 개발 도구
│   │   ├── SKILL.md             # 필수: 스킬 정의
│   │   ├── finding-packages.md  # 선택: 참고 문서
│   │   ├── modern-targets.md    # 선택: 참고 문서
│   │   ├── scripts/             # 헬퍼 스크립트
│   │   │   └── init_project.py
│   │   ├── assets/              # 프로젝트 템플릿
│   │   │   └── templates/
│   │   └── LICENSE.txt
│   │
│   └── [new-skill-name]/        # 스킬 3+ (같은 구조)
│
├── .claude-plugin/
│   └── marketplace.json         # 필수: 마켓플레이스 설정
├── spec/                        # 참고: 공식 명세
├── template/                    # 참고: 스킬 템플릿
├── .gitignore
└── README.md
\`\`\`

---

## ➕ 새로운 스킬 추가하기

### Step 1: 스킬 폴더 생성
\`\`\`bash
mkdir skills/my-new-skill
cd skills/my-new-skill
\`\`\`

### Step 2: SKILL.md 작성 (필수)
\`\`\`bash
cat > SKILL.md << 'EOF'
---
name: my-new-skill
description: 스킬이 무엇인지, 언제 사용하는지 설명
---

# My New Skill

## 사용 방법
[지시사항 작성]

## 예시
- 예시 1
- 예시 2
EOF
\`\`\`

### Step 3: marketplace.json 업데이트

**Option A: 기존 플러그인에 추가**
\`\`\`json
"plugins": [
  {
    "name": "document-skills",
    "description": "Collection of document processing capabilities",
    "source": "./",
    "strict": false,
    "skills": [
      "./skills/splitting-pdf-chapters",
      "./skills/my-new-skill"
    ]
  }
]
\`\`\`

**Option B: 새로운 플러그인 추가 (권장)**
\`\`\`json
"plugins": [
  {
    "name": "my-plugin",
    "description": "Description of my plugin",
    "source": "./",
    "strict": false,
    "skills": [
      "./skills/my-new-skill"
    ]
  }
]
\`\`\`

### Step 4: Git에 커밋
\`\`\`bash
git add .
git commit -m "Add my-new-skill"
git push
\`\`\`

---

## 📝 스킬 파일 설명

| 파일 | 필수 | 설명 |
|------|------|------|
| **SKILL.md** | ✅ | 스킬 정의 및 사용 지시사항 |
| **FORMS.md** | ❌ | 상세한 커맨드라인 옵션 가이드 |
| **REFERENCE.md** | ❌ | 기술적 깊이있는 문서 |
| **scripts/** | ❌ | 실행 가능한 코드 파일들 |
| **requirements.txt** | ❌ | Python 의존성 |

---

## 📖 스킬 SKILL.md 형식

### Frontmatter (필수)
\`\`\`yaml
---
name: skill-name              # 하이픈 케이스, 소문자
description: 설명             # 언제/왜 사용하는지 명시
---
\`\`\`

### 본문 (필수)
\`\`\`markdown
# Skill Title

## 사용 방법
[단계별 지시사항]

## 예시
- 예시 1
- 예시 2
\`\`\`

---

## 🔗 참고 자료

- [Agent Skills Spec](spec/agent-skills-spec.md)
- [Skill Template](template/SKILL.md)
- [Claude Skills 공식 가이드](https://support.claude.com/en/articles/12512198-creating-custom-skills)

---

## 🚢 배포

### GitHub + Marketplace (권장)
\`\`\`bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/hologramer/claude-code-env.git
git push -u origin main
\`\`\`

그 다음 Claude Code에서:
\`\`\`bash
/plugin marketplace add hologramer/claude-code-env
\`\`\`

---

**스킬을 만들 준비가 되셨습니까?** 🎉
