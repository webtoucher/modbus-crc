"""
CRC-16 calculation for the Modbus protocol.

The checksum is CRC-16/MODBUS: polynomial 0xA001 (reflected 0x8005),
initial value 0xFFFF, no final XOR, transmitted low byte first.

Copyright (c) 2026 webtoucher
Distributed under the BSD 3-Clause license. See LICENSE for more info.
"""

from typing import Union

__all__ = ["crc16", "add_crc", "check_crc"]

__version__ = "2.0"

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


def _crc_register(data: BytesLike) -> int:
    """Return the raw 16-bit CRC register value of data."""
    crc = 0xFFFF
    for byte in data:
        crc = (crc >> 8) ^ _CRC_TABLE[(crc ^ byte) & 0xFF]
    return crc


def crc16(data: BytesLike) -> bytes:
    """Calculate CRC-16/MODBUS of data, low byte first as on the wire."""
    crc = _crc_register(data)
    return bytes((crc & 0xFF, crc >> 8))


def add_crc(package: BytesLike) -> bytes:
    """Return package with CRC-16/MODBUS appended."""
    return bytes(package) + crc16(package)


def check_crc(package: BytesLike) -> bool:
    """Return True if package carries a valid trailing CRC-16/MODBUS."""
    return _crc_register(package) == 0
