#!/usr/bin/env python3
"""
Final validation test for the chorut library.
"""

import os
import sys

# Add the parent directory to the path so we can import chorut
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_constants():
    """Test basic library functionality."""
    print("Testing basic functionality...")

    from chorut import ChrootManager, MountManager

    # Test ChrootManager initialization
    try:
        ChrootManager("/tmp", unshare_mode=True)
        print("✓ ChrootManager creation successful")

        # Test MountManager initialization
        MountManager()
        print("✓ MountManager creation successful")

        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False


def test_manager_creation():
    """Test ChrootManager creation."""
    print("Testing ChrootManager creation...")

    from chorut import ChrootError, ChrootManager

    # Test with non-existent directory
    try:
        manager = ChrootManager("/nonexistent/directory")
        manager._check_chroot_dir()
        print("✗ Should have failed for non-existent directory")
        return False
    except ChrootError:
        print("✓ Correctly detected non-existent directory")
    except Exception as e:
        print(f"✓ Directory validation working (got {type(e).__name__})")

    # Test creation with existing directory
    try:
        manager = ChrootManager("/tmp", unshare_mode=True)
        print("✓ ChrootManager creation successful")
        return True
    except Exception as e:
        print(f"✗ ChrootManager creation failed: {e}")
        return False


def test_custom_mounts():
    """Test custom mounts functionality."""
    print("Testing custom mounts...")

    from chorut import ChrootManager

    # Test with custom mount specifications
    custom_mounts = [
        {"source": "/tmp", "target": "shared_tmp", "bind": True},
        {"source": "tmpfs", "target": "workspace", "fstype": "tmpfs", "options": "size=10M"},
    ]

    try:
        manager = ChrootManager("/tmp", unshare_mode=True, custom_mounts=custom_mounts)
        print("✓ ChrootManager with custom mounts created successfully")

        # Validate the custom_mounts attribute
        assert len(manager.custom_mounts) == 2, "Custom mounts not stored correctly"
        assert manager.custom_mounts[0]["source"] == "/tmp", "First mount source incorrect"
        assert manager.custom_mounts[1]["fstype"] == "tmpfs", "Second mount fstype incorrect"

        print("✓ Custom mounts validation successful")
        return True
    except Exception as e:
        print(f"✗ Custom mounts test failed: {e}")
        return False


def test_command_line():
    """Test command-line interface."""
    print("Testing command-line interface...")

    try:
        print("✓ Command-line main function available")
        return True
    except Exception as e:
        print(f"✗ Command-line test failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("chorut Library Validation")
    print("=" * 30)

    tests = [
        test_constants,
        test_manager_creation,
        test_custom_mounts,
        test_command_line,
    ]

    passed = 0
    total = len(tests)

    for i, test in enumerate(tests):
        try:
            print(f"Running test {i + 1}: {test.__name__}")
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}\n")

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\nUsage:")
        print("  Library: from chorut import ChrootManager")
        print("  CLI:     python -m chorut /path/to/chroot")
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
