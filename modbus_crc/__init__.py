"""
CRC-16 calculation for the Modbus protocol.

The checksum is CRC-16/MODBUS: polynomial 0x8005 (reflected 0xA001),
initial value 0xFFFF, no final XOR, transmitted low byte first.

Copyright (c) 2023–2026 webtoucher
Distributed under the BSD 3-Clause license. See LICENSE.md for more info.
"""

from typing import Union

__all__ = ["crc16", "add_crc", "check_crc", "BytesLike"]

__version__ = "2.1.1"

BytesLike = Union[bytes, bytearray, memoryview]


def _build_crc_table(polynomial: int = 0xA001) -> tuple:
    """Build the 256-entry lookup table for CRC-16/MODBUS."""
    table = []
    for index in range(256):
        crc = index
        for _ in range(8):
            crc = (crc >> 1) ^ polynomial if crc & 1 else crc >> 1
        table.append(crc)
    return tuple(table)


_CRC_TABLE = _build_crc_table()


def _as_bytes(data: BytesLike) -> bytes:
    """Return the raw bytes of data, flat and contiguous.

    A bytes object is already flat and is returned as is. Everything else is
    copied out of its buffer, so a view of wide items or a strided slice
    contributes the bytes it lays out, not its elements.
    """
    if type(data) is bytes:
        return data
    return memoryview(data).tobytes()


def _crc_register(data: bytes) -> int:
    """Return the raw 16-bit CRC register value of a byte string."""
    crc = 0xFFFF
    for byte in data:
        crc = (crc >> 8) ^ _CRC_TABLE[(crc ^ byte) & 0xFF]
    return crc


def _checksum(data: bytes) -> bytes:
    """Return the checksum of an already normalized byte string."""
    crc = _crc_register(data)
    return bytes((crc & 0xFF, crc >> 8))


def crc16(data: BytesLike) -> bytes:
    """Calculate CRC-16/MODBUS of data, low byte first as on the wire."""
    return _checksum(_as_bytes(data))


def add_crc(package: BytesLike) -> bytes:
    """Return package with CRC-16/MODBUS appended."""
    data = _as_bytes(package)
    return data + _checksum(data)


def check_crc(package: BytesLike) -> bool:
    """Return True if package carries a valid trailing CRC-16/MODBUS."""
    return _crc_register(_as_bytes(package)) == 0
