#!/usr/bin/env python3
"""
C++ Project Initialization with Automation Engine

Orchestrates project creation with auto-selection of frameworks, dependencies,
and error recovery. Used by Claude to create ready-to-build C++ projects.

Usage:
    python scripts/init_project.py myproject --type gui --gui-framework wxwidgets
    python scripts/init_project.py myapp --type cli
    python scripts/init_project.py --validate-only
"""

import os
import sys
import json
import platform
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class AutomationEngine:
    """Orchestrates C++ project generation with auto-decision making and error recovery."""

    def __init__(self, decisions_file: str = None, error_patterns_file: str = None):
        """Initialize the automation engine with decision and error pattern databases."""
        self.decisions_file = decisions_file or self._find_decisions_file()
        self.error_patterns_file = error_patterns_file or self._find_error_patterns_file()

        self.decisions = self._load_json(self.decisions_file)
        self.error_patterns = self._load_json(self.error_patterns_file)
        self.max_retry_attempts = 3

    def _find_decisions_file(self) -> str:
        """Find decisions.json in the cpp-dev-skills directory."""
        candidates = [
            Path(__file__).parent.parent / "skills" / "cpp-dev-skills" / "automation" / "decisions.json",
            Path.cwd() / "automation" / "decisions.json",
            Path(__file__).parent / "decisions.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        raise FileNotFoundError(f"decisions.json not found in {[str(c) for c in candidates]}")

    def _find_error_patterns_file(self) -> str:
        """Find error-patterns.json in the cpp-dev-skills directory."""
        candidates = [
            Path(__file__).parent.parent / "skills" / "cpp-dev-skills" / "automation" / "error-patterns.json",
            Path.cwd() / "automation" / "error-patterns.json",
            Path(__file__).parent / "error-patterns.json",
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        raise FileNotFoundError(f"error-patterns.json not found in {[str(c) for c in candidates]}")

    def _load_json(self, filepath: str) -> dict:
        """Load and parse JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load {filepath}: {e}")
            return {}

    def parse_user_request(self, user_request: str) -> Dict[str, any]:
        """Extract keywords and features from user request."""
        keywords = []
        request_lower = user_request.lower()

        # Extract framework mentions
        gui_frameworks = self.decisions.get("gui_frameworks", {}).keys()
        mentioned_frameworks = [f for f in gui_frameworks if f.lower() in request_lower]

        # Extract project type keywords
        project_type = "cli"
        if any(word in request_lower for word in ["gui", "window", "ui", "app", "viewer", "viewer", "graphics"]):
            project_type = "gui"
        elif any(word in request_lower for word in ["library", "lib", "static", "shared"]):
            project_type = "library"

        # Extract use case keywords
        use_cases = []
        if "3d" in request_lower or "viewer" in request_lower:
            use_cases.append("3d_viewer")
        if "enterprise" in request_lower or "professional" in request_lower:
            use_cases.append("enterprise_ui")
        if "game" in request_lower or "debug" in request_lower:
            use_cases.append("game_tools")
        if "simple" in request_lower or "minimal" in request_lower:
            use_cases.append("minimal_gui")

        return {
            "project_type": project_type,
            "mentioned_frameworks": mentioned_frameworks,
            "use_cases": use_cases,
            "keywords": request_lower.split(),
        }

    def auto_select_gui_framework(self, request_info: Dict) -> str:
        """Auto-select GUI framework based on use case keywords."""
        frameworks = self.decisions.get("gui_frameworks", {})

        # Score each framework based on use case matches
        scores = {}
        for framework_name, framework_info in frameworks.items():
            score = 0
            # Check if use case keywords match auto_select_when
            for use_case in request_info.get("use_cases", []):
                if use_case in framework_info.get("auto_select_when", []):
                    score += 10
            # Check for keyword matches in use_case_keywords
            for keyword in request_info.get("keywords", []):
                if keyword in str(framework_info.get("use_case_keywords", [])):
                    score += 5
            if score > 0:
                scores[framework_name] = score

        if not scores:
            # Default to wxWidgets if no clear match
            return "wxwidgets"

        # Return framework with highest score
        selected = max(scores.items(), key=lambda x: x[1])[0]

        # Check if user explicitly mentioned a framework
        if request_info.get("mentioned_frameworks"):
            mentioned = request_info["mentioned_frameworks"][0]
            if mentioned in frameworks:
                # Ask if user prefers the mentioned framework despite time trade-offs
                logger.info(f"⚠ Conflict: Use case suggests {selected}, but you mentioned {mentioned}")
                return mentioned  # Respect user preference

        return selected

    def validate_environment(self, fix: bool = False) -> Tuple[bool, List[str]]:
        """Validate C++ development environment. Returns (success, issues)."""
        issues = []

        # Check CMake
        try:
            result = subprocess.run(
                ["cmake", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                issues.append("CMake not found or not in PATH")
        except FileNotFoundError:
            issues.append("CMake not found. Install from https://cmake.org/download/")

        # Check C++ compiler
        cxx = os.environ.get("CXX")
        if not cxx:
            # Try to detect
            compilers = ["g++", "clang++", "cl"] if platform.system() == "Windows" else ["g++", "clang++"]
            found = False
            for compiler in compilers:
                try:
                    subprocess.run([compiler, "--version"], capture_output=True, timeout=2, check=True)
                    found = True
                    break
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            if not found:
                issues.append("No C++ compiler detected. Set CXX environment variable.")

        return len(issues) == 0, issues

    def match_error_pattern(self, error_output: str) -> Optional[Dict]:
        """Find matching error pattern in error_output."""
        patterns = self.error_patterns.get("patterns", [])
        for pattern in patterns:
            regex = pattern.get("regex", "")
            # Check if pattern applies to current platform
            pattern_platforms = pattern.get("platform", ["all"])
            current_platform = platform.system()
            if "all" not in pattern_platforms and current_platform not in pattern_platforms:
                continue

            if re.search(regex, error_output, re.IGNORECASE):
                return pattern
        return None

    def execute_auto_fix(self, pattern: Dict) -> bool:
        """Execute auto-fix commands for matched error pattern."""
        auto_fixes = pattern.get("auto_fix", [])
        if not auto_fixes:
            return False

        for fix in auto_fixes:
            method = fix.get("method", "")

            # Get platform-specific command
            if platform.system() == "Windows":
                cmd = fix.get("command_windows") or fix.get("command")
            else:
                cmd = fix.get("command_linux") or fix.get("command")

            if not cmd:
                logger.info(f"  → {fix.get('message', method)}")
                continue

            try:
                logger.info(f"  → Executing fix: {method}")
                result = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                if result.returncode == 0:
                    logger.info(f"  ✓ Fixed: {method}")
                    return True
            except subprocess.TimeoutExpired:
                logger.warning(f"  ✗ Fix timeout: {method}")
            except Exception as e:
                logger.warning(f"  ✗ Fix failed: {method} - {e}")

        return False

    def build_with_validation(self, project_dir: Path) -> Tuple[bool, str]:
        """Build project with error detection and auto-fix. Returns (success, message)."""
        project_dir = Path(project_dir)
        os.chdir(project_dir)

        for attempt in range(self.max_retry_attempts):
            logger.info(f"\n📦 Build attempt {attempt + 1}/{self.max_retry_attempts}")

            # Step 1: CMake configure
            logger.info("  → Running: cmake -B build")
            result = subprocess.run(
                ["cmake", "-B", "build"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                error_output = result.stderr + result.stdout
                logger.error(f"  ✗ CMake configure failed")

                # Try to match and fix error
                pattern = self.match_error_pattern(error_output)
                if pattern:
                    logger.warning(f"  → {pattern.get('user_message', 'Attempting auto-fix...')}")
                    if self.execute_auto_fix(pattern):
                        continue  # Retry after fix

                # Try fallback
                fallbacks = pattern.get("fallback", []) if pattern else []
                for fallback in fallbacks:
                    if self.execute_auto_fix({"auto_fix": [fallback]}):
                        continue

                return False, f"CMake configure failed: {error_output[:300]}"

            # Step 2: CMake build
            logger.info("  → Running: cmake --build build")
            result = subprocess.run(
                ["cmake", "--build", "build"],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                error_output = result.stderr + result.stdout
                logger.error(f"  ✗ Build failed")

                # Try to match and fix error
                pattern = self.match_error_pattern(error_output)
                if pattern:
                    logger.warning(f"  → {pattern.get('user_message', 'Attempting auto-fix...')}")
                    if self.execute_auto_fix(pattern):
                        continue  # Retry after fix

                # Try fallback
                fallbacks = pattern.get("fallback", []) if pattern else []
                for fallback in fallbacks:
                    if self.execute_auto_fix({"auto_fix": [fallback]}):
                        continue

                return False, f"Build failed: {error_output[:300]}"

            # Success!
            logger.info("  ✓ Build successful")
            return True, "Build completed successfully"

        return False, f"Build failed after {self.max_retry_attempts} attempts"

    def create_basic_project(self, project_name: str, project_type: str,
                            gui_framework: str = None) -> bool:
        """Create basic project structure."""
        project_dir = Path(project_name)
        project_dir.mkdir(exist_ok=True)

        # Create directory structure
        (project_dir / "src").mkdir(exist_ok=True)
        (project_dir / "include").mkdir(exist_ok=True)
        (project_dir / ".gitignore").write_text("build/\n.vs/\n*.o\n*.exe\n")

        # Create CMakeLists.txt
        if project_type == "gui" and gui_framework:
            self._create_gui_cmakelists(project_dir, project_name, gui_framework)
        else:
            self._create_cli_cmakelists(project_dir, project_name)

        # Create main.cpp
        if project_type == "gui":
            self._create_gui_main(project_dir, gui_framework, project_name)
        else:
            self._create_cli_main(project_dir, project_name)

        # Create vcpkg.json if needed
        if gui_framework:
            self._create_vcpkg_json(project_dir, gui_framework)

        # Create .clang-format configuration (Google C++ Style Guide)
        self._create_clang_format_config(project_dir)

        return True

    def _create_cli_cmakelists(self, project_dir: Path, project_name: str):
        """Create CMakeLists.txt for CLI project."""
        cmake_content = f"""cmake_minimum_required(VERSION 3.15)
project({project_name} VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable({project_name} src/main.cpp)
target_include_directories({project_name} PRIVATE include)

target_compile_options({project_name} PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic>
)
"""
        (project_dir / "CMakeLists.txt").write_text(cmake_content)

    def _create_gui_cmakelists(self, project_dir: Path, project_name: str, framework: str):
        """Create CMakeLists.txt for GUI project."""
        # Framework-specific CMakeLists.txt
        if framework == "qt6":
            find_package = "find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets)"
            target_link = "target_link_libraries({} PRIVATE Qt6::Core Qt6::Gui Qt6::Widgets)".format(project_name)
        elif framework == "wxwidgets":
            find_package = "find_package(wxWidgets REQUIRED COMPONENTS core base)"
            target_link = "target_link_libraries({} PRIVATE {}::core {}::base)".format(project_name, "${wxWidgets_LIBRARIES}")
        else:  # fltk, imgui, etc.
            find_package = f"find_package({framework.upper()} REQUIRED)"
            target_link = f"target_link_libraries({project_name} PRIVATE {framework.upper()}::{{framework}})"

        cmake_content = f"""cmake_minimum_required(VERSION 3.15)
project({project_name} VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Use vcpkg if available
if(DEFINED ENV{{VCPKG_ROOT}})
    set(CMAKE_TOOLCHAIN_FILE "$ENV{{VCPKG_ROOT}}/scripts/buildsystems/vcpkg.cmake")
endif()

{find_package}

add_executable({project_name} src/main.cpp)
target_include_directories({project_name} PRIVATE include)
{target_link}

target_compile_options({project_name} PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
    $<$<NOT:$<CXX_COMPILER_ID:MSVC>>:-Wall -Wextra -Wpedantic>
)
"""
        (project_dir / "CMakeLists.txt").write_text(cmake_content)

    def _create_cli_main(self, project_dir: Path, project_name: str = None):
        """Create basic CLI main.cpp with Google C++ Style Guide compliance."""
        if project_name is None:
            project_name = project_dir.name

        main_content = f"""// {project_name} - Command-line application
// Copyright (c) 2025

#include <iostream>

int main() {{
  std::cout << "Hello from {project_name}!" << std::endl;
  return 0;
}}
"""
        (project_dir / "src" / "main.cpp").write_text(main_content)

    def _create_gui_main(self, project_dir: Path, framework: str, project_name: str = None):
        """Create basic GUI main.cpp with Google C++ Style Guide compliance."""
        if project_name is None:
            project_name = project_dir.name

        if framework == "qt6":
            main_content = f"""// {project_name} - Qt6 GUI Application
// Copyright (c) 2025

#include <QApplication>
#include <QMainWindow>
#include <QLabel>

int main(int argc, char* argv[]) {{
  QApplication app(argc, argv);
  QMainWindow window;
  window.setWindowTitle("Qt Application");
  window.resize(400, 300);
  window.show();
  return app.exec();
}}
"""
        elif framework == "wxwidgets":
            main_content = f"""// {project_name} - wxWidgets GUI Application
// Copyright (c) 2025

#include <wx/wx.h>

class MainFrame : public wxFrame {{
 public:
  MainFrame() : wxFrame(nullptr, wxID_ANY, "wxWidgets Application") {{
    wxPanel* panel = new wxPanel(this);
    new wxStaticText(panel, wxID_ANY, "Hello, wxWidgets!");
    SetSize(400, 300);
  }}
}};

class MainApp : public wxApp {{
 public:
  bool OnInit() override {{
    MainFrame* frame = new MainFrame();
    frame->Show();
    return true;
  }}
}};

wxIMPLEMENT_APP(MainApp);
"""
        else:
            main_content = f"""// {project_name} - {framework.upper()} GUI Application
// Copyright (c) 2025

#include <iostream>

int main() {{
  std::cout << "Hello from {project_name}!" << std::endl;
  return 0;
}}
"""
        (project_dir / "src" / "main.cpp").write_text(main_content)

    def _create_vcpkg_json(self, project_dir: Path, framework: str):
        """Create vcpkg.json manifest."""
        dependencies = []
        if framework == "qt6":
            dependencies = ["qt6-base"]
        elif framework == "wxwidgets":
            dependencies = ["wxwidgets"]
        elif framework == "fltk":
            dependencies = ["fltk"]
        elif framework == "imgui":
            dependencies = ["imgui"]

        vcpkg_content = {
            "name": project_dir.name,
            "version": "1.0.0",
            "dependencies": dependencies
        }
        (project_dir / "vcpkg.json").write_text(json.dumps(vcpkg_content, indent=2))

    def _create_clang_format_config(self, project_dir: Path):
        """Create .clang-format configuration (Google C++ Style Guide)."""
        clang_format_config = """---
Language: Cpp
BasedOnStyle: Google
IndentWidth: 4
ColumnLimit: 120
PointerAlignment: Left
AllowShortFunctionsOnASingleLine: Empty
BreakBeforeBraces: Attach
---
"""
        (project_dir / ".clang-format").write_text(clang_format_config)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="C++ Project Initialization with Automation")
    parser.add_argument("project_name", nargs="?", help="Name of the project to create")
    parser.add_argument("--type", choices=["cli", "gui", "library"], default="cli",
                       help="Project type")
    parser.add_argument("--gui-framework", choices=["qt6", "wxwidgets", "fltk", "imgui"],
                       help="GUI framework (for --type gui)")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate environment, don't create project")
    parser.add_argument("--build", action="store_true",
                       help="Build project after creation")
    parser.add_argument("--user-request", help="Original user request for keyword extraction")

    args = parser.parse_args()

    # Initialize automation engine
    try:
        engine = AutomationEngine()
    except FileNotFoundError as e:
        logger.error(f"Failed to initialize automation engine: {e}")
        return 1

    # Validate environment
    logger.info("🔍 Validating C++ development environment...")
    success, issues = engine.validate_environment()
    if issues:
        for issue in issues:
            logger.warning(f"  ⚠ {issue}")
    if not success:
        logger.error("❌ Environment validation failed")
        return 1
    logger.info("✓ Environment validation passed")

    if args.validate_only:
        return 0

    if not args.project_name:
        logger.error("Project name required")
        return 1

    # Parse user request if provided
    gui_framework = args.gui_framework
    if args.user_request and args.type == "gui" and not gui_framework:
        request_info = engine.parse_user_request(args.user_request)
        gui_framework = engine.auto_select_gui_framework(request_info)
        logger.info(f"📋 Auto-selected GUI framework: {gui_framework}")

    # Create project
    logger.info(f"📁 Creating {args.type} project: {args.project_name}")
    if engine.create_basic_project(args.project_name, args.type, gui_framework):
        logger.info(f"✓ Project created: {args.project_name}/")
    else:
        logger.error("Failed to create project")
        return 1

    # Build if requested
    if args.build:
        logger.info(f"🔨 Building project...")
        success, message = engine.build_with_validation(args.project_name)
        if success:
            logger.info(f"✅ {message}")
            return 0
        else:
            logger.error(f"❌ {message}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
