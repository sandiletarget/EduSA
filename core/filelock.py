"""Cross-platform file locking helper.

Provides simple `lock_file` / `unlock_file` helpers and a `FileLock` context
manager that uses `msvcrt` on Windows and `fcntl` on POSIX.

Usage:
    with FileLock(open('myfile', 'r+')):
        # exclusive locked section

This file is safe to import on both Windows and Unix.
"""
from __future__ import annotations

import os
from typing import BinaryIO

IS_WINDOWS = os.name == "nt"

if IS_WINDOWS:
    import msvcrt


def _windows_lock(f: BinaryIO, exclusive: bool = True, blocking: bool = True) -> bool:
    mode = msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK
    # lock the whole file by using a large size
    try:
        msvcrt.locking(f.fileno(), mode, 0x7FFFFFFF)
        return True
    except OSError:
        return False


def _windows_unlock(f: BinaryIO) -> None:
    try:
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 0x7FFFFFFF)
    except OSError:
        # best-effort; ignore
        pass


def _posix_lock(f: BinaryIO, exclusive: bool = True, blocking: bool = True) -> bool:
    import fcntl

    flags = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
    if not blocking:
        flags |= fcntl.LOCK_NB
    try:
        fcntl.flock(f.fileno(), flags)
        return True
    except (IOError, OSError):
        return False


def _posix_unlock(f: BinaryIO) -> None:
    import fcntl

    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass


def lock_file(f: BinaryIO, exclusive: bool = True, blocking: bool = True) -> bool:
    """Lock file `f`. Returns True if lock acquired, False otherwise (for non-blocking)."""
    if IS_WINDOWS:
        return _windows_lock(f, exclusive=exclusive, blocking=blocking)
    return _posix_lock(f, exclusive=exclusive, blocking=blocking)


def unlock_file(f: BinaryIO) -> None:
    """Unlock file `f` (best-effort)."""
    if IS_WINDOWS:
        return _windows_unlock(f)
    return _posix_unlock(f)


class FileLock:
    """Context manager for file locking.

    Default is an exclusive, blocking lock.
    """

    def __init__(self, f: BinaryIO, exclusive: bool = True, blocking: bool = True):
        self.f = f
        self.exclusive = exclusive
        self.blocking = blocking

    def __enter__(self):
        acquired = lock_file(self.f, exclusive=self.exclusive, blocking=self.blocking)
        if not acquired and not self.blocking:
            # For non-blocking callers, raise to notify failure to acquire
            raise BlockingIOError("Could not acquire non-blocking file lock")
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            unlock_file(self.f)
        finally:
            return False
