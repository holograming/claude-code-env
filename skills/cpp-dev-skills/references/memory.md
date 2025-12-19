# Memory & Thread Analysis

## Sanitizers Overview

| Sanitizer | Detects | Compiler | Overhead |
|-----------|---------|----------|----------|
| **ASAN** | Memory errors, leaks, buffer overflow | GCC/Clang | ~2x |
| **TSAN** | Data races, deadlocks | GCC/Clang | ~5-15x |
| **UBSAN** | Undefined behavior | GCC/Clang | ~1x |
| **MSAN** | Uninitialized reads | Clang only | ~3x |

---

## ⚠️ CRITICAL: ASAN & TSAN Mutual Exclusion

**ASAN (AddressSanitizer) and TSAN (ThreadSanitizer) are mutually exclusive.**

They cannot be enabled together on the same target.

### Decision Logic

```
Problem to detect?
├─ Memory errors (buffer overflow, use-after-free, leaks)
│  └─ Use ASAN + UBSAN (recommended) ✅
│
├─ Thread bugs (data races, deadlocks)
│  └─ Use TSAN + UBSAN (recommended) ✅
│
└─ Both? (not recommended)
   └─ ❌ ASAN + TSAN: Will fail with runtime error
   └─ ✅ Workaround: Build 2 versions or profile separately
```

### Compatible Combinations

| Combination | Status | Use Case |
|-----------|--------|----------|
| **ASAN + UBSAN** | ✅ Compatible | Memory bugs + undefined behavior |
| **TSAN + UBSAN** | ✅ Compatible | Threading bugs + undefined behavior |
| **ASAN + TSAN** | ❌ **Mutual Exclusive** | **DO NOT USE** |
| **MSAN + UBSAN** | ✅ Compatible | Uninitialized memory + undefined behavior |

---

## Command Line Usage

```bash
# Memory checking (recommended)
cmake -B build -DENABLE_ASAN=ON -DENABLE_UBSAN=ON
cmake --build build
./build/myapp

# Thread checking (recommended)
cmake -B build -DENABLE_TSAN=ON -DENABLE_UBSAN=ON
cmake --build build
./build/myapp

# Undefined behavior only
cmake -B build -DENABLE_UBSAN=ON
cmake --build build
./build/myapp
```

---

## Sanitizer Details

### AddressSanitizer (ASAN)

Detects: buffer overflow, use-after-free, memory leaks, double free

```bash
clang++ -fsanitize=address -g -fno-omit-frame-pointer program.cpp -o program
ASAN_OPTIONS=detect_leaks=1:verbosity=2 ./program
```

### ThreadSanitizer (TSAN)

Detects: data races, deadlocks, signal races

```bash
clang++ -fsanitize=thread -g -fno-omit-frame-pointer program.cpp -o program
TSAN_OPTIONS=verbosity=2 ./program
```

### UndefinedBehaviorSanitizer (UBSAN)

Detects: undefined behavior (signed overflow, null pointer, division by zero)

```bash
clang++ -fsanitize=undefined -g program.cpp -o program
UBSAN_OPTIONS=print_stacktrace=1 ./program
```

---

## CMake Integration (Via Sanitizers.cmake)

```cmake
# Root CMakeLists.txt
include(cmake/Sanitizers.cmake)

add_executable(myapp main.cpp)
enable_sanitizers(myapp)

# Build with ASAN
# cmake -B build -DENABLE_ASAN=ON
# cmake --build build
```

See `scripts/templates/cmake_modules/Sanitizers.cmake` for full configuration.

---

## Environment Variables

```bash
# ASAN
ASAN_OPTIONS=detect_leaks=1:verbosity=2:halt_on_error=1

# TSAN
TSAN_OPTIONS=verbosity=2:halt_on_error=1

# UBSAN
UBSAN_OPTIONS=print_stacktrace=1:halt_on_error=1

# LSAN (Leak Sanitizer, part of ASAN)
LSAN_OPTIONS=verbosity=2:log_threads=1
```

---

## Valgrind (Alternative, for systems without Clang/GCC sanitizers)

```bash
# Memory leak detection
valgrind --leak-check=full --show-leak-kinds=all ./program

# Detailed report with origins
valgrind --leak-check=full --track-origins=yes ./program

# CPU profiling
valgrind --tool=callgrind ./program
kcachegrind callgrind.out.*
```
