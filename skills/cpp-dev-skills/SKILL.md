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

1. **요구사항 분석** → 필요한 라이브러리/기능 파악
2. **프로젝트 구조 생성** → 표준 디렉토리 구조
3. **CMake 설정** → Modern CMake 패턴 적용
4. **빌드 및 테스트** → 컴파일러/테스트 설정

### 표준 프로젝트 구조

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

## Reference 선택 가이드

| 사용자 요청 | 참조 파일 |
|------------|----------|
| CMake 설정, 빌드 시스템 | `references/cmake.md` |
| 컴파일러 옵션, 플래그 | `references/compilers.md` |
| 디버깅, GDB 사용 | `references/debug.md` |
| 테스트 작성, Google Test | `references/testing.md` |
| 코드 포맷팅, 린팅 | `references/codequality.md` |
| 메모리 분석, Valgrind | `references/memory.md` |
| 디자인 패턴 | `references/designpatterns.md` |
| Git 워크플로우 | `references/versioncontrols.md` |

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
