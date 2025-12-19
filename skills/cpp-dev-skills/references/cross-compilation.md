# 크로스 컴파일 가이드

**For Claude:** 다양한 플랫폼에 대한 자동화된 크로스 컴파일 결정 가이드.

## 크로스컴파일 시나리오

### Windows → Linux

**필요한 경우:**
- Windows에서 개발, Linux 서버에 배포
- CI/CD에서 Linux 바이너리 생성

**권장 방법:**

**1. WSL2 (Windows Subsystem for Linux) - 권장**
```bash
# WSL2 내에서 (Linux 환경)
export VCPKG_ROOT=/mnt/c/vcpkg
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
cmake --build build
```

**2. Docker (CI/CD)**
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y cmake git build-essential
WORKDIR /project
COPY . .
RUN cmake -B build && cmake --build build
```

**3. MinGW (제한적)**
```bash
# Windows에서 Linux 바이너리 직접 빌드 (매우 제한적)
# 권장하지 않음 - WSL2 사용
```

### Linux → Windows

**필요한 경우:**
- Linux CI/CD에서 Windows 바이너리 생성
- MinGW 크로스컴파일 사용

**방법:**
```bash
# Linux 환경
sudo apt install mingw-w64

# vcpkg triplet 설정
export VCPKG_DEFAULT_TRIPLET=x64-mingw-static

cmake -B build \
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake \
  -DVCPKG_TARGET_TRIPLET=x64-mingw-static \
  -DCMAKE_C_COMPILER=x86_64-w64-mingw32-gcc \
  -DCMAKE_CXX_COMPILER=x86_64-w64-mingw32-g++

cmake --build build
```

---

## Static vs Dynamic Linking 결정

### 결정 트리

```
배포 대상 환경 알려짐?
├─ YES (기업 내부, 서버, 컨테이너)
│   └─ 시스템 라이브러리 통일?
│       ├─ YES → Dynamic linking (공유 라이브러리)
│       └─ NO → Static linking (자체 포함)
│
└─ NO (다양한 환경)
    ├─ 단일 EXE 파일 배포? → Static linking
    ├─ 크기 최소화? → Dynamic linking
    └─ 플러그인 지원? → Dynamic linking
```

### Static Linking (자체 포함)

**메리트:**
- 단일 EXE 파일 (DLL 걱정 없음)
- 배포 간단

**단점:**
- 파일 크기 증가 (수 MB)
- GPL/LGPL 라이선스 고려 필요

**vcpkg 설정:**
```bash
export VCPKG_DEFAULT_TRIPLET=x64-windows-static
# 또는
export VCPKG_DEFAULT_TRIPLET=x64-linux-static
```

### Dynamic Linking (외부 DLL)

**메리트:**
- 파일 크기 작음
- 라이브러리 공유 (메모리 절약)

**단점:**
- DLL 배포 필요 (Windows)
- Runtime 의존성 관리 필요

**vcpkg 설정:**
```bash
export VCPKG_DEFAULT_TRIPLET=x64-windows
export VCPKG_DEFAULT_TRIPLET=x64-linux
```

**DLL 배포 (CMake):**
```cmake
if(MSVC)
    add_custom_command(TARGET myapp POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_RUNTIME_DLLS:myapp>
            $<TARGET_FILE_DIR:myapp>
        COMMAND_EXPAND_LISTS
    )
endif()
```

---

## vcpkg Triplet 선택

### 공통 Triplet

| Triplet | 플랫폼 | 링킹 | 용도 |
|---------|--------|------|------|
| `x64-windows` | Windows | Dynamic | ⭐ 기본 |
| `x64-windows-static` | Windows | Static | EXE 배포 |
| `x64-windows-static-md` | Windows | Static CRT | MSVC |
| `x64-linux` | Linux | Dynamic | ⭐ 기본 |
| `x64-linux-static` | Linux | Static | 임베디드 |
| `x64-osx` | macOS | Dynamic | ⭐ 기본 |
| `arm64-linux` | ARM64 | Dynamic | Raspberry Pi |
| `armv6-linux` | ARMv6 | Dynamic | Raspberry Pi (older) |
| `x64-mingw-static` | MinGW | Static | Windows 크로스컴파일 |

**자동 선택 로직:**
```python
triplet_decision = {
    ("Windows", "static"): "x64-windows-static",
    ("Windows", "dynamic"): "x64-windows",
    ("Linux", "static"): "x64-linux-static",
    ("Linux", "dynamic"): "x64-linux",
    ("macOS", "dynamic"): "x64-osx",
    ("Linux ARM64", "dynamic"): "arm64-linux",
}
```

### 커스텀 Triplet 생성

**File:** `triplets/x64-windows-static-md.cmake`

```cmake
set(VCPKG_TARGET_ARCHITECTURE x64)
set(VCPKG_CRT_LINKAGE dynamic)      # MSVC runtime 동적
set(VCPKG_LIBRARY_LINKAGE static)   # 라이브러리는 정적
set(VCPKG_BUILD_TYPE Release)
```

---

## ABI (Application Binary Interface) 호환성

### 호환 조건

```
ABI 호환 = True if:
✅ 같은 컴파일러 버전 (g++ 11.0 vs g++ 11.1 OK, g++ 11 vs g++ 12 주의)
✅ 같은 C++ 표준 (C++17)
✅ 같은 CRT (libstdc++ 또는 libc++)
✅ 같은 링킹 방식 (둘 다 dynamic 또는 static)

