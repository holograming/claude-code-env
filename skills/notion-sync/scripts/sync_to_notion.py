#!/usr/bin/env python3
"""
프로그래머스 README를 노션 데이터베이스에 동기화하는 스크립트

사용법:
    python sync_to_notion.py <github-readme-url>

설정 파일:
    .env.local 파일에 다음 내용 작성:
    NOTION_API_KEY=secret_xxxxx
    NOTION_DATABASE_ID=xxxxxxxx
"""

import os
import re
import sys
import json
from datetime import datetime
from urllib.parse import urlparse, unquote, quote
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ requests 패키지가 필요합니다: pip install requests")
    sys.exit(1)

# python-dotenv가 있으면 사용 (선택사항)
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False


# ============================================================================
# 설정
# ============================================================================

def load_env_file():
    """
    .env.local 파일에서 환경변수를 로드합니다.
    python-dotenv가 설치되어 있으면 사용하고, 없으면 수동 파싱합니다.
    """
    # 탐색할 경로들
    search_paths = [
        Path(__file__).parent.parent,    # 스킬 루트 폴더 (scripts의 상위)
        Path(__file__).parent,            # 스크립트가 있는 폴더
        Path.cwd(),                       # 현재 작업 디렉토리
    ]
    
    env_file = None
    for path in search_paths:
        candidate = path / ".env.local"
        if candidate.exists():
            env_file = candidate
            break
    
    if not env_file:
        return {}
    
    print(f"📁 설정 파일 로드: {env_file}")
    
    # python-dotenv가 있으면 사용
    if HAS_DOTENV:
        load_dotenv(env_file)
        return {}
    
    # 수동 파싱
    env_vars = {}
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 빈 줄이나 주석 무시
            if not line or line.startswith("#"):
                continue
            # KEY=VALUE 형식 파싱
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                # 따옴표 제거
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                env_vars[key] = value
                # 환경변수에도 설정
                os.environ[key] = value
    
    return env_vars


# .env.local 파일 로드
_env_config = load_env_file()

# 환경변수에서 가져오기
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# 언어 매핑
LANGUAGE_MAP = {
    "python": "Python",
    "py": "Python",
    "java": "Java",
    "cpp": "C++",
    "c++": "C++",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "go": "Go",
    "rust": "Rust",
}

# 알고리즘 태그 매핑
ALGORITHM_MAP = {
    "스택／큐": "스택/큐",
    "스택/큐": "스택/큐",
    "깊이／너비 우선 탐색(DFS／BFS)": "DFS/BFS",
    "DFS/BFS": "DFS/BFS",
    "동적계획법(Dynamic Programming)": "DP",
    "동적계획법": "DP",
    "탐욕법(Greedy)": "그리디",
    "탐욕법": "그리디",
    "해시": "해시",
    "정렬": "정렬",
    "완전탐색": "완전탐색",
    "이분탐색": "이분탐색",
    "그래프": "그래프",
    "힙(Heap)": "힙",
    "힙": "힙",
}


# ============================================================================
# GitHub README 파싱
# ============================================================================

def fetch_github_readme(url: str) -> str:
    """GitHub README URL에서 raw 콘텐츠를 가져옵니다."""
    print(f"📥 README 가져오는 중: {url[:80]}...")

    # GitHub blob URL 처리
    if "github.com" in url and "/blob/" in url:
        # URL 파싱: /owner/repo/blob/branch/path
        parts = url.split("/")
        owner = parts[3]
        repo = parts[4]
        branch = parts[6]
        path = "/".join(parts[7:])

        # URL 디코딩 (한글 경로와 특수 공백 처리)
        path = unquote(path)

        # GitHub API 호출 (특수 공백 포함 경로 처리)
        encoded_path = quote(path, safe='/')
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{encoded_path}?ref={branch}"

        print(f"📥 GitHub API 요청: {api_url[:80]}...")
        response = requests.get(api_url, timeout=10)

        if response.status_code == 200:
            file_info = response.json()
            download_url = file_info.get("download_url")

            if download_url:
                response = requests.get(download_url, timeout=10)
                response.raise_for_status()
                return response.text

        # API 실패 시 예외 발생
        response.raise_for_status()
    else:
        # raw URL인 경우 직접 사용
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text


