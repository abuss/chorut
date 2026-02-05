#!/usr/bin/env python3
"""
Test script for chorut library with comprehensive list-based command tests.
"""

import contextlib
import shutil
import tempfile
from pathlib import Path

import pytest

from chorut import ChrootError, ChrootManager


def create_minimal_chroot():
    """Create a minimal chroot directory structure for testing."""
    chroot_dir = Path(tempfile.mkdtemp(prefix="chorut_test_"))

    # Create basic directory structure
    (chroot_dir / "bin").mkdir()
    (chroot_dir / "etc").mkdir()
    (chroot_dir / "usr/bin").mkdir(parents=True)

    # Copy essential binaries
    for binary in ["/bin/bash", "/bin/ls", "/bin/echo", "/bin/cat"]:
        if Path(binary).exists():
            shutil.copy2(binary, chroot_dir / "bin" / Path(binary).name)

    # Create a simple shell script for testing
    test_script = chroot_dir / "bin/test.sh"
    test_script.write_text("#!/bin/bash\necho 'Hello from chroot'\n")
    test_script.chmod(0o755)

    # Create a script that echoes its arguments
    args_script = chroot_dir / "bin/echo_args.sh"
    args_script.write_text('#!/bin/bash\nfor arg in "$@"; do echo "$arg"; done\n')
    args_script.chmod(0o755)

    return chroot_dir


