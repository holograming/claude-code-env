---
name: cpp-dev-skills
description: |
  C++ 프로젝트 개발을 위한 종합 스킬. 사용 시점:
  (1) C++ 프로젝트 생성/초기화 및 구조 설계
  (2) CMake 빌드 시스템 설정
  (3) 컴파일러 옵션 설정 (GCC/Clang/MSVC)
  (4) 코드 품질 도구 설정 (clang-tidy, clang-format)
  (5) 디버깅 (GDB)
  (6) 테스팅 (Google Test)
  (7) 메모리 분석 (Valgrind, Sanitizers)
  (8) C++ 디자인 패턴 적용
  (9) Git 버전 관리 워크플로우
---

# C++ Development Skills

## Overview

C++ 프로젝트 개발에 필요한 빌드 시스템, 컴파일러, 디버깅, 테스팅, 코드 품질 도구에 대한 종합 가이드. Modern C++ (C++17 이상) 및 Modern CMake (3.15+) 베스트 프랙티스를 중심으로 구성.

## Quick Start: 프로젝트 생성 워크플로우

### 의사결정 플로우

**Step 1: 프로젝트 목적 결정**
```
무엇을 만드는가?
├─ 실행 가능한 프로그램
│  ├─ 명령줄 도구/서버? → CLI Application ✅
│  └─ 그래픽 사용자 인터페이스? → GUI Application ✅
└─ 코드를 배포/공유?
   ├─ 다른 프로젝트에 링크? → Library (Static/Shared) ✅
   └─ 헤더만으로 충분? → Header-Only Library ✅
```

**Step 2: 플랫폼 및 컴파일러 선택**
```
어떤 플랫폼에서 개발하는가?
├─ Windows → MSVC (Visual Studio) 권장 ⭐
├─ Linux → GCC 권장 ⭐
├─ macOS → Apple Clang (필수) ⭐
└─ 크로스 플랫폼 → CMake generator expressions 사용
```

**Step 3: 프로젝트 복잡도 판단**
```
타겟 수와 의존성을 기준으로:
├─ 1-2개 타겟, 의존성 ≤ 2개
│  → Level 1: 단일 CMakeLists.txt (간단함) ✅
├─ 2-3개 타겟, 의존성 2-3개
│  → Level 2: 서브디렉토리별 CMakeLists.txt ✅
└─ 3개+ 타겟, 의존성 3개+
   → Level 3: cmake/ 폴더로 모듈화 ✅
```

n**Step 4: CMake, 컴파일러, 의존성 자동 감지**

자동 감지 프로세스 (환경변수 우선):
```
1. 컴파일러 감지 (CXX 환경변수 확인)
   ├─ 설정됨 → 자동 사용 ✅
   └─ 미설정 → 플랫폼별 기본값 제시

2. CMake 확인 (설치 여부 및 버전)
   ├─ 설치됨 (3.15+) → 자동 사용 ✅
   └─ < 3.15 또는 미설치 → 사용자 확인

3. 의존성 관리 전략 (외부 라이브러리 필요시)
   ├─ VCPKG_ROOT 설정됨 → vcpkg 자동 사용 ✅
   ├─ CMAKE_PREFIX_PATH 설정됨 → find_package 사용 ✅
   └─ 미설정 → 사용자 선택:
      ├─ FetchContent (작은 라이브러리)
      ├─ find_package (시스템 패키지)
      ├─ vcpkg (팀 협업 권장)
      └─ Conan (고급)
```

**중요**: 환경변수 설정 후 다시 물어보지 않음!
- `export CXX=g++` → 자동 사용
- `export VCPKG_ROOT=~/vcpkg` → 자동 사용

자세한 내용: `references/project-setup.md`

### 프로젝트 유형별 빠른 생성

#### CLI Application
```bash
# 자동 생성 (권장)
python scripts/init_project.py myapp --type cli

# 또는 수동으로
mkdir myapp && cd myapp
cmake -B build
cmake --build build
./build/myapp
```

**CMakeLists.txt 예제**:
```cmake
cmake_minimum_required(VERSION 3.15)
project(MyApp VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

add_executable(myapp src/main.cpp src/utils.cpp)
target_include_directories(myapp PRIVATE include)

# 의존성 (선택)
find_package(fmt REQUIRED)
target_link_libraries(myapp PRIVATE fmt::fmt)
```

#### GUI Application (Qt 6)
```bash
# 자동 생성
python scripts/init_project.py myapp --type gui --gui-framework qt6

# CMakeLists.txt (Qt 6 예제)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets)

add_executable(myapp src/main.cpp src/mainwindow.cpp)
target_link_libraries(myapp PRIVATE Qt6::Widgets)
```

#### Static Library
```bash
# 자동 생성
python scripts/init_project.py mylib --type static-lib

# CMakeLists.txt
add_library(mylib STATIC src/lib.cpp)
target_include_directories(mylib
    PUBLIC include
    PRIVATE src
)
add_library(MyLib::mylib ALIAS mylib)
```

