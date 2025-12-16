### Clang-Tidy (Linting)
```
# Install
apt-get install clang-tidy

# Analyze single file
clang-tidy program.cpp -- -I. -std=c++17

# With CMake
cmake .. -DCMAKE_CXX_CLANG_TIDY="clang-tidy"
cmake --build .

# Custom checks
clang-tidy -checks="-*,readability-*" program.cpp
```

### Clang-Format (Code Formatting)
```
# Create .clang-format file
clang-format -style=llvm -dump-config > .clang-format

# Format file
clang-format -i program.cpp

# Check formatting (CI)
clang-format --dry-run --Werror program.cpp

# Format whole project
find . -name "*.cpp" -o -name "*.h" | xargs clang-format -i
```