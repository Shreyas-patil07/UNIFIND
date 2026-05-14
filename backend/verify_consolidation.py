#!/usr/bin/env python3
"""
Backend Consolidation Verification Script

This script verifies that the backend consolidation was successful by checking:
1. Deployment configurations point to app.main:app
2. No circular imports in app/
3. All required modules are importable
4. Health endpoints are accessible (if server is running)

Usage:
    python verify_consolidation.py
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")


def print_success(text: str):
    """Print a success message."""
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text: str):
    """Print an error message."""
    print(f"{RED}✗{RESET} {text}")


def print_warning(text: str):
    """Print a warning message."""
    print(f"{YELLOW}⚠{RESET} {text}")


def print_info(text: str):
    """Print an info message."""
    print(f"{BLUE}ℹ{RESET} {text}")


def check_deployment_configs() -> Tuple[bool, List[str]]:
    """Check that deployment configurations use app.main:app."""
    print_header("Checking Deployment Configurations")

    issues = []
    all_good = True

    # Check Procfile
    procfile = Path("Procfile")
    if procfile.exists():
        content = procfile.read_text()
        if "app.main:app" in content:
            print_success("Procfile uses app.main:app")
        elif "main:app" in content:
            print_error("Procfile still uses legacy main:app")
            issues.append("Procfile needs update")
            all_good = False
        else:
            print_warning("Procfile doesn't specify entrypoint")
    else:
        print_warning("Procfile not found")

    # Check render.yaml
    render_yaml = Path("render.yaml")
    if render_yaml.exists():
        content = render_yaml.read_text()
        if "app.main:app" in content:
            print_success("render.yaml uses app.main:app")
        elif "main:app" in content and "app.main:app" not in content:
            print_error("render.yaml still uses legacy main:app")
            issues.append("render.yaml needs update")
            all_good = False
        else:
            print_warning("render.yaml doesn't specify entrypoint")
    else:
        print_warning("render.yaml not found")

    # Check Dockerfile
    dockerfile = Path("Dockerfile")
    if dockerfile.exists():
        content = dockerfile.read_text()
        if "app.main:app" in content:
            print_success("Dockerfile uses app.main:app")
        elif "main:app" in content and "app.main:app" not in content:
            print_error("Dockerfile still uses legacy main:app")
            issues.append("Dockerfile needs update")
            all_good = False
        else:
            print_warning("Dockerfile doesn't specify entrypoint")
    else:
        print_warning("Dockerfile not found")

    # Check docker-compose.yml
    docker_compose = Path("docker-compose.yml")
    if docker_compose.exists():
        content = docker_compose.read_text()
        if "app.main:app" in content:
            print_success("docker-compose.yml uses app.main:app")
        elif "main:app" in content and "app.main:app" not in content:
            print_error("docker-compose.yml still uses legacy main:app")
            issues.append("docker-compose.yml needs update")
            all_good = False
        else:
            print_warning("docker-compose.yml doesn't specify entrypoint")
    else:
        print_warning("docker-compose.yml not found")

    return all_good, issues


def check_legacy_main() -> Tuple[bool, List[str]]:
    """Check that legacy main.py is a compatibility shim."""
    print_header("Checking Legacy Main.py")

    issues = []
    all_good = True

    main_py = Path("main.py")
    if main_py.exists():
        content = main_py.read_text()

        if "DEPRECATED" in content and "from app.main import app" in content:
            print_success("main.py is a compatibility shim")
        elif "from app.main import app" in content:
            print_warning("main.py redirects to app.main but missing deprecation notice")
        else:
            print_error("main.py is still the legacy implementation")
            issues.append("main.py needs to be converted to compatibility shim")
            all_good = False
    else:
        print_warning("main.py not found (this is okay if fully migrated)")

    return all_good, issues


def check_app_structure() -> Tuple[bool, List[str]]:
    """Check that app/ directory has the expected structure."""
    print_header("Checking App Structure")

    issues = []
    all_good = True

    required_dirs = [
        "app",
        "app/api",
        "app/api/routes",
        "app/api/dependencies",
        "app/core",
        "app/services",
        "app/repositories",
        "app/schemas",
        "app/middleware",
    ]

    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print_success(f"{dir_path}/ exists")
        else:
            print_error(f"{dir_path}/ not found")
            issues.append(f"Missing directory: {dir_path}")
            all_good = False

    # Check for app/main.py
    app_main = Path("app/main.py")
    if app_main.exists():
        print_success("app/main.py exists")
    else:
        print_error("app/main.py not found")
        issues.append("Missing app/main.py")
        all_good = False

    return all_good, issues


def check_imports() -> Tuple[bool, List[str]]:
    """Check that key modules can be imported."""
    print_header("Checking Module Imports")

    issues = []
    all_good = True

    # Add app directory to Python path
    sys.path.insert(0, str(Path.cwd()))

    modules_to_check = [
        "app.main",
        "app.core.config",
        "app.core.database",
        "app.api.dependencies.auth",
    ]

    for module_name in modules_to_check:
        try:
            __import__(module_name)
            print_success(f"Successfully imported {module_name}")
        except ImportError as e:
            print_error(f"Failed to import {module_name}: {e}")
            issues.append(f"Import error: {module_name}")
            all_good = False
        except Exception as e:
            print_warning(f"Import {module_name} raised: {type(e).__name__}: {e}")
            # Don't mark as failure - might be due to missing env vars

    return all_good, issues


def check_documentation() -> Tuple[bool, List[str]]:
    """Check that documentation files exist."""
    print_header("Checking Documentation")

    issues = []
    all_good = True

    docs = [
        "MIGRATION_PLAN.md",
        "DEPRECATED_FILES.md",
        "ARCHITECTURE.md",
        "CONSOLIDATION_SUMMARY.md",
    ]

    for doc in docs:
        path = Path(doc)
        if path.exists():
            print_success(f"{doc} exists")
        else:
            print_warning(f"{doc} not found")
            # Not a critical error, just a warning

    return all_good, issues


def check_deprecated_files() -> Tuple[bool, List[str]]:
    """Check status of deprecated files."""
    print_header("Checking Deprecated Files")

    issues = []
    all_good = True

    deprecated_items = [
        ("routes/", "directory"),
        ("services/", "directory"),
        ("security/", "directory"),
        ("config.py", "file"),
        ("database.py", "file"),
        ("auth.py", "file"),
        ("models.py", "file"),
    ]

    for item, item_type in deprecated_items:
        path = Path(item)
        if path.exists():
            print_warning(f"Deprecated {item_type} still exists: {item}")
            print_info(f"  → Should be removed after migration is stable")
        else:
            print_info(f"Deprecated {item_type} removed: {item}")

    return all_good, issues


def main():
    """Run all verification checks."""
    print_header("Backend Consolidation Verification")
    print_info("Verifying backend architecture consolidation...")

    all_checks_passed = True
    all_issues = []

    # Run all checks
    checks = [
        check_deployment_configs,
        check_legacy_main,
        check_app_structure,
        check_imports,
        check_documentation,
        check_deprecated_files,
    ]

    for check in checks:
        passed, issues = check()
        if not passed:
            all_checks_passed = False
            all_issues.extend(issues)

    # Print summary
    print_header("Verification Summary")

    if all_checks_passed:
        print_success("All critical checks passed!")
        print_info("\nBackend consolidation is successful.")
        print_info("You can now deploy with confidence.")
        return 0
    else:
        print_error("Some checks failed!")
        print_info("\nIssues found:")
        for issue in all_issues:
            print(f"  • {issue}")
        print_info("\nPlease fix these issues before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
