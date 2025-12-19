#!/usr/bin/env python3
"""
Modern C++ Project Initializer

Supports:
- CLI applications
- GUI applications (Qt/wxWidgets)
- Static/Shared libraries
- Header-only libraries

Platform-aware defaults:
- Windows: MSVC, Visual Studio generator, vcpkg
- Linux: GCC, Unix Makefiles/Ninja, Conan
- macOS: Clang, Unix Makefiles/Ninja, Homebrew
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ProjectTemplates:
    """Generate templates for each project type."""

    @staticmethod
    def cli_application(project_name: str, cpp_standard: int = 17) -> Dict[str, str]:
        """CLI Application templates."""
        templates = {}

        # CMakeLists.txt
        templates['CMakeLists.txt'] = f"""cmake_minimum_required(VERSION 3.15)
project({project_name} VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD {cpp_standard})
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Main executable
add_executable({project_name}
    src/main.cpp
)

target_include_directories({project_name} PRIVATE include)

# Compiler warnings
target_compile_options({project_name} PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic>
)

# Optional: Add find_package here
# find_package(fmt REQUIRED)
# target_link_libraries({project_name} PRIVATE fmt::fmt)

# Testing
enable_testing()
add_subdirectory(tests)
"""

        # main.cpp
        templates['src/main.cpp'] = f"""#include <iostream>

int main(int argc, char* argv[]) {{
    std::cout << "Hello from {project_name}!" << std::endl;
    return 0;
}}
"""

        # test_main.cpp
        templates['tests/CMakeLists.txt'] = f"""# Simple test example
# For Google Test, use: find_package(GTest REQUIRED)
# add_executable(tests test_main.cpp)
# target_link_libraries(tests PRIVATE GTest::Main)
# add_test(NAME MainTests COMMAND tests)
"""

        templates['tests/test_main.cpp'] = f"""#include <cassert>

// Simple test example
int main() {{
    assert(1 + 1 == 2);
    return 0;
}}
"""

        return templates

    @staticmethod
    def gui_application(project_name: str, framework: str = "qt6") -> Dict[str, str]:
        """GUI Application templates."""
        templates = {}

        if framework == "qt6":
            templates['CMakeLists.txt'] = f"""cmake_minimum_required(VERSION 3.16)
project({project_name} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 REQUIRED COMPONENTS
    Core
    Gui
    Widgets
)

add_executable({project_name}
    src/main.cpp
    src/mainwindow.cpp
    src/mainwindow.h
    resources/icons.qrc
)

target_link_libraries({project_name} PRIVATE Qt6::Widgets)

if(WIN32)
    set_target_properties({project_name} PROPERTIES WIN32_EXECUTABLE ON)
endif()
"""

            templates['src/main.cpp'] = f"""#include <QApplication>
#include "mainwindow.h"

int main(int argc, char *argv[])
{{
    QApplication app(argc, argv);

    MainWindow window;
    window.show();

    return app.exec();
}}
"""

            templates['src/mainwindow.h'] = f"""#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

class MainWindow : public QMainWindow {{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();
}};

#endif // MAINWINDOW_H
"""

            templates['src/mainwindow.cpp'] = f"""#include "mainwindow.h"
#include <QLabel>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{{
    setWindowTitle("Hello Qt 6");
    setGeometry(100, 100, 400, 300);

    auto *label = new QLabel("Welcome to Qt 6!", this);
    setCentralWidget(label);
}}

MainWindow::~MainWindow() {{}}
"""

        return templates

    @staticmethod
    def static_library(project_name: str) -> Dict[str, str]:
        """Static Library templates."""
        templates = {}

        templates['CMakeLists.txt'] = f"""cmake_minimum_required(VERSION 3.15)
