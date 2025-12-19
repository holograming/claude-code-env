#!/usr/bin/env python3
"""
C++ Development Tools Detector

Detects available compilers, build tools, package managers, and code quality tools.
"""

import json
import platform
import re
import subprocess
import sys
from typing import Dict, Optional, Tuple


class ToolDetector:
    """Detect available C++ development tools."""

    def __init__(self):
        self.os_name = platform.system()
        self.tools = {
            'compilers': {},
            'build_tools': {},
            'package_managers': {},
            'code_quality_tools': {}
        }

    def run_command(self, cmd: str) -> Tuple[bool, str]:
        """Run command and return (success, output)."""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            return result.returncode == 0, result.stdout.strip() + result.stderr.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, ""

    def detect_gcc(self) -> Optional[str]:
        """Detect GCC compiler."""
        success, output = self.run_command("g++ --version")
        if success:
            match = re.search(r'(\d+\.\d+\.\d+)', output)
            if match:
                return match.group(1)
        return None

    def detect_clang(self) -> Optional[str]:
        """Detect Clang compiler."""
        success, output = self.run_command("clang++ --version")
        if success:
            match = re.search(r'version (\d+\.\d+\.\d+)', output)
            if match:
                return match.group(1)
        return None

    def detect_msvc(self) -> Optional[str]:
        """Detect MSVC compiler (Windows)."""
        if self.os_name != "Windows":
            return None
        success, output = self.run_command("cl.exe")
        if success or "Version" in output:
            match = re.search(r'(\d+\.\d+\.\d+)', output)
            if match:
                return match.group(1)
        return None

    def detect_apple_clang(self) -> Optional[str]:
        """Detect Apple Clang compiler."""
        success, output = self.run_command("clang++ --version")
        if success and "Apple" in output:
            match = re.search(r'version (\d+\.\d+)', output)
            if match:
                return match.group(1)
        return None

    def detect_compilers(self) -> None:
        """Detect all installed compilers."""
        compilers = {}

        # GCC
        gcc_version = self.detect_gcc()
        if gcc_version:
            compilers['GCC'] = {
                'version': gcc_version,
                'path': self._find_path('g++'),
                'status': '✅ Available'
            }

        # Clang
        clang_version = self.detect_clang()
        if clang_version:
            compilers['Clang'] = {
                'version': clang_version,
                'path': self._find_path('clang++'),
                'status': '✅ Available'
            }

        # MSVC
        msvc_version = self.detect_msvc()
        if msvc_version:
            compilers['MSVC'] = {
                'version': msvc_version,
                'path': 'cl.exe',
                'status': '✅ Available'
            }

        # Apple Clang
        apple_clang_version = self.detect_apple_clang()
        if apple_clang_version:
            compilers['Apple Clang'] = {
                'version': apple_clang_version,
                'path': self._find_path('clang++'),
                'status': '✅ Available'
            }

        self.tools['compilers'] = compilers if compilers else {'None': {'status': '❌ No compilers detected'}}

    def detect_cmake(self) -> None:
        """Detect CMake."""
        success, output = self.run_command("cmake --version")
        if success:
            match = re.search(r'cmake version (\d+\.\d+\.\d+)', output)
            if match:
                self.tools['build_tools']['CMake'] = {
                    'version': match.group(1),
                    'path': self._find_path('cmake'),
                    'status': '✅ Available'
                }

    def detect_ninja(self) -> None:
        """Detect Ninja build system."""
        success, output = self.run_command("ninja --version")
        if success:
            self.tools['build_tools']['Ninja'] = {
                'version': output.strip(),
                'path': self._find_path('ninja'),
                'status': '✅ Available'
            }

    def detect_make(self) -> None:
        """Detect Make build tool."""
        success, output = self.run_command("make --version")
        if success:
            match = re.search(r'Make (\d+\.\d+)', output)
            version = match.group(1) if match else "Unknown"
            self.tools['build_tools']['Make'] = {
                'version': version,
                'path': self._find_path('make'),
                'status': '✅ Available'
            }

    def detect_build_tools(self) -> None:
        """Detect build tools."""
        self.detect_cmake()
        self.detect_ninja()
        self.detect_make()

        if not self.tools['build_tools']:
            self.tools['build_tools']['None'] = {'status': '❌ No build tools detected'}

    def detect_conan(self) -> None:
        """Detect Conan package manager."""
        success, output = self.run_command("conan --version")
        if success:
            match = re.search(r'Conan version (\d+\.\d+\.\d+)', output)
            if match:
                self.tools['package_managers']['Conan'] = {
                    'version': match.group(1),
                    'path': self._find_path('conan'),
                    'status': '✅ Available'
                }

    def detect_vcpkg(self) -> None:
        """Detect vcpkg package manager."""
        import os
        vcpkg_root = os.environ.get('VCPKG_ROOT')
        if vcpkg_root:
            self.tools['package_managers']['vcpkg'] = {
                'root': vcpkg_root,
                'path': vcpkg_root,
                'status': '✅ Available (VCPKG_ROOT set)'
            }

    def detect_package_managers(self) -> None:
        """Detect package managers."""
        self.detect_conan()
        self.detect_vcpkg()

        if not self.tools['package_managers']:
            self.tools['package_managers']['None'] = {'status': '❌ No package managers detected'}

    def detect_clang_format(self) -> None:
        """Detect clang-format."""
        success, output = self.run_command("clang-format --version")
        if success:
            match = re.search(r'version (\d+\.\d+\.\d+)', output)
            if match:
                self.tools['code_quality_tools']['clang-format'] = {
                    'version': match.group(1),
                    'path': self._find_path('clang-format'),
                    'status': '✅ Available'
                }

    def detect_clang_tidy(self) -> None:
        """Detect clang-tidy."""
        success, output = self.run_command("clang-tidy --version")
        if success:
            match = re.search(r'version (\d+\.\d+\.\d+)', output)
            if match:
                self.tools['code_quality_tools']['clang-tidy'] = {
                    'version': match.group(1),
                    'path': self._find_path('clang-tidy'),
                    'status': '✅ Available'
                }

    def detect_code_quality_tools(self) -> None:
        """Detect code quality tools."""
        self.detect_clang_format()
        self.detect_clang_tidy()

        if not self.tools['code_quality_tools']:
            self.tools['code_quality_tools']['None'] = {'status': '❌ No tools detected'}

    def detect_all(self) -> None:
        """Detect all tools."""
        print("🔍 Detecting C++ development tools...\n")
        self.detect_compilers()
        self.detect_build_tools()
        self.detect_package_managers()
        self.detect_code_quality_tools()

    def _find_path(self, tool: str) -> str:
        """Find tool path."""
        try:
            result = subprocess.run(
                f"which {tool}" if self.os_name != "Windows" else f"where {tool}",
                shell=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except:
            return "Unknown"

    def print_report(self) -> None:
        """Print human-readable report."""
        print("=" * 60)
        print("C++ Development Tools Report")
        print("=" * 60)
        print(f"\nPlatform: {self.os_name}")
        print()

        # Compilers
        print("📦 Compilers:")
        print("-" * 60)
        for name, info in self.tools['compilers'].items():
            if 'version' in info:
                print(f"  {name:20} {info['status']:15} v{info['version']}")
                print(f"  {'Path:':20} {info.get('path', 'N/A')}")
            else:
                print(f"  {info['status']}")

        # Build Tools
        print("\n🔨 Build Tools:")
        print("-" * 60)
        for name, info in self.tools['build_tools'].items():
            if 'version' in info:
                print(f"  {name:20} {info['status']:15} v{info['version']}")
                print(f"  {'Path:':20} {info.get('path', 'N/A')}")
            else:
                print(f"  {info['status']}")

        # Package Managers
        print("\n📚 Package Managers:")
        print("-" * 60)
        for name, info in self.tools['package_managers'].items():
            if 'version' in info:
                print(f"  {name:20} {info['status']:15} v{info['version']}")
            elif 'root' in info:
                print(f"  {name:20} {info['status']}")
                print(f"  {'Root:':20} {info['root']}")
            else:
                print(f"  {info['status']}")

        # Code Quality Tools
        print("\n✨ Code Quality Tools:")
        print("-" * 60)
        for name, info in self.tools['code_quality_tools'].items():
            if 'version' in info:
                print(f"  {name:20} {info['status']:15} v{info['version']}")
                print(f"  {'Path:':20} {info.get('path', 'N/A')}")
            else:
                print(f"  {info['status']}")

        print("\n" + "=" * 60)

    def get_tools_dict(self) -> Dict:
        """Return tools as dictionary."""
        return self.tools

    def print_json(self) -> None:
        """Print report as JSON."""
        print(json.dumps(self.tools, indent=2))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Detect C++ development tools")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--check", choices=["compilers", "build-tools", "package-managers", "quality-tools"],
                       help="Check specific category")

    args = parser.parse_args()

    detector = ToolDetector()
    detector.detect_all()

    if args.json:
        detector.print_json()
    else:
        detector.print_report()

    # Exit with error if critical tools missing
    if not detector.tools['compilers'] or "No compilers" in str(detector.tools['compilers']):
        print("\n⚠️  Warning: No C++ compiler detected!")
        print("Please install GCC, Clang, or MSVC to compile C++ projects.")
        return 1

    if not detector.tools['build_tools'] or "No build tools" in str(detector.tools['build_tools']):
        print("\n⚠️  Warning: No build tools detected!")
        print("Please install CMake to build C++ projects.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
