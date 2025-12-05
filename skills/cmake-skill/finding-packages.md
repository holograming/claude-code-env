# Finding Packages with CMake

This document provides comprehensive guidance on using `find_package()` to locate and integrate external libraries and programs into your CMake projects.

## Overview

`find_package()` is CMake's primary mechanism for finding system-installed packages, libraries, and programs. Understanding package discovery is critical for managing external dependencies in modern C/C++ projects.

### When to Use find_package vs FetchContent

| Scenario | Recommended | Reason |
|----------|-------------|--------|
| System library (pre-installed) | `find_package()` | Cleaner, respects user's system setup |
| No system installation available | `FetchContent` | Downloads and builds from source |
| Optional dependency | `find_package()` with `REQUIRED` omitted | Use if available, disable features if not |
| Development version needed | `FetchContent` | More control over version |
| Large library (OpenSSL, Boost) | `find_package()` | Usually pre-installed on systems |

---

## find_package Modes

CMake searches for packages using two complementary approaches:

### Module Mode (Find Modules)

**How it works**: CMake looks for `FindXXX.cmake` modules in CMAKE_MODULE_PATH.

```cmake
find_package(Boost 1.70 REQUIRED COMPONENTS system filesystem)
```

CMake searches for `FindBoost.cmake` in:
1. `<CMAKE_MODULE_PATH>`
2. `<CMAKE_PREFIX_PATH>/share/cmake-X.Y/Modules`
3. Default CMake modules directory

**Characteristics**:
- Maintains compatibility with older packages
- Bundled with CMake for standard libraries
- Developed and maintained by CMake community
- Searches CMake's built-in modules by default

### Config Mode (Package Config Files)

**How it works**: CMake looks for `XXXConfig.cmake` or `xxx-config.cmake` files.

```cmake
find_package(nlohmann_json CONFIG REQUIRED)
```

CMake searches in:
1. `<CMAKE_PREFIX_PATH>/(lib|share)/cmake/XXX/`
2. Package-specific paths set by find module
3. System standard paths (`/usr/local`, `/opt`, etc.)

**Characteristics**:
- Modern approach used by active projects
- Provided by the library author
- More reliable and feature-rich
- Configurable by library maintainers

### Automatic Mode (Default)

By default, `find_package()` tries **Module mode first**, then **Config mode**:

```cmake
find_package(Boost)  # Try FindBoost.cmake, then BoostConfig.cmake
```

### Explicit Mode Selection

Force a specific search mode:

```cmake
find_package(Boost MODULE)      # Module mode only
find_package(Boost CONFIG)      # Config mode only (modern packages)
```

---

## Common Find Modules

### FindBoost

Boost is one of the most commonly used C++ libraries. Finding Boost can be complex due to:
- Multiple component libraries
- Versioning issues
- Different build configurations (debug/release, static/shared)

**Basic usage**:

```cmake
find_package(Boost REQUIRED COMPONENTS system filesystem)
target_link_libraries(myapp PRIVATE Boost::system Boost::filesystem)
```

**Advanced usage**:

```cmake
find_package(Boost 1.70
    REQUIRED
    COMPONENTS
        system filesystem thread
    OPTIONAL_COMPONENTS
        python
)

if(Boost_python_FOUND)
    target_compile_definitions(myapp PRIVATE HAVE_BOOST_PYTHON)
endif()

target_link_libraries(myapp PRIVATE Boost::system Boost::filesystem)
```

**Troubleshooting**:

```cmake
# Set Boost location explicitly
set(BOOST_ROOT "/opt/boost-1.81.0")
find_package(Boost REQUIRED)

# Or via command line
cmake -B build -DBOOST_ROOT=/usr/local
```

### FindOpenSSL

SSL/TLS support for secure communications.

```cmake
find_package(OpenSSL REQUIRED)
target_link_libraries(myapp PRIVATE OpenSSL::SSL OpenSSL::Crypto)

# Optional: check version
if(OPENSSL_VERSION VERSION_GREATER_EQUAL "3.0.0")
    message(STATUS "OpenSSL 3.x detected")
endif()
```

### FindPython

Modern Python integration.

```cmake
find_package(Python COMPONENTS Interpreter Development)

if(Python_FOUND)
    message(STATUS "Python version: ${Python_VERSION}")
    message(STATUS "Python executable: ${Python_EXECUTABLE}")

    target_link_libraries(myapp PRIVATE Python::Python)
endif()
```

### FindQt6 / FindQt5

Qt GUI framework. Requires components:

```cmake
find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets)

add_executable(myapp main.cpp)
target_link_libraries(myapp PRIVATE Qt6::Core Qt6::Gui Qt6::Widgets)

set_target_properties(myapp PROPERTIES
    AUTOMOC ON
    AUTORCC ON
    AUTOUIC ON
)
```

### FindPkgConfig

Discover packages via pkg-config (common on Linux):

```cmake
find_package(PkgConfig REQUIRED)
pkg_check_modules(GTK REQUIRED gtk+-3.0)

target_link_libraries(myapp PRIVATE ${GTK_LIBRARIES})
target_include_directories(myapp PRIVATE ${GTK_INCLUDE_DIRS})
target_compile_options(myapp PRIVATE ${GTK_CFLAGS})
```