def parse_path_info(url: str) -> dict:
    """
    GitHub URL 경로에서 플랫폼, 난이도, 문제번호를 추출합니다.
    
    예: /프로그래머스/2/12909.올바른괄호/README.md
    """
    parsed = urlparse(unquote(url))
    path_parts = parsed.path.split("/")
    
    info = {
        "platform": "프로그래머스",
        "level": "Lv.2",
        "problem_number": None,
        "problem_name": "Unknown",
    }
    
    for i, part in enumerate(path_parts):
        # 플랫폼 감지
        if "프로그래머스" in part:
            info["platform"] = "프로그래머스"
        elif "백준" in part or "BOJ" in part.upper():
            info["platform"] = "백준"
        elif "leetcode" in part.lower():
            info["platform"] = "LeetCode"
        
        # 난이도 감지 (숫자만 있는 폴더)
        if part.isdigit() and 1 <= int(part) <= 5:
            info["level"] = f"Lv.{part}"
        
        # 문제번호.문제명 폴더 감지
        if "." in part and part.split(".")[0].isdigit():
            parts = part.split(".", 1)
            info["problem_number"] = int(parts[0])
            if len(parts) > 1:
                # URL 인코딩된 공백 문자 처리
                name = parts[1].replace("\u2005", " ").replace("%E2%80%85", " ").strip()
                info["problem_name"] = name
    
    return info


def parse_readme_content(content: str) -> dict:
    """README 본문에서 문제 정보를 추출합니다."""
    result = {
        "title": None,
        "description": "",
        "constraints": "",
        "algorithm_tags": [],
        "language": "Python",
        "review": "",
    }
    
    lines = content.split("\n")
    current_section = None
    section_content = []
    in_review = False
    review_lines = []
    
    for i, line in enumerate(lines):
        # review 섹션 감지 (---로 구분된 영역)
        if line.strip() == "## review" or line.strip() == "## Review":
            in_review = True
            continue
        
        if in_review:
            if line.startswith("---") or line.startswith("# "):
                in_review = False
                result["review"] = "\n".join(review_lines).strip()
            else:
                review_lines.append(line)
            continue
        
        # 제목 추출 (# 으로 시작)
        if line.startswith("# ") and result["title"] is None:
            # [level X] 형식 제거
            title = line[2:].strip()
            title = re.sub(r'\[level \d+\]\s*', '', title, flags=re.IGNORECASE)
            # 문제번호 제거 (예: "올바른 괄호 - 12909" -> "올바른 괄호")
            title = re.sub(r'\s*-\s*\d+\s*$', '', title)
            result["title"] = title.strip()
            continue
        
        # 알고리즘 태그 추출
        if "코딩테스트 연습 >" in line:
            match = re.search(r'코딩테스트 연습 >\s*["\']?([^"\'<>\n]+)["\']?', line)
            if match:
                tag_raw = match.group(1).strip()
                tag = ALGORITHM_MAP.get(tag_raw, tag_raw)
                if tag not in result["algorithm_tags"]:
                    result["algorithm_tags"].append(tag)
        
        # 언어 추출 (코드 블록에서)
        if line.startswith("```"):
            lang = line[3:].strip().lower()
            if lang in LANGUAGE_MAP:
                result["language"] = LANGUAGE_MAP[lang]
        
        # 섹션 감지
        if line.startswith("## ") or line.startswith("### "):
            # 이전 섹션 저장
            if current_section == "문제 설명":
                result["description"] = "\n".join(section_content).strip()
            elif current_section in ["제한사항", "제한 사항"]:
                result["constraints"] = "\n".join(section_content).strip()
            
            current_section = line.lstrip("#").strip()
            section_content = []
        else:
            section_content.append(line)
    
    # 마지막 섹션 저장
    if current_section == "문제 설명":
        result["description"] = "\n".join(section_content).strip()
    elif current_section in ["제한사항", "제한 사항"]:
        result["constraints"] = "\n".join(section_content).strip()
    
    # review가 남아있으면 저장
    if review_lines and not result["review"]:
        result["review"] = "\n".join(review_lines).strip()
    
    return result


def get_code_file_url(readme_url: str) -> str:
    """README URL에서 같은 폴더의 코드 파일 URL을 추론합니다."""
    # README.md를 제거하고 폴더 URL 반환
    base_url = readme_url.rsplit("/", 1)[0]
    return base_url


# ============================================================================
# 노션 API
# ============================================================================

def notion_request(method: str, endpoint: str, data: dict = None) -> dict:
    """노션 API 요청을 수행합니다."""
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }
    
    url = f"{NOTION_API_URL}{endpoint}"
    
    if method == "POST":
        response = requests.post(url, headers=headers, json=data, timeout=30)
    elif method == "GET":
        response = requests.get(url, headers=headers, timeout=30)
    elif method == "PATCH":
        response = requests.patch(url, headers=headers, json=data, timeout=30)
    else:
        raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
    
    if not response.ok:
        print(f"❌ 노션 API 오류: {response.status_code}")
        print(response.text)
        response.raise_for_status()
    
    return response.json()


