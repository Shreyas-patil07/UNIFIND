#!/usr/bin/env python3
"""
UNIFIND Backend - Architecture Validation Script

This script validates that the backend architecture is properly consolidated
and that no legacy imports or duplicate registrations exist.

Usage:
    python scripts/validate_architecture.py

Exit Codes:
    0 - All checks passed
    1 - Architecture issues found
"""
import ast
import os
import sys
from pathlib import Path
from typing import List, Set, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ArchitectureValidator:
    """Validates backend architecture consolidation."""

    def __init__(self):
        self.backend_root = Path(__file__).parent.parent
        self.app_root = self.backend_root / "app"
        self.issues: List[str] = []
        self.warnings: List[str] = []

    def log_issue(self, message: str):
        """Log an architecture issue."""
        self.issues.append(f"❌ {message}")
        print(f"❌ {message}")

    def log_warning(self, message: str):
        """Log an architecture warning."""
        self.warnings.append(f"⚠️  {message}")
        print(f"⚠️  {message}")

    def log_success(self, message: str):
        """Log a successful check."""
        print(f"✅ {message}")

    def check_no_legacy_imports(self) -> bool:
        """Check that no code imports from legacy structure."""
        print("\n" + "=" * 60)
        print("PHASE 1: Legacy Import Detection")
        print("=" * 60)

        legacy_patterns = [
            "from routes.",
            "import routes.",
            "from services.",
            "import services.",
            "from security.",
            "import security.",
            "from main import",
            "import main",
        ]

        found_legacy = False

        # Check all Python files in app/ and tests/
        for directory in ["app", "tests"]:
            dir_path = self.backend_root / directory
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue

                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    for pattern in legacy_patterns:
                        if pattern in content:
                            self.log_issue(
                                f"Legacy import found in {py_file.relative_to(self.backend_root)}: {pattern}"
                            )
                            found_legacy = True
                except Exception as e:
                    self.log_warning(f"Could not read {py_file}: {e}")

        if not found_legacy:
            self.log_success("No legacy imports found")
            return True
        return False

    def check_single_entrypoint(self) -> bool:
        """Check that only app.main:app is used as entrypoint."""
        print("\n" + "=" * 60)
        print("PHASE 2: Entrypoint Validation")
        print("=" * 60)

        config_files = [
            "Procfile",
            "render.yaml",
            "Dockerfile",
            "docker-compose.yml",
            "Makefile",
            "scripts/start.sh",
        ]

        all_correct = True

        for config_file in config_files:
            file_path = self.backend_root / config_file
            if not file_path.exists():
                self.log_warning(f"{config_file} not found")
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for legacy entrypoint (main:app without app. prefix)
                if "main:app" in content and "app.main:app" not in content:
                    # Check if it's actually the legacy pattern
                    lines_with_legacy = [
                        line
                        for line in content.split("\n")
                        if "main:app" in line and "app.main:app" not in line
                    ]
                    if lines_with_legacy:
                        self.log_issue(
                            f"{config_file} uses legacy entrypoint 'main:app' instead of 'app.main:app'"
                        )
                        all_correct = False
                        continue

                # Check for correct entrypoint
                if "app.main:app" in content:
                    self.log_success(f"{config_file} uses correct entrypoint")
                else:
                    self.log_warning(f"{config_file} does not reference entrypoint")

            except Exception as e:
                self.log_warning(f"Could not read {config_file}: {e}")

        return all_correct

    def check_route_registration(self) -> bool:
        """Check that routes are registered only once."""
        print("\n" + "=" * 60)
        print("PHASE 3: Route Registration Validation")
        print("=" * 60)

        main_file = self.app_root / "main.py"
        if not main_file.exists():
            self.log_issue("app/main.py not found")
            return False

        try:
            with open(main_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST to find include_router calls
            tree = ast.parse(content)

            router_registrations = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr == "include_router":
                            # Extract router name and prefix
                            if node.args:
                                router_arg = node.args[0]
                                if isinstance(router_arg, ast.Attribute):
                                    router_name = f"{router_arg.value.id}.{router_arg.attr}"
                                else:
                                    router_name = "unknown"

                                # Extract prefix from kwargs
                                prefix = None
                                for keyword in node.keywords:
                                    if keyword.arg == "prefix":
                                        if isinstance(keyword.value, ast.Constant):
                                            prefix = keyword.value.value

                                router_registrations.append((router_name, prefix))

            # Check for duplicates
            seen = set()
            duplicates = []
            for router, prefix in router_registrations:
                key = (router, prefix)
                if key in seen:
                    duplicates.append(key)
                seen.add(key)

            if duplicates:
                for router, prefix in duplicates:
                    self.log_issue(f"Duplicate route registration: {router} with prefix {prefix}")
                return False
            else:
                self.log_success(
                    f"No duplicate route registrations ({len(router_registrations)} routes registered)"
                )
                return True

        except Exception as e:
            self.log_warning(f"Could not parse app/main.py: {e}")
            return False

    def check_directory_structure(self) -> bool:
        """Check that the canonical directory structure exists."""
        print("\n" + "=" * 60)
        print("PHASE 4: Directory Structure Validation")
        print("=" * 60)

        required_dirs = [
            "app",
            "app/api",
            "app/api/routes",
            "app/api/dependencies",
            "app/services",
            "app/repositories",
            "app/core",
            "app/middleware",
        ]

        all_exist = True
        for dir_path in required_dirs:
            full_path = self.backend_root / dir_path
            if full_path.exists():
                self.log_success(f"Directory exists: {dir_path}")
            else:
                self.log_issue(f"Required directory missing: {dir_path}")
                all_exist = False

        return all_exist

    def check_legacy_files_removed(self) -> bool:
        """Check that legacy files have been removed."""
        print("\n" + "=" * 60)
        print("PHASE 5: Legacy File Removal Validation")
        print("=" * 60)

        legacy_files = [
            "main.py",
            "routes/",
            "services/",
            "security/",
        ]

        all_removed = True
        for file_path in legacy_files:
            full_path = self.backend_root / file_path
            if full_path.exists():
                self.log_issue(f"Legacy file/directory still exists: {file_path}")
                all_removed = False
            else:
                self.log_success(f"Legacy file/directory removed: {file_path}")

        return all_removed

    def check_import_structure(self) -> bool:
        """Check that imports follow the canonical structure."""
        print("\n" + "=" * 60)
        print("PHASE 6: Import Structure Validation")
        print("=" * 60)

        # Check that app modules import from app.*
        valid_import_patterns = [
            "from app.",
            "import app.",
            "from fastapi",
            "from pydantic",
            "from typing",
            "import os",
            "import sys",
            "import logging",
        ]

        issues_found = False

        for py_file in self.app_root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse imports
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.ImportFrom):
                            module = node.module or ""
                            # Check for relative imports outside app
                            if module and not any(
                                module.startswith(pattern.replace("from ", "").replace("import ", ""))
                                for pattern in valid_import_patterns
                            ):
                                # Allow standard library and third-party imports
                                if not module.startswith("app.") and "." in module:
                                    # This might be a third-party import, skip
                                    continue

            except Exception as e:
                self.log_warning(f"Could not parse {py_file}: {e}")

        if not issues_found:
            self.log_success("Import structure follows canonical pattern")
            return True
        return False

    def print_summary(self) -> bool:
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("ARCHITECTURE VALIDATION SUMMARY")
        print("=" * 60)

        total_issues = len(self.issues)
        total_warnings = len(self.warnings)

        print(f"\n❌ Issues: {total_issues}")
        print(f"⚠️  Warnings: {total_warnings}")

        if total_issues > 0:
            print("\n" + "=" * 60)
            print("ISSUES FOUND:")
            print("=" * 60)
            for issue in self.issues:
                print(issue)

        if total_warnings > 0:
            print("\n" + "=" * 60)
            print("WARNINGS:")
            print("=" * 60)
            for warning in self.warnings:
                print(warning)

        if total_issues == 0:
            print("\n✅ ARCHITECTURE VALIDATION PASSED")
            print("The backend architecture is properly consolidated.")
            return True
        else:
            print("\n❌ ARCHITECTURE VALIDATION FAILED")
            print("Please fix the issues above before deploying.")
            return False

    def run_all_checks(self) -> bool:
        """Run all architecture validation checks."""
        print("=" * 60)
        print("UNIFIND BACKEND - ARCHITECTURE VALIDATION")
        print("=" * 60)

        self.check_directory_structure()
        self.check_no_legacy_imports()
        self.check_single_entrypoint()
        self.check_route_registration()
        self.check_legacy_files_removed()
        self.check_import_structure()

        return self.print_summary()


def main():
    """Main entry point."""
    validator = ArchitectureValidator()

    try:
        success = validator.run_all_checks()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n\nUnexpected error during validation: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
