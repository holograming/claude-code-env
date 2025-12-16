# C++ Project Setup & Dependency Management

프로젝트 생성부터 의존성 관리까지 전체 과정을 다루는 통합 가이드입니다.

## 프로젝트 초기화 전체 흐름

```
프로젝트 생성 시작
    |
    ├─ Step 1: 프로젝트 유형 결정 (CLI/GUI/Library)
    |
    ├─ Step 2: 컴파일러 선택
    |  └─ 자동감지 (CXX 환경변수) → (없으면) 사용자 선택
    |
    ├─ Step 3: 구조 설계 (Level 1/2/3)
    |
    ├─ Step 4: CMake 확인
    |  └─ 자동감지 → (필요시) 설치 여부 확인
    |
    ├─ Step 5: 의존성 관리 전략 결정 (핵심)
    |  ├─ 의존성 필요 여부 판단
    |  ├─ 환경변수 확인 (VCPKG_ROOT, CMAKE_PREFIX_PATH)
    |  └─ (없으면) 전략 선택
    |
    └─ Step 6: 프로젝트 생성 및 구성 완료
```

---

## Step 1: 프로젝트 유형 결정

사용자에게 다음을 물어봅니다:

```
무엇을 만드는가?

[1] CLI Application (명령줄 프로그램)
    └─ main.cpp 1개, 간단한 구조 (Level 1-2)

[2] GUI Application (그래픽 UI)
    └─ Qt/GTK 등 사용, 더 복잡한 구조 (Level 2-3)

[3] Static Library (.a / .lib)
    └─ (Level 1-2)

[4] Shared Library (DLL/SO)
    └─ (Level 1-2)

[5] Header-Only Library
    └─ 헤더만 제공 (Level 1)

[6] Multi-Target Project
    └─ 여러 실행파일 + 라이브러리 (Level 3)
```

---

## Step 2: 컴파일러 자동 감지 및 선택

### 감지 프로세스

```
1. CXX 환경변수 확인
   ├─ 설정됨 → 자동 사용 (물어보지 않음) ✓
   └─ 미설정 → 2단계

2. 플랫폼 감지 및 기본값 제시
   ├─ Windows → MSVC 권장
   ├─ Linux → GCC 권장
   └─ macOS → Apple Clang 권장

3. 설치된 컴파일러 자동 감지
   └─ [1] MSVC  [2] GCC  [3] Clang  [4] 수동입력

4. 사용자 선택
```

### 플랫폼별 기본값

| 플랫폼 | 기본값 | 대안 |
|--------|--------|------|
| Windows | MSVC | MinGW-w64, Clang-cl |
| Linux | GCC | Clang |
| macOS | Apple Clang | GCC (Homebrew) |

자세한 내용: `references/compilers.md` → "컴파일러 자동 감지" 섹션

---

## Step 3: 프로젝트 복잡도 선택

타겟 수와 의존성으로 결정:

### Level 1: 단순 (1-2 타겟, 의존성 ≤2)
```
project/
├── CMakeLists.txt
├── src/main.cpp
└── include/mylib.h
```

### Level 2: 중간 (2-3 타겟, 의존성 2-3)
```
project/
├── CMakeLists.txt
├── src/
│   ├── CMakeLists.txt
│   └── [app/, lib/]
└── tests/CMakeLists.txt
```

### Level 3: 복잡 (3+ 타겟, 의존성 3+)
```
project/
├── CMakeLists.txt
├── cmake/
│   ├── Dependencies.cmake
│   └── [CompilerWarnings.cmake, ...]
├── src/
│   ├── CMakeLists.txt
│   ├── app1/
│   └── app2/
└── tests/CMakeLists.txt
```

자세한 내용: `references/cmake.md` → "Multi-Target Project" 섹션

---

## Step 4: CMake 확인

### 감지 및 검증

