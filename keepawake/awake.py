"""Prevent system/display sleep via SetThreadExecutionState."""

from __future__ import annotations

import ctypes

kernel32 = ctypes.windll.kernel32

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

kernel32.SetThreadExecutionState.argtypes = [ctypes.c_uint]
kernel32.SetThreadExecutionState.restype = ctypes.c_uint


class AwakeGuard:
    def __init__(self) -> None:
        self._active = False

    @property
    def active(self) -> bool:
        return self._active

    def enable(self) -> bool:
        flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        prev = kernel32.SetThreadExecutionState(flags)
        self._active = prev != 0
        return self._active

    def disable(self) -> bool:
        prev = kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        self._active = False
        return prev != 0

    def toggle(self) -> bool:
        if self._active:
            self.disable()
        else:
            self.enable()
        return self._active
