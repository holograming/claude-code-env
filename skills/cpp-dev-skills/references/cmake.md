# CMake Build System

Modern CMake (3.15+) 베스트 프랙티스 가이드.

## Basic Template

```cmake
cmake_minimum_required(VERSION 3.15)
project(MyProject VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(myapp src/main.cpp src/utils.cpp)

target_compile_features(myapp PRIVATE cxx_std_17)
target_include_directories(myapp PRIVATE include)

target_compile_options(myapp PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic>
)
```

## Build Commands

```bash
# Configure (out-of-source build)
cmake -B build

# Build
cmake --build build

# Release build
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release

# Install
cmake --install build --prefix /usr/local

# Run tests
ctest --test-dir build
```

## Library Creation

### Static/Shared Library

```cmake
add_library(mylib STATIC  # or SHARED
    src/mylib.cpp
    src/internal.cpp
)

add_library(MyLib::mylib ALIAS mylib)

target_include_directories(mylib
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_features(mylib PUBLIC cxx_std_17)
```

### Header-Only Library

```cmake
add_library(myheaderlib INTERFACE)
add_library(MyLib::header ALIAS myheaderlib)

target_include_directories(myheaderlib INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

target_compile_features(myheaderlib INTERFACE cxx_std_17)
```

## Dependencies

### find_package (설치된 패키지)

```cmake
find_package(OpenSSL REQUIRED)
target_link_libraries(myapp PRIVATE OpenSSL::SSL OpenSSL::Crypto)

find_package(Boost 1.70 REQUIRED COMPONENTS system filesystem)
target_link_libraries(myapp PRIVATE Boost::system Boost::filesystem)

# Optional package
find_package(Doxygen)
if(Doxygen_FOUND)
    # ...
endif()
```

### FetchContent (소스에서 빌드)

```cmake
include(FetchContent)

FetchContent_Declare(
    fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG 9.1.0
)

FetchContent_Declare(
    json
    URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz
)

FetchContent_MakeAvailable(fmt json)

target_link_libraries(myapp PRIVATE fmt::fmt nlohmann_json::nlohmann_json)
```

## Visibility Specifiers

| Specifier | 의미 | 사용 시점 |
|-----------|------|----------|
| PUBLIC | 타겟과 소비자 모두 필요 | public API 헤더, C++ 표준 요구사항 |
| PRIVATE | 타겟만 필요 | 내부 구현, 내부 의존성 |
| INTERFACE | 소비자만 필요 | header-only 라이브러리 |

```cmake
target_include_directories(mylib
    PUBLIC include      # 소비자도 필요
    PRIVATE src         # 내부 구현만
)

target_link_libraries(mylib
    PUBLIC Boost::system    # 소비자도 링크 필요
    PRIVATE zlib            # 내부에서만 사용
)
```

## Multi-Target Project

```cmake
cmake_minimum_required(VERSION 3.15)
project(GameEngine)

# Core library
add_library(game_core src/core.cpp)
target_include_directories(game_core PUBLIC include)
target_compile_features(game_core PUBLIC cxx_std_17)

# Engine library (depends on core)
add_library(game_engine src/engine.cpp)
target_link_libraries(game_engine PUBLIC game_core)

# Executable
add_executable(game_app main.cpp)
target_link_libraries(game_app PRIVATE game_engine)

# Tests
enable_testing()
add_executable(test_game tests/test_game.cpp)
target_link_libraries(test_game PRIVATE game_engine)
add_test(NAME GameTests COMMAND test_game)
```

---

## Anti-Patterns (피해야 할 패턴)

### 1. ❌ file(GLOB) 사용

```cmake
# [BAD] 새 파일 추가해도 빌드 시스템이 감지 못함
file(GLOB SOURCES src/*.cpp)
add_library(mylib ${SOURCES})

# [GOOD] 명시적 소스 리스트
add_library(mylib
    src/file1.cpp
    src/file2.cpp
    src/file3.cpp
)
```

**이유**: CMake는 configure 시점에만 GLOB 실행. 파일 추가/삭제 시 재구성 필요.

---

### 2. ❌ Global Commands 사용

```cmake
# [BAD] 모든 타겟에 영향, 추적 어려움
include_directories(${PROJECT_SOURCE_DIR}/include)
add_definitions(-DUSE_FEATURE)
link_directories(/usr/local/lib)
link_libraries(somelib)

# [GOOD] 타겟별 명시적 설정
target_include_directories(mylib PUBLIC include)
target_compile_definitions(mylib PRIVATE USE_FEATURE)
target_link_directories(mylib PRIVATE /usr/local/lib)
target_link_libraries(mylib PRIVATE somelib)
```

