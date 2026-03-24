#!/usr/bin/env python3
"""
Test runner script for the CICT Grade Portal.
Provides convenient commands for running different types of tests.
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a subprocess command."""
    if description:
        print(f"\n🔄 {description}")
    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode == 0


def run_tests(args):
    """Run pytest with specified options."""
    cmd = ["python", "-m", "pytest"]

    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])
    elif args.coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    elif args.fast:
        cmd.extend(["-x", "--tb=short"])

    if args.verbose:
        cmd.append("-v")

    if args.pattern:
        cmd.extend(["-k", args.pattern])

    if args.file:
        cmd.append(args.file)

    return run_command(cmd, "Running tests")


def check_code_quality():
    """Run code quality checks."""
    print("\n🧹 Running code quality checks...")

    # Check if tools are available
    tools = {
        'flake8': 'Code style (PEP 8)',
        'black': 'Code formatting',
        'isort': 'Import sorting',
        'mypy': 'Type checking'
    }

    results = {}

    for tool, description in tools.items():
        print(f"\n📊 Checking {description}...")

        if tool == 'flake8':
            success = run_command(['python', '-m', 'flake8', 'app', 'tests'])
        elif tool == 'black':
            success = run_command(['python', '-m', 'black', '--check', 'app', 'tests'])
        elif tool == 'isort':
            success = run_command(['python', '-m', 'isort', '--check-only', 'app', 'tests'])
        elif tool == 'mypy':
            success = run_command(['python', '-m', 'mypy', 'app'])

        results[tool] = success

        if success:
            print(f"✅ {description} passed")
        else:
            print(f"❌ {description} failed")

    return all(results.values())


def install_dependencies():
    """Install test dependencies."""
    print("\n📦 Installing test dependencies...")

    test_deps = [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'pytest-env>=0.8.0',
        'pytest-mock>=3.10.0',
        'coverage>=7.0.0',
        'flake8>=6.0.0',
        'black>=23.0.0',
        'isort>=5.12.0',
        'mypy>=1.0.0'
    ]

    cmd = ['pip', 'install'] + test_deps
    return run_command(cmd, "Installing dependencies")


def generate_test_report():
    """Generate comprehensive test report."""
    print("\n📋 Generating comprehensive test report...")

    # Run tests with coverage
    cmd = [
        "python", "-m", "pytest",
        "--cov=app",
        "--cov-report=html:reports/coverage",
        "--cov-report=xml:reports/coverage.xml",
        "--cov-report=term",
        "--junit-xml=reports/junit.xml"
    ]

    # Create reports directory
    Path("reports").mkdir(exist_ok=True)

    success = run_command(cmd, "Running tests with coverage")

    if success:
        print("\n✅ Test report generated successfully!")
        print("📊 Coverage report: reports/coverage/index.html")
        print("📄 JUnit report: reports/junit.xml")

    return success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CICT Grade Portal Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                   # Run all tests
  python test_runner.py --unit            # Run unit tests only
  python test_runner.py --integration     # Run integration tests only
  python test_runner.py --coverage        # Run tests with coverage
  python test_runner.py --fast            # Run tests fast (stop on first failure)
  python test_runner.py --pattern auth    # Run tests matching 'auth'
  python test_runner.py --file tests/test_models.py  # Run specific test file
  python test_runner.py --quality         # Check code quality
  python test_runner.py --install         # Install test dependencies
  python test_runner.py --report          # Generate comprehensive report
        """
    )

    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--coverage', action='store_true', help='Run tests with coverage')
    parser.add_argument('--fast', action='store_true', help='Fast run (stop on first failure)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--pattern', '-k', help='Run tests matching pattern')
    parser.add_argument('--file', '-f', help='Run specific test file')
    parser.add_argument('--quality', action='store_true', help='Check code quality')
    parser.add_argument('--install', action='store_true', help='Install test dependencies')
    parser.add_argument('--report', action='store_true', help='Generate comprehensive test report')

    args = parser.parse_args()

    print("🧪 CICT Grade Portal Test Runner")
    print("=" * 40)

    success = True

    if args.install:
        success = install_dependencies()
    elif args.quality:
        success = check_code_quality()
    elif args.report:
        success = generate_test_report()
    else:
        success = run_tests(args)

    if success:
        print("\n✅ All operations completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some operations failed. Please check the output above.")
        sys.exit(1)


if __name__ == '__main__':
    main()