project({project_name} VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library({project_name} STATIC
    src/lib.cpp
)

add_library({project_name}::{project_name} ALIAS {project_name})

target_include_directories({project_name}
    PUBLIC
        $<BUILD_INTERFACE:${{CMAKE_CURRENT_SOURCE_DIR}}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${{CMAKE_CURRENT_SOURCE_DIR}}/src
)

target_compile_features({project_name} PUBLIC cxx_std_17)

# Testing
enable_testing()
add_subdirectory(tests)

# Installation
install(TARGETS {project_name} ARCHIVE DESTINATION lib)
install(DIRECTORY include/{project_name} DESTINATION include)
"""

        templates['include/lib.h'] = f"""#pragma once

namespace {project_name} {{

void hello();

}}  // namespace {project_name}
"""

        templates['src/lib.cpp'] = f"""#include "{project_name}/lib.h"
#include <iostream>

namespace {project_name} {{

void hello() {{
    std::cout << "Hello from {project_name} library!" << std::endl;
}}

}}  // namespace {project_name}
"""

        return templates

    @staticmethod
    def shared_library(project_name: str) -> Dict[str, str]:
        """Shared Library templates."""
        templates = ProjectTemplates.static_library(project_name)

        # Change to SHARED
        templates['CMakeLists.txt'] = templates['CMakeLists.txt'].replace(
            'add_library(' + project_name + ' STATIC',
            'add_library(' + project_name + ' SHARED'
        ).replace(
            'install(TARGETS',
            '''set_target_properties(''' + project_name + ''' PROPERTIES
    VERSION 1.0.0
    SOVERSION 1
)

# Installation (update)
install(TARGETS'''
        )

        return templates

    @staticmethod
    def header_only_library(project_name: str) -> Dict[str, str]:
        """Header-Only Library templates."""
        templates = {}

        templates['CMakeLists.txt'] = f"""cmake_minimum_required(VERSION 3.15)
project({project_name} VERSION 1.0.0 LANGUAGES CXX)

add_library({project_name} INTERFACE)
add_library({project_name}::{project_name} ALIAS {project_name})

target_include_directories({project_name} INTERFACE
    $<BUILD_INTERFACE:${{CMAKE_CURRENT_SOURCE_DIR}}/include>
    $<INSTALL_INTERFACE:include>
)

target_compile_features({project_name} INTERFACE cxx_std_17)

enable_testing()
add_subdirectory(tests)

install(DIRECTORY include/{project_name} DESTINATION include)
"""

        templates['include/lib.h'] = f"""#pragma once

namespace {project_name} {{

template<typename T>
T add(T a, T b) {{
    return a + b;
}}

}}  // namespace {project_name}
"""

        return templates


class PlatformDetector:
    """Detect platform and recommend defaults."""

    @staticmethod
    def detect_os() -> str:
        """Detect operating system."""
        system = platform.system()
        if system == 'Windows':
            return 'Windows'
        elif system == 'Linux':
            return 'Linux'
        elif system == 'Darwin':
            return 'macOS'
        return 'Unknown'

    @staticmethod
    def recommend_compiler() -> str:
        """Recommend compiler based on platform."""
        os_name = PlatformDetector.detect_os()
        if os_name == 'Windows':
            return 'MSVC'
        elif os_name == 'Linux':
            return 'GCC'
        elif os_name == 'macOS':
            return 'Clang'
        return 'GCC'

    @staticmethod
    def recommend_generator() -> str:
        """Recommend CMake generator based on platform."""
        os_name = PlatformDetector.detect_os()
        if os_name == 'Windows':
            return 'Visual Studio 17 2022'
        elif os_name == 'macOS':
            return 'Unix Makefiles'
        else:
            return 'Unix Makefiles'

    @staticmethod
    def recommend_package_manager() -> str:
        """Recommend package manager based on platform."""
        os_name = PlatformDetector.detect_os()
        if os_name == 'Windows':
            return 'vcpkg'
        elif os_name == 'Linux':
            return 'Conan'
        elif os_name == 'macOS':
            return 'Conan'
        return 'None'


class DependencyManager:
    """Manage dependency strategies."""

    @staticmethod
    def detect_vcpkg() -> Optional[str]:
        """Detect vcpkg installation."""
        vcpkg_root = os.environ.get('VCPKG_ROOT')
        if vcpkg_root and os.path.exists(vcpkg_root):
            return vcpkg_root
        return None

    @staticmethod
    def detect_conan() -> bool:
        """Detect Conan installation."""
        try:
            subprocess.run(['conan', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @staticmethod
    def generate_dependencies_cmake() -> str:
        """Generate Dependencies.cmake template."""
        return '''# Common dependencies for all targets
include(FetchContent)

# Example 1: Using FetchContent
# FetchContent_Declare(fmt
#     GIT_REPOSITORY https://github.com/fmtlib/fmt.git
#     GIT_TAG 9.1.0
# )
# FetchContent_MakeAvailable(fmt)

# Example 2: Using find_package
# find_package(fmt REQUIRED)

# Function to link common dependencies
function(link_common_dependencies target)
    # target_link_libraries(${target} PRIVATE fmt::fmt)
endfunction()
'''

    @staticmethod
    def generate_compiler_warnings_cmake() -> str:
        """Generate CompilerWarnings.cmake template."""
        return '''# Compiler warnings setup

function(target_set_warnings target)
    target_compile_options(${target} PRIVATE
        $<$<CXX_COMPILER_ID:MSVC>:
            /W4
            /permissive-
        >
        $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:
            -Wall
            -Wextra
            -Wpedantic
        >
    )
endfunction()
'''

    @staticmethod
    def generate_sanitizers_cmake() -> str:
        """Generate Sanitizers.cmake template."""
        return '''# Sanitizer options

option(ENABLE_ASAN "Enable AddressSanitizer" OFF)
option(ENABLE_TSAN "Enable ThreadSanitizer" OFF)
option(ENABLE_UBSAN "Enable UndefinedBehaviorSanitizer" OFF)

function(enable_sanitizers target)
    if(ENABLE_ASAN AND NOT MSVC)
        target_compile_options(${target} PRIVATE -fsanitize=address)
        target_link_options(${target} PRIVATE -fsanitize=address)
    endif()

    if(ENABLE_TSAN AND NOT MSVC)
        target_compile_options(${target} PRIVATE -fsanitize=thread)
        target_link_options(${target} PRIVATE -fsanitize=thread)
    endif()

    if(ENABLE_UBSAN AND NOT MSVC)
        target_compile_options(${target} PRIVATE -fsanitize=undefined)
        target_link_options(${target} PRIVATE -fsanitize=undefined)
    endif()
endfunction()
'''


class CMakeModuleGenerator:
    """Generate cmake/ folder and modules for complex projects."""

    @staticmethod
    def should_create_cmake_folder(num_targets: int, num_dependencies: int) -> bool:
        """Determine if cmake/ folder is needed."""
        return num_targets >= 3 or num_dependencies >= 3

    @staticmethod
    def create_cmake_modules(project_path: Path, project_name: str) -> None:
        """Create cmake/ folder and modules."""
        cmake_dir = project_path / 'cmake'
        cmake_dir.mkdir(exist_ok=True)

        # Dependencies.cmake
        (cmake_dir / 'Dependencies.cmake').write_text(
            DependencyManager.generate_dependencies_cmake()
        )

        # CompilerWarnings.cmake
        (cmake_dir / 'CompilerWarnings.cmake').write_text(
            DependencyManager.generate_compiler_warnings_cmake()
        )

        # Sanitizers.cmake
        (cmake_dir / 'Sanitizers.cmake').write_text(
            DependencyManager.generate_sanitizers_cmake()
        )


class ProjectInitializer:
    """Main project initialization orchestrator."""

    def __init__(self, project_name: str, project_type: str, interactive: bool = False):
        self.project_name = project_name
        self.project_type = project_type
        self.interactive = interactive
        self.project_path = Path(project_name)

        # Defaults
        self.compiler = PlatformDetector.recommend_compiler()
        self.generator = PlatformDetector.recommend_generator()
        self.package_manager = PlatformDetector.recommend_package_manager()
        self.cpp_standard = 17
        self.gui_framework = 'qt6'
        self.use_cmake_modules = False

    def create_directory_structure(self) -> bool:
        """Create project directories."""
        try:
            self.project_path.mkdir(exist_ok=False)
            (self.project_path / 'src').mkdir()
            (self.project_path / 'include').mkdir()
            (self.project_path / 'tests').mkdir()
            return True
        except FileExistsError:
            print(f"❌ Directory '{self.project_name}' already exists!")
            return False

    def generate_source_files(self) -> bool:
        """Generate source code templates."""
        try:
            if self.project_type == 'cli':
                templates = ProjectTemplates.cli_application(self.project_name, self.cpp_standard)
            elif self.project_type == 'gui':
                templates = ProjectTemplates.gui_application(self.project_name, self.gui_framework)
            elif self.project_type == 'static-lib':
                templates = ProjectTemplates.static_library(self.project_name)
            elif self.project_type == 'shared-lib':
                templates = ProjectTemplates.shared_library(self.project_name)
            elif self.project_type == 'header-only':
                templates = ProjectTemplates.header_only_library(self.project_name)
            else:
                print(f"❌ Unknown project type: {self.project_type}")
                return False

            # Write files
            for file_path, content in templates.items():
                full_path = self.project_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content)

            return True
        except Exception as e:
            print(f"❌ Error generating source files: {e}")
            return False

    def generate_config_files(self) -> bool:
        """Generate configuration files."""
        try:
            # .clang-format
            clang_format = """---
Language:        Cpp
BasedOnStyle:    LLVM
IndentWidth:     4
TabWidth:        4
UseTab:          Never
ColumnLimit:     120
---
"""
            (self.project_path / '.clang-format').write_text(clang_format)

            # .gitignore
            gitignore = """# Build directories
build/
cmake-build-*/
out/

# CMake
CMakeCache.txt
CMakeFiles/
*.cmake

# IDE
.vscode/
.idea/
*.vcxproj
*.sln

# Executables
*.exe
*.out
*.o
*.a
*.so

# OS
.DS_Store
.vs/
"""
            (self.project_path / '.gitignore').write_text(gitignore)

            return True
        except Exception as e:
            print(f"❌ Error generating config files: {e}")
            return False

    def generate_documentation(self) -> bool:
        """Generate README.md."""
        try:
            readme = f"""# {self.project_name}

Modern C++ project using CMake.

## Building

```bash
cmake -B build
cmake --build build
```

## Running

```bash
./build/{self.project_name}
```

## Testing

```bash
ctest --test-dir build
```

## Requirements

- CMake 3.15+
- C++{self.cpp_standard} compiler
- (Additional dependencies as needed)
"""
            (self.project_path / 'README.md').write_text(readme)
            return True
        except Exception as e:
            print(f"❌ Error generating documentation: {e}")
            return False

    def initialize(self) -> bool:
        """Run full initialization."""
        print(f"🔧 Initializing {self.project_type} project '{self.project_name}'...\n")

        steps = [
            ("Creating directory structure", self.create_directory_structure),
            ("Generating source files", self.generate_source_files),
            ("Generating configuration files", self.generate_config_files),
            ("Generating documentation", self.generate_documentation),
        ]

        for step_name, step_func in steps:
            print(f"→ {step_name}...")
            if not step_func():
                return False
            print(f"  ✅ {step_name}")

        # Create cmake/ folder if needed
        if self.use_cmake_modules:
            print("→ Creating cmake/ modules...")
            CMakeModuleGenerator.create_cmake_modules(self.project_path, self.project_name)
            print("  ✅ CMake modules created")

        return True


def main():
    parser = argparse.ArgumentParser(description="Initialize modern C++ project")
    parser.add_argument("name", help="Project name")
    parser.add_argument("--type", choices=["cli", "gui", "static-lib", "shared-lib", "header-only"],
                       default="cli", help="Project type (default: cli)")
    parser.add_argument("--cpp-std", type=int, choices=[11, 14, 17, 20, 23],
                       default=17, help="C++ standard (default: 17)")
    parser.add_argument("--gui-framework", choices=["qt6", "wxwidgets", "imgui"],
                       default="qt6", help="GUI framework for GUI projects (default: qt6)")
    parser.add_argument("--compiler", help="C++ compiler (auto-detected if not specified)")
    parser.add_argument("--use-cmake-modules", action="store_true",
                       help="Create cmake/ modules for complex projects")
    parser.add_argument("--interactive", action="store_true",
                       help="Interactive mode with prompts")

    args = parser.parse_args()

    initializer = ProjectInitializer(args.name, args.type, args.interactive)
    initializer.cpp_standard = args.cpp_std
    if args.gui_framework:
        initializer.gui_framework = args.gui_framework
    if args.compiler:
        initializer.compiler = args.compiler
    initializer.use_cmake_modules = args.use_cmake_modules

    if initializer.initialize():
        print(f"\n✅ Project '{args.name}' created successfully!\n")
        print(f"Next steps:")
        print(f"  cd {args.name}")
        print(f"  cmake -B build")
        print(f"  cmake --build build")
        return 0
    else:
        print(f"\n❌ Failed to create project")
        return 1


if __name__ == "__main__":
    sys.exit(main())
