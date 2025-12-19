# CMake Presets

CMakePresets.json을 사용한 표준 빌드 구성 (CMake 3.19+).

---

## Presets란?

CMakePresets.json은 빌드 구성을 선언적으로 정의하는 파일입니다.

**장점**:
- 📝 IDE와 명령줄 간 일관된 빌드 설정
- 🚀 빠른 구성 전환
- 🤝 팀 전체 공유 가능
- 🔄 재현 가능한 빌드

---

## 기본 구조

```json
{
  "version": 3,
  "cmakeMinimumRequired": {
    "major": 3,
    "minor": 19,
    "patch": 0
  },
  "configurePresets": [
    {
      "name": "default",
      "description": "Default configuration",
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build/${presetName}",
      "cacheVariables": {
        "CMAKE_CXX_STANDARD": "17",
        "CMAKE_CXX_STANDARD_REQUIRED": "ON",
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
      }
    }
  ],
  "buildPresets": [
    {
      "name": "default",
      "configurePreset": "default",
      "jobs": 4,
      "targets": ["all"]
    }
  ],
  "testPresets": [
    {
      "name": "default",
      "configurePreset": "default",
      "output": {
        "outputOnFailure": true
      }
    }
  ]
}
```

---

## 플랫폼별 Presets

### Windows (MSVC + Visual Studio)

```json
{
  "version": 3,
  "configurePresets": [
    {
      "name": "windows-debug",
      "displayName": "Windows Debug (MSVC)",
      "description": "Visual Studio 2022 with Debug configuration",
      "generator": "Visual Studio 17 2022",
      "architecture": {
        "value": "x64",
        "strategy": "set"
      },
      "binaryDir": "${sourceDir}/build/${presetName}",
      "cacheVariables": {
        "CMAKE_CXX_STANDARD": "17",
        "CMAKE_CXX_FLAGS_DEBUG": "/MDd /Zi /Ob0"
      }
    },
    {
      "name": "windows-release",
      "displayName": "Windows Release (MSVC)",
      "generator": "Visual Studio 17 2022",
      "architecture": {
        "value": "x64",
        "strategy": "set"
      },
      "binaryDir": "${sourceDir}/build/${presetName}",
      "cacheVariables": {
        "CMAKE_CXX_STANDARD": "17",
        "CMAKE_CXX_FLAGS_RELEASE": "/MD /O2 /Oi /GL"
      }
    },
    {
      "name": "windows-ninja-clang",
      "displayName": "Windows Ninja + Clang",
      "description": "Fast builds with Clang compiler",
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build/${presetName}",
      "cacheVariables": {
        "CMAKE_CXX_COMPILER": "clang-cl",
        "CMAKE_C_COMPILER": "clang-cl"
      }
    }
  ],
  "buildPresets": [
    {
      "name": "windows-debug",
      "configurePreset": "windows-debug",
      "configuration": "Debug"
    },
    {
      "name": "windows-release",
      "configurePreset": "windows-release",
      "configuration": "Release"
    }
  ]
}
```

### Linux (GCC/Clang + Unix Makefiles/Ninja)

```json
{
  "version": 3,
  "configurePresets": [
    {
      "name": "linux-gcc-debug",
      "displayName": "Linux GCC Debug",
      "generator": "Unix Makefiles",
      "binaryDir": "${sourceDir}/build/${presetName}",
      "cacheVariables": {
        "CMAKE_CXX_COMPILER": "g++",
        "CMAKE_C_COMPILER": "gcc",
        "CMAKE_CXX_STANDARD": "17",
        "CMAKE_CXX_FLAGS_DEBUG": "-g -O0 -fno-omit-frame-pointer",
        "CMAKE_BUILD_TYPE": "Debug"
      }
    },
    {
      "name": "linux-clang-release",
      "displayName": "Linux Clang Release",
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build/${presetName}",
      "cacheVariables": {
        "CMAKE_CXX_COMPILER": "clang++",
        "CMAKE_C_COMPILER": "clang",
        "CMAKE_CXX_STANDARD": "20",
        "CMAKE_CXX_FLAGS_RELEASE": "-O3 -DNDEBUG",
        "CMAKE_BUILD_TYPE": "Release"
      }
    },
    {
      "name": "linux-asan",
      "displayName": "Linux with AddressSanitizer",
      "inherits": "linux-gcc-debug",
      "cacheVariables": {
        "CMAKE_CXX_FLAGS_DEBUG": "-g -O0 -fsanitize=address,undefined",
        "CMAKE_EXE_LINKER_FLAGS": "-fsanitize=address,undefined"
      }
    }
  ],
  "buildPresets": [
    {
      "name": "linux-gcc-debug",
      "configurePreset": "linux-gcc-debug",
      "jobs": 4
    },
    {
      "name": "linux-clang-release",
      "configurePreset": "linux-clang-release",
      "jobs": 8
    }
  ],
  "testPresets": [
    {
      "name": "linux-gcc-debug",
      "configurePreset": "linux-gcc-debug",
      "output": {
        "outputOnFailure": true
      }
    }
  ]
}
```

### macOS (Clang + Unix Makefiles/Xcode)

```json
{
  "version": 3,
  "configurePresets": [
    {
      "name": "macos-debug",
      "displayName": "macOS Debug (Apple Clang)",
      "generator": "Unix Makefiles",
      "binaryDir": "${sourceDir}/build/${presetName}",
      "cacheVariables": {
        "CMAKE_CXX_STANDARD": "17",
        "CMAKE_BUILD_TYPE": "Debug",
        "CMAKE_OSX_DEPLOYMENT_TARGET": "11.0"
      }
    },
    {
      "name": "macos-xcode",
      "displayName": "macOS Xcode Generator",
      "generator": "Xcode",
      "binaryDir": "${sourceDir}/build/${presetName}",
      "cacheVariables": {
        "CMAKE_CXX_STANDARD": "17"
      }
    },
    {
      "name": "macos-universal",
      "displayName": "macOS Universal Binary (Intel + ARM)",
      "inherits": "macos-debug",
      "cacheVariables": {
        "CMAKE_OSX_ARCHITECTURES": "x86_64;arm64"
      }
    }
  ],
  "buildPresets": [
    {
      "name": "macos-debug",
      "configurePreset": "macos-debug",
      "jobs": 4
    }
  ]
}
```

