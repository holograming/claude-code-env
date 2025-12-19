# C++ Project Setup & Dependency Management

**For Claude Automation:** 프로젝트 생성 전 의존성 관리 전략 결정 로직만 포함. 사용자 튜토리얼 제거.

## 환경 변수 우선순위

```
의존성 필요?
├─ NO → 의존성 설정 불필요 ✓
└─ YES
   ├─ VCPKG_ROOT 환경변수 설정됨?
   │  └─ YES → vcpkg 자동 사용 ✓
   │     cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
   │
   ├─ CMAKE_PREFIX_PATH 설정됨?
   │  └─ YES → find_package() 자동 사용 ✓
   │     cmake -B build
   │
   ├─ CXX 컴파일러 지정됨?
   │  └─ YES → 자동 사용 ✓
   │     cmake -B build -DCMAKE_CXX_COMPILER=$CXX
   │
   └─ 모두 없음?
      └─ 플랫폼별 기본값 사용:
         Windows: MSVC
         Linux: GCC
         macOS: AppleClang
```

---

## 프로젝트 유형별 CMakeLists.txt 구조

### Level 1: 단순 (1-2 타겟, 의존성 ≤2)
```
project/
├── CMakeLists.txt (50-100줄)
├── src/main.cpp
└── include/mylib.h
```

### Level 2: 중간 (2-3 타겟, 의존성 2-3)
```
project/
├── CMakeLists.txt
├── src/CMakeLists.txt
└── tests/CMakeLists.txt
```

### Level 3: 복잡 (3+ 타겟, 의존성 3+)
```
project/
├── CMakeLists.txt
├── cmake/
│   ├── Dependencies.cmake
│   ├── CompilerWarnings.cmake
│   └── Sanitizers.cmake
├── src/
│   ├── CMakeLists.txt
│   ├── app1/
│   └── app2/
└── tests/CMakeLists.txt
```

---

## 의존성 관리 전략 결정

| 전략 | 라이브러리 크기 | 빌드 시간 | 사용 환경 |
|------|----------|--------|---------|
| **FetchContent** | < 1MB | 증가 | 프로토타입, 최신 버전 필요 |
| **find_package** | 모두 가능 | 빠름 | 시스템 설치됨, 빠른 빌드 중요 |
| **vcpkg** (권장) | 모두 가능 | 느림 | 팀 협업, 버전 제어 중요 |
| **Conan** | 모두 가능 | 느림 | 복잡한 빌드, 고급 |

---

## 빌드 명령 (환경변수별)

```bash
# 기본 (컴파일러 자동 감지)
cmake -B build && cmake --build build

# vcpkg 사용
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
cmake --build build

# 특정 컴파일러
cmake -B build -DCMAKE_CXX_COMPILER=g++
cmake --build build

# 커스텀 패키지 경로 + vcpkg
cmake -B build \
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake \
  -DCMAKE_PREFIX_PATH=/usr/local
cmake --build build
```

---

## CMake Presets (환경 공유)

```json
{
  "version": 3,
  "configurePresets": [
    {
      "name": "default",
      "cacheVariables": {
        "CMAKE_TOOLCHAIN_FILE": "$env{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake",
        "CMAKE_CXX_COMPILER": "$env{CXX}",
        "CMAKE_PREFIX_PATH": "/usr/local"
      }
    }
  ]
}
```

```bash
cmake --preset=default -B build
cmake --build build
```

---

## 컴파일러 자동 감지 순서

| 플랫폼 | 우선순위 |
|--------|---------|
| Windows | 1. MSVC 2. MinGW-w64 3. Clang-cl |
| Linux | 1. GCC 2. Clang |
| macOS | 1. AppleClang 2. GCC (Homebrew) |

설정: `export CXX=<compiler>` 또는 `decisions.json` 참조

---

## 참조

| 항목 | 파일 |
|------|------|
| 자동 결정 로직 | `automation/decisions.json` |
| 에러 복구 | `automation/error-patterns.json` |
| CMake 상세 가이드 | `references/cmake.md` |
| vcpkg 관리 | `references/vcpkg.md` |
| 컴파일러 선택 | `references/compilers.md` |