---

## Package Configuration Files

Modern libraries provide **CMake config files** that define how to use them:

### Structure of a Config Package

A package must provide:

1. **XXXConfig.cmake** (or xxx-config.cmake)
   - Main entry point
   - Defines version and components
   - Sets up targets

2. **XXXConfigVersion.cmake** (or xxx-config-version.cmake)
   - Declares version and compatibility

3. **XXXTargets.cmake** (or xxx-targets.cmake)
   - Defines IMPORTED targets

4. **Optional**: Utility modules (.cmake files)

### Location in Installed Package

```
/usr/local/lib/cmake/MyLib/
├── MyLibConfig.cmake
├── MyLibConfigVersion.cmake
└── MyLibTargets.cmake
```

### What a Good Config File Provides

```cmake
# MyLibConfig.cmake
include_guard(GLOBAL)

# Version handling
include(${CMAKE_CURRENT_LIST_DIR}/MyLibConfigVersion.cmake)

# Define targets
include(${CMAKE_CURRENT_LIST_DIR}/MyLibTargets.cmake)

# Example: MyLibTargets.cmake defines IMPORTED targets:
# - MyLib::mylib (the main library)
# - MyLib::header (interface library for headers only)
```

When using such a package:

```cmake
find_package(MyLib REQUIRED)
target_link_libraries(myapp PRIVATE MyLib::mylib)
```

---

## Finding Programs

Use `find_program()` to locate executable programs:

```cmake
find_program(PYTHON_EXECUTABLE NAMES python3 python)
if(PYTHON_EXECUTABLE)
    message(STATUS "Found Python: ${PYTHON_EXECUTABLE}")
endif()

# Using in custom commands
add_custom_command(
    OUTPUT generated.cpp
    COMMAND ${PYTHON_EXECUTABLE} scripts/generate.py
    DEPENDS scripts/generate.py
)
```

---

## Troubleshooting Package Discovery

### CMAKE_PREFIX_PATH

The most important environment variable for package discovery. CMake looks for packages in:

```
${CMAKE_PREFIX_PATH}/lib/cmake/XXX/
${CMAKE_PREFIX_PATH}/share/cmake/XXX/
```

**Setting CMAKE_PREFIX_PATH**:

```bash
# Via command line
cmake -B build -DCMAKE_PREFIX_PATH=/usr/local:/opt/custom

# Via environment variable
export CMAKE_PREFIX_PATH=/usr/local:/opt/custom
cmake -B build

# In CMakeLists.txt (not recommended)
list(APPEND CMAKE_PREFIX_PATH "/opt/custom")
```

**Typical locations on different systems**:

```
Linux:    /usr, /usr/local, /opt
macOS:    /usr/local, /opt/homebrew, /Applications/*/Contents
Windows:  C:\Program Files, C:\Program Files (x86)
```

### Package-Specific Paths

Many Find modules accept package-specific hints:

```cmake
find_package(Boost HINTS /opt/boost)
find_package(OpenSSL HINTS /usr/local/openssl)
find_package(Qt6 HINTS /opt/qt6)
```

Or set environment variables before running CMake:

```bash
export BOOST_ROOT=/opt/boost
export Qt6_DIR=/opt/qt6/lib/cmake/Qt6
cmake -B build
```

### Debugging find_package

**Enable verbose output**:

```bash
cmake --debug-find -B build
```

This shows:
- Paths searched
- Files checked
- Why packages were found or not found

**Diagnostic message in CMakeLists.txt**:

```cmake
find_package(Boost QUIET)
if(NOT Boost_FOUND)
    message(FATAL_ERROR "Boost not found! Searched paths: ${CMAKE_PREFIX_PATH}")
endif()
```

**Check what was found**:

```cmake
find_package(Boost REQUIRED)
message("Boost version: ${Boost_VERSION}")
message("Boost include dirs: ${Boost_INCLUDE_DIRS}")
message("Boost libraries: ${Boost_LIBRARIES}")
message("Boost components: ${Boost_FOUND_COMPONENTS}")
```

### Common Errors and Solutions

**Error**: `Could not find XXX`

```cmake
# Solution 1: Install the package first
# Solution 2: Set CMAKE_PREFIX_PATH
cmake -B build -DCMAKE_PREFIX_PATH=/opt/custom

# Solution 3: Use FetchContent instead
include(FetchContent)
FetchContent_Declare(XXX GIT_REPOSITORY ...)
```

**Error**: `Version not found: need at least 1.70, found 1.60`

```cmake
# Solution: Install newer version or adjust requirement
find_package(Boost 1.60 REQUIRED)  # Accept older version

# Or use specific location
find_package(Boost 1.70 REQUIRED HINTS /opt/boost-1.81)
```

---

## Writing Custom Find Modules

For packages without CMake support, create a Find module:

### Basic Find Module Template