---

## 빌드 타입별 Presets

### Debug Configuration (개발용)

```json
{
  "name": "debug",
  "displayName": "Debug (Sanitizers enabled)",
  "inherits": ["default"],
  "cacheVariables": {
    "CMAKE_BUILD_TYPE": "Debug",
    "ENABLE_ASAN": "ON",
    "ENABLE_UBSAN": "ON"
  }
}
```

### Release Configuration (배포용)

```json
{
  "name": "release",
  "displayName": "Release (Optimized)",
  "inherits": ["default"],
  "cacheVariables": {
    "CMAKE_BUILD_TYPE": "Release",
    "CMAKE_CXX_FLAGS_RELEASE": "-O3 -DNDEBUG",
    "ENABLE_LTO": "ON"
  }
}
```

### RelWithDebInfo Configuration

```json
{
  "name": "relwithdebinfo",
  "displayName": "Release with Debug Info",
  "inherits": ["default"],
  "cacheVariables": {
    "CMAKE_BUILD_TYPE": "RelWithDebInfo",
    "CMAKE_CXX_FLAGS": "-g -O2"
  }
}
```

---

## Presets 사용법

### Preset 목록 확인

```bash
cmake --list-presets
```

### Preset으로 구성

```bash
# Named preset 사용
cmake --preset=windows-debug

# 또는 커스텀 경로
cmake -B build --preset=linux-gcc-debug
```

### 빌드 (Preset 이용)

```bash
# Preset 이용
cmake --build --preset=windows-debug

# 또는 직접 빌드
cmake --build build --config Debug
```

### 테스트 (Preset 이용)

```bash
ctest --preset=default

# 또는 직접 테스트
ctest --test-dir build --output-on-failure
```

---

## Presets 상속

복잡한 Presets을 간단히 관리:

```json
{
  "version": 3,
  "configurePresets": [
    {
      "name": "base",
      "hidden": true,
      "cacheVariables": {
        "CMAKE_CXX_STANDARD": "17",
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
      }
    },
    {
      "name": "debug",
      "displayName": "Debug Build",
      "inherits": "base",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug"
      }
    },
    {
      "name": "release",
      "displayName": "Release Build",
      "inherits": "base",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Release"
      }
    }
  ]
}
```

---

## 베스트 프랙티스

### 1. 프로젝트별 Default Preset 정의

```json
{
  "version": 3,
  "include": ["CMakeUserPresets.json"],
  "configurePresets": [
    {
      "name": "default",
      "displayName": "Default (Platform-specific)",
      "inherits": ["${hostSystemName}-default"]
    }
  ]
}
```

### 2. CI/CD를 위한 Preset

```json
{
  "name": "ci-linux",
  "displayName": "CI Build (Linux)",
  "generator": "Ninja",
  "binaryDir": "${sourceDir}/build",
  "cacheVariables": {
    "CMAKE_CXX_STANDARD": "17",
    "ENABLE_TESTING": "ON",
    "ENABLE_SANITIZERS": "ON"
  }
}
```

### 3. 경고를 오류로 처리

```json
{
  "name": "strict",
  "displayName": "Strict Build (All warnings as errors)",
  "cacheVariables": {
    "CMAKE_CXX_FLAGS": "-Wall -Wextra -Wpedantic -Werror"
  }
}
```

---

## IDE 통합

### Visual Studio Code

```bash
# CMake Tools 확장 설치 후 자동 감지
# Ctrl+Shift+P → "CMake: Select Configure Preset"
```

### Visual Studio

```bash
# Visual Studio 2022에서 자동 감지
# 프로젝트 열기 → CMakePresets.json 선택
```

### CLion

```bash
# JetBrains CLion에서 자동 감지
# Settings → CMake → CMakePresets.json 경로 설정
```

---

## 완전한 예제 프로젝트

```json
{
  "version": 3,
  "cmakeMinimumRequired": {
    "major": 3,
    "minor": 19,
    "patch": 0
  },
  "configurePresets": [
    {
      "name": "default",
      "hidden": true,
      "generator": "Ninja",
      "binaryDir": "${sourceDir}/build/${presetName}",
      "cacheVariables": {
        "CMAKE_CXX_STANDARD": "17",
        "CMAKE_CXX_STANDARD_REQUIRED": "ON",
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON"
      }
    },
    {
      "name": "debug",
      "displayName": "Debug",
      "inherits": "default",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Debug",
        "ENABLE_ASAN": "ON"
      }
    },
    {
      "name": "release",
      "displayName": "Release",
      "inherits": "default",
      "cacheVariables": {
        "CMAKE_BUILD_TYPE": "Release"
      }
    }
  ],
  "buildPresets": [
    {
      "name": "debug",
      "configurePreset": "debug",
      "jobs": 4
    },
    {
      "name": "release",
      "configurePreset": "release",
      "jobs": 8
    }
  ],
  "testPresets": [
    {
      "name": "debug",
      "configurePreset": "debug",
      "output": {
        "outputOnFailure": true
      }
    }
  ]
}
```

---

## 참고

- [CMake Presets 공식 문서](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html)
- [CMakeUserPresets.json (로컬 오버라이드)](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html#user-presets)
