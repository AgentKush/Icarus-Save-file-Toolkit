"""#51: Unified test runner — auto-discovers and runs all test_*.py files.

Features:
- Auto-discovers all test_*.py files in the tests/ directory
- Runs each test file as a subprocess
- Tracks timing per test file (performance regression detection)
- Reports pass/fail summary
- Non-zero exit code if any test file fails
- Works on clean checkout (no local state dependency)

Usage:
    python tests/run_all.py           # run all tests
    python tests/run_all.py --list    # list discovered tests without running
"""
import os
import sys
import time
import subprocess
import glob


def discover_tests():
    """Find all test_*.py files in the tests/ directory."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(tests_dir, "test_*.py")
    test_files = sorted(glob.glob(pattern))
    return test_files


def run_test(test_path):
    """Run a single test file, return (success, duration, output)."""
    start = time.time()
    result = subprocess.run(
        [sys.executable, test_path],
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    duration = time.time() - start
    output = result.stdout + result.stderr
    return result.returncode == 0, duration, output


def main():
    # Handle --list flag
    if "--list" in sys.argv:
        tests = discover_tests()
        print(f"Discovered {len(tests)} test file(s):")
        for t in tests:
            print(f"  {os.path.basename(t)}")
        return 0

    tests = discover_tests()
    if not tests:
        print("❌ No test files discovered!")
        return 1

    print(f"╔══════════════════════════════════════════════════╗")
    print(f"║  Test Runner — {len(tests)} test file(s) discovered       ║")
    print(f"╚══════════════════════════════════════════════════╝")
    print()

    results = []
    total_start = time.time()

    for test_path in tests:
        name = os.path.basename(test_path)
        print(f"▶ Running {name} ...", end=" ", flush=True)

        try:
            success, duration, output = run_test(test_path)
        except subprocess.TimeoutExpired:
            success, duration, output = False, 120.0, "TIMEOUT after 120s"
        except Exception as e:
            success, duration, output = False, 0.0, str(e)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} ({duration:.1f}s)")

        if not success:
            # Show output for failed tests
            print(f"  ┌─ Output ─────────────────────────────────")
            for line in output.strip().split("\n")[-20:]:  # last 20 lines
                print(f"  │ {line}")
            print(f"  └──────────────────────────────────────────")

        results.append((name, success, duration))

    total_duration = time.time() - total_start

    # Summary
    passed = sum(1 for _, s, _ in results if s)
    failed = sum(1 for _, s, _ in results if not s)

    print()
    print(f"╔══════════════════════════════════════════════════╗")
    print(f"║  Summary                                        ║")
    print(f"╠══════════════════════════════════════════════════╣")
    print(f"║  Test Files:  {len(results):<35}║")
    print(f"║  Passed:      {passed:<35}║")
    print(f"║  Failed:      {failed:<35}║")
    print(f"║  Total Time:  {total_duration:.1f}s{' ' * (33 - len(f'{total_duration:.1f}s'))}║")
    print(f"╠══════════════════════════════════════════════════╣")

    # Timing breakdown
    print(f"║  Timing Breakdown:                              ║")
    for name, success, duration in sorted(results, key=lambda x: -x[2]):
        icon = "✅" if success else "❌"
        line = f"{icon} {name}: {duration:.1f}s"
        print(f"║    {line:<46}║")

    print(f"╚══════════════════════════════════════════════════╝")

    if failed > 0:
        print(f"\n❌ {failed} test file(s) FAILED")
        return 1
    else:
        print(f"\n✅ All {passed} test file(s) passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