#### Shared Library
```bash
# 자동 생성
python scripts/init_project.py mylib --type shared-lib

# CMakeLists.txt
add_library(mylib SHARED src/lib.cpp)
set_target_properties(mylib PROPERTIES
    VERSION 1.0.0
    SOVERSION 1
)
```

#### Header-Only Library
```bash
# 자동 생성
python scripts/init_project.py mylib --type header-only

# CMakeLists.txt
add_library(mylib INTERFACE)
target_include_directories(mylib INTERFACE include)
```

### 표준 프로젝트 구조

**단순 프로젝트** (Level 1-2):
```
project/
├── CMakeLists.txt          # 빌드 설정
├── src/                    # 소스 파일
│   ├── main.cpp
│   └── lib/
├── include/                # Public 헤더
│   └── mylib/
├── tests/                  # 테스트 파일
│   └── test_main.cpp
├── .clang-format           # 코드 포맷팅 설정
├── .clang-tidy             # 린팅 설정
└── .gitignore
```

**복잡한 프로젝트** (Level 3, 3개+ 타겟):
```
project/
├── CMakeLists.txt              # 루트 설정 (간결)
├── cmake/                      # CMake 모듈 (공통 설정 분리)
│   ├── Dependencies.cmake
│   ├── CompilerWarnings.cmake
│   └── Sanitizers.cmake
├── src/
│   ├── app1/
│   │   ├── CMakeLists.txt
│   │   └── main.cpp
│   ├── app2/
│   │   ├── CMakeLists.txt
│   │   └── main.cpp
│   └── common/
│       ├── CMakeLists.txt
│       └── lib.cpp
├── include/
├── tests/
└── .gitignore
```

자세한 내용: `references/project-setup.md`

## Reference 선택 가이드

| 사용자 요청 | 참조 파일 |
|------------|----------|
| **프로젝트 생성, 타입 선택, cmake 구조, 의존성 관리** | **`references/project-setup.md`** ⭐ |
| **컴파일러 선택, 플랫폼별 기본값, auto-detection** | **`references/compilers.md`** ⭐ |
| CMake 설정, 빌드 시스템, 모던 CMake 패턴 | `references/cmake.md` |
| CMake Presets (3.19+), 플랫폼별 빌드 구성 | `references/cmake-presets.md` |
| 디버깅, GDB 사용 | `references/debug.md` |
| 테스트 작성, Google Test | `references/testing.md` |
| 코드 포맷팅, 린팅 | `references/codequality.md` |
| 메모리 분석, Valgrind, Sanitizers | `references/memory.md` |
| 디자인 패턴 | `references/designpatterns.md` |
| Git 워크플로우 | `references/versioncontrols.md` |

**⭐ 새로 추가된 내용**: 프로젝트 생성과 컴파일러 선택 가이드가 대폭 강화되었습니다. 프로젝트를 시작할 때 먼저 `project-setup.md`를 참조하세요!

## Core Principles

### Modern C++ 핵심 원칙

- **RAII** - Resource Acquisition Is Initialization
- **Smart Pointers** - `std::unique_ptr`, `std::shared_ptr` 사용, raw new/delete 금지
- **Move Semantics** - 효율적인 리소스 이동
- **const correctness** - 가능한 모든 곳에 const 사용
- **STL 알고리즘 활용** - 수동 루프보다 알고리즘 우선

### Modern CMake 핵심 원칙

- **Target 기반** - 전역 명령 대신 `target_*` 명령 사용
- **Visibility 명시** - PUBLIC/PRIVATE/INTERFACE 구분
- **Imported Targets** - 변수 대신 `Package::Target` 형식 사용
- **CMake 3.15+** - 최신 기능 활용

## Quick Reference: CMake 기본 템플릿

```cmake
cmake_minimum_required(VERSION 3.15)
project(MyProject VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(myapp src/main.cpp)

target_compile_features(myapp PRIVATE cxx_std_17)

target_compile_options(myapp PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic>
)
```

## Quick Reference: 빌드 명령

```bash
# Configure & Build
cmake -B build
cmake --build build

# With specific config
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release

# Run tests
ctest --test-dir build
```

## 일반적인 작업 흐름

### 새 프로젝트 생성 시

1. 프로젝트 구조 생성
2. `references/cmake.md` 참조하여 CMakeLists.txt 작성
3. `.gitignore` 설정 (`references/versioncontrols.md`)
4. 코드 품질 도구 설정 (`references/codequality.md`)

### 라이브러리 의존성 추가 시

1. `find_package()` 또는 `FetchContent` 사용
2. `target_link_libraries()`로 연결
3. 상세 내용은 `references/cmake.md` 참조

### 디버깅 필요 시

1. Debug 빌드: `cmake -B build -DCMAKE_BUILD_TYPE=Debug`
2. GDB 사용법: `references/debug.md` 참조
3. 메모리 이슈: `references/memory.md` 참조
