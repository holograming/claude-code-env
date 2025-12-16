# 사용 예제

## 기본 예제

### 예제 1: GitHub blob URL 사용

```bash
python scripts/sync_to_notion.py "https://github.com/holograming/cote-programmers/blob/main/프로그래머스/2/12909.올바른괄호/README.md"
```

**출력**:
```
📁 설정 파일 로드: .env.local
📥 README 가져오는 중: https://github.com/holograming/...
📂 경로 정보: 플랫폼=프로그래머스, 난이도=Lv.2, 번호=12909
📝 파싱 정보: 제목=올바른 괄호, 알고리즘=['스택/큐'], 언어=Python
📤 노션 페이지 생성 중...

==================================================
✅ 노션 페이지 생성 완료!
🔗 페이지 URL: https://www.notion.so/2c4c90b872eb81108a67cc69761b28083
==================================================
```

### 예제 2: Raw GitHub URL 사용

```bash
python scripts/sync_to_notion.py "https://raw.githubusercontent.com/user/repo/refs/heads/main/프로그래머스/2/12909.올바른괄호/README.md"
```

## Python 모듈로 사용

### 예제 3: 직접 함수 호출

```python
import sys
sys.path.insert(0, 'scripts')
from sync_to_notion import create_notion_page

# 환경 변수 로드
from sync_to_notion import load_env_file
load_env_file()

# 페이지 생성
result = create_notion_page(
    title="올바른 괄호",
    platform="프로그래머스",
    level="Lv.2",
    problem_number=12909,
    algorithm_tags=["스택/큐"],
    language="Python",
    problem_url="https://school.programmers.co.kr/learn/courses/30/lessons/12909",
    github_url="https://github.com/holograming/cote-programmers/tree/main/프로그래머스/2/12909.올바른괄호",
    description="괄호가 바르게 짝지어졌는지 확인하는 문제입니다.",
    constraints="문자열 길이: 100,000 이하",
    code_url="https://github.com/holograming/cote-programmers/tree/main/프로그래머스/2/12909.올바른괄호",
    review="Stack을 사용하여 괄호의 짝을 확인합니다."
)

print(f"✅ 페이지 생성: {result.get('url')}")
```

### 예제 4: 배치 처리

```python
import sys
sys.path.insert(0, 'scripts')
from sync_to_notion import fetch_github_readme, create_notion_page, load_env_file, parse_path_info, parse_readme_content

load_env_file()

# 여러 문제를 한 번에 처리
problems = [
    "https://github.com/user/repo/blob/main/프로그래머스/2/12909.올바른괄호/README.md",
    "https://github.com/user/repo/blob/main/프로그래머스/2/12973.짝지어제거하기/README.md",
    "https://github.com/user/repo/blob/main/프로그래머스/3/43162.네트워크/README.md",
]

for url in problems:
    try:
        print(f"처리 중: {url}")

        # README 가져오기
        readme = fetch_github_readme(url)

        # 정보 파싱
        path_info = parse_path_info(url)
        content_info = parse_readme_content(readme)

        # 페이지 생성
        title = content_info["title"] or path_info["problem_name"]

        result = create_notion_page(
            title=title,
            platform=path_info["platform"],
            level=path_info["level"],
            problem_number=path_info["problem_number"],
            algorithm_tags=content_info["algorithm_tags"],
            language=content_info["language"],
            problem_url=f"https://school.programmers.co.kr/learn/courses/30/lessons/{path_info['problem_number']}",
            github_url=url,
            description=content_info["description"],
            constraints=content_info["constraints"],
            code_url=url.rsplit("/", 1)[0],
            review=content_info["review"],
        )

        print(f"✅ 완료: {result.get('url')}\n")

    except Exception as e:
        print(f"❌ 오류: {e}\n")
```

## 실전 시나리오

### 시나리오 1: 정기적인 풀이 기록

매주 풀이를 Notion에 자동으로 기록:

```bash
#!/bin/bash
# sync-problems.sh

python scripts/sync_to_notion.py \
  "https://github.com/my-account/cote/blob/main/프로그래머스/2/12909.올바른괄호/README.md" && \
python scripts/sync_to_notion.py \
  "https://github.com/my-account/cote/blob/main/프로그래머스/3/43162.네트워크/README.md"
```

실행:
```bash
bash sync-problems.sh
```

### 시나리오 2: GitHub Actions 연동

`.github/workflows/sync-notion.yml`:

```yaml
name: Sync to Notion

on:
  push:
    paths:
      - 'solutions/**/*.md'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r scripts/requirements.txt

      - name: Sync to Notion
        env:
          NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
        run: |
          python scripts/sync_to_notion.py \
            "https://github.com/${{ github.repository }}/blob/${{ github.ref }}/프로그래머스/2/12909.올바른괄호/README.md"
```

GitHub Secrets 설정:
- `NOTION_API_KEY`: Notion Integration 토큰
- `NOTION_DATABASE_ID`: Database ID

### 시나리오 3: 로컬 폴더 모니터링

```python
import os
import glob
from pathlib import Path
from urllib.parse import quote

# 로컬 프로젝트 구조
base_path = "./solutions/프로그래머스"
repo_url = "https://github.com/my-account/cote/blob/main"

# 모든 README.md 찾기
readme_files = glob.glob(f"{base_path}/**/README.md", recursive=True)

for readme_file in readme_files:
    # 상대 경로 추출
    relative_path = Path(readme_file).relative_to("./solutions")

    # GitHub URL 구성
    github_url = f"{repo_url}/프로그래머스/{relative_path.as_posix()}"

    # 동기화
    print(f"Syncing: {github_url}")
    os.system(f'python scripts/sync_to_notion.py "{github_url}"')
```

## 고급 활용

### 언어별 필터링

```python
supported_languages = ["Python", "Java", "C++"]

if content_info["language"] in supported_languages:
    # 페이지 생성
    create_notion_page(...)
else:
    print(f"지원하지 않는 언어: {content_info['language']}")
```

### 난이도별 처리

```python
difficulty_weights = {
    "Lv.1": 1,
    "Lv.2": 2,
    "Lv.3": 3,
    "Lv.4": 4,
    "Lv.5": 5,
}

difficulty = path_info["level"]
weight = difficulty_weights.get(difficulty, 0)

# 난이도에 따른 처리
if weight >= 3:
    print(f"어려운 문제: {title}")
```

## 에러 처리

### 전체 에러 핸들링

```python
from sync_to_notion import fetch_github_readme, create_notion_page
import traceback

try:
    readme = fetch_github_readme(url)
    # ... 처리
except requests.exceptions.RequestException as e:
    print(f"❌ 네트워크 오류: {e}")
except json.JSONDecodeError as e:
    print(f"❌ JSON 파싱 오류: {e}")
except Exception as e:
    print(f"❌ 예기치 않은 오류: {e}")
    traceback.print_exc()
```
