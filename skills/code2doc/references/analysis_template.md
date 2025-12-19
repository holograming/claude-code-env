# Code Analysis Template

코드 분석 시 확인해야 할 체크리스트

## 1. 프로젝트 기본 정보

```markdown
- [ ] 프로젝트명:
- [ ] 언어/프레임워크:
- [ ] 빌드 시스템:
- [ ] 주요 의존성:
- [ ] 실행 환경:
```

## 2. 디렉토리 구조 분석

```bash
# 전체 구조 파악
tree -L 3 -I 'node_modules|__pycache__|.git|venv|build|dist'

# 소스 파일 목록
find . -type f \( -name "*.py" -o -name "*.cpp" -o -name "*.h" -o -name "*.js" -o -name "*.ts" \) | head -50

# 설정 파일 확인
ls -la *.json *.yaml *.yml *.toml CMakeLists.txt Makefile 2>/dev/null
```

## 3. 진입점 (Entry Point) 식별

| 언어 | 일반적인 진입점 |
|------|----------------|
| Python | `main.py`, `app.py`, `__main__.py` |
| C/C++ | `main.cpp`, `main.c` |
| JavaScript | `index.js`, `app.js`, `server.js` |
| TypeScript | `index.ts`, `main.ts` |
| Java | `Main.java`, `Application.java` |

## 4. 모듈별 분석 템플릿

각 핵심 모듈에 대해 다음을 파악:

```markdown
### 모듈명: [이름]

**파일 위치**: path/to/file.ext

**목적**: 
- 이 모듈이 하는 일 (한 문장)

**의존성**:
- 이 모듈이 import하는 것
- 이 모듈을 import하는 곳

**주요 클래스/함수**:
| 이름 | 역할 | 입력 | 출력 |
|------|------|------|------|
| | | | |

**데이터 흐름**:
- 입력: 어디서 데이터가 오는가
- 처리: 무엇을 하는가
- 출력: 결과가 어디로 가는가
```

## 5. 의존성 분석

```python
# Python - import 분석
import ast
import sys

def analyze_imports(filepath):
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)
    
    return imports
```

```bash
# C++ - include 분석
grep -rh "#include" --include="*.cpp" --include="*.h" | sort | uniq -c | sort -rn
```

## 6. 함수/클래스 추출

```python
# Python - 클래스/함수 목록
import ast

def extract_definitions(filepath):
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    classes = []
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)
    
    return classes, functions
```

## 7. 데이터 흐름 파악

질문 체크리스트:
- [ ] 입력 데이터는 어디서 오는가? (파일, API, 사용자 입력)
- [ ] 데이터는 어떤 형식인가? (JSON, CSV, binary, 이미지)
- [ ] 중간 처리 단계는 무엇인가?
- [ ] 최종 출력은 무엇인가?
- [ ] 에러 처리는 어떻게 되는가?

## 8. 설정/환경 파악

```markdown
- [ ] 환경 변수: .env 파일 확인
- [ ] 설정 파일: config.*, settings.* 확인
- [ ] 시크릿: API 키, 인증 정보 위치
- [ ] 빌드 설정: CMakeLists.txt, package.json, requirements.txt
```

## 9. 테스트 코드 확인

```bash
# 테스트 파일 찾기
find . -name "*test*.py" -o -name "*_test.cpp" -o -name "*.test.js"

# 테스트 커버리지 확인
pytest --cov=. --cov-report=html  # Python
```

## 10. 문서화 상태 확인

```markdown
- [ ] README.md 존재 여부
- [ ] API 문서 (Swagger, docstring 등)
- [ ] 주석 품질 (함수/클래스 설명)
- [ ] 변경 이력 (CHANGELOG)
```

## 분석 결과 정리 템플릿

```markdown
# [프로젝트명] 코드 분석 결과

## 요약
- **목적**: 
- **기술 스택**: 
- **복잡도**: 낮음/중간/높음

## 핵심 모듈
1. 모듈A - 역할
2. 모듈B - 역할

## 데이터 흐름
입력 → 처리1 → 처리2 → 출력

## 주의사항
- 
- 

## 개선 제안
- 
- 
```
