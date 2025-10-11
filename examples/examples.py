#!/usr/bin/env python3
"""
Example usage of the chorut library.
"""

import sys

from chorut import ChrootError, ChrootManager


def example_basic_usage():
    """Example of basic library usage."""
    print("=== Basic Usage Example ===")

    # Replace with your actual chroot directory
    chroot_path = "/tmp/my_chroot"

    try:
        # Create and use chroot with context manager
        with ChrootManager(chroot_path, unshare_mode=True) as chroot:
            # Execute a simple command using list
            result = chroot.execute(["echo", "Hello from chroot!"])
            print(f"List command exit code: {result.returncode}")

            # Execute a simple command using string
            result = chroot.execute("echo 'Hello from chroot with string!'")
            print(f"String command exit code: {result.returncode}")

            # Execute a command and capture its output
            result = chroot.execute("echo 'Captured output!'", capture_output=True)
            print(f"Capture command exit code: {result.returncode}")
            if result.stdout:
                print(f"Captured output: {result.stdout.strip()}")

            # Execute an interactive bash session (if running interactively)
            # result = chroot.execute()  # defaults to /bin/bash

    except ChrootError as e:
        print(f"Chroot error: {e}")
    except FileNotFoundError:
        print(f"Chroot directory not found: {chroot_path}")
        print("Please create a chroot directory or update the path")


def example_manual_setup():
    """Example of manual setup and teardown."""
    print("\n=== Manual Setup Example ===")

    chroot_path = "/tmp/my_chroot"

    # Manual setup and teardown
    chroot = ChrootManager(chroot_path, unshare_mode=True)

    try:
        print("Setting up chroot...")
        chroot.setup()

        print("Executing command...")
        result = chroot.execute(["whoami"])
        print(f"List command exit code: {result.returncode}")

        result = chroot.execute("whoami")
        print(f"String command exit code: {result.returncode}")

        result = chroot.execute("whoami", capture_output=True)
        print(f"Capture command exit code: {result.returncode}")
        if result.stdout:
            print(f"Captured user: {result.stdout.strip()}")
        if result.stderr:
            print(f"Captured error: {result.stderr.strip()}")

    except ChrootError as e:
        print(f"Error: {e}")
    finally:
        print("Tearing down chroot...")
        chroot.teardown()


def example_with_userspec():
    """Example using different user specification."""
    print("\n=== User Specification Example ===")

    chroot_path = "/tmp/my_chroot"

    try:
        with ChrootManager(chroot_path) as chroot:  # Root mode
            # Run as specific user (requires root privileges)
            result = chroot.execute(["id"], userspec="nobody")
            print(f"User command exit code: {result.returncode}")

    except ChrootError as e:
        print(f"Error: {e}")
        print("Note: This example requires root privileges")


def example_shell_features():
    """Example of using shell features with string commands."""
    print("\n=== Shell Features Example ===")

    chroot_path = "/tmp/my_chroot"

    try:
        with ChrootManager(chroot_path, unshare_mode=True) as chroot:
            # Simple commands work directly
            result = chroot.execute("echo 'Hello World'")
            print(f"Simple string command exit code: {result.returncode}")

            # Shell features now work automatically with auto_shell=True (default)
            print("\n--- Auto-detected shell features ---")

            # Pipes - now works automatically
            result = chroot.execute("ls /tmp | wc -l", capture_output=True)
            print(f"Pipe command exit code: {result.returncode}")
            if result.stdout:
                print(f"Pipe output: {result.stdout.strip()}")

            # Logical operators - now works automatically
            result = chroot.execute("echo hello && echo world", capture_output=True)
            print(f"Logical operator exit code: {result.returncode}")
            if result.stdout:
                print(f"Logical operator output: {result.stdout.strip()}")

            # Command substitution - now works automatically
            result = chroot.execute("echo `ls /tmp | wc -l`", capture_output=True)
            print(f"Command substitution exit code: {result.returncode}")
            if result.stdout:
                print(f"Command substitution output: {result.stdout.strip()}")

            # Glob patterns - now works automatically
            result = chroot.execute("ls /tmp/*.* 2>/dev/null || echo 'no files'", capture_output=True)
            print(f"Glob pattern exit code: {result.returncode}")
            if result.stdout:
                print(f"Glob pattern output: {result.stdout.strip()}")

            print("\n--- Manual shell invocation (still works) ---")
            # Manual shell invocation still works for complex cases
            result = chroot.execute("bash -c 'echo manually invoked shell'", capture_output=True)
            print(f"Manual bash -c exit code: {result.returncode}")
            if result.stdout:
                print(f"Manual bash -c output: {result.stdout.strip()}")

        print("\n--- With auto_shell=False ---")
        # Demonstrate auto_shell=False behavior
        with ChrootManager(chroot_path, unshare_mode=True, auto_shell=False) as chroot_manual:
            # This will NOT work without explicit bash -c when auto_shell=False
            result = chroot_manual.execute("echo 'simple command works'", capture_output=True)
            print(f"Simple command with auto_shell=False exit code: {result.returncode}")
            if result.stdout:
                print(f"Simple command output: {result.stdout.strip()}")

            # Shell features require explicit bash -c when auto_shell=False
            result = chroot_manual.execute("bash -c 'echo hello && echo world'", capture_output=True)
            print(f"Explicit bash -c with auto_shell=False exit code: {result.returncode}")
            if result.stdout:
                print(f"Explicit bash -c output: {result.stdout.strip()}")

    except ChrootError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print(f"Chroot directory not found: {chroot_path}")
        print("Please create a chroot directory or update the path")


