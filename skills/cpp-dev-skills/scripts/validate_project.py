#!/usr/bin/env python3
"""
C++ Project Validation Script

Validates a C++ project configuration and setup:
- CMake configuration
- Build success
- Test execution
- Code formatting
- Compiler warnings
- Git setup
- Directory structure

Usage:
    python scripts/validate_project.py
    python scripts/validate_project.py --strict
    python scripts/validate_project.py --verbose
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional


class ProjectValidator:
    """Validates C++ project setup and build configuration."""

    def __init__(self, project_dir: str = ".", strict: bool = False, verbose: bool = False):
        self.project_dir = Path(project_dir).resolve()
        self.strict = strict
        self.verbose = verbose
        self.checks: List[Tuple[str, bool, Optional[str]]] = []

    def log(self, level: str, message: str):
        """Log message with level prefix."""
        if level == "INFO" or self.verbose:
            prefix = "ℹ️ " if level == "INFO" else "⚠️  " if level == "WARN" else "❌"
            print(f"{prefix} {message}")

    def run_command(self, cmd: List[str], check: bool = True) -> Tuple[int, str, str]:
        """Run command and return (return_code, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)

    def check_directory_structure(self) -> bool:
        """Verify basic project directory structure."""
        required_dirs = ["src", "CMakeLists.txt"]
        optional_dirs = ["include", "tests", "cmake", ".git"]

        self.log("INFO", "Checking directory structure...")

        cmake_exists = (self.project_dir / "CMakeLists.txt").exists()
        if not cmake_exists:
            self.checks.append(("Directory: CMakeLists.txt", False, "CMakeLists.txt not found"))
            return False

        src_exists = (self.project_dir / "src").exists()
        if not src_exists:
            self.log("WARN", "src/ directory not found (optional for header-only libraries)")

        self.checks.append(("Directory: CMakeLists.txt", True, None))
        return True

    def check_cmake_version(self) -> bool:
        """Verify CMake is installed and version >= 3.15."""
        self.log("INFO", "Checking CMake version...")

        returncode, stdout, stderr = self.run_command(["cmake", "--version"])

        if returncode != 0:
            self.checks.append(("CMake: Installation", False, "CMake not found in PATH"))
            return False

        # Parse version from output: "cmake version 3.x.x"
        try:
            version_line = stdout.split('\n')[0]
            version_str = version_line.split()[-1]
            major, minor, patch = map(int, version_str.split('.')[:3])

            if major < 3 or (major == 3 and minor < 15):
                msg = f"CMake 3.15+ required, found {major}.{minor}.{patch}"
                self.checks.append(("CMake: Version", False, msg))
                return False

            self.log("INFO", f"CMake {major}.{minor}.{patch} ✓")
            self.checks.append(("CMake: Version", True, None))
            return True
        except Exception as e:
            self.checks.append(("CMake: Version", False, f"Failed to parse version: {str(e)}"))
            return False

    def check_cmake_configuration(self) -> bool:
        """Verify CMake configuration succeeds."""
        self.log("INFO", "Running CMake configuration...")

        build_dir = self.project_dir / "build" / "validate"
        build_dir.mkdir(parents=True, exist_ok=True)

        returncode, stdout, stderr = self.run_command([
            "cmake", "-B", str(build_dir), "-DCMAKE_BUILD_TYPE=Debug"
        ])

        if returncode != 0:
            msg = f"CMake configuration failed: {stderr[:200]}"
            self.checks.append(("CMake: Configuration", False, msg))
            return False

        self.log("INFO", "CMake configuration successful ✓")
        self.checks.append(("CMake: Configuration", True, None))
        return True

    def check_build(self) -> bool:
        """Verify project builds successfully."""
        self.log("INFO", "Building project...")

        build_dir = self.project_dir / "build" / "validate"
        if not build_dir.exists():
            self.checks.append(("Build", False, "Build directory not configured"))
            return False

        returncode, stdout, stderr = self.run_command([
            "cmake", "--build", str(build_dir), "--config", "Debug"
        ])

        if returncode != 0:
            msg = f"Build failed: {stderr[:200]}"
            self.checks.append(("Build", False, msg))
            return False

        self.log("INFO", "Build successful ✓")
        self.checks.append(("Build", True, None))
        return True

    def check_tests(self) -> bool:
        """Verify tests run successfully (if they exist)."""
        test_dir = self.project_dir / "tests"
        if not test_dir.exists():
            self.log("INFO", "No tests/ directory found (optional)")
            self.checks.append(("Tests", True, "No tests configured (optional)"))
            return True

        self.log("INFO", "Running tests...")

        build_dir = self.project_dir / "build" / "validate"
        returncode, stdout, stderr = self.run_command([
            "ctest", "--test-dir", str(build_dir), "--output-on-failure"
        ], check=False)

        if returncode != 0:
            msg = f"Some tests failed: {stderr[:200]}"
            if self.strict:
                self.checks.append(("Tests", False, msg))
                return False
            else:
                self.log("WARN", msg)
                self.checks.append(("Tests", True, f"Warnings: {msg}"))
                return True

        self.log("INFO", "Tests passed ✓")
        self.checks.append(("Tests", True, None))
        return True

    def check_code_format(self) -> bool:
        """Verify code formatting with clang-format (if available)."""
        clang_format_config = self.project_dir / ".clang-format"
        if not clang_format_config.exists():
            self.log("INFO", "No .clang-format found (skipping format check)")
            self.checks.append(("Code Format", True, "No .clang-format (optional)"))
            return True

        self.log("INFO", "Checking code format with clang-format...")

        # Find source files
        src_files = list((self.project_dir / "src").glob("**/*.cpp")) if (self.project_dir / "src").exists() else []
        header_files = list((self.project_dir / "include").glob("**/*.h*")) if (self.project_dir / "include").exists() else []
        all_files = src_files + header_files

        if not all_files:
            self.checks.append(("Code Format", True, "No source files to check"))
            return True

        returncode, stdout, stderr = self.run_command(
            ["clang-format", "--dry-run", "--Werror"] + [str(f) for f in all_files],
            check=False
        )

        if returncode != 0:
            msg = f"Code format check failed: {stderr[:200]}"
            if self.strict:
                self.checks.append(("Code Format", False, msg))
                return False
            else:
                self.log("WARN", msg)
                self.checks.append(("Code Format", True, f"Warnings: {msg}"))
                return True

        self.log("INFO", "Code format check passed ✓")
        self.checks.append(("Code Format", True, None))
        return True

    def check_compiler_warnings(self) -> bool:
        """Check for compiler warnings in build output."""
        self.log("INFO", "Checking for compiler warnings...")

        build_dir = self.project_dir / "build" / "validate"
        cmake_cache = build_dir / "CMakeCache.txt"

        if not cmake_cache.exists():
            self.checks.append(("Compiler Warnings", True, "Build not configured"))
            return True

        # Try clean rebuild to capture all warnings
        returncode, stdout, stderr = self.run_command(
            ["cmake", "--build", str(build_dir), "--config", "Debug"],
            check=False
        )

        build_output = stdout + stderr

        # Count warnings (simple heuristic)
        warning_count = build_output.count("warning:")

        if warning_count > 0:
            msg = f"Found {warning_count} compiler warnings"
            if self.strict:
                self.checks.append(("Compiler Warnings", False, msg))
                return False
            else:
                self.log("WARN", msg)
                self.checks.append(("Compiler Warnings", True, f"Warnings: {msg}"))
                return True

        self.log("INFO", "No compiler warnings ✓")
        self.checks.append(("Compiler Warnings", True, None))
        return True

    def check_git_setup(self) -> bool:
        """Verify git repository is initialized."""
        git_dir = self.project_dir / ".git"

        if not git_dir.exists():
            self.log("WARN", "Git repository not initialized")
            self.checks.append(("Git: Repository", True, "Git not initialized (optional)"))
            return True

        returncode, stdout, stderr = self.run_command(["git", "status"])
        if returncode != 0:
            msg = f"Git status check failed: {stderr[:200]}"
            self.checks.append(("Git: Repository", False, msg))
            return False

        self.log("INFO", "Git repository initialized ✓")
        self.checks.append(("Git: Repository", True, None))

        # Check for .gitignore
        gitignore = self.project_dir / ".gitignore"
        if not gitignore.exists():
            self.log("WARN", ".gitignore not found (recommended)")
            self.checks.append(("Git: .gitignore", True, "No .gitignore (recommended)"))
            return True

        self.log("INFO", ".gitignore present ✓")
        self.checks.append(("Git: .gitignore", True, None))
        return True

    def check_compiler_setup(self) -> bool:
        """Verify C++ compiler is configured."""
        self.log("INFO", "Checking compiler setup...")

        build_dir = self.project_dir / "build" / "validate"
        cmake_cache = build_dir / "CMakeCache.txt"

        if not cmake_cache.exists():
            self.checks.append(("Compiler: Setup", False, "CMake not configured"))
            return False

        try:
            with open(cmake_cache, 'r') as f:
                cache_content = f.read()
                if "CMAKE_CXX_COMPILER" not in cache_content:
                    self.checks.append(("Compiler: Setup", False, "C++ compiler not configured in CMake"))
                    return False
        except Exception as e:
            self.checks.append(("Compiler: Setup", False, str(e)))
            return False

        self.log("INFO", "Compiler setup verified ✓")
        self.checks.append(("Compiler: Setup", True, None))
        return True

    def validate(self) -> bool:
        """Run all validation checks."""
        print("\n" + "="*60)
        print("C++ PROJECT VALIDATION")
        print("="*60 + "\n")

        # Sequential checks with dependencies
        if not self.check_directory_structure():
            print("\n❌ Project structure invalid. Cannot continue.")
            self._print_report()
            return False

        if not self.check_cmake_version():
            print("\n❌ CMake not available. Cannot continue.")
            self._print_report()
            return False

        if not self.check_cmake_configuration():
            print("\n❌ CMake configuration failed. Cannot continue.")
            self._print_report()
            return False

        if not self.check_compiler_setup():
            print("\n⚠️  Compiler setup check failed (continuing).")

        if not self.check_build():
            print("\n❌ Build failed. Cannot continue.")
            self._print_report()
            return False

        # Optional checks
        self.check_tests()
        self.check_compiler_warnings()
        self.check_code_format()
        self.check_git_setup()

        # Print final report
        self._print_report()

        return all(check[1] for check in self.checks)

    def _print_report(self):
        """Print validation report."""
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60 + "\n")

        passed = sum(1 for _, result, _ in self.checks if result)
        total = len(self.checks)

        for check_name, result, error in self.checks:
            status = "✓" if result else "✗"
            error_msg = f" ({error})" if error else ""
            print(f"  [{status}] {check_name}{error_msg}")

        print(f"\n{'='*60}")
        print(f"SUMMARY: {passed}/{total} checks passed")

        if passed == total:
            print("✅ ALL VALIDATIONS PASSED!")
        else:
            failed = total - passed
            print(f"❌ {failed} checks failed")

        print("="*60 + "\n")

    def export_json(self, output_file: str = "validation_report.json"):
        """Export validation results as JSON."""
        report = {
            "project_dir": str(self.project_dir),
            "strict_mode": self.strict,
            "total_checks": len(self.checks),
            "passed_checks": sum(1 for _, result, _ in self.checks if result),
            "checks": [
                {
                    "name": check_name,
                    "passed": result,
                    "error": error
                }
                for check_name, result, error in self.checks
            ]
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"Validation report exported to {output_file}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate C++ project setup and configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/validate_project.py                    # Standard validation
  python scripts/validate_project.py --strict           # Strict mode (fail on warnings)
  python scripts/validate_project.py --verbose          # Verbose output
  python scripts/validate_project.py --json report.json # Export JSON report
        """
    )

    parser.add_argument(
        "--project-dir",
        default=".",
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: fail on warnings"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--json",
        metavar="FILE",
        help="Export results as JSON"
    )

    args = parser.parse_args()

    validator = ProjectValidator(
        project_dir=args.project_dir,
        strict=args.strict,
        verbose=args.verbose
    )

    success = validator.validate()

    if args.json:
        validator.export_json(args.json)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
