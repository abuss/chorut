#!/usr/bin/env python3
"""
Simple test script for chorut library.
"""

import shutil
import tempfile
from pathlib import Path

from chorut import ChrootError, ChrootManager


def create_minimal_chroot():
    """Create a minimal chroot directory structure for testing."""
    chroot_dir = Path(tempfile.mkdtemp(prefix="chorut_test_"))

    # Create basic directory structure
    (chroot_dir / "bin").mkdir()
    (chroot_dir / "etc").mkdir()
    (chroot_dir / "usr/bin").mkdir(parents=True)

    # Copy essential binaries
    for binary in ["/bin/bash", "/bin/ls", "/bin/echo"]:
        if Path(binary).exists():
            shutil.copy2(binary, chroot_dir / "bin" / Path(binary).name)

    # Create a simple shell script for testing
    test_script = chroot_dir / "bin/test.sh"
    test_script.write_text("#!/bin/bash\necho 'Hello from chroot'\n")
    test_script.chmod(0o755)

    return chroot_dir


def test_library():
    """Test the chorut library functionality."""
    print("Creating test chroot directory...")
    chroot_dir = create_minimal_chroot()

    try:
        print(f"Testing with chroot directory: {chroot_dir}")

        # Test basic functionality
        print("Testing ChrootManager initialization...")
        chroot = ChrootManager(chroot_dir, unshare_mode=True)

        print("Testing setup...")
        chroot.setup()

        print("Testing command execution...")
        result = chroot.execute(["/bin/test.sh"])
        print(f"Command exit code: {result.returncode}")

        print("Testing teardown...")
        chroot.teardown()

        print("Testing context manager...")
        with ChrootManager(chroot_dir, unshare_mode=True) as cm:
            result = cm.execute(["echo", "Context manager test"])
            print(f"Context manager exit code: {result.returncode}")

        print("All tests completed successfully!")

    except ChrootError as e:
        print(f"ChrootError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print(f"Cleaning up test directory: {chroot_dir}")
        shutil.rmtree(chroot_dir)


if __name__ == "__main__":
    test_library()
