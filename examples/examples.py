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

            # Shell features require explicit bash invocation
            # This will NOT work (backticks are treated as literal):
            # result = chroot.execute("echo `ls | wc -l`")

            # This WILL work (explicit shell):
            result = chroot.execute("bash -c 'echo `ls /tmp | wc -l`'")
            print(f"Command substitution exit code: {result.returncode}")

            result = chroot.execute("bash -c 'ls /tmp | wc -l'")
            print(f"Pipe command exit code: {result.returncode}")

            result = chroot.execute("bash -c 'echo hello && echo world'")
            print(f"Logical operator exit code: {result.returncode}")

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

    # Only try root mode if running as root
    if sys.platform == "linux":
        example_with_userspec()
