# Compilers

C++ 프로젝트 개발을 위한 컴파일러 선택 가이드 및 활용법입니다.

---

## 컴파일러 선택 가이드

### 플랫폼별 기본 컴파일러 (권장)

| 플랫폼 | 기본 컴파일러 | 이유 | 대안 |
|--------|------------|------|------|
| **Windows** | MSVC (Microsoft Visual C++) | Windows API 완벽 지원, Visual Studio 통합, 뛰어난 최적화 | MinGW-w64 (GCC), Clang-cl |
| **Linux** | GCC (g++) | 리눅스 표준, 최적화 우수, 광범위한 라이브러리 지원 | Clang, Intel ICC |
| **macOS** | Apple Clang | Xcode 통합, Apple SDK 필수, 시스템 라이브러리 지원 | GCC (Homebrew) |
| **크로스 플랫폼** | 플랫폼별 표준 + CMake | 각 플랫폼 표준 컴파일러 사용 | 크로스 컴파일러 (권장 아님) |

---

### 컴파일러 기능 비교

#### C++ 표준 지원

| 컴파일러 | C++11 | C++14 | C++17 | C++20 | C++23 | 최신 버전 |
|---------|-------|-------|-------|-------|-------|---------|
| **GCC** | ✅ 4.8+ | ✅ 5.0+ | ✅ 7.0+ | ✅ 10.0+ | 🔶 11.0+ | 14.x |
| **Clang** | ✅ 3.1+ | ✅ 3.4+ | ✅ 5.0+ | ✅ 10.0+ | 🔶 12.0+ | 17.x |
| **MSVC** | ✅ 2010+ | ✅ 2013+ | ✅ 2015+ | ✅ 2019+ | 🔶 2022+ | 17.x |

**범례**: ✅ 완전 지원 | 🔶 부분 지원 | ❌ 미지원

#### 최적화 성능 비교

| 측면 | GCC | Clang | MSVC | 비고 |
|------|-----|-------|------|------|
| **컴파일 속도** | 보통 | 빠름 ⭐ | 느림 | 빌드 타임에 영향 |
| **실행 성능** | 우수 | 우수 | 우수 | 일반적으로 비슷함 |
| **최적화 수준** | 높음 | 높음 | 높음 | `-O3` vs `clang -O3` vs `/O2` |
| **디버그 정보 크기** | 중간 | 작음 ⭐ | 중간 | 바이너리 크기에 영향 |

#### 고급 기능 지원

| 기능 | GCC | Clang | MSVC |
|------|-----|-------|------|
| **AddressSanitizer** | ✅ | ✅ | 🔶 (실험적) |
| **ThreadSanitizer** | ✅ | ✅ | ❌ |
| **UndefinedBehaviorSanitizer** | ✅ | ✅ | ❌ |
| **MemorySanitizer** | ❌ | ✅ | ❌ |
| **Link Time Optimization (LTO)** | ✅ | ✅ | ✅ |
| **Profile Guided Optimization** | ✅ | ✅ | ✅ |

---

## CMake에서 컴파일러 감지 및 선택

### 현재 컴파일러 확인

```cmake
message(STATUS "C++ Compiler: ${CMAKE_CXX_COMPILER_ID}")
message(STATUS "C++ Compiler Version: ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "Compiler Path: ${CMAKE_CXX_COMPILER}")

# 출력 예
# C++ Compiler: GNU (또는 MSVC, Clang, AppleClang)
# C++ Compiler Version: 11.2.0
# Compiler Path: /usr/bin/g++
```

### 컴파일러별 조건부 설정

```cmake
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    # GCC 특화 옵션
    target_compile_options(myapp PRIVATE
        -fno-rtti
        -fno-exceptions
        -fcoroutines
    )
    message(STATUS "Configuring for GCC")

elseif(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    # Clang 특화 옵션
    target_compile_options(myapp PRIVATE
        -fcolor-diagnostics
        -fmodules
    )
    message(STATUS "Configuring for Clang")

elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    # MSVC 특화 옵션
    target_compile_options(myapp PRIVATE
        /permissive-
        /std:c++latest
    )
    message(STATUS "Configuring for MSVC")

elseif(CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")
    # Apple Clang 특화 옵션
    target_compile_options(myapp PRIVATE
        -fapple-pragma-pack
    )
    message(STATUS "Configuring for Apple Clang")

else()
    message(WARNING "Unknown compiler: ${CMAKE_CXX_COMPILER_ID}")
endif()
```