```
1. CMake 설치 확인
   ├─ 설치됨 → 버전 확인
   │  ├─ 3.15+ → 사용 ✓
   │  └─ < 3.15 → "최신 버전으로?"
   |     ├─ YES → 다운로드
   |     └─ NO → 경고, 진행
   └─ 미설치 → "CMake 설치?"
      ├─ YES → 자동 다운로드
      └─ NO → 수동 설치 안내
```

### 확인 명령

```bash
cmake --version      # 버전 확인
which cmake          # 경로 확인
cmake -B build       # 동작 확인
```

자세한 내용: `references/cmake.md` → "CMake & vcpkg 자동 감지" 섹션

---

## Step 5: 의존성 관리 전략 (핵심!)

### 5-1. 의존성 필요 여부

```
외부 라이브러리 필요?
├─ NO → 의존성 관리 불필요 ✓
└─ YES → Step 5-2로 진행
```

### 5-2. 환경변수 확인 (우선!)

```
환경변수 설정 확인
├─ VCPKG_ROOT 설정됨
│  └─ vcpkg 자동 사용 ✓
│     cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
│
├─ CMAKE_PREFIX_PATH 설정됨
│  └─ find_package() 자동 사용 ✓
│     cmake -B build
│
└─ 둘 다 없음 → Step 5-3으로 진행
```

### 5-3. 의존성 관리 전략 선택

사용자가 선택할 수 있는 옵션:

#### 옵션 1: FetchContent (소스에서 다운로드)
```
장점:
- 최신 버전 자동 획득
- 크로스 플랫폼 일관성

단점:
- 빌드 시간 증가
- 네트워크 의존

추천: 작은 라이브러리 (< 1MB)

CMakeLists.txt:
include(FetchContent)
FetchContent_Declare(fmt ...)
FetchContent_MakeAvailable(fmt)
target_link_libraries(myapp PRIVATE fmt::fmt)
```

#### 옵션 2: find_package (시스템 설치)
```
장점:
- 빠른 빌드
- 시스템 라이브러리 재사용

단점:
- 사전 설치 필요
- 플랫폼별 설치 방법 다름

추천: 큰 라이브러리 (Qt, Boost)

CMakeLists.txt:
find_package(Qt6 REQUIRED COMPONENTS Core Gui)
target_link_libraries(myapp PRIVATE Qt6::Widgets)

빌드:
cmake -B build -DCMAKE_PREFIX_PATH=/usr/local
```

#### 옵션 3: vcpkg (권장)
```
장점:
- 정확한 버전 제어
- 크로스 플랫폼
- 팀 협업 용이

단점:
- 초기 설정 필요
- 빌드 시간 증가 가능

추천: 팀 프로젝트, 버전 제어 중요

옵션 A: 프로젝트별 설치 (격리 - 권장)
git clone https://github.com/microsoft/vcpkg.git
./vcpkg/bootstrap-vcpkg.sh
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$PWD/vcpkg/scripts/buildsystems/vcpkg.cmake

옵션 B: 기존 vcpkg 사용 (팀 공유)
export VCPKG_ROOT=$HOME/vcpkg
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
```

#### 옵션 4: Conan (고급)
```
추천: 복잡한 빌드 환경, 자동화 중요
```

### 5-4. 전체 결정 플로우

```
의존성 필요?
├─ NO → 의존성 설정 불필요 ✓
└─ YES
   ├─ 환경변수 확인
   │  ├─ VCPKG_ROOT 있음
   │  │  └─ "기존 vcpkg 사용할까?"
   │  │     ├─ YES → vcpkg 자동 사용 ✓
   │  │     └─ NO → Step 5-3
   │  │
   │  ├─ CMAKE_PREFIX_PATH 있음
   │  │  └─ find_package 자동 사용 ✓
   │  │
   │  └─ 없음 → Step 5-3
   │
   └─ 전략 선택 (Step 5-3)
      ├─ [1] FetchContent (작은 라이브러리)
      ├─ [2] find_package (이미 설치됨)
      ├─ [3] vcpkg (팀 협업)
      ├─ [4] Conan (고급)
      └─ [5] 수동 설정
```

자세한 내용: `references/cmake.md` → "의존성 관리 전략" 섹션

