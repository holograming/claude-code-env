
Development tools, build systems (CMake), compilers (GCC/Clang), debugging, testing frameworks, and best practices for professional C++.

### CMake - Build System
 - Read reference\CMAKE.md

### Compilers
  - Read reference\COMPILERS.md

### Debugging with GDB
  - Read reference\DEBUG.md

### Testing with Google Test (GTest)
  - Read reference\Testing.md

### Version Control with Git
  - Read reference\versioncontorls.md

### Code Quality Tools 
  - Read reference\codequality.md

### Valgrind (Memory Analysis)
  - Read reference\memory.md

### Design Patterns
  - Read reference\designpatterns.md

### C++ Core Guidelines
- RAII - Resource Acquisition Is Initialization
- Move semantics - Efficient resource transfer
- const correctness - Mark functions as const
- No naked new/delete - Use smart pointers
- Error handling - Use exceptions appropriately
- Avoid global variables - Encapsulate state
- Use STL algorithms - Over manual loops
- Follow naming conventions - Clear, consistent names


### Documentation
```
/// Calculate factorial of n
/// @param n The input number (must be non-negative)
/// @return Factorial of n
/// @throws std::invalid_argument if n < 0
int factorial(int n);
```

### Project Structure Best Practices
```
project/
├── CMakeLists.txt          # Build configuration
├── src/                    # Source files
│   ├── main.cpp
│   └── lib/
├── include/                # Public headers
│   └── mylib.h
├── tests/                  # Test files
│   └── test_lib.cpp
├── docs/                   # Documentation
└── .gitignore
```

###  When to Use This Skill
Setting up new C++ projects
Debugging complex issues
Writing and running tests
Optimizing build performance
Code quality and style enforcement
Team development and version control
Professional project management