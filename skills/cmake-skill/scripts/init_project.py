#!/usr/bin/env python3
"""
Initialize a modern CMake project

Usage:
    init_project.py <project-name> [--type TYPE] [--language LANG]

Types:
    - minimal: Simple executable (default)
    - library: Library with proper exports
    - header-only: Header-only INTERFACE library
    - with-deps: Project with dependency examples

Languages:
    - cpp (default)
    - c
"""

import sys
from pathlib import Path
import argparse


def create_minimal_cmake(project_name):
    """Generate minimal CMakeLists.txt"""
    return f"""cmake_minimum_required(VERSION 3.15)
project({project_name} VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(${{PROJECT_NAME}} src/main.cpp)
target_compile_features(${{PROJECT_NAME}} PRIVATE cxx_std_17)
target_compile_options(${{PROJECT_NAME}} PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic>
)

enable_testing()
"""


def init_project(project_name):
    """Initialize project structure"""
    project_dir = Path(project_name)
    if project_dir.exists():
        print(f"ERROR: Directory {project_name} already exists")
        return False
    
    # Create directories
    project_dir.mkdir()
    (project_dir / "src").mkdir()
    (project_dir / "include").mkdir()
    (project_dir / "tests").mkdir()
    
    # Create CMakeLists.txt
    cmake_content = create_minimal_cmake(project_name)
    (project_dir / "CMakeLists.txt").write_text(cmake_content)
    
    # Create main.cpp
    main_cpp = """#include <iostream>

int main() {
    std::cout << "Hello from """ + project_name + """!\" << std::endl;
    return 0;
}
"""
    (project_dir / "src" / "main.cpp").write_text(main_cpp)
    
    # Create README
    readme = f"""# {project_name}

Modern CMake project.

## Building

```bash
cmake -B build
cmake --build build
```

## Running

```bash
./build/{project_name}
```
"""
    (project_dir / "README.md").write_text(readme)
    
    # Create .gitignore
    gitignore = """build/
cmake-build-*/
.vscode/
.idea/
*.swp
"""
    (project_dir / ".gitignore").write_text(gitignore)
    
    print(f"Created project: {project_name}")
    print(f"Directory structure created")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: init_project.py <project-name>")
        return 1
    
    project_name = sys.argv[1]
    
    if init_project(project_name):
        print(f"Project initialized successfully!")
        print(f"Next steps:")
        print(f"  cd {project_name}")
        print(f"  cmake -B build")
        print(f"  cmake --build build")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