---

## 컴파일러 수동 선택

### 환경 변수 (구성 전)

```bash
# GCC 사용
export CXX=g++ CC=gcc
cmake -B build

# Clang 사용
export CXX=clang++ CC=clang
cmake -B build

# 특정 버전 지정
export CXX=/usr/bin/g++-11 CC=/usr/bin/gcc-11
cmake -B build
```

### CMake 플래그 (구성 시)

```bash
# GCC 지정
cmake -B build -DCMAKE_CXX_COMPILER=g++ -DCMAKE_C_COMPILER=gcc

# Clang 지정
cmake -B build -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_COMPILER=clang

# 절대 경로 지정
cmake -B build -DCMAKE_CXX_COMPILER=/usr/bin/g++-11

# Windows: Clang-cl (MSVC 호환)
cmake -B build -DCMAKE_CXX_COMPILER=clang-cl
```

### Visual Studio 선택 (Windows)

```bash
# Visual Studio 2022 (기본)
cmake -B build -G "Visual Studio 17 2022"

# Visual Studio 2019
cmake -B build -G "Visual Studio 16 2019"

# 특정 아키텍처
cmake -B build -G "Visual Studio 17 2022" -A x64
cmake -B build -G "Visual Studio 17 2022" -A ARM64
```

### Ninja 빌드 시스템 (빠른 빌드)

```bash
# Clang + Ninja (권장)
cmake -B build -G Ninja -DCMAKE_CXX_COMPILER=clang++
cmake --build build

# GCC + Ninja
cmake -B build -G Ninja -DCMAKE_CXX_COMPILER=g++
cmake --build build
```

---

## 컴파일러별 경고 옵션

### GCC 및 Clang 공통

```cmake
target_compile_options(myapp PRIVATE
    # 기본 경고
    -Wall                  # 일반적인 경고
    -Wextra                # 추가 경고
    -Wpedantic             # 엄격한 표준 준수

    # 권장 추가 경고
    -Wconversion           # 타입 변환 경고
    -Wsign-conversion      # 부호 변환 경고
    -Wdouble-promotion     # float → double 승격 경고
    -Wnull-dereference     # NULL 역참조 경고
    -Wnon-virtual-dtor     # 가상 소멸자 부재 경고
    -Woverloaded-virtual   # 오버로드된 가상 함수

    # Clang 추가 옵션
    $<$<CXX_COMPILER_ID:Clang>:-Wmost>
)
```

### MSVC

```cmake
target_compile_options(myapp PRIVATE
    /W4                    # 경고 레벨 4 (최대)
    /permissive-           # 엄격한 표준 준수
    /WX                    # 경고를 오류로 변환 (선택)
)
```

---

## Sanitizer 지원 및 활용

### Sanitizer 비교

| Sanitizer | GCC | Clang | MSVC | 목적 |
|-----------|-----|-------|------|------|
| **AddressSanitizer (ASan)** | ✅ | ✅ | 🔶 | 메모리 오류 감지 (버퍼 오버플로우, use-after-free) |
| **ThreadSanitizer (TSan)** | ✅ | ✅ | ❌ | 데이터 레이스 감지 (멀티스레딩) |
| **UndefinedBehaviorSanitizer (UBSan)** | ✅ | ✅ | ❌ | 미정의 동작 감지 |
| **MemorySanitizer (MSan)** | ❌ | ✅ | ❌ | 초기화되지 않은 메모리 감지 |
| **LeakSanitizer (LSan)** | ✅ (ASan 포함) | ✅ (ASan 포함) | ❌ | 메모리 누수 감지 |

### CMake에서 Sanitizer 활성화

