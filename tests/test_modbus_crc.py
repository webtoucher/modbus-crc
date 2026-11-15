"""Tests for the modbus_crc package."""

import array
import random

import pytest

import modbus_crc
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


def test_table_matches_reference_for_every_one_and_two_byte_input():
    """Exhaustive check of all 256 one-byte and all 65 536 two-byte inputs."""
    for value in range(256):
        data = bytes((value,))
        assert crc16(data) == _reference_crc16(data), data
    for value in range(65536):
        data = value.to_bytes(2, "little")
        assert crc16(data) == _reference_crc16(data), data


def test_table_matches_reference_for_long_payloads():
    rng = random.Random(20231115)
    for length in [0, 3, 8, 32, 255, 1024]:
        data = bytes(rng.randrange(256) for _ in range(length))
        assert crc16(data) == _reference_crc16(data), data


def test_empty_package_is_rejected():
    assert not check_crc(b"")


def test_every_single_byte_corruption_is_rejected():
    """Flip every non-empty mask of every byte, as the README promises."""
    signed = add_crc(b"\x01\x03\x00\x00\x00\x0A")
    for index in range(len(signed)):
        for mask in range(1, 0x100):
            corrupted = bytearray(signed)
            corrupted[index] ^= mask
            assert not check_crc(corrupted), (
                f"corruption 0x{mask:02X} at byte {index} not detected"
            )


def test_unsigned_package_is_rejected():
    assert not check_crc(b"\x01\x03\x00\x00\x00\x0A")


def test_accepts_bytes_like_objects():
    payload = b"\x01\x03\x00\x00\x00\x0A"
    as_bytes = (bytearray(payload), memoryview(payload), array.array("B", payload))
    for same_payload in as_bytes:
        assert crc16(same_payload) == crc16(payload)
        assert add_crc(same_payload) == add_crc(payload)
        assert check_crc(add_crc(same_payload))
    assert isinstance(add_crc(bytearray(payload)), bytes)


def test_non_byte_memoryview_is_read_as_raw_bytes():
    """A view of wide items counts the same bytes as its flat representation."""
    words = array.array("H", [0x0102, 0x0304])
    raw = bytes(words)
    assert crc16(memoryview(words)) == crc16(raw)
    assert add_crc(memoryview(words)) == add_crc(raw)
    assert check_crc(add_crc(memoryview(words)))


def test_strided_memoryview_is_read_as_its_bytes():
    view = memoryview(b"abcdef")[::2]
    assert crc16(view) == crc16(b"ace")
    assert add_crc(view) == add_crc(b"ace")


@pytest.mark.parametrize("not_bytes_like", [5, "abc", None, [0x01, 0x03]])
def test_rejects_non_bytes_like_input(not_bytes_like):
    with pytest.raises(TypeError):
        crc16(not_bytes_like)
    with pytest.raises(TypeError):
        add_crc(not_bytes_like)
    with pytest.raises(TypeError):
        check_crc(not_bytes_like)


def test_checksum_is_two_bytes():
    assert len(crc16(b"\x01\x03")) == 2
    assert len(crc16(b"")) == 2


def test_public_api_is_explicit():
    for name in __all__:
        assert not name.startswith("_"), f"{name} is not a public name"
        assert hasattr(modbus_crc, name), f"{name} is in __all__ but missing in the module"
