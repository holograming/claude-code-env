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
