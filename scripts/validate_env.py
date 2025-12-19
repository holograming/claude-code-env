#!/usr/bin/env python3
"""
C++ Environment Validator

Pre-flight checks before project creation:
- CMake version >= 3.15
- C++ compiler availability
- VCPKG_ROOT validation (path length, existence)
- Windows long path setting
- Disk space

Usage:
    python scripts/validate_env.py
    python scripts/validate_env.py --fix
"""

import os
import sys
import platform
import subprocess
import re
from pathlib import Path
from typing import List, Tuple


class EnvironmentValidator:
    """Validate C++ development environment."""

    def __init__(self, auto_fix: bool = False):
        self.auto_fix = auto_fix
        self.issues = []
        self.warnings = []

    def check_cmake(self) -> bool:
        """Check CMake installation and version."""
        try:
            result = subprocess.run(
                ["cmake", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            version_match = re.search(r"cmake version (\d+)\.(\d+)\.(\d+)", result.stdout)

            if version_match:
                major, minor, patch = map(int, version_match.groups())
                version_str = f"{major}.{minor}.{patch}"

                if (major, minor) >= (3, 15):
                    print(f"✓ CMake {version_str} (>= 3.15 required)")
                    return True
                else:
                    self.issues.append(f"CMake {version_str} found, but 3.15+ required")
                    print(f"❌ CMake {version_str} (< 3.15)")
                    return False
            else:
                self.issues.append("CMake version could not be determined")
                return False

        except (FileNotFoundError, subprocess.TimeoutExpired):
            self.issues.append("CMake not found in PATH")
            print("❌ CMake not found")
            return False

    def check_compiler(self) -> bool:
        """Check C++ compiler availability."""
        cxx = os.environ.get("CXX")

        if cxx:
            print(f"✓ CXX environment variable set: {cxx}")
            return True

        # Try to detect compilers
        compilers = {
            "Windows": ["cl", "g++", "clang++"],
            "Linux": ["g++", "clang++"],
            "Darwin": ["clang++", "g++"],
        }

        os_name = platform.system()
        to_check = compilers.get(os_name, ["g++", "clang++"])

        for compiler in to_check:
            try:
                result = subprocess.run(
                    [compiler, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    print(f"✓ Detected C++ compiler: {compiler}")
                    return True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        self.warnings.append(
            "No C++ compiler detected. Set CXX environment variable."
        )
        print("⚠ No C++ compiler found")
        return False

    def check_vcpkg(self) -> bool:
        """Check VCPKG_ROOT configuration."""
        vcpkg_root = os.environ.get("VCPKG_ROOT")

        if not vcpkg_root:
            print("ℹ VCPKG_ROOT not set (vcpkg not configured)")
            return True  # Not an error

        # Check existence
        vcpkg_path = Path(vcpkg_root)
        if not vcpkg_path.exists():
            self.warnings.append(
                f"VCPKG_ROOT points to non-existent path: {vcpkg_root}"
            )
            print(f"⚠ VCPKG_ROOT path doesn't exist: {vcpkg_root}")
            return False

        # Check path length (Windows)
        if platform.system() == "Windows":
            path_len = len(str(vcpkg_path))
            if path_len > 200:
                self.warnings.append(
                    f"VCPKG_ROOT path is long ({path_len} chars). May cause MAX_PATH issues."
                )
                print(f"⚠ VCPKG_ROOT path: {path_len} characters (recommend <200)")
            else:
                print(f"✓ VCPKG_ROOT: {vcpkg_root} ({path_len} chars)")
        else:
            print(f"✓ VCPKG_ROOT: {vcpkg_root}")

        return True

    def check_windows_long_paths(self) -> bool:
        """Check if Windows long path support is enabled."""
        if platform.system() != "Windows":
            return True  # Not applicable

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    'Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem" -Name "LongPathsEnabled"',
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if "LongPathsEnabled" in result.stdout and ": 1" in result.stdout:
                print("✓ Windows long paths enabled")
                return True
            else:
                self.warnings.append(
                    "Windows long paths not enabled (may cause MAX_PATH errors)"
                )
                print("⚠ Windows long paths not enabled")

                if self.auto_fix:
                    print("  → Attempting to enable long paths...")
                    self.fix_windows_long_paths()

                return False
        except (subprocess.TimeoutExpired, Exception):
            self.warnings.append("Could not check Windows long path setting")
            return True  # Don't fail, just warn

    def fix_windows_long_paths(self) -> bool:
        """Enable Windows long path support (requires admin)."""
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    'New-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem" '
                    '-Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force',
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                print("  ✓ Long paths enabled (reboot required)")
                return True
            else:
                print("  ❌ Failed (requires admin privileges)")
                return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

    def check_disk_space(self) -> bool:
        """Check available disk space (warn if <10GB)."""
        try:
            import shutil

            total, used, free = shutil.disk_usage(Path.cwd())
            free_gb = free // (2**30)  # Convert to GB

            if free_gb < 10:
                self.warnings.append(
                    f"Low disk space: {free_gb}GB available (recommend 10GB+)"
                )
                print(f"⚠ Disk space: {free_gb}GB available")
            else:
                print(f"✓ Disk space: {free_gb}GB available")

            return True
        except Exception:
            return True  # Don't fail on this check

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating C++ development environment...\n")

        checks = [
            ("CMake", self.check_cmake),
            ("C++ Compiler", self.check_compiler),
            ("vcpkg Configuration", self.check_vcpkg),
            ("Disk Space", self.check_disk_space),
        ]

        if platform.system() == "Windows":
            checks.append(("Windows Long Paths", self.check_windows_long_paths))

        all_passed = True
        for name, check_func in checks:
            try:
                result = check_func()
                if not result and name in ["CMake"]:  # Critical checks
                    all_passed = False
            except Exception as e:
                print(f"❌ {name} check failed: {e}")
                all_passed = False

        print("\n" + "=" * 50)

        if self.issues:
            print("\n❌ Critical Issues:")
            for issue in self.issues:
                print(f"  • {issue}")

        if self.warnings:
            print("\n⚠ Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")

        if all_passed and not self.issues:
            print("\n✅ Environment ready for C++ development")
            return True
        else:
            print("\n❌ Environment validation failed")
            print("\nRecommended actions:")
            if "CMake" in str(self.issues):
                print("  1. Install CMake 3.15+: https://cmake.org/download/")
            if "compiler" in str(self.warnings):
                print("  2. Install C++ compiler (MSVC/GCC/Clang)")
            if "long path" in str(self.warnings):
                print("  3. Enable long paths: Run as admin and reboot")

            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate C++ development environment")
    parser.add_argument(
        "--fix", action="store_true", help="Attempt to auto-fix issues (may require admin)"
    )

    args = parser.parse_args()

    validator = EnvironmentValidator(auto_fix=args.fix)
    success = validator.validate_all()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
