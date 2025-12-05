---
name: cmake-skill
description: Modern CMake build system configuration for C/C++ projects. Use when working with CMakeLists.txt files, configuring build systems, managing dependencies with find_package or FetchContent, setting compiler flags and target properties, or troubleshooting CMake build issues. Focuses on modern CMake (3.15+) best practices with target-based commands.
license: MIT
---

# CMake Build Configuration

## Overview

Modern CMake (3.15+) is a powerful, language-independent build system for C/C++ projects. This skill provides best practices for intermediate developers who understand CMake basics and want to write clean, maintainable, and portable build configurations.

### Key Modern CMake Principles

**1. Target-Based Approach**: Use "target_*" commands instead of global commands. Each target encapsulates its own compilation and linking requirements.

"""cmake
# [LEGACY] Legacy: Global scope
include_directories(${PROJECT_SOURCE_DIR}/include)
add_library(mylib src/lib.cpp)

# [GOOD] Modern: Target-specific
add_library(mylib src/lib.cpp)
target_include_directories(mylib PUBLIC include)
"""

**2. Visibility Specifiers**: Clearly distinguish between interface requirements (what consumers need) and implementation details.

- "PUBLIC": Part of the target's public interface (consumed by downstream targets)
- "PRIVATE": Implementation detail (not visible to consumers)
- "INTERFACE": Required by consumers but not by the target itself (header-only libraries)

**3. Minimum Required Version**: Always specify "cmake_minimum_required()" to enable modern features and avoid legacy behavior.

**4. Explicit Source Lists**: Avoid "file(GLOB)" for source files-explicitly list sources for reproducible builds.

### When to Use This Skill

This skill helps with:
- Setting up new CMake projects with modern patterns
- Adding and managing library dependencies
- Configuring compiler flags and C++ standards properly
- Troubleshooting common CMake issues and anti-patterns
- Understanding target properties and linking models

---

## Quick Start

### Creating a Simple Executable

"""cmake
cmake_minimum_required(VERSION 3.15)
project(MyApp VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Create executable
add_executable(myapp
    src/main.cpp
    src/utils.cpp
)

# Set compile features
target_compile_features(myapp PRIVATE cxx_std_17)

# Add compiler warnings
target_compile_options(myapp PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic>
)
"""

### Creating a Library

"""cmake
add_library(mylib
    src/mylib.cpp
    src/internal.cpp
)

# Create alias for consistency
add_library(MyLib::mylib ALIAS mylib)

# Public interface
target_include_directories(mylib
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

# Compile features visible to consumers
target_compile_features(mylib PUBLIC cxx_std_17)
"""

### Adding Dependencies

"""cmake
# Find an installed package
find_package(Boost 1.70 REQUIRED COMPONENTS system)
target_link_libraries(myapp PRIVATE Boost::system)

# Or fetch from source
include(FetchContent)
FetchContent_Declare(json
    URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz
)
FetchContent_MakeAvailable(json)
target_link_libraries(myapp PRIVATE nlohmann_json::nlohmann_json)
"""

### Running CMake

"""bash
# Configure (out-of-source build)
cmake -B build

# Build
cmake --build build

# Install
cmake --install build --prefix /usr/local

# Run tests
ctest --test-dir build
"""

---

## Project Setup

### Quick Project Initialization

Use the included "init_project.py" script to generate a modern CMake project structure:

"""bash
python3 scripts/init_project.py my-awesome-app --type minimal
python3 scripts/init_project.py my-library --type library
python3 scripts/init_project.py my-headers --type header-only
python3 scripts/init_project.py my-app --type with-deps
"""

**Project Types**:
- "minimal": Simple executable project
- "library": Shared or static library with proper exports
- "header-only": Interface library pattern (no compiled code)
- "with-deps": Demonstrates find_package and FetchContent usage

The script generates:
- Modern "CMakeLists.txt" with 3.15+ features
- "src/" and "include/" directories
- "tests/" directory with CTest setup
- "README.md" with build instructions
- ".gitignore" for CMake artifacts

### Manual Project Structure

For maximum control, follow this structure:

"""
my-project/
 CMakeLists.txt
 README.md
 src/
    main.cpp
 include/
    mylib.h
 tests/
    CMakeLists.txt
    test_main.cpp
 CMakePresets.json (optional)
"""

**Root CMakeLists.txt Structure**:

"""cmake
cmake_minimum_required(VERSION 3.15)
project(MyProject VERSION 1.0.0 DESCRIPTION "..." LANGUAGES CXX)

# Set C++ standard and features
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add main library/executable
add_library(mylib src/mylib.cpp)
add_executable(myapp src/main.cpp)

# Link targets
target_link_libraries(myapp PRIVATE mylib)

# Enable testing
enable_testing()
add_subdirectory(tests)

# Install rules (optional)
install(TARGETS mylib DESTINATION lib)
install(DIRECTORY include/ DESTINATION include)
"""

---

## Dependencies

### Finding Installed Packages

Use "find_package()" to locate libraries installed on the system:

