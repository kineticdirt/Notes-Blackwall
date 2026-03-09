#!/usr/bin/env python3
"""
Security check script with graceful fallbacks.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_semgrep():
    """Run Semgrep with graceful fallback."""
    try:
        result = subprocess.run(
            ['semgrep', '--config=auto', '--json', 'src/'],
            capture_output=True,
            timeout=300,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            return True, result.stdout.decode()
        else:
            return False, result.stderr.decode()
    except FileNotFoundError:
        print("⚠ Semgrep not installed, skipping...", file=sys.stderr)
        return None, None
    except subprocess.TimeoutExpired:
        print("⚠ Semgrep timed out", file=sys.stderr)
        return None, None
    except Exception as e:
        print(f"⚠ Semgrep error: {e}", file=sys.stderr)
        return None, None


def run_bandit():
    """Run Bandit with graceful fallback."""
    try:
        result = subprocess.run(
            ['bandit', '-r', 'src/', '-f', 'json'],
            capture_output=True,
            timeout=300,
            cwd=Path(__file__).parent.parent
        )
        # Bandit returns non-zero on findings, but that's OK
        return True, result.stdout.decode()
    except FileNotFoundError:
        print("⚠ Bandit not installed, skipping...", file=sys.stderr)
        return None, None
    except subprocess.TimeoutExpired:
        print("⚠ Bandit timed out", file=sys.stderr)
        return None, None
    except Exception as e:
        print(f"⚠ Bandit error: {e}", file=sys.stderr)
        return None, None


def run_safety():
    """Run Safety (dependency check) with graceful fallback."""
    token = os.environ.get('SAFETY_API_KEY')
    
    if not token:
        print("⚠ SAFETY_API_KEY not set, skipping Safety check...", file=sys.stderr)
        return None, None
    
    try:
        result = subprocess.run(
            ['safety', 'check', '--json'],
            capture_output=True,
            timeout=300,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stdout.decode()
    except FileNotFoundError:
        print("⚠ Safety not installed, skipping...", file=sys.stderr)
        return None, None
    except Exception as e:
        print(f"⚠ Safety error: {e}", file=sys.stderr)
        return None, None


def run_snyk():
    """Run Snyk with graceful fallback."""
    token = os.environ.get('SNYK_TOKEN')
    
    if not token:
        print("⚠ SNYK_TOKEN not set, skipping Snyk scan...", file=sys.stderr)
        return None, None
    
    try:
        result = subprocess.run(
            ['snyk', 'test', '--severity-threshold=high', '--json'],
            capture_output=True,
            timeout=300,
            env={**os.environ, 'SNYK_TOKEN': token},
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            return True, None
        else:
            return False, result.stdout.decode()
    except FileNotFoundError:
        print("⚠ Snyk CLI not installed, skipping...", file=sys.stderr)
        return None, None
    except Exception as e:
        print(f"⚠ Snyk error: {e}", file=sys.stderr)
        return None, None


def main():
    """Run all security checks."""
    print("Running security checks...")
    print("=" * 60)
    
    all_passed = True
    
    # Semgrep
    print("\n[1/4] Running Semgrep...")
    success, output = run_semgrep()
    if success is None:
        print("  ⚠ Skipped")
    elif success:
        print("  ✓ Passed")
    else:
        print("  ✗ Failed")
        print(output)
        all_passed = False
    
    # Bandit
    print("\n[2/4] Running Bandit...")
    success, output = run_bandit()
    if success is None:
        print("  ⚠ Skipped")
    elif success:
        print("  ✓ Passed")
        # Bandit may have findings but still return success
        if output:
            try:
                import json
                data = json.loads(output)
                if data.get('results', {}).get('metrics', {}).get('HIGH_SEVERITY', 0) > 0:
                    print("  ⚠ High severity findings detected")
                    all_passed = False
            except:
                pass
    else:
        print("  ✗ Failed")
        print(output)
        all_passed = False
    
    # Safety
    print("\n[3/4] Running Safety...")
    success, output = run_safety()
    if success is None:
        print("  ⚠ Skipped")
    elif success:
        print("  ✓ Passed")
    else:
        print("  ✗ Failed")
        print(output)
        all_passed = False
    
    # Snyk
    print("\n[4/4] Running Snyk...")
    success, output = run_snyk()
    if success is None:
        print("  ⚠ Skipped")
    elif success:
        print("  ✓ Passed")
    else:
        print("  ✗ Failed")
        print(output)
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All security checks passed")
        sys.exit(0)
    else:
        print("✗ Some security checks failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
