# Modern Target-Based CMake

This document covers target types, visibility specifiers, target properties, and advanced linking patterns that form the foundation of modern CMake (3.15+).

## Overview

Modern CMake organizes build information around **targets** rather than global variables. Each target encapsulates:
- Source files
- Compile flags and definitions
- Include directories
- Link libraries and options
- Compiler features required

This approach provides clarity, maintainability, and proper dependency management.

---

## Target Types

### Executables

Created with `add_executable()`:

```cmake
add_executable(myapp
    src/main.cpp
    src/utils.cpp
)

# Executable properties
target_include_directories(myapp PRIVATE include)
target_compile_features(myapp PRIVATE cxx_std_17)
target_link_libraries(myapp PRIVATE mylib)
```

**Characteristics**:
- Produces a runnable binary
- Has compiler flags, include dirs, and dependencies
- Cannot be linked by other targets

### Static Libraries

Created with `add_library(name STATIC ...)`:

```cmake
add_library(mylib STATIC
    src/file1.cpp
    src/file2.cpp
)

target_include_directories(mylib
    PUBLIC include
    PRIVATE src
)

target_compile_features(mylib PUBLIC cxx_std_17)
```

**Characteristics**:
- Produces `.a` or `.lib` archive
- Linked directly into consuming targets
- Code duplication if used by multiple executables
- No runtime dependency on library

### Shared Libraries

Created with `add_library(name SHARED ...)`:

```cmake
add_library(mylib SHARED src/mylib.cpp)

target_include_directories(mylib
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

target_compile_features(mylib PUBLIC cxx_std_17)

# Enable proper symbol export on Windows
set_target_properties(mylib PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)
```

**Characteristics**:
- Produces `.so`, `.dylib`, or `.dll`
- Loaded at runtime
- Single copy in memory for multiple processes
- Requires runtime library paths (RPATH on Unix, PATH on Windows)

**RPATH Handling**:

```cmake
set_target_properties(myapp PROPERTIES
    BUILD_RPATH "${CMAKE_BINARY_DIR}/lib"
    INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib"
)
```

### Interface Libraries (Header-Only)

Created with `add_library(name INTERFACE)`:

```cmake
add_library(myheaderlib INTERFACE)

target_include_directories(myheaderlib INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

target_compile_features(myheaderlib INTERFACE cxx_std_17)

# Link other dependencies
target_link_libraries(myheaderlib INTERFACE Boost::system)
```

**Characteristics**:
- No compiled source
- Propagates only interface requirements
- Ideal for header-only libraries
- No PRIVATE properties (everything is INTERFACE)

**Creating Aliases**:

```cmake
add_library(MyLib::myheaderlib ALIAS myheaderlib)

# Usage:
target_link_libraries(myapp PRIVATE MyLib::myheaderlib)
```

### Object Libraries

Created with `add_library(name OBJECT ...)`:

```cmake
add_library(shared_obj OBJECT
    src/common.cpp
    src/utils.cpp
)

target_include_directories(shared_obj PUBLIC include)
target_compile_features(shared_obj PUBLIC cxx_std_17)
```

**Use Cases**:
- Share compiled object files between static and shared libraries
- Avoid code duplication

**Using Object Library**:

```cmake
add_library(mylib_static STATIC $<TARGET_OBJECTS:shared_obj> src/static_impl.cpp)
add_library(mylib_shared SHARED $<TARGET_OBJECTS:shared_obj> src/shared_impl.cpp)

target_link_libraries(mylib_static PRIVATE shared_obj)
target_link_libraries(mylib_shared PRIVATE shared_obj)
```

---

## Visibility Specifiers

Every `target_*` command accepts visibility keywords: `PUBLIC`, `PRIVATE`, or `INTERFACE`.

### PUBLIC

**Definition**: Required by both the target and its consumers.

```cmake
add_library(mylib src/mylib.cpp)

# Include directory needed by mylib AND by anything using mylib
target_include_directories(mylib PUBLIC include)

# C++ standard needed by mylib AND by consumers
target_compile_features(mylib PUBLIC cxx_std_17)

# Dependency needed by mylib AND by consumers
target_link_libraries(mylib PUBLIC Boost::system)
```

**When to use**:
- Include directories for your library's public API
- C++ standard requirements
- Public dependencies

### PRIVATE

**Definition**: Required only by the target itself.

```cmake
add_library(mylib src/mylib.cpp)

# Implementation detail, not visible to consumers
target_include_directories(mylib PRIVATE src/internal)

# Internal dependency not needed by consumers
target_link_libraries(mylib PRIVATE zlib)

# Compile flags for implementation
target_compile_options(mylib PRIVATE -Wno-deprecated-declarations)
```

