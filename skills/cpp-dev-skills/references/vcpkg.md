# vcpkg 자동화 가이드

**For Claude:** 에러 패턴과 자동화 결정 로직만 포함. 사용자 설치 가이드 없음.

## vcpkg 사용 여부 결정

```
큰 라이브러리 필요? (Qt, OpenCV 등)
│
├─ Yes → 빌드 시간 허용 가능? (보통 5-30분)
│   ├─ Yes → vcpkg 사용 ✅
│   └─ No → 대안: 시스템 패키지, 더 가벼운 프레임워크
│
└─ No (작은 라이브러리) → FetchContent 또는 vcpkg 선택
```

## vcpkg.json 예제

```json
{
  "name": "myproject",
  "version": "1.0.0",
  "dependencies": [
    "wxwidgets",
    "fmt"
  ]
}
```

## 빌드 시간 비교 (자동 선택 참고)

| 패키지 | 첫 빌드 | Binary Cache | 권장 |
|--------|---------|--------------|------|
| **Qt6** | 20-40분 | 2분 | Enterprise GUI만 |
| **wxWidgets** | 5-10분 | 1분 | 일반 GUI ✅ |
| **FLTK** | 2-3분 | 30초 | 최소한 GUI ✅ |
| **Boost** | 10-20분 | 2분 | 필요시만 |
| **OpenCV** | 8-15분 | 2분 | 큰 프로젝트 |
| **fmt** | 1분 | 10초 | 항상 안전 ✅ |

**결론:** Framework 선택 시 automation/decisions.json 쿼리

---

## 공통 에러 & 자동 복구

### 에러 1: Windows MAX_PATH (260 자)

**증상:**
```
error: vcpkg installation path exceeds 260 characters
fatal: could not create work tree
```

**자동 복구 (순서):**
1. Registry 긴 경로 활성화: `powershell -Command "New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name 'LongPathsEnabled' -Value 1 -PropertyType DWORD -Force"`
2. VCPKG_ROOT를 짧은 경로로: `C:\vcpkg`
3. Fallback: Junction point `mklink /J C:\v %VCPKG_ROOT%`

**See:** automation/error-patterns.json → "windows_max_path"

### 에러 2: DLL Not Found

**증상:**
```
The application failed to start because <lib>.dll was not found
```

**자동 복구:**
```python
import shutil, os
vcpkg_bin = os.path.join(os.environ['VCPKG_ROOT'], 'installed', 'x64-windows', 'bin')
[shutil.copy(os.path.join(vcpkg_bin, f), 'build/Debug') for f in os.listdir(vcpkg_bin) if f.endswith('.dll')]
```

**Prevention:** Static linking 또는 CMAKE_INSTALL_RPATH

### 에러 3: Memory Exhaustion (Qt6 빌드)

**증상:**
```
out of memory
cannot allocate memory during Qt build
```

**자동 복구:**
```powershell
$env:VCPKG_MAX_CONCURRENCY=4
vcpkg install qt6-base:x64-windows
```

**권장 값:** CPU cores ÷ 2 (8코어 → 4)

### 에러 4: Package Not Found

**증상:**
```
CMake Error: Could not find a package configuration file provided by "Qt6"
```

**자동 복구:**
```bash
# Windows
cmake -B build -DCMAKE_TOOLCHAIN_FILE=%VCPKG_ROOT%/scripts/buildsystems/vcpkg.cmake

# Linux/macOS
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
```

### 에러 5: Version Conflict

**증상:**
```
version conflict, incompatible versions, constraint not satisfied
```

**자동 복구:**
```bash
vcpkg x-update-baseline
```

### 에러 6: File Locked (Windows)

**증상:**
```
File is locked, vcpkg_installed locked, Permission denied
```

**자동 복구:**
```powershell
taskkill /F /IM vcpkg.exe
```

---

## Qt6/Qt5 vcpkg 지원

**Important:** Qt는 vcpkg로 **가능**하지만 **실용적이지 않을 수 있음**

### Qt6 vcpkg 현황

| 항목 | 상태 |
|------|------|
| **포트 존재** | ✅ qt6-base, qt6-widgets, qt6-protobuf |
| **빌드 시간** | 20-40분 (첫 빌드) |
| **DLL 크기** | 100MB+ |
| **권장 대안** | wxWidgets (5분) |

**참고:** [Qt Protobuf vcpkg 가이드](https://doc.qt.io/qt-6/qtprotobuf-installation-windows-vcpkg.html)

### Qt 사용 결정

```
Qt 필수?
├─ Yes → VCPKG_MAX_CONCURRENCY=4 설정
├─ No → wxWidgets 권장 (빠른 빌드, 안정적)
└─ Maybe → decisions.json 확인 (자동 선택)
```

---

## 빠른 문제 해결 인덱스

| 에러 유형 | Pattern ID | 자동 복구 | 수동 단계 |
|----------|-----------|----------|----------|
| 경로 너무 길음 | windows_max_path | ✅ (registry) | Reboot 필요 |
| DLL 없음 | dll_not_found | ✅ (복사) | 없음 |
| 메모리 부족 | vcpkg_memory_exhaustion | ✅ (병렬 제한) | 없음 |
| Package 못 찾음 | cmake_package_not_found | ✅ (toolchain) | 없음 |
| Version 충돌 | version_conflict | ✅ (baseline) | 없음 |
| 파일 잠김 | vcpkg_file_locked | ✅ (kill) | 없음 |

**전체 에러 데이터베이스:** automation/error-patterns.json

---

## CMake 통합

### 옵션 1: Manifest Mode (권장)

```cmake
cmake -B build -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
cmake --build build
```

### 옵션 2: CMakePresets.json

```json
{
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

```bash
cmake --preset=default -B build
```

---

## 의존성 관리 전략 결정

**See:** automation/decisions.json → "dependency_strategies"

```
의존성 필요?
├─ NO → 의존성 관리 불필요
└─ YES
   ├─ $VCPKG_ROOT 설정됨? → vcpkg 자동
   ├─ $CMAKE_PREFIX_PATH 설정됨? → find_package 자동
   └─ 둘 다 없음? → 자동 선택:
      ├─ FetchContent (작은 라이브러리 <1MB)
      ├─ find_package (이미 설치됨)
      ├─ vcpkg (팀 협업, 버전 관리)
      └─ Conan (고급 요구)
```

---

## Best Practices

**DO:**
- VCPKG_MAX_CONCURRENCY 설정 (큰 패키지)
- Binary caching 활성화 (CI/CD)
- vcpkg.json으로 버전 관리
- CMAKE_TOOLCHAIN_FILE 항상 사용

**DON'T:**
- 긴 경로에 vcpkg 설치 (Windows MAX_PATH)
- 여러 버전의 vcpkg 사용
- Classic mode (Manifest mode 권장)
- Qt 필요 없는데 Qt 선택

---

## 참조

| 항목 | 파일 |
|------|------|
| 에러 자동 복구 | automation/error-patterns.json |
| 자동 결정 로직 | automation/decisions.json |
| 의존성 관리 상세 | references/cmake.md |
| 크로스컴파일 | references/cross-compilation.md |
