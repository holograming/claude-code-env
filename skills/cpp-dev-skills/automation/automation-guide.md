# Claude Automation Guide for C++ Project Generation

**이 문서는 Claude를 위한 완전한 자동화 실행 프로토콜입니다.**

## 개요

사용자 요청 → 키워드 추출 → decisions.json 쿼리 → 환경 검증 → 프로젝트 생성 → 빌드 검증 → 에러 자동 복구 → 완성 프로젝트 제시

**목표:** "Qt로 3D 뷰어 만들어줘" → 0-1개 질문 → 2-5분 내 완성된 실행 파일

---

## Step 1: 사용자 요청 파싱

### 키워드 추출

```python
request = "Qt로 3D 뷰어 만들어줘"
keywords = ["Qt", "3D", "뷰어", "viewer"]

features = {
    "project_type": "gui",           # "뷰어"→gui 감지
    "gui_framework_mentioned": "qt6", # 명시적 "Qt"
    "use_case": "3d_viewer",         # "3D" + "viewer"
    "dependencies_implied": ["opengl", "3d_library"]
}
```

### 키워드 → 기능 매핑

| 키워드 | Project Type | Framework 힌트 | 의존성 |
|--------|--------------|----------------|--------|
| "viewer", "뷰어" | gui | - | - |
| "Qt", "qt6" | gui | qt6 | - |
| "3D", "OpenGL" | gui | lightweight | opengl, glm |
| "server", "daemon" | cli | - | - |
| "library", "lib" | library | - | - |

---

## Step 2: decisions.json 쿼리 → 자동 선택

### 결정 로직

```python
# decisions.json에서 조회
use_case = "3d_viewer"
frameworks = decisions['gui_frameworks']

# 각 framework 점수 계산
scores = {}
for name, framework in frameworks.items():
    if use_case in framework['auto_select_when']:
        scores[name] = framework['score']

# wxwidgets (5분) vs qt6 (20분) 충돌 해결
if 'qt6' in scores and 'wxwidgets' in scores:
    if user_mentioned_qt:
        selected = 'qt6'  # 사용자 명시 우선
    else:
        selected = 'wxwidgets'  # 빠른 빌드 우선
```

### 충돌 해결 규칙

```
사용자 명시 "Qt" vs 자동 선택 "wxWidgets" (3D viewer)

→ "Qt6 (20분 빌드)를 사용할까요, 아니면 wxWidgets (5분)로 빠르게?"
→ 사용자 선택 존중
```

---

## Step 3: 환경 자동 검증

### validate_env.py 실행

```bash
python scripts/validate_env.py

# 출력:
# ✓ CMake 3.27.0 found (>= 3.15 required)
# ✓ VCPKG_ROOT: C:\vcpkg
# ⚠ Windows long paths not enabled (will auto-fix)
# ✓ MSVC 19.39 detected
# → Ready for project generation
```

### 환경 변수 감지

```
VCPKG_ROOT 설정됨? → vcpkg 자동 사용
CMAKE_PREFIX_PATH 설정됨? → find_package 자동 사용
CXX 설정됨? → 컴파일러 자동 사용
→ 아무것도 없음? → 플랫폼 기본값 사용
```

---

## Step 4: 프로젝트 자동 생성

### init_project.py 호출

```python
cmd = [
    'python', 'scripts/init_project.py',
    'my3dviewer',              # 프로젝트명 (사용자 요청에서 추출)
    '--type', 'gui',            # Step 1에서 결정
    '--gui-framework', 'wxwidgets',  # Step 2에서 결정
    '--cpp-std', '17',          # 기본값
    '--user-request', 'Qt로 3D 뷰어 만들어줘'  # 키워드 추출용
]

subprocess.run(cmd)
```

### 생성되는 파일

```
my3dviewer/
├── CMakeLists.txt              # wxWidgets + OpenGL 설정
├── vcpkg.json                  # ["wxwidgets", "glm"]
├── src/main.cpp                # wxWidgets 기본 window
├── include/mylib.h
├── .gitignore
└── build/                       # cmake -B build && cmake --build build
```