def example_output_capture():
    """Example of capturing command output."""
    print("\n=== Output Capture Example ===")

    chroot_path = "/tmp/my_chroot"

    try:
        with ChrootManager(chroot_path, unshare_mode=True) as chroot:
            # Execute command without capturing output (goes to terminal)
            print("Command without capture:")
            result = chroot.execute("echo 'This goes to terminal'")
            print(f"Exit code: {result.returncode}")
            print(f"Stdout available: {result.stdout is not None}")

            print("\nCommand with capture:")
            # Execute command with output capture
            result = chroot.execute("echo 'This is captured'", capture_output=True)
            print(f"Exit code: {result.returncode}")
            print(f"Captured stdout: '{result.stdout.strip() if result.stdout else ''}'")
            print(f"Captured stderr: '{result.stderr.strip() if result.stderr else ''}'")

            print("\nShell command with capture:")
            # Capture output from shell commands
            result = chroot.execute("bash -c 'echo hello; echo world'", capture_output=True)
            print(f"Exit code: {result.returncode}")
            if result.stdout:
                print(f"Multi-line output: {result.stdout!r}")

            print("\nCommand with stderr:")
            # Capture stderr
            result = chroot.execute("bash -c 'echo stdout; echo stderr >&2; exit 0'", capture_output=True)
            print(f"Exit code: {result.returncode}")
            print(f"Stdout: '{result.stdout.strip() if result.stdout else ''}'")
            print(f"Stderr: '{result.stderr.strip() if result.stderr else ''}'")

    except ChrootError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print(f"Chroot directory not found: {chroot_path}")
        print("Please create a chroot directory or update the path")


def example_custom_mounts():
    """Example using custom mounts."""
    print("\n=== Custom Mounts Example ===")

    chroot_path = "/tmp/my_chroot"

    # Define custom mounts
    custom_mounts = [
        {
            "source": "/home",
            "target": "home",
            "bind": True,
            "options": "ro",  # Read-only bind mount
        },
        {"source": "/var/cache", "target": "var/cache", "bind": True},
        {"source": "tmpfs", "target": "workspace", "fstype": "tmpfs", "options": "size=1G"},
    ]

    try:
        with ChrootManager(chroot_path, unshare_mode=True, custom_mounts=custom_mounts) as chroot:
            result = chroot.execute(["df", "-h"])
            print(f"Mount listing exit code: {result.returncode}")

    except ChrootError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print(f"Chroot directory not found: {chroot_path}")
        print("Please create a chroot directory or update the path")


if __name__ == "__main__":
    print("chorut Library Examples")
    print("========================")

    example_basic_usage()
    example_manual_setup()
    example_custom_mounts()
    example_shell_features()
    example_output_capture()

    # Only try root mode if running as root
    if sys.platform == "linux":
        example_with_userspec()