**이유**: 전역 명령은 의도치 않은 부작용 발생. 타겟 기반은 의존성 명확.

---

### 3. ❌ CMAKE_CXX_FLAGS 직접 수정

```cmake
# [BAD] 플랫폼 의존적, visibility 추적 불가
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -O3")

# [GOOD] 타겟별 옵션
target_compile_options(mylib PRIVATE -Wall)
target_compile_options(mylib PRIVATE $<$<CONFIG:Release>:-O3>)

# [GOOD] C++ 표준은 compile_features 사용
target_compile_features(mylib PUBLIC cxx_std_17)
```

**이유**: CMAKE_CXX_FLAGS는 모든 타겟에 영향, 플랫폼별 분기 필요.

---

### 4. ❌ Old-style find_package (변수 사용)

```cmake
# [BAD] 변수 기반, include/link 누락 위험
find_package(OpenSSL)
include_directories(${OPENSSL_INCLUDE_DIR})
target_link_libraries(myapp ${OPENSSL_LIBRARIES})

# [GOOD] Imported targets 사용
find_package(OpenSSL REQUIRED)
target_link_libraries(myapp PRIVATE OpenSSL::SSL OpenSSL::Crypto)
```

**이유**: Imported targets는 include dirs, compile flags 자동 전파.

---

### 5. ❌ 낮은 CMake 버전

```cmake
# [BAD] 레거시 동작 활성화됨
cmake_minimum_required(VERSION 2.8)
cmake_minimum_required(VERSION 3.10)

# [GOOD] Modern CMake 기능 사용 가능
cmake_minimum_required(VERSION 3.15)
```

**이유**: 3.15+에서 타겟 기반 명령, generator expressions 등 현대적 기능 지원.

---

## Generator Expressions

조건부 설정에 유용:

```cmake
# 컴파일러별 옵션
target_compile_options(mylib PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4 /WX>
    $<$<CXX_COMPILER_ID:GNU>:-Wall -Wextra -Werror>
    $<$<CXX_COMPILER_ID:Clang>:-Wall -Wextra -Werror>
)

# 빌드 타입별 설정
target_compile_definitions(mylib PRIVATE
    $<$<CONFIG:Debug>:DEBUG_MODE>
    $<$<CONFIG:Release>:NDEBUG>
)

# Build vs Install interface
target_include_directories(mylib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
```

## Troubleshooting

### Package Not Found

```bash
# 검색 경로 확인
cmake -B build -DCMAKE_PREFIX_PATH=/usr/local:/opt/custom

# 디버그 출력
cmake --debug-find -B build
```

### Linker Errors

1. `target_link_libraries()` 누락 확인
2. visibility (PUBLIC/PRIVATE) 확인
3. 링크 순서 확인 (의존성 순서)

## Quick Reference

| 작업 | 명령 |
|------|------|
| 실행파일 생성 | `add_executable(name src.cpp)` |
| 라이브러리 생성 | `add_library(name STATIC/SHARED src.cpp)` |
| 헤더 경로 | `target_include_directories(name PUBLIC/PRIVATE dir)` |
| 링크 | `target_link_libraries(name PRIVATE lib)` |
| 컴파일 옵션 | `target_compile_options(name PRIVATE -Wall)` |
| 전처리기 정의 | `target_compile_definitions(name PRIVATE DEF)` |
| C++ 표준 | `target_compile_features(name PUBLIC cxx_std_17)` |
| 패키지 찾기 | `find_package(Name REQUIRED)` |
| 소스 빌드 | `FetchContent_Declare() + FetchContent_MakeAvailable()` |

---

## 의존성 관리 전략

프로젝트에서 외부 라이브러리를 사용할 때 고려할 수 있는 3가지 주요 전략입니다.

### 전략 1: FetchContent (소스에서 다운로드)

**사용 시점**: 작은 라이브러리, 특정 버전 고정, CI/CD 파이프라인

```cmake
include(FetchContent)

FetchContent_Declare(fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG 9.1.0
)

FetchContent_MakeAvailable(fmt)

add_executable(myapp main.cpp)
target_link_libraries(myapp PRIVATE fmt::fmt)
```

**장점**:
- ✅ 최신 버전 자동 획득
- ✅ 크로스 플랫폼 일관성
- ✅ 버전 고정 가능

**단점**:
- ❌ 빌드 시간 증가
- ❌ 네트워크 의존성

---

### 전략 2: find_package (시스템 설치 참조)

