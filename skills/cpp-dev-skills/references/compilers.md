# Compilers

## GCC

```bash
# Compile single file
g++ -std=c++17 -O2 program.cpp -o program

# Multiple files
g++ -std=c++17 -O2 main.cpp util.cpp -o program

# With warnings
g++ -Wall -Wextra -Wpedantic -std=c++17 program.cpp

# Generate dependency files
g++ -MM program.cpp  # Shows header dependencies

# Position independent code (for shared lib)
g++ -fPIC -shared lib.cpp -o lib.so
```

## Clang

```bash
# Similar to GCC
clang++ -std=c++17 -O2 program.cpp -o program

# Address Sanitizer (memory safety)
clang++ -fsanitize=address -g program.cpp

# Thread Sanitizer (data races)
clang++ -fsanitize=thread -g program.cpp

# UndefinedBehavior Sanitizer
clang++ -fsanitize=undefined -g program.cpp
```

## MSVC (Windows)

```cmd
REM Compile
cl /std:c++latest /O2 program.cpp

REM Create static library
lib object.obj /OUT:library.lib

REM Create DLL
cl /LD /O2 library.cpp
```