---

## Step 5: 빌드 검증 루프 (核心!)

**절대 불완전한 프로젝트를 사용자에게 제시하지 마세요**

### 프로토콜

```python
def validate_build(project_dir):
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        # 1. CMake configure
        result = run("cmake -B build")
        if result.returncode != 0:
            error = result.stderr
            pattern = error_patterns.match(error)  # error-patterns.json
            if pattern and auto_fix(pattern):
                attempt += 1
                continue
            else:
                return False, f"CMake failed: {error[:300]}"

        # 2. CMake build
        result = run("cmake --build build")
        if result.returncode != 0:
            error = result.stderr
            pattern = error_patterns.match(error)
            if pattern and auto_fix(pattern):
                attempt += 1
                continue
            else:
                return False, f"Build failed: {error[:300]}"

        # 3. SUCCESS!
        return True, "Build successful"

    return False, "Max retry attempts (3) reached"
```

### 에러 자동 복구

```python
def auto_fix_error(error_output):
    for pattern in error_patterns['patterns']:
        if re.search(pattern['regex'], error_output):
            print(f"⚙ {pattern['user_message']}")

            # 자동 복구 시도
            for fix in pattern['auto_fix']:
                if execute_fix(fix):
                    print(f"✓ Fixed: {fix['method']}")
                    return True

            # Fallback 체인
            for fallback in pattern.get('fallback', []):
                if execute_fix(fallback):
                    print(f"✓ Fallback: {fallback['method']}")
                    return True

    return False  # 매칭되는 패턴 없음
```

### Fallback 체인 예제

```
에러: Qt6 빌드 실패 (메모리 부족)
  ↓
auto_fix: VCPKG_MAX_CONCURRENCY=4 설정 → 재빌드
  ↓
실패 → fallback: wxWidgets 대체 제안
```

---

## Step 6: 완성 프로젝트 제시 (성공만 가능)

### 조건

✅ cmake -B build 성공
✅ cmake --build build 성공
✅ ./build/my3dviewer 실행 확인
**이 3가지 모두 만족했을 때만 사용자에게 제시**

### 사용자에게 전달

```markdown
✅ wxWidgets 3D 뷰어 프로젝트 생성 완료 (빌드 5분)

프로젝트 위치: ./my3dviewer
빌드됨: ./my3dviewer/build/my3dviewer.exe

실행: ./build/my3dviewer

생성된 파일:
- CMakeLists.txt (wxWidgets + OpenGL 설정)
- vcpkg.json (의존성: wxwidgets, glm)
- src/main.cpp (기본 윈도우)

다음 단계:
1. 3D 렌더링 코드 추가 (OpenGL)
2. wxWidgets 레이아웃 커스터마이징
3. 파일 로드 기능 구현

참고: Qt를 선호하신다면, 20분 빌드 시간을 감당 가능하신지 먼저 확인하세요.
```

---

## Step 7: 에러 발생 시 사용자 보고 (자동 복구 실패)

### 조건

3회 자동 복구 시도 후에도 실패한 경우

### 사용자에게 전달

```markdown
❌ 빌드 실패 (자동 복구 불가)

에러: Windows MAX_PATH 제한 (경로 260자 초과)
자동 복구 시도:
  1. ✓ Registry에서 긴 경로 활성화
  2. ✗ 재부팅 필요 (다시 시도했지만 여전히 실패)

수동 조치 필요:
1. Windows를 재부팅하세요
2. vcpkg를 C:\vcpkg로 이동하세요 (더 짧은 경로)
3. VCPKG_ROOT를 업데이트하세요
4. 다시 시도해주세요

재시도 준비되셨으면 말씀해주세요.
```

---

## 최소 질문 전략

### ONLY IF 매우 모호한 경우:

```
"GUI 만들어줘" (framework 불명확)

→ 1개 질문만:
"어떤 UI 스타일?
[1] 간단함 (FLTK, 2분)
[2] 기본 (wxWidgets, 5분)
[3] 풍부함 (Qt6, 20분)"
```

### 절대 묻지 말 것:

❌ 컴파일러 선택 (자동 감지: Windows→MSVC, Linux→GCC)
❌ vcpkg vs FetchContent (자동 결정: VCPKG_ROOT 있으면 vcpkg)
❌ 빌드 타입 (자동: Debug for dev, Release for prod)
❌ CMake 버전 (검증만, 질문 안 함)
❌ 프로젝트 구조 (자동: 타겟 수로 결정)

**제한:** 세션당 최대 1-2개 질문

---

## 결정 예제

### 예제 1: CLI 도구

```
사용자: "파일 압축하는 CLI 만들어줘"
Step 1: type=cli, dependencies=zlib
Step 2: 의존성 자동 선택 (FetchContent, <1MB)
Step 3: 환경 검증 (CMake, compiler)
Step 4: 생성 (시간: 1분)
Step 5: 빌드 (cmake -B build && cmake --build build)
Step 6: 완성: ./build/mycompress
질문 수: 0
```

### 예제 2: GUI (모호함)

```
사용자: "그래픽 프로그램 만들어줘"
Step 1: type=gui, framework=? (모호함)
Step 2: 1개 질문 → "간단한 UI (FLTK) or 풍부한 UI (wxWidgets)?"
→ 사용자 선택: wxWidgets
Step 3-6: 진행
질문 수: 1
```

### 예제 3: 기업용 GUI

```
사용자: "엔터프라이즈 고객 관리 시스템 GUI"
Step 1: type=gui, keywords=enterprise
Step 2: decisions.json → Qt6 자동 선택 (enterprise_ui)
Step 3: VCPKG_MAX_CONCURRENCY 경고 (20분 빌드)
Step 4-6: 진행 (시간: 22분)
질문 수: 0
```

---

## 프로토콜 흐름도

```
사용자 요청
    ↓
Step 1: 키워드 추출
    ↓
Step 2: decisions.json 쿼리 → Framework/Compiler 결정
    ↓
Step 3: validate_env.py → 환경 검증
    ↓
Step 4: init_project.py 실행 → 프로젝트 생성
    ↓
Step 5: 빌드 검증 루프
    ├─ cmake -B build
    │   ├─ 실패? → error-patterns.json 매칭 → auto-fix → 재시도 (max 3회)
    │   └─ 성공? ↓
    ├─ cmake --build build
    │   ├─ 실패? → error-patterns.json 매칭 → auto-fix → 재시도 (max 3회)
    │   └─ 성공? ↓
    └─ 모두 성공?
            ↓
    Step 6: 사용자에게 완성 프로젝트 제시
            ↓
        (또는 Step 7: 에러 보고 & 수동 조치)
```

---

## 성공 지표

| 항목 | Before | After |
|------|--------|-------|
| 사용자 질문 수 | 6개 | 0-1개 |
| 빌드 시간 (예: 3D 뷰어) | 30분 | 5분 |
| 수동 개입 필요 | 자주 | 거의 없음 |
| 자동화 준비도 | 30% | 90% |
| Claude 구현 시간 | 15분 | 2분 |

---

## Troubleshooting

**If decisions.json 매칭 실패:**
- 키워드 추출 재확인
- 더 유사한 use_case_keywords 찾기
- 기본값으로 wxWidgets 선택 (안전함)

**If error-patterns.json 매칭 실패:**
- 새 에러 패턴 추가 (automation/error-patterns.json)
- 사용자에게 보고 (Step 7)

**If auto-fix 실패:**
- Fallback 체인 실행
- 여전히 실패? 최대 3회 시도 후 사용자 보고

---

**이 프로토콜을 따르면, "Qt로 3D 뷰어 만들어줘"는:**
- 1개 질문 (또는 0개)
- 5분 빌드
- 완성된 실행 파일 제시

되어야 합니다.