**When to use**:
- Internal implementation include directories
- Internal dependencies
- Implementation-specific compiler flags

### INTERFACE

**Definition**: Required by consumers but not by the target itself.

```cmake
add_library(myheaderlib INTERFACE)

# Only consumers need this, myheaderlib itself doesn't compile anything
target_include_directories(myheaderlib INTERFACE include)

# Consumers inherit this requirement
target_compile_features(myheaderlib INTERFACE cxx_std_17)
```

**When to use**:
- Header-only libraries
- When defining interface requirements without implementation
- CMake properties that only make sense for consumers

### Build vs Install Interface

Distinguish between build-time and install-time:

```cmake
target_include_directories(mylib PUBLIC
    # During build, use source directory
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    # After installation, use install prefix
    $<INSTALL_INTERFACE:include>
)
```

---

## Target Properties

### Include Directories

```cmake
# Set include directories
target_include_directories(mylib
    PUBLIC include
    PRIVATE src
    INTERFACE ${EXTERNAL_INCLUDE}
)

# Add to existing includes (not replacing)
target_include_directories(mylib APPEND PUBLIC extra_include)
```

### Compile Definitions

Preprocessor defines:

```cmake
# Simple definition
target_compile_definitions(mylib PRIVATE DEBUG_MODE)

# Definition with value
target_compile_definitions(mylib PUBLIC MYLIB_VERSION="${PROJECT_VERSION}")

# Configuration-dependent
target_compile_definitions(mylib PRIVATE
    $<$<CONFIG:Debug>:ENABLE_LOGGING>
    $<$<CONFIG:Release>:NDEBUG>
)
```

### Compile Options

Compiler flags:

```cmake
# Platform-specific warnings
target_compile_options(mylib PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4 /WX>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic -Werror>
)

# Optimization (rarely needed, use build types instead)
target_compile_options(mylib PRIVATE
    $<$<CONFIG:Release>:-O3>
)
```

### Compile Features

Require C++ standard features:

```cmake
# Require C++17 for this target
target_compile_features(mylib PUBLIC cxx_std_17)

# Specific features
target_compile_features(myapp PRIVATE cxx_variadic_templates cxx_auto_type)
```

**Advantages**:
- Works across all compilers
- Automatically sets -std=c++17 (GCC/Clang) or /std:c++17 (MSVC)
- Consumers inherit requirement
- CMake verifies compiler support

### Link Libraries

```cmake
# Link a target
target_link_libraries(myapp PRIVATE mylib)

# Link multiple
target_link_libraries(myapp PRIVATE lib1 lib2 lib3)

# Mix targets and system libraries
target_link_libraries(myapp PRIVATE mylib Boost::system pthread)

# Link-time options (uncommon)
target_link_options(myapp PRIVATE -Wl,--as-needed)
```

---

## Advanced Linking Patterns

### Transitive Dependencies

When `myapp` links `mylib` which depends on `Boost`:

```cmake
# In mylib
target_link_libraries(mylib PUBLIC Boost::system)

# In myapp
target_link_libraries(myapp PRIVATE mylib)

# myapp automatically gets Boost::system through mylib
# No need to explicitly link Boost in myapp
```

**Visibility determines propagation**:

```cmake
# PUBLIC: mylib's consumers inherit this dependency
target_link_libraries(mylib PUBLIC Boost::system)

# PRIVATE: mylib's consumers don't inherit this
target_link_libraries(mylib PRIVATE zlib)
```

### Linking with Different Configurations

```cmake
# Debug and Release have different libraries
target_link_libraries(myapp PRIVATE
    $<$<CONFIG:Debug>:mydebug_lib>
    $<$<CONFIG:Release>:myoptimized_lib>
)
```

### Cyclic Dependency Management

Avoid circular dependencies:

```cmake
# ❌ Avoid this
add_library(liba src_a.cpp)
add_library(libb src_b.cpp)
target_link_libraries(liba PRIVATE libb)
target_link_libraries(libb PRIVATE liba)  # Circular!

# ✅ Solution: Create interface library
add_library(shared_interface INTERFACE)
target_link_libraries(liba PRIVATE shared_interface)
target_link_libraries(libb PRIVATE shared_interface)
```

### Grouped Link Dependencies

```cmake
# Create object library with common dependencies
add_library(common_obj OBJECT src/common.cpp)
target_link_libraries(common_obj PUBLIC Boost::system)

# Use in multiple targets
add_library(lib1 src/lib1.cpp $<TARGET_OBJECTS:common_obj>)
add_library(lib2 src/lib2.cpp $<TARGET_OBJECTS:common_obj>)
```

---

## Compiler and Linker Essentials

### Standard Library Selection

