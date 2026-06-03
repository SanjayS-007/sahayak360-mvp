"""
═══════════════════════════════════════════════════════════════
 SAHAYAK 360 — LOCAL TEST RUNNER
═══════════════════════════════════════════════════════════════

Quick-run script for verifying the deployed platform at any time.
Runs all tests in sequence: health → E2E → lifecycle demo.

Usage:
  python run_tests.py              # Run against deployed API
  python run_tests.py --local      # Run against localhost:8000
  python run_tests.py --quick      # Health + E2E only (skip lifecycle)
  python run_tests.py --lifecycle  # Full lifecycle only
"""

import subprocess
import sys
import time
from datetime import datetime

DIVIDER = "═" * 60

def run_script(name, path, extra_args=None):
    """Run a test script and return (passed, output)."""
    cmd = [sys.executable, path] + (extra_args or [])
    print(f"\n{DIVIDER}")
    print(f" Running: {name}")
    print(f" Command: {' '.join(cmd)}")
    print(f"{DIVIDER}\n")
    
    start = time.time()
    result = subprocess.run(cmd, capture_output=False, text=True)
    elapsed = time.time() - start
    
    passed = result.returncode == 0
    print(f"\n  {'✅' if passed else '❌'} {name} completed in {elapsed:.1f}s (exit={result.returncode})")
    return passed


def main():
    args = sys.argv[1:]
    extra = [a for a in args if a.startswith("--") and a not in ("--quick", "--lifecycle")]
    quick = "--quick" in args
    lifecycle_only = "--lifecycle" in args

    print(f"\n{DIVIDER}")
    print(f" SAHAYAK 360 — TEST RUNNER")
    print(f" Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" Mode: {'quick' if quick else 'lifecycle-only' if lifecycle_only else 'full'}")
    print(f"{DIVIDER}")

    results = []

    if not lifecycle_only:
        # Run E2E test suite (21 tests)
        results.append(("E2E Suite (21 tests)", run_script("E2E Test Suite", "e2e_test.py", extra)))

    if not quick:
        # Run full lifecycle demo (34 tests)
        results.append(("Lifecycle Demo (34 tests)", run_script("Full Lifecycle Demo", "full_lifecycle_demo.py", extra)))

    # Summary
    print(f"\n\n{DIVIDER}")
    print(f" FINAL SUMMARY")
    print(f"{DIVIDER}")
    all_pass = True
    for name, passed in results:
        icon = "✅" if passed else "❌"
        print(f"  {icon} {name}")
        if not passed:
            all_pass = False

    if all_pass:
        print(f"\n  🎉 ALL TESTS PASSED!")
    else:
        print(f"\n  ⚠️  SOME TESTS FAILED — check output above")
    
    print(f"\n  Platform URLs:")
    print(f"    Frontend: https://sahayak360-mvp.vercel.app")
    print(f"    API Docs: https://sahayak360-api.onrender.com/docs")
    print(f"    API Base: https://sahayak360-api.onrender.com")
    print(f"\n{DIVIDER}\n")
    
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