**사용 시점**: 큰 라이브러리 (Qt, Boost), 시스템 라이브러리, 빠른 빌드 원할 때

```cmake
find_package(fmt REQUIRED)
find_package(Boost 1.81 REQUIRED COMPONENTS system filesystem)

add_executable(myapp main.cpp)
target_link_libraries(myapp PRIVATE
    fmt::fmt
    Boost::system
    Boost::filesystem
)
```

**장점**:
- ✅ 빠른 빌드
- ✅ 시스템 패키지 재사용

**단점**:
- ❌ 플랫폼별 설치 필요
- ❌ 버전 불일치 가능

**CMAKE_PREFIX_PATH 사용**:

```bash
# 커스텀 설치 경로에서 검색
cmake -B build -DCMAKE_PREFIX_PATH="/opt/custom;/usr/local"
```

---

### 전략 3: vcpkg 통합

**옵션 A: 기존 설치 참조** (팀 공유, 디스크 절약)

```bash
export VCPKG_ROOT=~/vcpkg
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
```

**옵션 B: 프로젝트별 설치** (격리, 독립성)

```bash
git clone https://github.com/microsoft/vcpkg.git
./vcpkg/bootstrap-vcpkg.sh
cmake -B build -DCMAKE_TOOLCHAIN_FILE=./vcpkg/scripts/buildsystems/vcpkg.cmake
```

**Manifest Mode** (vcpkg.json으로 의존성 선언)

```json
{
    "dependencies": ["fmt", "boost-system"]
}
```

```bash
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
```

---

### 전략 선택 플로우

```
의존성이 있는가?
├─ 없음 → 설정 필요 없음 ✅
└─ 있음 → 의존성의 특성?
    ├─ 매우 작음 (헤더 온리, <100KB)
    │  → FetchContent 권장 ✅
    │
    ├─ 표준 라이브러리 (fmt, boost, openssl)
    │  → vcpkg 또는 Conan 권장 ✅
    │
    ├─ 큰 라이브러리 (Qt, LLVM)
    │  ├─ 빌드 시간 중요?
    │  │  ├─ YES → find_package (기존 설치) ✅
    │  │  └─ NO → FetchContent 또는 vcpkg ✅
    │
    └─ 정확한 버전 제어 필요?
       ├─ YES → vcpkg manifest 또는 Conan ✅
       └─ NO → find_package (기존 설치) ✅
```

---

## 프로젝트 초기화 가이드

### 단계 1: 프로젝트 구조 결정

간단한 프로젝트 vs 복잡한 멀티타겟 프로젝트 → `references/project-setup.md` 참조

### 단계 2: 자동 또는 수동 생성

```bash
# 자동 생성 (권장)
python scripts/init_project.py myproject --type cli

# 또는 수동
mkdir myproject && cd myproject
```

### 단계 3: 컴파일러 및 플랫폼 설정

```bash
# 플랫폼별 기본값 확인
python scripts/detect_tools.py

# 수동 설정
cmake -B build -DCMAKE_CXX_COMPILER=g++
```

### 단계 4: 의존성 관리 전략 선택

위의 "의존성 관리 전략" 섹션 참조

### 단계 5: 빌드 및 테스트

```bash
cmake -B build
cmake --build build
ctest --test-dir build
```

---

## CMake Presets (CMake 3.19+)

표준화된 빌드 구성을 JSON으로 정의:

```bash
# Preset 목록 확인
cmake --list-presets

# Preset으로 구성
cmake --preset=debug

# 빌드
cmake --build --preset=debug

# 테스트
ctest --preset=debug
```

자세한 내용: `references/cmake-presets.md` 참조

---

## 복잡한 프로젝트: cmake/ 폴더 활용

타겟이 3개 이상이고 의존성이 많으면 cmake/ 폴더로 모듈화:

```
project/
├── CMakeLists.txt          # 간결한 루트 설정
├── cmake/                  # 공통 설정 분리
│   ├── Dependencies.cmake  # 의존성 관리
│   ├── CompilerWarnings.cmake
│   └── Sanitizers.cmake
├── src/
│   ├── app1/CMakeLists.txt
│   ├── app2/CMakeLists.txt
│   └── lib/CMakeLists.txt
└── tests/CMakeLists.txt
```

**루트 CMakeLists.txt** (간결함):

```cmake
cmake_minimum_required(VERSION 3.15)
project(MyProject)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

include(Dependencies)
include(CompilerWarnings)

add_subdirectory(src)
add_subdirectory(tests)
```

자세한 내용: `references/project-setup.md` → "cmake/ 폴더 사용 판단 기준" 참조

