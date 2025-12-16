# 설정 가이드

## 1단계: Notion Integration 생성

### 1.1 Notion Integrations 페이지 접속
- https://www.notion.so/my-integrations 열기
- 로그인 필요

### 1.2 새 Integration 생성
1. "New Integration" 클릭
2. Integration 이름 입력 (예: `claude-code-sync`)
3. 필수 설정:
   - **Associated workspace**: 대상 워크스페이스 선택
   - **Capabilities**: `Read content`, `Update content`, `Create content` 선택
4. "Submit" 클릭

### 1.3 API Token 복사
- "Internal Integration Token" 섹션에서 토큰 복사
- 안전하게 보관 (재생성 불가)

## 2단계: Notion Database 준비

### 2.1 Database 생성 또는 선택

#### 새로 생성하는 경우

1. Notion Workspace에서 새 Database 생성
2. Database 이름: "코딩테스트" 등 (자유)
3. 템플릿: "빈 데이터베이스" 선택

#### 기존 Database 사용

- 이미 있는 Database 활용 가능

### 2.2 Database ID 확인

Database URL 형식:
```
https://www.notion.so/{DATABASE_ID}?v={VIEW_ID}
```

**DATABASE_ID 추출**:
- URL에서 `?` 앞 부분의 32자 문자열
- 예: `2c3c90b872eb806e8871f9f650357d83`

### 2.3 속성 생성

**필수 속성 5개** (생성 순서):

1. **문제명** (Title) - 기본으로 존재
   - 타입: Title
   - 이름: "문제명"

2. **플랫폼** (Select)
   - 타입: Select
   - 옵션: 프로그래머스, 백준, LeetCode

3. **난이도** (Select)
   - 타입: Select
   - 옵션: Lv.1, Lv.2, Lv.3, Lv.4, Lv.5

4. **풀이 날짜** (Date)
   - 타입: Date
   - 날짜 형식: 자동

5. **상태** (Status)
   - 타입: Status
   - 옵션: 완료, 재시도, 진행중

**선택 속성** (필요시 추가):

```
문제 번호 (Number)
알고리즘 (Multi-Select)
문제 링크 (URL)
언어 (Select)
```

## 3단계: Integration 권한 설정

### 3.1 Database에 Integration 추가

1. Database 우측 상단 "•••" 메뉴 열기
2. "Add connection" 클릭
3. 1단계에서 생성한 Integration 선택
4. "Confirm" 클릭

## 4단계: 환경 변수 설정

### 4.1 `.env.local` 파일 생성

스크립트 실행 위치에 파일 생성:

```bash
# .env.local

# Notion Integration 토큰 (1.3에서 복사한 값)
NOTION_API_KEY=secret_xxxxx...

# Notion Database ID (2.2에서 추출한 값)
NOTION_DATABASE_ID=2c3c90b872eb806e8871f9f650357d83
```

### 4.2 권한 확인

스크립트 실행으로 확인:

```bash
python scripts/sync_to_notion.py "https://github.com/user/repo/blob/main/.../README.md"
```

**성공 메시지**:
```
📁 설정 파일 로드: .env.local
✅ 노션 페이지 생성 완료!
🔗 페이지 URL: https://www.notion.so/...
```

## 트러블슈팅

### `NOTION_API_KEY가 설정되지 않았습니다`

- ✅ `.env.local` 파일이 존재하는가?
- ✅ 파일이 같은 디렉토리에 있는가?
- ✅ `NOTION_API_KEY=` 형식이 올바른가?

### `401 Unauthorized`

- ✅ API 토큰이 유효한가?
- ✅ Integration이 활성화되었는가?
- ✅ 토큰을 다시 복사해서 확인

### `400 Bad Request`

- ✅ Database ID가 정확한가?
- ✅ Database 속성명이 정확한가?
- ✅ Integration이 Database에 추가되었나?

### `404 Not Found`

Database에 Integration이 추가되지 않음:
1. Database 우측 상단 "•••" 메뉴
2. "Connections" → Integration 확인
3. 없으면 "Add connections" 다시 진행

## 다중 Database 사용

여러 Database를 사용하려면:

```bash
# Database 1
NOTION_DATABASE_ID_PROGRAMMERS=2c3c90b872eb806e8871f9f650357d83

# Database 2
NOTION_DATABASE_ID_LEETCODE=5d4d90b872eb806e8871f9f650357d84
```

스크립트 수정으로 동적 선택 가능.
