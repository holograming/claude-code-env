# Memory Analysis

## Valgrind

```bash
# Memory leak detection
valgrind --leak-check=full --show-leak-kinds=all ./program

# Detailed report with origins
valgrind --leak-check=full --track-origins=yes ./program

# CPU profiling
valgrind --tool=callgrind ./program
kcachegrind callgrind.out.*
```

## Sanitizers (Clang/GCC)

```bash
# Address Sanitizer - buffer overflow, use-after-free
clang++ -fsanitize=address -g program.cpp -o program

# Memory Sanitizer - uninitialized reads
clang++ -fsanitize=memory -g program.cpp -o program

# Thread Sanitizer - data races
clang++ -fsanitize=thread -g program.cpp -o program

# Undefined Behavior Sanitizer
clang++ -fsanitize=undefined -g program.cpp -o program
```

## CMake Integration

```cmake
# Add sanitizer option
option(ENABLE_SANITIZERS "Enable sanitizers" OFF)

if(ENABLE_SANITIZERS)
    target_compile_options(myapp PRIVATE -fsanitize=address,undefined)
    target_link_options(myapp PRIVATE -fsanitize=address,undefined)
endif()
```