def create_notion_page(
    title: str,
    platform: str,
    level: str,
    problem_number: int,
    algorithm_tags: list,
    language: str,
    problem_url: str,
    github_url: str,
    description: str,
    constraints: str,
    code_url: str,
    review: str = "",
) -> dict:
    """노션 데이터베이스에 새 페이지를 생성합니다."""
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 속성 구성
    properties = {
        "문제명": {
            "title": [{"text": {"content": title}}]
        },
        "플랫폼": {
            "select": {"name": platform}
        },
        "난이도": {
            "select": {"name": level}
        },
        "풀이 날짜": {
            "date": {"start": today}
        },
        "상태": {
            "status": {"name": "완료"}
        },
    }
    
    # 선택적 속성 추가
    if problem_number:
        properties["문제 번호"] = {"number": problem_number}
    
    if algorithm_tags:
        properties["알고리즘"] = {
            "multi_select": [{"name": tag} for tag in algorithm_tags]
        }
    
    if problem_url:
        properties["문제 링크"] = {"url": problem_url}
    
    # GitHub 링크는 데이터베이스에 없으면 추가하지 않음
    # if github_url:
    #     properties["GitHub 링크"] = {"url": github_url}
    
    if language:
        properties["언어"] = {"select": {"name": language}}
    
    # 본문 블록 구성
    children = [
        # 문제 설명 섹션
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📝 문제 설명"}}]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": description[:2000] if description else "문제 설명을 추가하세요."}}]
            }
        },
        # 구분선
        {"object": "block", "type": "divider", "divider": {}},
        
        # 제한 사항 섹션
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📋 제한 사항"}}]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": constraints[:2000] if constraints else "제한 사항을 추가하세요."}}]
            }
        },
        # 구분선
        {"object": "block", "type": "divider", "divider": {}},
        
        # 풀이 코드 섹션
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "💻 풀이 코드"}}]
            }
        },
        {
            "object": "block",
            "type": "bookmark",
            "bookmark": {
                "url": code_url
            }
        },
        # 구분선
        {"object": "block", "type": "divider", "divider": {}},
        
        # 풀이 메모 섹션
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📒 풀이 메모"}}]
            }
        },
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "💡"},
                "rich_text": [{"type": "text", "text": {"content": review if review else "접근 방법, 회고 등을 작성하세요."}}]
            }
        },
    ]
    
    # 페이지 생성 요청
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": properties,
        "children": children,
    }
    
    return notion_request("POST", "/pages", data)


# ============================================================================
# 메인 함수
# ============================================================================

def main():
    # 환경변수 확인
    if not NOTION_API_KEY:
        print("❌ 오류: NOTION_API_KEY가 설정되지 않았습니다.")
        print("   .env.local 파일을 생성하고 NOTION_API_KEY를 설정하세요.")
        sys.exit(1)
    
    if not NOTION_DATABASE_ID:
        print("❌ 오류: NOTION_DATABASE_ID가 설정되지 않았습니다.")
        print("   .env.local 파일을 생성하고 NOTION_DATABASE_ID를 설정하세요.")
        sys.exit(1)
    
    # 인자 확인
    if len(sys.argv) < 2:
        print("사용법: python sync_to_notion.py <github-readme-url>")
        print()
        print("예시:")
        print('  python sync_to_notion.py "https://github.com/user/repo/blob/main/프로그래머스/2/12909.올바른괄호/README.md"')
        sys.exit(1)
    
    github_url = sys.argv[1]
    
    try:
        # README 가져오기
        readme_content = fetch_github_readme(github_url)
        print("✅ README 가져오기 완료")
        
        # 경로에서 정보 추출
        path_info = parse_path_info(github_url)
        print(f"📂 경로 정보: 플랫폼={path_info['platform']}, 난이도={path_info['level']}, 번호={path_info['problem_number']}")
        
        # README 내용 파싱
        content_info = parse_readme_content(readme_content)
        print(f"📝 파싱 정보: 제목={content_info['title']}, 알고리즘={content_info['algorithm_tags']}, 언어={content_info['language']}")
        
        # 최종 정보 병합
        title = content_info["title"] or path_info["problem_name"]
        problem_number = path_info["problem_number"]
        
        # 플랫폼별 문제 URL 생성
        if path_info["platform"] == "프로그래머스" and problem_number:
            problem_url = f"https://school.programmers.co.kr/learn/courses/30/lessons/{problem_number}"
        else:
            problem_url = ""
        
        code_url = get_code_file_url(github_url)
        
        # 노션 페이지 생성
        print("📤 노션 페이지 생성 중...")
        result = create_notion_page(
            title=title,
            platform=path_info["platform"],
            level=path_info["level"],
            problem_number=problem_number,
            algorithm_tags=content_info["algorithm_tags"],
            language=content_info["language"],
            problem_url=problem_url,
            github_url=github_url,
            description=content_info["description"],
            constraints=content_info["constraints"],
            code_url=code_url,
            review=content_info["review"],
        )
        
        page_url = result.get("url", "")
        print()
        print("=" * 50)
        print("✅ 노션 페이지 생성 완료!")
        print(f"🔗 페이지 URL: {page_url}")
        print("=" * 50)
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