"""cmake
find_package(OpenSSL REQUIRED)
target_link_libraries(myapp PRIVATE OpenSSL::SSL OpenSSL::Crypto)
"""

**Find Mode vs Config Mode**:

CMake searches for packages in two ways:
- **Module Mode**: Uses FindXXX.cmake modules (for standard packages like Boost, OpenSSL, Python)
- **Config Mode**: Uses XXXConfig.cmake files (for modern packages with CMake support)

Typically, CMake tries Module mode first, then Config mode. For the complete reference on package discovery and custom Find modules, see [finding-packages.md](references/finding-packages.md).

**Common Patterns**:

"""cmake
# Required package (build fails if not found)
find_package(Qt6 REQUIRED COMPONENTS Core Gui)

# Optional package (build succeeds even if not found)
find_package(Doxygen)
if(Doxygen_FOUND)
    add_custom_target(docs ${DOXYGEN_EXECUTABLE} ...)
endif()

# Specific version
find_package(Boost 1.70 REQUIRED)

# With components
find_package(Boost REQUIRED COMPONENTS system filesystem)
"""

### Using FetchContent (Modern Approach)

For dependencies not yet installed, use "FetchContent" to fetch and integrate them at configure time:

"""cmake
include(FetchContent)

FetchContent_Declare(
    fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG 9.1.0
)

FetchContent_MakeAvailable(fmt)

target_link_libraries(myapp PRIVATE fmt::fmt)
"""

**Advantages Over ExternalProject**:
- Simpler syntax
- Better integration with target-based approach
- Automatically makes downloaded targets available
- Supports URL, Git, SVN sources

### Dependency Resolution Order

When using multiple dependencies:

"""cmake
# System packages first
find_package(Boost REQUIRED)
find_package(OpenSSL REQUIRED)

# Then fetch dependencies
include(FetchContent)
FetchContent_Declare(json URL https://...)
FetchContent_MakeAvailable(json)

# Link in dependency order
target_link_libraries(myapp PRIVATE Boost::system OpenSSL::SSL json)
"""

For advanced dependency management patterns and troubleshooting, see [finding-packages.md](references/finding-packages.md).

---

## Build Configuration

### Setting C++ Standard

**Modern approach** using target_compile_features:

"""cmake
target_compile_features(mylib PUBLIC cxx_std_17)
"""

This:
- Works across all compilers (MSVC, Clang, GCC)
- Exposes the requirement to consumers
- Avoids manual "-std=c++17" flags

### Compiler Flags

Use "target_compile_options()" for target-specific flags:

"""cmake
# Platform-specific warnings
target_compile_options(mylib PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4 /WX>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic -Werror>
)

# Optimization flags by build type
target_compile_options(mylib PRIVATE
    $<$<CONFIG:Debug>:-O0 -g>
    $<$<CONFIG:Release>:-O3>
)
"""

### Compiler Definitions

Add preprocessor definitions:

"""cmake
# Global for this target
target_compile_definitions(mylib PRIVATE ENABLE_LOGGING)

# Version from project
target_compile_definitions(mylib PUBLIC MYLIB_VERSION="${PROJECT_VERSION}")

# Configuration-dependent
target_compile_definitions(mylib PRIVATE
    $<$<CONFIG:Debug>:DEBUG_MODE>
)
"""

### Include Directories

Distinguish between build and install interfaces:

"""cmake
target_include_directories(mylib
    PUBLIC
        # Used during build
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        # Used after installation
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)
"""

### Target Properties Deep Dive

For comprehensive coverage of target types, visibility specifiers, advanced linking patterns, and property propagation, see [modern-targets.md](references/modern-targets.md).

---

## Anti-Patterns to Avoid

### [LEGACY] Using file(GLOB) for Source Files

"""cmake
# BAD - doesn't detect new files, unreliable with build systems
file(GLOB SOURCES src/*.cpp)
add_library(mylib ${SOURCES})
"""

**Why**: Build systems don't re-run CMake when you add files. Use explicit lists or subdirectories instead.

**[GOOD] Good alternatives**:

"""cmake
# Explicit list
add_library(mylib
    src/file1.cpp
    src/file2.cpp
    src/file3.cpp
)

# Or use subdirectories with explicit lists
"""

### [LEGACY] Using Global Commands

"""cmake
# BAD - affects all targets in current directory and subdirectories
include_directories(${PROJECT_SOURCE_DIR}/include)
add_definitions(-DUSE_FEATURE)
link_directories(/usr/local/lib)
"""

**[GOOD] Use target-specific commands instead**:

"""cmake
target_include_directories(mylib PUBLIC include)
target_compile_definitions(mylib PRIVATE USE_FEATURE)
target_link_directories(mylib PRIVATE /usr/local/lib)
"""

### [LEGACY] Modifying CMAKE_CXX_FLAGS Directly

"""cmake
# BAD - error-prone, platform-specific, doesn't track visibility
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -O3")
"""

**[GOOD] Use target_compile_options**:

