# chorut

A Python library that provides chroot functionality inspired by arch-chroot with minimal dependencies, using only Python standard library modules.

## Features

- **Complete chroot setup**: Automatically mounts proc, sys, dev, devpts, shm, run, and tmp filesystems
- **Custom mounts**: Support for user-defined bind mounts and filesystem mounts
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

# With custom mounts
custom_mounts = [
    {
        "source": "/home",
        "target": "home",
        "bind": True,
        "options": "ro"  # Read-only bind mount
    },
    {
        "source": "tmpfs",
        "target": "workspace",
        "fstype": "tmpfs",
        "options": "size=1G"
    }
]

with ChrootManager('/path/to/chroot', custom_mounts=custom_mounts) as chroot:
    result = chroot.execute(['df', '-h'])
```

### Custom Mounts

You can specify additional mounts to be set up in the chroot environment. Each mount specification is a dictionary with the following keys:

- `source` (required): Source path, device, or filesystem type
- `target` (required): Target path relative to chroot root
- `fstype` (optional): Filesystem type (e.g., "tmpfs", "ext4")
- `options` (optional): Mount options (e.g., "ro", "size=1G")
- `bind` (optional): Whether this is a bind mount (default: False)
- `mkdir` (optional): Whether to create target directory (default: True)

#### Examples:

```python
# Bind mount home directory as read-only
{
    "source": "/home",
    "target": "home",
    "bind": True,
    "options": "ro"
}

# Create a tmpfs workspace
{
    "source": "tmpfs",
    "target": "tmp/workspace",
    "fstype": "tmpfs",
    "options": "size=512M,mode=1777"
}

# Bind mount a specific directory
{
    "source": "/var/cache/pacman",
    "target": "var/cache/pacman",
    "bind": True
}
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

# Custom mounts
chorut -m "/home:home:bind,ro" -m "tmpfs:workspace:size=1G" /path/to/chroot

# Multiple custom mounts
chorut -N \
  -m "/var/cache:var/cache:bind" \
  -m "tmpfs:tmp/build:size=2G" \
  /path/to/chroot make -j4
```

#### Command Line Mount Format

The `-m/--mount` option accepts mount specifications in the format:

```
SOURCE:TARGET[:OPTIONS]
```

- **SOURCE**: Source path, device, or filesystem type
- **TARGET**: Target path relative to chroot (without leading slash)
- **OPTIONS**: Comma-separated mount options (optional)

Special options:
- `bind` - Creates a bind mount
- Other options are passed to the mount command

Examples:
- `-m "/home:home:bind,ro"` - Read-only bind mount of /home
- `-m "tmpfs:workspace:size=1G"` - 1GB tmpfs at /workspace
- `-m "/dev/sdb1:mnt/data:rw"` - Mount device with read-write access

### Command Line Options

- `-h, --help`: Show help message
- `-N, --unshare`: Run in unshare mode as regular user
- `-u USER[:GROUP], --userspec USER[:GROUP]`: Specify user/group to run as
- `-v, --verbose`: Enable verbose logging
- `-m SOURCE:TARGET[:OPTIONS], --mount SOURCE:TARGET[:OPTIONS]`: Add custom mount (can be used multiple times)

## API Reference

### ChrootManager

The main class for managing chroot environments.

#### Constructor

```python
ChrootManager(chroot_dir, unshare_mode=False, custom_mounts=None)
```

- `chroot_dir`: Path to the chroot directory
- `unshare_mode`: Whether to use unshare mode for non-root operation
- `custom_mounts`: Optional list of custom mount specifications

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
