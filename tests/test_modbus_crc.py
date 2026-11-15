"""Tests for the modbus_crc package."""

import random

import pytest

from modbus_crc import __all__, add_crc, check_crc, crc16

# Frame without checksum and the checksum exactly as it goes on the wire
# (low byte first). The first three frames are canonical Modbus examples.
KNOWN_FRAMES = [
    (b"\x01\x03\x00\x00\x00\x0A", b"\xC5\xCD"),
    (b"\x11\x03\x00\x6B\x00\x03", b"\x76\x87"),
    (b"\x00\x12\x34\xAB\xCD\xEF", b"\xD2\xD4"),
    (b"\xFF" * 8, b"\x01\x8F"),
    (b"\x00", b"\xBF\x40"),
    (b"\xFF", b"\xFF\x00"),
    (b"", b"\xFF\xFF"),
]


def _reference_crc16(data: bytes) -> bytes:
    """Bit-by-bit CRC-16/MODBUS, written straight from the protocol spec."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return bytes((crc & 0xFF, crc >> 8))


@pytest.mark.parametrize("frame, checksum", KNOWN_FRAMES)
def test_known_frames(frame, checksum):
    assert crc16(frame) == checksum
    assert add_crc(frame) == frame + checksum
    assert check_crc(frame + checksum)


@pytest.mark.parametrize("frame, checksum", KNOWN_FRAMES)
def test_reference_oracle_agrees_with_known_frames(frame, checksum):
    assert _reference_crc16(frame) == checksum


def test_table_matches_reference_implementation():
    rng = random.Random(20231115)
    for length in [0, 1, 2, 3, 8, 32, 255, 1024]:
        data = bytes(rng.randrange(256) for _ in range(length))
        assert crc16(data) == _reference_crc16(data)


def test_empty_package_is_rejected():
    assert not check_crc(b"")


def test_corrupted_package_is_rejected():
    signed = add_crc(b"\x01\x03\x00\x00\x00\x0A")
    for index in range(len(signed)):
        corrupted = bytearray(signed)
        corrupted[index] ^= 0x01
        assert not check_crc(corrupted), f"corruption at byte {index} not detected"


def test_unsigned_package_is_rejected():
    assert not check_crc(b"\x01\x03\x00\x00\x00\x0A")


def test_accepts_bytes_like_objects():
    payload = b"\x01\x03\x00\x00\x00\x0A"
    assert crc16(bytearray(payload)) == crc16(payload)
    assert crc16(memoryview(payload)) == crc16(payload)
    assert isinstance(add_crc(bytearray(payload)), bytes)


def test_checksum_is_two_bytes():
    assert crc16(b"\x01\x03") == crc16(b"\x01\x03")
    assert len(crc16(b"\x01\x03")) == 2


def test_public_api_is_explicit():
    assert __all__ == ["crc16", "add_crc", "check_crc"]
