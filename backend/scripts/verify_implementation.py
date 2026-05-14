#!/usr/bin/env python3
"""
Verification script to check if all production components are properly implemented.
"""
import sys
from pathlib import Path
from typing import Tuple

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check_file_exists(path: Path, description: str) -> Tuple[bool, str]:
    """Check if a file exists."""
    if path.exists():
        return True, f"✓ {description}"
    return False, f"✗ {description} (missing: {path})"


def check_directory_exists(path: Path, description: str) -> Tuple[bool, str]:
    """Check if a directory exists."""
    if path.is_dir():
        return True, f"✓ {description}"
    return False, f"✗ {description} (missing: {path})"


def main():
    """Run implementation verification."""
    print(f"{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}UNIFIND Backend - Implementation Verification{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    backend_dir = Path(__file__).parent.parent
    root_dir = backend_dir.parent

    checks = []

    # Testing Infrastructure
    print(f"{BLUE}Testing Infrastructure:{RESET}")
    checks.append(check_directory_exists(backend_dir / "tests", "tests/ directory"))
    checks.append(check_file_exists(backend_dir / "tests" / "conftest.py", "conftest.py"))
    checks.append(check_directory_exists(backend_dir / "tests" / "unit", "tests/unit/"))
    checks.append(
        check_directory_exists(backend_dir / "tests" / "integration", "tests/integration/")
    )
    checks.append(
        check_file_exists(backend_dir / "tests" / "unit" / "test_auth_service.py", "Unit tests")
    )
    checks.append(
        check_file_exists(
            backend_dir / "tests" / "integration" / "test_auth_routes.py", "Integration tests"
        )
    )
    checks.append(check_file_exists(backend_dir / "pytest.ini", "pytest.ini"))

    for passed, message in checks[-7:]:
        print(f"  {GREEN if passed else RED}{message}{RESET}")

    # CI/CD
    print(f"\n{BLUE}CI/CD Pipeline:{RESET}")
    ci_checks = [
        check_directory_exists(root_dir / ".github" / "workflows", ".github/workflows/"),
        check_file_exists(root_dir / ".github" / "workflows" / "ci.yml", "ci.yml"),
        check_file_exists(root_dir / ".github" / "workflows" / "security.yml", "security.yml"),
    ]
    checks.extend(ci_checks)

    for passed, message in ci_checks:
        print(f"  {GREEN if passed else RED}{message}{RESET}")

    # Docker
    print(f"\n{BLUE}Docker Configuration:{RESET}")
    docker_checks = [
        check_file_exists(backend_dir / "Dockerfile", "Dockerfile"),
        check_file_exists(backend_dir / ".dockerignore", ".dockerignore"),
        check_file_exists(backend_dir / "docker-compose.yml", "docker-compose.yml"),
    ]
    checks.extend(docker_checks)

    for passed, message in docker_checks:
        print(f"  {GREEN if passed else RED}{message}{RESET}")

    # Configuration
    print(f"\n{BLUE}Configuration Files:{RESET}")
    config_checks = [
        check_file_exists(backend_dir / ".env.example", ".env.example"),
        check_file_exists(backend_dir / "pyproject.toml", "pyproject.toml"),
        check_file_exists(backend_dir / ".flake8", ".flake8"),
        check_file_exists(backend_dir / ".pre-commit-config.yaml", ".pre-commit-config.yaml"),
        check_file_exists(root_dir / ".gitignore", ".gitignore"),
    ]
    checks.extend(config_checks)

    for passed, message in config_checks:
        print(f"  {GREEN if passed else RED}{message}{RESET}")

    # Scripts
    print(f"\n{BLUE}Utility Scripts:{RESET}")
    script_checks = [
        check_directory_exists(backend_dir / "scripts", "scripts/"),
        check_file_exists(backend_dir / "scripts" / "quality_check.py", "quality_check.py"),
        check_file_exists(backend_dir / "scripts" / "health_check.py", "health_check.py"),
        check_file_exists(backend_dir / "scripts" / "validate_env.py", "validate_env.py"),
    ]
    checks.extend(script_checks)

    for passed, message in script_checks:
        print(f"  {GREEN if passed else RED}{message}{RESET}")

    # Documentation
    print(f"\n{BLUE}Documentation:{RESET}")
    doc_checks = [
        check_file_exists(backend_dir / "README.md", "README.md"),
        check_file_exists(backend_dir / "DEPLOYMENT.md", "DEPLOYMENT.md"),
        check_file_exists(backend_dir / "PRODUCTION_CHECKLIST.md", "PRODUCTION_CHECKLIST.md"),
        check_file_exists(backend_dir / "IMPLEMENTATION_SUMMARY.md", "IMPLEMENTATION_SUMMARY.md"),
        check_file_exists(backend_dir / "tests" / "README.md", "tests/README.md"),
        check_file_exists(backend_dir / "Makefile", "Makefile"),
    ]
    checks.extend(doc_checks)

    for passed, message in doc_checks:
        print(f"  {GREEN if passed else RED}{message}{RESET}")

    # Enhanced Code
    print(f"\n{BLUE}Enhanced Application Code:{RESET}")
    code_checks = [
        check_file_exists(backend_dir / "app" / "core" / "logging.py", "Enhanced logging"),
        check_file_exists(backend_dir / "app" / "core" / "config.py", "Enhanced config"),
        check_file_exists(backend_dir / "app" / "main.py", "Enhanced main.py"),
    ]
    checks.extend(code_checks)

    for passed, message in code_checks:
        print(f"  {GREEN if passed else RED}{message}{RESET}")

    # Dependencies
    print(f"\n{BLUE}Dependencies:{RESET}")
    req_file = backend_dir / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text()
        deps = [
            ("pytest", "pytest"),
            ("pytest-asyncio", "pytest-asyncio"),
            ("pytest-cov", "pytest-cov"),
            ("httpx", "httpx"),
            ("gunicorn", "gunicorn"),
            ("ruff", "ruff"),
            ("black", "black"),
            ("isort", "isort"),
            ("bandit", "bandit"),
            ("safety", "safety"),
        ]

        for dep_name, dep_check in deps:
            if dep_check in content:
                print(f"  {GREEN}✓ {dep_name}{RESET}")
                checks.append((True, f"{dep_name} in requirements.txt"))
            else:
                print(f"  {RED}✗ {dep_name} (not in requirements.txt){RESET}")
                checks.append((False, f"{dep_name} in requirements.txt"))
    else:
        print(f"  {RED}✗ requirements.txt not found{RESET}")
        checks.append((False, "requirements.txt"))

    # Summary
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Summary:{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

    passed = sum(1 for p, _ in checks if p)
    total = len(checks)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"Checks Passed: {passed}/{total} ({percentage:.1f}%)")

    if passed == total:
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}✅ All implementation checks passed!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}\n")
        print(f"{GREEN}Your backend is production-ready!{RESET}\n")
        print(f"Next steps:")
        print(f"  1. Run: python scripts/validate_env.py")
        print(f"  2. Run: python scripts/quality_check.py")
        print(f"  3. Review: PRODUCTION_CHECKLIST.md")
        print(f"  4. Deploy! 🚀")
        return 0
    else:
        print(f"\n{YELLOW}{'='*70}{RESET}")
        print(f"{YELLOW}⚠ Some checks failed ({total - passed} issues){RESET}")
        print(f"{YELLOW}{'='*70}{RESET}\n")

        print(f"Failed checks:")
        for passed, message in checks:
            if not passed:
                print(f"  • {message}")

        return 1


if __name__ == "__main__":
    sys.exit(main())
