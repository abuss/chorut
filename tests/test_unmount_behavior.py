#!/usr/bin/env python3
"""
Test to verify unmount behavior with busy mounts.
"""

import subprocess
import unittest
from unittest.mock import Mock, patch

import pytest

from chorut import MountError, MountManager


class TestUnmountBehavior(unittest.TestCase):
    """Test unmount behavior with busy mounts."""

    def test_unmount_success(self):
        """Test successful unmount without errors."""
        manager = MountManager()
        manager.active_mounts = ["/test/mount"]

        with patch("subprocess.run") as mock_run:
            # Mock successful unmount
            mock_run.return_value = Mock(returncode=0, stderr=b"")

            manager.unmount_all()

            # Verify umount was called
            mock_run.assert_called_once_with(["umount", "/test/mount"], check=True, capture_output=True)

    def test_unmount_busy_fallback_to_lazy(self):
        """Test that busy mounts fall back to lazy unmount."""
        manager = MountManager()
        manager.active_mounts = ["/test/mount"]

        with patch("subprocess.run") as mock_run:
            # Create a CalledProcessError with stderr attribute
            error = subprocess.CalledProcessError(
                returncode=32, cmd=["umount", "/test/mount"], stderr=b"umount: /test/mount: target is busy.\n"
            )

            # First call (regular unmount) raises exception
            # Second call (lazy unmount) succeeds
            mock_run.side_effect = [
                error,  # First call raises
                None,  # Second call succeeds
            ]

            # Should not raise an error
            manager.unmount_all()

            # Verify both calls were made
            assert mock_run.call_count == 2

            # Verify the calls
            calls = mock_run.call_args_list
            assert calls[0][0][0] == ["umount", "/test/mount"]
            assert calls[1][0][0] == ["umount", "--lazy", "/test/mount"]

    def test_unmount_device_busy_fallback(self):
        """Test that device busy errors also fall back to lazy unmount."""
        manager = MountManager()
        manager.active_mounts = ["/test/mount"]

        with patch("subprocess.run") as mock_run:
            # First call fails with "device is busy"
            error = subprocess.CalledProcessError(
                returncode=32, cmd=["umount", "/test/mount"], stderr=b"umount: /test/mount: device is busy.\n"
            )

            mock_run.side_effect = [
                error,  # First call raises
                None,  # Second call succeeds
            ]

            manager.unmount_all()

            # Verify lazy unmount was attempted
            assert mock_run.call_count == 2
            calls = mock_run.call_args_list
            assert calls[1][0][0] == ["umount", "--lazy", "/test/mount"]

    def test_unmount_other_error_raises(self):
        """Test that other unmount errors are raised immediately."""
        manager = MountManager()
        manager.active_mounts = ["/test/mount"]

        with patch("subprocess.run") as mock_run:
            # Mock a different error (not busy)
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1, cmd=["umount", "/test/mount"], stderr=b"umount: /test/mount: not mounted.\n"
            )

            # Should raise MountError
            with pytest.raises(MountError) as cm:
                manager.unmount_all()

            # Should not attempt lazy unmount for non-busy errors
            assert mock_run.call_count == 1
            assert "not mounted" in str(cm.value)

    def test_lazy_unmount_failure_raises(self):
        """Test that lazy unmount failure is reported."""
        manager = MountManager()
        manager.active_mounts = ["/test/mount"]

        with patch("subprocess.run") as mock_run:
            # Both regular and lazy unmount fail
            error1 = subprocess.CalledProcessError(
                returncode=32, cmd=["umount", "/test/mount"], stderr=b"umount: /test/mount: target is busy.\n"
            )
            error2 = subprocess.CalledProcessError(
                returncode=1,
                cmd=["umount", "--lazy", "/test/mount"],
                stderr=b"umount: /test/mount: permission denied.\n",
            )

            mock_run.side_effect = [error1, error2]

            # Should raise MountError about lazy unmount failure
            with pytest.raises(MountError) as cm:
                manager.unmount_all()

            assert "Failed to lazy unmount" in str(cm.value)
            assert mock_run.call_count == 2

    def test_multiple_mounts_with_mixed_busy(self):
        """Test unmounting multiple mounts where some are busy."""
        manager = MountManager()
        manager.active_mounts = ["/test/mount1", "/test/mount2", "/test/mount3"]

        with patch("subprocess.run") as mock_run:
            # mount1: succeeds immediately
            # mount2: busy, lazy succeeds
            # mount3: succeeds immediately
            error = subprocess.CalledProcessError(
                returncode=32, cmd=["umount", "/test/mount2"], stderr=b"umount: /test/mount2: target is busy.\n"
            )

            mock_run.side_effect = [
                None,  # mount1 success
                error,  # mount2 regular fails
                None,  # mount2 lazy success
                None,  # mount3 success
            ]

            manager.unmount_all()

            # Verify all unmounts completed
            assert mock_run.call_count == 4


if __name__ == "__main__":
    unittest.main(verbosity=2)
