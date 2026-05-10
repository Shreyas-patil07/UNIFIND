#!/usr/bin/env python3
"""
Quality check script for UNIFIND backend.
Runs all linters, formatters, and tests.
"""
import subprocess
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def run_command(name: str, command: list[str], check: bool = True) -> bool:
    """Run a command and return success status."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Running: {name}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    try:
        result = subprocess.run(
            command,
            check=check,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n{GREEN}✓ {name} passed{RESET}")
            return True
        else:
            print(f"\n{RED}✗ {name} failed{RESET}")
            return False
    except subprocess.CalledProcessError:
        print(f"\n{RED}✗ {name} failed{RESET}")
        return False
    except FileNotFoundError:
        print(f"\n{YELLOW}⚠ {name} skipped (command not found){RESET}")
        return True


def main():
    """Run all quality checks."""
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}UNIFIND Backend - Quality Check{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    
    results = {}
    
    # 1. Ruff linter
    results['Ruff Linter'] = run_command(
        'Ruff Linter',
        ['ruff', 'check', '.'],
        check=False
    )
    
    # 2. Black formatter check
    results['Black Formatter'] = run_command(
        'Black Formatter Check',
        ['black', '--check', '--diff', '.'],
        check=False
    )
    
    # 3. isort import check
    results['isort Import Check'] = run_command(
        'isort Import Check',
        ['isort', '--check-only', '--diff', '.'],
        check=False
    )
    
    # 4. Flake8
    results['Flake8'] = run_command(
        'Flake8',
        ['flake8', 'app/', '--max-line-length=100', '--extend-ignore=E203,W503'],
        check=False
    )
    
    # 5. Bandit security scan
    results['Bandit Security Scan'] = run_command(
        'Bandit Security Scan',
        ['bandit', '-r', 'app/', '-ll', '-f', 'screen'],
        check=False
    )
    
    # 6. Safety dependency check
    results['Safety Dependency Check'] = run_command(
        'Safety Dependency Check',
        ['safety', 'check', '--file', 'requirements.txt'],
        check=False
    )
    
    # 7. Run tests with coverage
    results['Tests with Coverage'] = run_command(
        'Tests with Coverage',
        [
            'pytest', 'tests/',
            '--cov=app',
            '--cov-report=term-missing',
            '--cov-report=html',
            '--cov-fail-under=60',
            '-v'
        ],
        check=False
    )
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, status in results.items():
        status_icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        print(f"{status_icon} {check}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    
    if passed == total:
        print(f"{GREEN}All checks passed! ({passed}/{total}){RESET}")
        return 0
    else:
        print(f"{RED}Some checks failed. ({passed}/{total} passed){RESET}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