❌ 호환성 깨짐:
❌ 다른 컴파일러 (gcc vs clang)
❌ 다른 C++ 표준 라이브러리 (libstdc++ vs libc++)
❌ 다른 MSVC 버전 (VS 2019 vs VS 2022)
```

### 불일치 해결

```
Binary A (libstdc++ static) + Binary B (libstdc++ dynamic) = ❌ 충돌

해결책:
1. 같은 설정으로 재빌드
2. 소스 코드에서 함께 컴파일
3. Symbol versioning 사용 (고급)
```

---

## DLL Hell (Windows 전용) 해결

### 문제

```
myapp.exe 실행 → qt6core.dll 찾음
→ 시스템 PATH에 여러 qt6core.dll 존재
→ 잘못된 버전 로드 → 크래시
```

### 해결책

**1. 같은 폴더에 DLL 배포 (권장)**
```cmake
# Post-build: DLL 복사
add_custom_command(TARGET myapp POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        $<TARGET_RUNTIME_DLLS:myapp>
        $<TARGET_FILE_DIR:myapp>
    COMMAND_EXPAND_LISTS
)
```

**2. Embedded manifest**
```cmake
set_target_properties(myapp PROPERTIES LINK_FLAGS "/MANIFESTUAC:\"level='asInvoker'\"")
```

**3. Static linking (최고의 해결책)**
```cmake
set(VCPKG_DEFAULT_TRIPLET x64-windows-static)
```

---

## CMAKE_PREFIX_PATH 설정 (크로스컴파일)

### Windows → Linux WSL2

```bash
# WSL2 내
export CMAKE_PREFIX_PATH=/usr/lib/x86_64-linux-gnu/cmake

cmake -B build \
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake \
  -DCMAKE_PREFIX_PATH=/usr/lib/x86_64-linux-gnu/cmake
```

### macOS → iOS (고급)

```bash
# iOS 크로스컴파일 (CMake 도구 필요)
cmake -B build \
  -DCMAKE_TOOLCHAIN_FILE=/path/to/ios.toolchain.cmake \
  -DPLATFORM=OS
```

---

## 자동화 결정 규칙

**For Claude:**

```json
{
  "cross_compilation": {
    "static_linking": {
      "use_when": [
        "single_file_deployment",
        "unknown_target_environment",
        "embedded",
        "license_checking_needed"
      ],
      "vcpkg_triplet_suffix": "-static"
    },
    "dynamic_linking": {
      "use_when": [
        "known_environment",
        "binary_size_critical",
        "plugin_architecture",
        "memory_critical"
      ],
      "vcpkg_triplet_suffix": ""
    },
    "platform_detection": {
      "current_platform": "auto-detect",
      "target_platform": "parse_from_user_request"
    }
  }
}
```

---

## Triplet 결정 흐름

```
Target Platform = ?
├─ Windows x64
│   ├─ Single EXE? → x64-windows-static
│   └─ DLL OK? → x64-windows
│
├─ Linux x64
│   ├─ Embedded? → x64-linux-static
│   └─ Server? → x64-linux
│
├─ Raspberry Pi
│   ├─ Pi 4 (ARM64) → arm64-linux
│   └─ Pi 3/Zero (ARMv6) → armv6-linux
│
└─ macOS
    ├─ Intel → x64-osx
    └─ Apple Silicon → arm64-osx
```

---

## 전형적인 크로스컴파일 명령어

### Windows (Static)
```bash
cmake -B build \
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake \
  -DVCPKG_TARGET_TRIPLET=x64-windows-static
cmake --build build
```

### Linux (Dynamic)
```bash
cmake -B build \
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake \
  -DVCPKG_TARGET_TRIPLET=x64-linux
cmake --build build
```

### Raspberry Pi (ARM)
```bash
cmake -B build \
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake \
  -DVCPKG_TARGET_TRIPLET=arm64-linux
cmake --build build
```

---

## 참조

| 항목 | 파일 |
|------|------|
| 자동화 결정 | automation/decisions.json |
| vcpkg Triplet | vcpkg 공식 문서 |
| CMake Toolchain | references/cmake.md |
| 메모리 & 링커 | references/memory.md |
