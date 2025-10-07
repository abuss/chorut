# chorut

A Python library that provides chroot functionality inspired by arch-chroot with minimal dependencies, using only Python standard library modules.

## Features

- **Complete chroot setup**: Automatically mounts proc, sys, dev, devpts, shm, run, and tmp filesystems
- **Unshare mode**: Support for running as non-root user using Linux namespaces
- **Context manager**: Clean automatic setup and teardown
- **resolv.conf handling**: Proper DNS configuration in chroot
- **Error handling**: Comprehensive error reporting and cleanup
- **Zero external dependencies**: Uses only Python standard library

## Installation

```bash
pip install chorut
```

## Usage

### As a Library

```python
from chorut import ChrootManager

# Basic usage as root
with ChrootManager('/path/to/chroot') as chroot:
    result = chroot.execute(['ls', '-la'])

# Non-root usage with unshare mode
with ChrootManager('/path/to/chroot', unshare_mode=True) as chroot:
    result = chroot.execute(['whoami'])

# Manual setup/teardown
chroot = ChrootManager('/path/to/chroot')
chroot.setup()
try:
    result = chroot.execute(['bash', '-c', 'echo "Hello from chroot"'])
finally:
    chroot.teardown()
```

### Command Line

```bash
# Basic chroot (requires root)
sudo chorut /path/to/chroot

# Run specific command
sudo chorut /path/to/chroot ls -la

# Non-root mode
chorut -N /path/to/chroot

# Specify user
sudo chorut -u user:group /path/to/chroot

# Verbose output
chorut -v -N /path/to/chroot
```

## API Reference

### ChrootManager

The main class for managing chroot environments.

#### Constructor

```python
ChrootManager(chroot_dir, unshare_mode=False)
```

- `chroot_dir`: Path to the chroot directory
- `unshare_mode`: Whether to use unshare mode for non-root operation

#### Methods

- `setup()`: Set up the chroot environment
- `teardown()`: Clean up the chroot environment
- `execute(command=None, userspec=None)`: Execute a command in the chroot

### Exceptions

- `ChrootError`: Raised for chroot-related errors
- `MountError`: Raised for mount-related errors

## Requirements

- Python 3.12+
- Linux system with mount/umount utilities
- Root privileges (unless using unshare mode)

## License

This project is in the public domain.