```cmake
# Use libc++ instead of libstdc++ (Clang)
target_compile_options(myapp PRIVATE -stdlib=libc++)
target_link_options(myapp PRIVATE -stdlib=libc++)

# Or set globally for C++ projects
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")
endif()
```

### Position Independent Code

```cmake
# Create position-independent executables (PIE)
set_target_properties(myapp PROPERTIES POSITION_INDEPENDENT_CODE ON)

# Or globally
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
```

### Symbol Visibility

```cmake
# Hide symbols by default on Unix-like systems
set_target_properties(mylib PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
)
```

### Runtime Library

```cmake
# Link with static runtime (MSVC)
set_target_properties(myapp PROPERTIES
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
)
```

### Link-Time Optimization

```cmake
# Enable LTO (available in CMake 3.9+)
set_target_properties(mylib PROPERTIES INTERPROCEDURAL_OPTIMIZATION ON)

# Or per-configuration
set_target_properties(mylib PROPERTIES
    INTERPROCEDURAL_OPTIMIZATION_RELEASE ON
)
```

---

## Complete Examples

### Example 1: Simple Library with Proper Visibility

```cmake
cmake_minimum_required(VERSION 3.15)
project(MathLib VERSION 1.0.0 LANGUAGES CXX)

add_library(mathlib
    src/add.cpp
    src/multiply.cpp
)

# Public API: consumers need this
target_include_directories(mathlib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# C++ standard for public API
target_compile_features(mathlib PUBLIC cxx_std_17)

# Internal include (implementation detail)
target_include_directories(mathlib PRIVATE src)

# Create alias for consistency
add_library(Math::mathlib ALIAS mathlib)
```

### Example 2: Header-Only Library with Dependencies

```cmake
add_library(json_helper INTERFACE)
add_library(JSON::Helper ALIAS json_helper)

find_package(nlohmann_json REQUIRED)

target_include_directories(json_helper INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Consumers inherit this dependency
target_link_libraries(json_helper INTERFACE nlohmann_json::nlohmann_json)

target_compile_features(json_helper INTERFACE cxx_std_17)
```

### Example 3: Multi-Component Project

```cmake
cmake_minimum_required(VERSION 3.15)
project(MyProject VERSION 1.0.0)

# Common utilities
add_library(common
    src/common/logger.cpp
    src/common/config.cpp
)
target_include_directories(common PUBLIC include)
target_compile_features(common PUBLIC cxx_std_17)

# Network component
add_library(network
    src/network/socket.cpp
    src/network/server.cpp
)
target_link_libraries(network PUBLIC common)
target_include_directories(network PUBLIC include)

# Database component
add_library(database
    src/database/connection.cpp
)
target_link_libraries(database PUBLIC common)
target_include_directories(database PUBLIC include)

# Main application
add_executable(myapp src/main.cpp)
target_link_libraries(myapp PRIVATE network database common)
```

### Example 4: Conditional Features with Generator Expressions

```cmake
add_library(mylib src/mylib.cpp)

# Warnings for all configurations
target_compile_options(mylib PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra>
)

# Optimization and debug symbols
target_compile_options(mylib PRIVATE
    $<$<CONFIG:Debug>:-O0 -g>
    $<$<CONFIG:Release>:-O3>
    $<$<CONFIG:RelWithDebInfo>:-O2 -g>
)

# Debug defines
target_compile_definitions(mylib PRIVATE
    $<$<CONFIG:Debug>:DEBUG_MODE ENABLE_ASSERTIONS>
)

# Position independent code
set_target_properties(mylib PROPERTIES
    POSITION_INDEPENDENT_CODE $<NOT:$<BOOL:${WIN32}>>
)
```

---

## Best Practices

1. **Always use IMPORTED targets** instead of variables:
   ```cmake
   # ❌ Don't
   target_link_libraries(myapp PRIVATE ${BOOST_LIBRARIES})

   # ✅ Do
   target_link_libraries(myapp PRIVATE Boost::system)
   ```

2. **Use correct visibility specifiers**:
   ```cmake
   # ❌ Don't make everything PUBLIC
   target_include_directories(mylib PUBLIC src)

   # ✅ Do use PRIVATE for implementation
   target_include_directories(mylib PRIVATE src)
   ```

3. **Use target_compile_features instead of manual flags**:
   ```cmake
   # ❌ Don't
   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")

   # ✅ Do
   target_compile_features(mylib PUBLIC cxx_std_17)
   ```

4. **Separate build and install interfaces**:
   ```cmake
   target_include_directories(mylib PUBLIC
       $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
       $<INSTALL_INTERFACE:include>
   )
   ```

5. **Create target aliases for consistency**:
   ```cmake
   add_library(MyLib::Core ALIAS mylib_core)
   # Users always use MyLib::Core namespace
   ```
