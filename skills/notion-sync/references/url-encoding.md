# URL 인코딩 및 특수 문자 처리

## 문제 배경

GitHub에 저장된 한글 폴더명, 특히 파일명에 포함된 특수 공백 문자 때문에 URL 인코딩 문제가 발생할 수 있습니다.

## 특수 공백 문자 (U+2005)

### 무엇인가?

- **문자명**: Four-Per-Em Space
- **코드포인트**: U+2005
- **용도**: 타이포그래피에서 사용되는 특수 공백
- **외관**: 일반 공백(space, U+0020)처럼 보임

### GitHub에서의 사용

프로그래머스 폴더명 예시:
```
12909.​올바른​괄호
    ↑          ↑
 U+2005    U+2005
```

## 인코딩 방식

### UTF-8 바이트 표현
```
U+2005 → 0xE2 0x80 0x85 → %E2%80%85
```

### 일반 공백과의 비교

| 문자 | Unicode | UTF-8 | URL 인코딩 |
|------|---------|-------|-----------|
| Space | U+0020 | 0x20 | %20 |
| Four-Per-Em Space | U+2005 | E2 80 85 | %E2%80%85 |

## 스크립트에서의 처리

### 1. URL 파싱

```python
from urllib.parse import unquote, quote

# GitHub blob URL
url = "https://github.com/user/repo/blob/main/.../README.md"

# 경로 추출 및 디코딩
parts = url.split("/")
path = "/".join(parts[7:])
path = unquote(path)  # 자동으로 UTF-8 디코딩
```

### 2. GitHub API 호출

```python
# quote()로 특수 공백 포함 경로 인코딩
encoded_path = quote(path, safe='/')
api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{encoded_path}"
```

### 3. 요청 처리

```python
response = requests.get(api_url)
# requests가 자동으로 올바른 UTF-8 인코딩 처리
```

## 실제 예시

### Before (실패)

```python
# ❌ raw URL 직접 사용 (특수 공백 처리 실패)
raw_url = "https://raw.githubusercontent.com/user/repo/main/.../%E2%80%85.../README.md"
response = requests.get(raw_url)  # 404 Not Found
```

### After (성공)

```python
# ✅ GitHub API 사용 (올바른 인코딩)
api_url = "https://api.github.com/repos/user/repo/contents/프로그래머스/2/12909.올바른괄호/README.md"
response = requests.get(api_url, params={"ref": "main"})  # 200 OK
```

## 문제 해결

### 404 오류 발생

```
❌ 404 Client Error: Not Found
```

**원인**: 특수 공백 문자 미처리

**해결책**:
1. ✅ GitHub API 사용 (권장)
2. ✅ URL 다시 인코딩
3. ✅ Repository를 public으로 변경

### 인코딩 확인 방법

Python에서 확인:

```python
from urllib.parse import quote, unquote

# 디코딩
decoded = unquote("%E2%80%85%EC%98%AC%EB%B0%94%EB%A5%B8%EA%B4%84%ED%98%B8")
# → "​올바른​괄호" (U+2005 포함)

# 인코딩
path = "프로그래머스/2/12909.올바른괄호/README.md"
encoded = quote(path, safe='/')
# → "%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%A8%B4%EC%8A%A4/2/12909.%E2%80%85%EC%98%AC%EB%B0%94%EB%A5%B8%E2%80%85%EA%B4%84%ED%98%B8/README.md"
```

## 추천 사항

- 🔄 **GitHub blob URL**: 스크립트가 자동으로 처리
- 🔄 **Raw URL**: 일반 공백으로 수동 수정 필요
- ✅ **GitHub API**: 가장 안정적 (권장)