---

## Step 6: 자동 프로젝트 생성

### 초기화 스크립트 사용

```bash
python scripts/init_project.py myproject --type cli

# 실행 결과:
# Step 1: Project Type
#   └─ CLI Application selected
#
# Step 2: Compiler Detection
#   ├─ CXX not set
#   ├─ Platform: Linux
#   ├─ Recommended: GCC
#   ├─ Installed: [1] g++  [2] clang++
#   └─ Select (1-2): 1
#   └─ Using: g++
#
# Step 3: Complexity
#   ├─ Target count: 1
#   ├─ Dependencies: 0
#   └─ Level: 1
#
# Step 4: CMake Check
#   └─ CMake 3.23.0 ✓
#
# Step 5: Dependency Management
#   ├─ External libraries needed? (y/n): n
#   └─ No dependency management needed
#
# ✓ Project created: myproject/
# ✓ First build:
#    cmake -B build
#    cmake --build build
```

---

## 첫 빌드 명령

```bash
# 1. 기본 구성 및 빌드
cmake -B build
cmake --build build

# 2. 특정 컴파일러 사용
cmake -B build -DCMAKE_CXX_COMPILER=g++
cmake --build build

# 3. vcpkg 사용
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
cmake --build build

# 4. 커스텀 패키지 경로
cmake -B build -DCMAKE_PREFIX_PATH=/usr/local:/opt/custom
cmake --build build

# 5. 모두 함께
cmake -B build \
  -DCMAKE_CXX_COMPILER=g++ \
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake \
  -DCMAKE_PREFIX_PATH=/usr/local
cmake --build build
```

---

## 팀 협업: 환경 공유

### `.env.setup` (리포지토리에 포함)

```bash
#!/bin/bash
# 팀 공용 환경 설정

# 옵션 A: 팀 공용 vcpkg 사용
export VCPKG_ROOT=$HOME/vcpkg
export CMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake

# 옵션 B: 프로젝트 내 vcpkg 사용
# export CMAKE_TOOLCHAIN_FILE=$PWD/vcpkg/scripts/buildsystems/vcpkg.cmake

# 옵션 C: 시스템 패키지 경로
# export CMAKE_PREFIX_PATH=/usr/local

# 컴파일러 고정 (필요시)
# export CXX=g++ CC=gcc

echo "✓ Team environment configured"
```

### 사용법

```bash
# 초기 한 번
source .env.setup

# 이후 빌드
cmake -B build
cmake --build build
```

### CMake Presets 활용 (권장)

```json
// CMakePresets.json
{
  "version": 3,
  "configurePresets": [
    {
      "name": "default",
      "cacheVariables": {
        "CMAKE_TOOLCHAIN_FILE": "$env{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
      }
    }
  ]
}
```

사용:
```bash
cmake --preset=default -B build
```

---

## 초기화 체크리스트

- [ ] **Step 1**: 프로젝트 유형 선택
- [ ] **Step 2**: 컴파일러 결정 (자동감지 또는 선택)
- [ ] **Step 3**: 복잡도 레벨 선택
- [ ] **Step 4**: CMake 확인 (설치 여부)
- [ ] **Step 5**: 의존성 관리 전략 결정
  - [ ] 의존성 필요 여부 판단
  - [ ] 환경변수 확인
  - [ ] (필요시) 전략 선택
- [ ] **Step 6**: 프로젝트 구조 생성
- [ ] **Test**: 첫 빌드 성공 확인

```bash
cmake -B build && cmake --build build
```

---

## 상세 참고 문서

| 항목 | 참조 |
|------|------|
| 컴파일러 선택 & 감지 | `references/compilers.md` |
| CMake 설정 & 의존성 | `references/cmake.md` |
| CMake Presets | `references/cmake-presets.md` |
| 코드 품질 도구 | `references/codequality.md` |
| 테스트 작성 | `references/testing.md` |
| 디버깅 | `references/debug.md` |
| Git 워크플로우 | `references/versioncontrols.md` |