"""cmake
target_compile_options(mylib PRIVATE -Wall)
target_compile_options(mylib PRIVATE $<$<CONFIG:Release>:-O3>)
"""

### [LEGACY] Using Old-Style find_package

"""cmake
# BAD - uses variables instead of imported targets
find_package(OpenSSL)
include_directories(${OPENSSL_INCLUDE_DIR})
target_link_libraries(myapp ${OPENSSL_LIBRARIES})
"""

**[GOOD] Use modern imported targets**:

"""cmake
find_package(OpenSSL REQUIRED)
target_link_libraries(myapp PRIVATE OpenSSL::SSL OpenSSL::Crypto)
"""

### [LEGACY] Old CMake Minimum Version

"""cmake
# BAD - enables legacy behavior
cmake_minimum_required(VERSION 3.10)
"""

**[GOOD] Use 3.15 or newer**:

"""cmake
cmake_minimum_required(VERSION 3.15)
# Enables modern defaults and features
"""

---

## Quick Reference

### Essential CMake Commands

| Command | Purpose | Example |
|---------|---------|---------|
| "add_executable()" | Create executable target | "add_executable(myapp main.cpp)" |
| "add_library()" | Create library target | "add_library(mylib src.cpp)" |
| "target_link_libraries()" | Link dependencies | "target_link_libraries(myapp PRIVATE mylib)" |
| "target_include_directories()" | Add include paths | "target_include_directories(mylib PUBLIC include)" |
| "target_compile_definitions()" | Add preprocessor defines | "target_compile_definitions(mylib PRIVATE DEBUG)" |
| "target_compile_options()" | Add compiler flags | "target_compile_options(mylib PRIVATE -Wall)" |
| "target_compile_features()" | Require C++ standard | "target_compile_features(mylib PUBLIC cxx_std_17)" |
| "find_package()" | Locate dependencies | "find_package(Boost REQUIRED)" |
| "add_subdirectory()" | Include subdir | "add_subdirectory(src)" |
| "add_test()" | Register test | "add_test(NAME test1 COMMAND test_exe)" |

### Task-to-Command Mapping

| Task | Commands |
|------|----------|
| Create new project | "project()", "add_executable/add_library()" |
| Add dependencies | "find_package()" or "FetchContent_*()" |
| Set C++ standard | "target_compile_features(target PUBLIC cxx_std_XX)" |
| Add warnings | "target_compile_options()" with "-Wall", "/W4" |
| Conditional compilation | "target_compile_definitions()" with generator expressions |
| Create library exports | "install(EXPORT ...)" with package config files |
| Build tests | "enable_testing()", "add_test()", "add_subdirectory(tests)" |

---

## Troubleshooting

### Package Not Found

**Symptom**: "find_package(SomeLib)" fails silently or with error.

**Diagnosis**:

"""bash
# Check where CMake searches
cmake --debug-find
"""

**Solutions**:

1. **Set CMAKE_PREFIX_PATH**:
   """bash
   cmake -B build -DCMAKE_PREFIX_PATH=/usr/local:/opt/custom
   """

2. **Set package-specific path**:
   """cmake
   find_package(Boost REQUIRED HINTS /usr/local/boost)
   """

3. **Verify package is installed**:
   """bash
   ls /usr/local/lib/cmake/Boost  # Should exist for config packages
   """

4. **Use FetchContent if not available**:
   """cmake
   include(FetchContent)
   FetchContent_Declare(SomeLib GIT_REPOSITORY ...)
   FetchContent_MakeAvailable(SomeLib)
   """

### Linker Errors

**Symptom**: "undefined reference" or "unresolved external symbol" errors.

**Common causes**:

1. **Missing target_link_libraries()**:
   """cmake
   # Missing this:
   target_link_libraries(myapp PRIVATE mylib)
   """

2. **Wrong visibility specifier**:
   """cmake
   # If mylib depends on Boost, use PUBLIC not PRIVATE:
   target_link_libraries(mylib PUBLIC Boost::system)
   """

3. **Out-of-order linking** (older linkers):
   """cmake
   # Linker may need: app -> mylib -> boost
   # Reverse order can cause undefined references
   """

### Validator Script

Use the included "cmake_validator.py" to check for common issues:

"""bash
python3 scripts/cmake_validator.py CMakeLists.txt
python3 scripts/cmake_validator.py CMakeLists.txt --strict  # Stricter checks
"""

Checks for:
- "file(GLOB)" usage (unreliable)
- Global commands ("include_directories", "link_directories")
- Manual "CMAKE_CXX_FLAGS" modification
- Minimum CMake version < 3.15
- Missing visibility specifiers
- Pattern violations

---

## Next Steps

- For advanced find_package patterns and custom Find modules, see [finding-packages.md](references/finding-packages.md)
- For target types, linking models, and advanced propagation, see [modern-targets.md](references/modern-targets.md)
- Generate a new project: "python3 scripts/init_project.py"
- Validate your CMakeLists.txt: "python3 scripts/cmake_validator.py CMakeLists.txt"
