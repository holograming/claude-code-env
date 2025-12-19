---
name: cpp-dev-skills
description: |
  Claude를 위한 C++ 자동화 엔진. 사용자 요청 → 프로젝트 자동 생성/구성.
  "로그인 페이지 만들어줘"처럼 C++ 프로젝트 생성이 작동해야 함.
---

# C++ Automation Engine

## 🚨 CRITICAL: 자동화 모드

**이 skill은 사용자 튜토리얼이 아니라 Claude의 자동화 엔진입니다.**
모든 프로젝트 생성 **BEFORE** 먼저 읽으세요: **`automation/automation-guide.md`**

## 자동화 프로토콜 요약

**User Request** → Parse Keywords → Query decisions.json → Validate Environment → Generate Project → Build & Test → Present ✅

## 의사결정 플로우

### Step 1: 프로젝트 타입 결정
```
만들 프로젝트?
├─ CLI Application (명령줄 도구)
├─ GUI Application (윈도우 앱) → Framework 자동 선택 (decisions.json)
├─ Static Library
├─ Shared Library
└─ Header-Only Library
```

### Step 2: 자동 감지 (환경변수 우선)
```
1. 컴파일러: $CXX 확인 → Platform default
2. CMake: 버전 >= 3.15
3. 의존성: $VCPKG_ROOT → $CMAKE_PREFIX_PATH → FetchContent
```

### Step 3: 프로젝트 복잡도
```
├─ Level 1: 1-2 타겟, 의존성 ≤ 2 (단순 CMakeLists.txt)
├─ Level 2: 2-3 타겟, 의존성 2-3
└─ Level 3: 3+ 타겟, 의존성 3+ (cmake/ 모듈)
```

## 자동화 결정 데이터베이스

**자동 framework 선택:**
```json
{
  "3d_viewer": "wxwidgets",  // 빠른 빌드 (5분)
  "enterprise_ui": "qt6",     // 풍부한 기능 (20분)
  "simple_gui": "fltk"        // 최소한 (2분)
}
```

→ `automation/decisions.json` (GUI framework, dependency strategies)
→ `automation/error-patterns.json` (에러 자동 복구)

## 표준 프로젝트 구조

**단순 프로젝트** (Level 1-2):
```
project/
├── CMakeLists.txt          # 빌드 설정
├── src/                    # 소스 파일
│   └── main.cpp
├── include/                # Public 헤더
└── .gitignore
```

**복잡한 프로젝트** (Level 3, 3+ 타겟):
```
project/
├── CMakeLists.txt              # 루트 설정
├── cmake/                      # CMake 모듈
│   ├── Dependencies.cmake
│   └── Sanitizers.cmake
├── src/
│   ├── app1/CMakeLists.txt
│   ├── app2/CMakeLists.txt
│   └── common/CMakeLists.txt
└── tests/CMakeLists.txt
```

## Reference 가이드

| 작업 | 파일 |
|------|------|
| **자동화 프로토콜 (필수)** | **`automation/automation-guide.md`** ⭐ |
| **결정 데이터베이스** | **`automation/decisions.json`** |
| **에러 복구** | **`automation/error-patterns.json`** |
| 프로젝트 생성 & 의존성 | `references/project-setup.md` |
| 컴파일러 & 플랫폼 | `references/compilers.md` |
| vcpkg 패키지 관리 | `references/vcpkg.md` |
| CMake 빌드 시스템 | `references/cmake.md` |
| 크로스컴파일 & 링킹 | `references/cross-compilation.md` |
| Sanitizers & 메모리 분석 | `references/memory.md` |
| 디버깅 (GDB) | `references/debug.md` |
| 테스팅 (Google Test) | `references/testing.md` |
| 코드 품질 도구 | `references/codequality.md` |
| Git 워크플로우 | `references/versioncontrols.md` |

## 에러 처리 체크리스트

빌드 실패 시:
- [ ] 에러 출력 캡처
- [ ] `automation/error-patterns.json`에서 매칭
- [ ] 자동 수정 명령 실행 (최대 3회)
- [ ] 실패하면 fallback 적용
- [ ] 여전히 실패하면 사용자에게 보고

## 빌드 검증 프로토콜

**절대 불완전한 프로젝트를 사용자에게 제시하지 마세요:**
1. 모든 파일 생성 (CMakeLists.txt, source, vcpkg.json)
2. `cmake -B build` 실행
3. CMake 실패 → 자동 수정 → 재시도
4. `cmake --build build` 실행
5. Build 실패 → 자동 수정 → 재시도
6. **SUCCESS ONLY**: `./build/<project>` 실행 확인 후 사용자에게 제시

## 최소 질문 전략

사용자에게 묻기 **ONLY IF**:
- Framework 선택 모호 (Qt vs wxWidgets 둘 다 유효)
- Custom 요구사항 불명확

**절대 묻지 말 것:**
- 컴파일러 (자동 감지)
- vcpkg vs FetchContent (자동 결정)
- 빌드 타입 (자동: Debug/Release)
- CMake 버전 (검증, 질문 안 함)

**제한:** 세션당 최대 1-2개 질문
