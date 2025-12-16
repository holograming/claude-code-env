---
name: notion-sync
description: Notion 데이터베이스에 GitHub README를 자동 동기화. 프로그래머스 코딩테스트 풀이를 GitHub에서 가져와 Notion 페이지로 생성. 한글 경로와 특수 공백 문자 처리 지원.
license: MIT
---

# Notion 코딩테스트 동기화 스킬

GitHub의 코딩테스트 풀이 README를 Notion 데이터베이스에 자동으로 동기화합니다.

## 주요 기능

- ✅ GitHub blob URL에서 README 자동 가져오기
- ✅ 한글 경로명 완벽 지원 (U+2005 특수 공백 포함)
- ✅ README 자동 파싱 (문제명, 난이도, 알고리즘 태그, 언어 등)
- ✅ Notion 페이지 자동 생성 (문제 설명, 제약사항, 풀이 메모)
- ✅ 정적 분석 기반 (외부 API 불필요)

## 언제 사용하나요?

1. **프로그래머스 풀이를 Notion에 기록**할 때
2. **코딩테스트 풀이를 Notion DB로 관리**할 때
3. **GitHub 코테 레포를 Notion과 연동**할 때

## 필수 설정

### 1. Notion Integration 설정

Notion 계정에서 Integration 생성:
1. https://www.notion.so/my-integrations 접속
2. 새 Integration 생성
3. **API Token** 복사
4. 대상 Database에 Integration 추가

### 2. 환경 변수 설정

`.env.local` 파일 생성:
```
NOTION_API_KEY=secret_xxxxx...     # Notion Integration 토큰
NOTION_DATABASE_ID=xxxxxxxx...     # 대상 데이터베이스 ID
```

## 사용 방법

### CLI 사용

```bash
python scripts/sync_to_notion.py <github-url>
```

**URL 형식**:
```bash
# 방식 1: GitHub blob URL (자동 인코딩)
python scripts/sync_to_notion.py "https://github.com/user/repo/blob/main/프로그래머스/2/12909.올바른괄호/README.md"

# 방식 2: Raw GitHub URL
python scripts/sync_to_notion.py "https://raw.githubusercontent.com/user/repo/main/.../README.md"
```

### Python 모듈로 사용

```python
from sync_to_notion import create_notion_page

create_notion_page(
    title="올바른 괄호",
    platform="프로그래머스",
    level="Lv.2",
    problem_number=12909,
    algorithm_tags=["스택/큐"],
    language="Python",
    problem_url="https://school.programmers.co.kr/...",
    github_url="https://github.com/...",
    description="문제 설명",
    constraints="제약사항",
    code_url="https://github.com/.../12909.올바른괄호",
    review="풀이 메모"
)
```

## 데이터베이스 스키마

### 필수 속성 (5개)

| 속성명 | 타입 | 설명 |
|--------|------|------|
| 문제명 | Title | 문제 이름 |
| 플랫폼 | Select | 프로그래머스 |
| 난이도 | Select | Lv.1 ~ Lv.5 |
| 풀이 날짜 | Date | 풀이 완료 날짜 |
| 상태 | Status | 완료/재시도/진행중 |

### 추가 속성 (선택)

| 속성명 | 타입 |
|--------|------|
| 문제 번호 | Number |
| 알고리즘 | Multi-Select |
| 문제 링크 | URL |
| 언어 | Select |

## 페이지 본문 구조

자동 생성되는 Notion 페이지:

```
📝 문제 설명
   (README에서 추출된 문제 설명)

📋 제한 사항
   (입력/출력 제약사항)

💻 풀이 코드
   🔗 GitHub 링크 (Bookmark)

📒 풀이 메모
   💡 접근 방법, 회고, 주의사항 (Callout)
```

## 지원하는 언어

- Python / Py
- Java
- C++ / Cpp
- JavaScript / Js
- Kotlin, Swift, Go, Rust 등

## 특수 기능

### 한글 경로명 처리

GitHub의 한글 폴더명과 특수 공백 문자(U+2005)를 자동으로 처리합니다.

```
입력 URL: https://github.com/user/repo/blob/main/프로그래머스/2/12909.올바른괄호/README.md
          ↓
GitHub API: 올바른 인코딩 및 특수 공백 처리
          ↓
결과: ✅ 성공 (공개 저장소라면 항상 작동)
```

### 알고리즘 태그 자동 매핑

README의 카테고리를 자동 변환:

| 입력 | 변환 |
|------|------|
| 스택／큐 | 스택/큐 |
| 깊이／너비 우선 탐색(DFS／BFS) | DFS/BFS |
| 동적계획법(Dynamic Programming) | DP |
| 탐욕법(Greedy) | 그리디 |

## 문제 해결

### README 파일을 찾을 수 없음

```
❌ 404 Client Error
```

**해결책**:
1. ✅ Repository가 **public**인지 확인
2. ✅ URL의 경로가 **정확한지** 확인
3. ✅ `/blob/main/` (또는 branch명) 형식 확인

### Notion API 오류

```
❌ 401 Unauthorized / 400 Bad Request
```

**확인 사항**:
- NOTION_API_KEY가 유효한가?
- Database에 Integration이 추가되었나?
- 데이터베이스 속성명이 정확한가?

### 특수 공백 문자 오류

GitHub의 폴더명에 특수 공백(U+2005)이 포함되면:
- ✅ 스크립트가 자동으로 처리합니다
- 💡 사용자는 일반 공백을 입력해도 괜찮습니다

## 참고 자료

- [GitHub API 문서](https://docs.github.com/rest/repos/contents)
- [Notion API 문서](https://developers.notion.com/docs)
- [Notion Database Schema](./references/schema.md)
- [URL 인코딩 처리](./references/url-encoding.md)