---

## CMake & vcpkg 자동 감지 (Environment Variable 우선)

프로젝트 초기화 시 CMake와 vcpkg를 자동으로 감지하고 선택하는 전략입니다.

### CMake 자동 감지 프로세스

```
우선순위 순서:
1. CMake 설치 확인
   - 설치됨 (버전 3.15+) → 자동 사용
   - < 3.15 → 최신 버전 다운로드 여부 물어보기
   - 미설치 → 다운로드 필요 여부 물어보기

2. 사용자 선택
   - 설치된 CMake 사용할 것인가?
   - 최신 버전을 다운로드할 것인가?
```

### CMake 환경 확인

**CMake 버전 및 경로 확인 (bash)**:
```bash
echo "=== CMake Environment ==="

if command -v cmake &> /dev/null; then
    echo "✓ CMake 설치됨: $(cmake --version | head -1)"
else
    echo "✗ CMake 미설치"
fi

if [ -n "$CMAKE_PREFIX_PATH" ]; then
    echo "✓ CMAKE_PREFIX_PATH: $CMAKE_PREFIX_PATH"
fi
```

### vcpkg 자동 감지 프로세스

```
외부 라이브러리 필요 여부?
 |
 ├─ 필요 없음 (단순 프로그램) → vcpkg 불필요
 |
 └─ 필요함 (외부 라이브러리)
    |
    ├─ VCPKG_ROOT 환경변수 확인
    │  ├─ 설정됨 → 자동 사용 (물어보지 않음)
    │  └─ 미설정 → 사용자 선택
    |     ├─ [1] 프로젝트별 설치 (권장, 격리)
    |     ├─ [2] 기존 vcpkg 사용 (경로 입력)
    |     ├─ [3] 수동 설정
    |     └─ [4] 다른 도구 (Conan)
    |
    └─ 선택한 방식으로 CMakeLists.txt 자동 생성
```

### vcpkg 환경 확인

**VCPKG_ROOT 확인 (bash)**:
```bash
echo "=== vcpkg Environment ==="

if [ -n "$VCPKG_ROOT" ]; then
    echo "✓ VCPKG_ROOT: $VCPKG_ROOT"
    if [ -f "$VCPKG_ROOT/vcpkg" ]; then
        echo "  상태: 유효한 설치"
    fi
else
    echo "✗ VCPKG_ROOT: 설정 안됨"
fi

if [ -n "$CMAKE_TOOLCHAIN_FILE" ]; then
    echo "✓ CMAKE_TOOLCHAIN_FILE: $CMAKE_TOOLCHAIN_FILE"
fi
```

### CMake 초기화 검증

CMakeLists.txt에서 자동 감지:

```cmake
message(STATUS "=== CMake & Dependencies Setup ===")

# CMake 버전 확인
if(${CMAKE_VERSION} VERSION_LESS "3.15")
    message(FATAL_ERROR "CMake 3.15+ required")
endif()

# vcpkg 감지
if(DEFINED CMAKE_TOOLCHAIN_FILE)
    message(STATUS "✓ Using toolchain: ${CMAKE_TOOLCHAIN_FILE}")
    if(CMAKE_TOOLCHAIN_FILE MATCHES "vcpkg")
        message(STATUS "  Dependency manager: vcpkg")
    endif()
endif()

# CMAKE_PREFIX_PATH 확인
if(DEFINED CMAKE_PREFIX_PATH)
    message(STATUS "✓ Package search paths configured")
endif()
```

### vcpkg 설정 옵션

**옵션 1: 프로젝트별 설치 (권장)**:
```bash
git clone https://github.com/microsoft/vcpkg.git
./vcpkg/bootstrap-vcpkg.sh
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$PWD/vcpkg/scripts/buildsystems/vcpkg.cmake
```

**옵션 2: 기존 vcpkg 사용**:
```bash
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
```

**옵션 3: find_package + CMAKE_PREFIX_PATH**:
```bash
cmake -B build -DCMAKE_PREFIX_PATH=/usr/local:/opt/custom
```

### CMake 명령 요약

```bash
# 기본 구성
cmake -B build

# vcpkg 사용
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake

# 커스텀 패키지 경로
cmake -B build -DCMAKE_PREFIX_PATH=/usr/local

# 컴파일러 명시
cmake -B build -DCMAKE_CXX_COMPILER=g++

# 모두 함께
cmake -B build \
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake \
  -DCMAKE_PREFIX_PATH=/usr/local \
  -DCMAKE_CXX_COMPILER=g++
```