```cmake
# AddressSanitizer (메모리 오류 감지)
option(ENABLE_ASAN "Enable AddressSanitizer" OFF)
if(ENABLE_ASAN AND NOT MSVC)
    target_compile_options(myapp PRIVATE -fsanitize=address -g)
    target_link_options(myapp PRIVATE -fsanitize=address)
endif()

# ThreadSanitizer (데이터 레이스 감지)
option(ENABLE_TSAN "Enable ThreadSanitizer" OFF)
if(ENABLE_TSAN AND NOT MSVC)
    target_compile_options(myapp PRIVATE -fsanitize=thread -g)
    target_link_options(myapp PRIVATE -fsanitize=thread)
endif()

# UndefinedBehaviorSanitizer
option(ENABLE_UBSAN "Enable UndefinedBehaviorSanitizer" OFF)
if(ENABLE_UBSAN AND NOT MSVC)
    target_compile_options(myapp PRIVATE -fsanitize=undefined -g)
    target_link_options(myapp PRIVATE -fsanitize=undefined)
endif()

# 모든 Sanitizer 한번에 (Debug 빌드)
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(myapp PRIVATE
        $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-fsanitize=address,undefined>
    )
    target_link_options(myapp PRIVATE
        $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-fsanitize=address,undefined>
    )
endif()
```

**빌드 및 실행**:
```bash
# Sanitizer 활성화 빌드
cmake -B build -DENABLE_ASAN=ON
cmake --build build

# 실행 (오류 발견 시 리포트)
./build/myapp
```

---

## 크로스 컴파일

### Linux → Windows (MinGW)

```bash
# MinGW-w64 도구 설정 파일 (toolchain.cmake)
cat > toolchain.cmake << EOF
set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR x86_64)

set(CMAKE_CXX_COMPILER x86_64-w64-mingw32-g++)
set(CMAKE_C_COMPILER x86_64-w64-mingw32-gcc)

set(CMAKE_FIND_ROOT_PATH /usr/x86_64-w64-mingw32)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
EOF

# CMake 구성
cmake -B build -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake
```

### Windows → Linux (gcc)

```bash
# 도구 설정 파일 생성 후 동일하게 적용
cmake -B build -DCMAKE_TOOLCHAIN_FILE=toolchain.cmake
```

### Dockerfile를 이용한 크로스 플랫폼 빌드

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    cmake \
    g++-11 \
    clang-14 \
    build-essential

WORKDIR /app
COPY . .

RUN cmake -B build -DCMAKE_CXX_COMPILER=g++-11
RUN cmake --build build
```

---

## 컴파일러 선택 의사결정 플로우

```
어떤 플랫폼에서 개발하는가?

├─ Windows
│  └─ MSVC (Visual Studio) 권장 ⭐
│     또는 Clang-cl, MinGW-w64
│
├─ Linux
│  └─ GCC 권장 ⭐ (리눅스 표준)
│     또는 Clang
│
├─ macOS
│  └─ Apple Clang 권장 ⭐ (필수)
│     또는 GCC (Homebrew)
│
└─ 크로스 플랫폼 개발?
   └─ 각 플랫폼의 표준 컴파일러 사용
      + CMake generator expressions로 분기 처리
```

---

## GCC

### 기본 사용법



```bash
# Compile single file
g++ -std=c++17 -O2 program.cpp -o program

# Multiple files
g++ -std=c++17 -O2 main.cpp util.cpp -o program

# With warnings
g++ -Wall -Wextra -Wpedantic -std=c++17 program.cpp

# Generate dependency files
g++ -MM program.cpp  # Shows header dependencies

# Position independent code (for shared lib)
g++ -fPIC -shared lib.cpp -o lib.so
```

## Clang

```bash
# Similar to GCC
clang++ -std=c++17 -O2 program.cpp -o program

# Address Sanitizer (memory safety)
clang++ -fsanitize=address -g program.cpp

# Thread Sanitizer (data races)
clang++ -fsanitize=thread -g program.cpp

# UndefinedBehavior Sanitizer
clang++ -fsanitize=undefined -g program.cpp
```

## MSVC (Windows)

```cmd
REM Compile
cl /std:c++latest /O2 program.cpp

REM Create static library
lib object.obj /OUT:library.lib

REM Create DLL
cl /LD /O2 library.cpp
```