```cmake
# FindMyLib.cmake
include_guard(GLOBAL)

# Find the header
find_path(MYLIB_INCLUDE_DIR mylib.h)

# Find the library
find_library(MYLIB_LIBRARY NAMES mylib)

# Handle version (if available)
if(MYLIB_INCLUDE_DIR AND EXISTS "${MYLIB_INCLUDE_DIR}/mylib_version.h")
    file(STRINGS "${MYLIB_INCLUDE_DIR}/mylib_version.h" _mylib_version
        REGEX "#define MYLIB_VERSION"
    )
    string(REGEX MATCH "[0-9]+" MYLIB_VERSION "${_mylib_version}")
endif()

# Standard package handling
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(MyLib
    REQUIRED_VARS MYLIB_LIBRARY MYLIB_INCLUDE_DIR
    VERSION_VAR MYLIB_VERSION
)

# Create imported target
if(MYLIB_FOUND AND NOT TARGET MyLib::MyLib)
    add_library(MyLib::MyLib UNKNOWN IMPORTED)
    set_target_properties(MyLib::MyLib PROPERTIES
        IMPORTED_LOCATION "${MYLIB_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${MYLIB_INCLUDE_DIR}"
    )
endif()

mark_as_advanced(MYLIB_LIBRARY MYLIB_INCLUDE_DIR)
```

**Using custom Find module**:

```cmake
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
find_package(MyLib REQUIRED)
target_link_libraries(myapp PRIVATE MyLib::MyLib)
```

---

## Complete Examples

### Example 1: Using Boost

```cmake
cmake_minimum_required(VERSION 3.15)
project(BoostExample)

find_package(Boost 1.70 REQUIRED COMPONENTS system thread)

add_executable(myapp main.cpp)
target_link_libraries(myapp PRIVATE Boost::system Boost::thread)

# Check for optional components
find_package(Boost COMPONENTS python)
if(Boost_python_FOUND)
    message(STATUS "Building with Python support")
    target_compile_definitions(myapp PRIVATE HAS_PYTHON)
    target_link_libraries(myapp PRIVATE Boost::python)
endif()
```

### Example 2: Using OpenSSL and Qt

```cmake
cmake_minimum_required(VERSION 3.15)
project(SecureApp)

find_package(OpenSSL REQUIRED)
find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets)

add_executable(myapp
    main.cpp
    securedialog.cpp
)

target_link_libraries(myapp PRIVATE
    OpenSSL::SSL
    OpenSSL::Crypto
    Qt6::Core
    Qt6::Gui
    Qt6::Widgets
)

set_target_properties(myapp PROPERTIES
    AUTOMOC ON
    CXX_STANDARD 17
)
```

### Example 3: Conditional Dependencies

```cmake
cmake_minimum_required(VERSION 3.15)
project(ConditionalDeps)

# Always required
find_package(Boost REQUIRED COMPONENTS system)

# Optional
find_package(OpenSSL)
find_package(PNG)
find_package(ZLIB)

add_executable(myapp main.cpp)

target_link_libraries(myapp PRIVATE Boost::system)

# Add optional features
if(OPENSSL_FOUND)
    target_link_libraries(myapp PRIVATE OpenSSL::SSL)
    target_compile_definitions(myapp PRIVATE HAVE_OPENSSL)
endif()

if(PNG_FOUND)
    target_link_libraries(myapp PRIVATE PNG::PNG)
    target_compile_definitions(myapp PRIVATE HAVE_PNG)
endif()

if(ZLIB_FOUND)
    target_link_libraries(myapp PRIVATE ZLIB::ZLIB)
    target_compile_definitions(myapp PRIVATE HAVE_ZLIB)
endif()

# Report what was found
message(STATUS "Optional features:")
message(STATUS "  OpenSSL: ${OPENSSL_FOUND}")
message(STATUS "  PNG: ${PNG_FOUND}")
message(STATUS "  ZLIB: ${ZLIB_FOUND}")
```

### Example 4: CMakePresets with Package Paths

Store package paths in CMakePresets.json:

```json
{
  "version": 3,
  "configurePresets": [
    {
      "name": "default",
      "generator": "Unix Makefiles",
      "binaryDir": "${sourceDir}/build",
      "cacheVariables": {
        "CMAKE_PREFIX_PATH": "/opt/boost;/usr/local/openssl;/opt/qt6"
      }
    }
  ]
}
```

Usage:

```bash
cmake --preset default
```

---

## Best Practices

1. **Always use modern IMPORTED targets** instead of variables:
   ```cmake
   # ❌ Old
   target_link_libraries(myapp PRIVATE ${Boost_LIBRARIES})

   # ✅ Modern
   target_link_libraries(myapp PRIVATE Boost::system)
   ```

2. **Specify minimum versions** when possible:
   ```cmake
   find_package(Boost 1.70 REQUIRED)  # Specify version requirement
   ```

3. **Use REQUIRED for mandatory dependencies**:
   ```cmake
   find_package(OpenSSL REQUIRED)  # Build fails if not found
   ```

4. **Document your dependencies**:
   ```cmake
   # README.md: "Requires: Boost >= 1.70, OpenSSL >= 1.1.1"
   ```

5. **Provide clear cmake_prefix_path hints in documentation** for users building on unusual systems.