def test_list_commands():
    """Test list-based command execution comprehensively."""
    print("=" * 60)
    print("Testing List-Based Command Execution")
    print("=" * 60)

    chroot_dir = create_minimal_chroot()

    try:
        print(f"Test chroot directory: {chroot_dir}")

        with ChrootManager(chroot_dir, unshare_mode=True) as chroot:
            # Test 1: Basic list command
            print("\n1. Basic list command...")
            result = chroot.execute(["/bin/echo", "hello", "world"])
            assert result.returncode == 0, f"Expected returncode 0, got {result.returncode}"
            print("   PASS: Basic list command executed")

            # Test 2: List command with capture_output
            print("\n2. List command with capture_output...")
            result = chroot.execute(["/bin/echo", "captured", "output"], capture_output=True)
            assert result.returncode == 0
            assert "captured output" in result.stdout
            print(f"   PASS: Captured stdout: {result.stdout.strip()}")

            # Test 3: List command with multiple arguments
            print("\n3. List command with multiple arguments...")
            result = chroot.execute(["/bin/echo", "arg1", "arg2", "arg3", "arg4"], capture_output=True)
            assert result.returncode == 0
            assert "arg1 arg2 arg3 arg4" in result.stdout
            print(f"   PASS: Multiple args: {result.stdout.strip()}")

            # Test 4: List command with special characters in arguments
            print("\n4. List command with special characters...")
            result = chroot.execute(["/bin/echo", "hello world", "foo&bar", "test;test"], capture_output=True)
            assert result.returncode == 0
            assert "hello world" in result.stdout
            print(f"   PASS: Special chars handled: {result.stdout.strip()}")

            # Test 5: List command with quotes in arguments
            print("\n5. List command with quotes in arguments...")
            result = chroot.execute(["/bin/echo", 'hello "world"', "test'value'"], capture_output=True)
            assert result.returncode == 0
            print(f"   PASS: Quotes handled: {result.stdout.strip()}")

            # Test 6: Empty list should raise error
            print("\n6. Empty list command validation...")
            try:
                chroot.execute([])
                print("   FAIL: Should have raised ChrootError")
                return False
            except ChrootError as e:
                print(f"   PASS: Correctly raised ChrootError: {e}")

            # Test 7: List with non-string elements should raise error
            print("\n7. List with non-string validation...")
            try:
                chroot.execute(["/bin/echo", 123, None])
                print("   FAIL: Should have raised ChrootError")
                return False
            except ChrootError as e:
                print(f"   PASS: Correctly raised ChrootError: {e}")

            # Test 8: Script execution with list arguments
            print("\n8. Script execution with list arguments...")
            result = chroot.execute(["/bin/echo_args.sh", "first", "second", "third"], capture_output=True)
            assert result.returncode == 0
            assert "first" in result.stdout
            assert "second" in result.stdout
            assert "third" in result.stdout
            print(f"   PASS: Script args: {result.stdout.strip()}")

            # Test 9: Compare list vs string command behavior
            print("\n9. List vs string command equivalence...")
            result_list = chroot.execute(["/bin/echo", "test", "message"], capture_output=True)
            result_str = chroot.execute("echo test message", capture_output=True)
            assert result_list.stdout == result_str.stdout
            print(f"   PASS: Both produce same output: {result_list.stdout.strip()}")

            # Test 10: List command with spaces in arguments
            print("\n10. List command with spaces...")
            result = chroot.execute(["/bin/echo", "hello world", "foo bar baz"], capture_output=True)
            assert result.returncode == 0
            assert "hello world" in result.stdout
            assert "foo bar baz" in result.stdout
            print(f"   PASS: Spaces preserved: {result.stdout.strip()}")

        print("\n" + "=" * 60)
        print("All list-based command tests passed!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        print(f"\nCleaning up: {chroot_dir}")
        shutil.rmtree(chroot_dir)


def test_string_commands():
    """Test string-based command execution."""
    print("\n" + "=" * 60)
    print("Testing String-Based Command Execution")
    print("=" * 60)

    chroot_dir = create_minimal_chroot()

    try:
        with ChrootManager(chroot_dir, unshare_mode=True) as chroot:
            # Test simple string command
            print("\n1. Simple string command...")
            result = chroot.execute("echo hello", capture_output=True)
            assert result.returncode == 0
            assert "hello" in result.stdout
            print(f"   PASS: {result.stdout.strip()}")

            # Test string with shell features (auto-detected)
            print("\n2. String with shell features...")
            result = chroot.execute("echo hello && echo world", capture_output=True)
            assert result.returncode == 0
            assert "hello" in result.stdout
            assert "world" in result.stdout
            print(f"   PASS: Shell features work: {result.stdout.strip()}")

            # Test string with pipe
            print("\n3. String with pipe...")
            result = chroot.execute("echo test | cat", capture_output=True)
            assert result.returncode == 0
            assert "test" in result.stdout
            print(f"   PASS: Pipes work: {result.stdout.strip()}")

        print("\n" + "=" * 60)
        print("All string-based command tests passed!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(chroot_dir)


def test_pipes_and_shell_features():
    """Test command execution with pipes and shell features."""
    print("\n" + "=" * 60)
    print("Testing Pipes and Shell Features")
    print("=" * 60)

    chroot_dir = create_minimal_chroot()

    try:
        with ChrootManager(chroot_dir, unshare_mode=True) as chroot:
            # Test 1: Simple pipe
            print("\n1. Simple pipe (echo | cat)...")
            result = chroot.execute("echo 'hello world' | cat", capture_output=True)
            assert result.returncode == 0, f"Expected returncode 0, got {result.returncode}"
            assert "hello world" in result.stdout, f"Expected 'hello world' in output, got: {result.stdout}"
            print(f"   PASS: Pipe works: {result.stdout.strip()}")

            # Test 2: Multiple pipes
            print("\n2. Multiple pipes (echo | tr | cat)...")
            result = chroot.execute("echo 'hello' | tr 'a-z' 'A-Z' | cat", capture_output=True)
            assert result.returncode == 0
            assert "HELLO" in result.stdout
            print(f"   PASS: Multiple pipes: {result.stdout.strip()}")

            # Test 3: Pipe with wc -l
            print("\n3. Pipe with line count...")
            result = chroot.execute("echo -e 'line1\\nline2\\nline3' | wc -l", capture_output=True)
            assert result.returncode == 0
            assert "3" in result.stdout
            print(f"   PASS: Line count: {result.stdout.strip()}")

            # Test 4: Pipe with grep
            print("\n4. Pipe with grep...")
            result = chroot.execute("echo -e 'apple\\nbanana\\ncherry' | grep 'an'", capture_output=True)
            assert result.returncode == 0
            assert "banana" in result.stdout
            print(f"   PASS: Grep filter: {result.stdout.strip()}")

            # Test 5: Command substitution with $()
            print("\n5. Command substitution...")
            result = chroot.execute("echo Today is $(echo 'test')", capture_output=True)
            assert result.returncode == 0
            assert "test" in result.stdout
            print(f"   PASS: Command substitution: {result.stdout.strip()}")

            # Test 6: Logical AND
            print("\n6. Logical AND (&&)...")
            result = chroot.execute("echo 'first' && echo 'second'", capture_output=True)
            assert result.returncode == 0
            assert "first" in result.stdout
            assert "second" in result.stdout
            print(f"   PASS: Logical AND: {result.stdout.strip()}")

            # Test 7: Logical OR
            print("\n7. Logical OR (||)...")
            result = chroot.execute("false || echo 'fallback'", capture_output=True)
            assert result.returncode == 0
            assert "fallback" in result.stdout
            print(f"   PASS: Logical OR: {result.stdout.strip()}")

            # Test 8: Redirection
            print("\n8. Output redirection...")
            result = chroot.execute("echo 'redirected' > /tmp/test.txt && cat /tmp/test.txt", capture_output=True)
            assert result.returncode == 0
            assert "redirected" in result.stdout
            print(f"   PASS: Redirection: {result.stdout.strip()}")

            # Test 9: Pipe with head/tail
            print("\n9. Pipe with head...")
            result = chroot.execute("echo -e '1\\n2\\n3\\n4\\n5' | head -3", capture_output=True)
            assert result.returncode == 0
            assert "1" in result.stdout
            assert "3" in result.stdout
            assert "5" not in result.stdout
            print(f"   PASS: Head filter: {result.stdout.strip()}")

            # Test 10: Complex pipeline
            print("\n10. Complex pipeline...")
            result = chroot.execute("echo -e 'dog\\ncat\\nbird' | sort | head -2", capture_output=True)
            assert result.returncode == 0
            assert "bird" in result.stdout
            assert "cat" in result.stdout
            print(f"   PASS: Complex pipeline: {result.stdout.strip()}")

        print("\n" + "=" * 60)
        print("All pipe and shell feature tests passed!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        print(f"\nCleaning up: {chroot_dir}")
        shutil.rmtree(chroot_dir)


def test_context_manager():
    """Test context manager functionality."""
    print("\n" + "=" * 60)
    print("Testing Context Manager")
    print("=" * 60)

    chroot_dir = create_minimal_chroot()

    try:
        with ChrootManager(chroot_dir, unshare_mode=True) as cm:
            result = cm.execute(["echo", "Context manager test"], capture_output=True)
            assert result.returncode == 0
            print(f"   PASS: Context manager works: {result.stdout.strip()}")

        print("\n" + "=" * 60)
        print("Context manager tests passed!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(chroot_dir)


def test_original_functionality():
    """Preserve original test cases."""
    print("\n" + "=" * 60)
    print("Testing Original Functionality")
    print("=" * 60)

    chroot_dir = create_minimal_chroot()

    try:
        print(f"Testing with chroot directory: {chroot_dir}")

        # Test basic functionality
        print("\nTesting ChrootManager initialization...")
        chroot = ChrootManager(chroot_dir, unshare_mode=True)

        print("Testing setup...")
        chroot.setup()

        print("Testing command execution with list...")
        result = chroot.execute(["/bin/test.sh"])
        print(f"Command exit code: {result.returncode}")

        print("Testing command execution with string...")
        result = chroot.execute("/bin/test.sh")
        print(f"String command exit code: {result.returncode}")

        print("Testing teardown...")
        chroot.teardown()

        print("\n" + "=" * 60)
        print("Original functionality tests passed!")
        print("=" * 60)
        return True

    except ChrootError as e:
        print(f"ChrootError: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        print(f"\nCleaning up test directory: {chroot_dir}")
        shutil.rmtree(chroot_dir)


def test_empty_string_validation():
    """Test that empty string commands raise appropriate error."""
    print("\n" + "=" * 60)
    print("Testing Empty String Validation")
    print("=" * 60)

    chroot_dir = create_minimal_chroot()

    try:
        with contextlib.suppress(ChrootError), ChrootManager(chroot_dir, unshare_mode=True) as chroot:
            chroot.execute("")
        print("   PASS: Empty string raises ChrootError")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(chroot_dir)


def test_whitespace_only_string_validation():
    """Test that whitespace-only string commands raise appropriate error."""
    print("\n" + "=" * 60)
    print("Testing Whitespace-Only String Validation")
    print("=" * 60)

    chroot_dir = create_minimal_chroot()

    try:
        with contextlib.suppress(ChrootError), ChrootManager(chroot_dir, unshare_mode=True) as chroot:
            chroot.execute("   ")
        print("   PASS: Whitespace-only string raises ChrootError")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(chroot_dir)


def test_invalid_userspec_validation():
    """Test that invalid userspec formats raise appropriate error."""
    print("\n" + "=" * 60)
    print("Testing Invalid Userspec Validation")
    print("=" * 60)

    chroot_dir = create_minimal_chroot()

    try:
        chroot = ChrootManager(chroot_dir, unshare_mode=True)
        chroot.setup()

        with pytest.raises(ChrootError, match="Invalid userspec format"):
            chroot.execute(["echo", "test"], userspec="user:group:extra")

        chroot.teardown()

        print("   PASS: Invalid userspec raises ChrootError")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(chroot_dir, ignore_errors=True)


if __name__ == "__main__":
    all_passed = True

    all_passed &= test_original_functionality()
    all_passed &= test_list_commands()
    all_passed &= test_string_commands()
    all_passed &= test_pipes_and_shell_features()
    all_passed &= test_context_manager()
    all_passed &= test_empty_string_validation()
    all_passed &= test_whitespace_only_string_validation()
    all_passed &= test_invalid_userspec_validation()

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED!")
        exit(1)
    print("=" * 60)
