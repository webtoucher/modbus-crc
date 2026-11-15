"""Compare the current CRC-16/MODBUS implementation with the one from 1.x.

The 1.x loop is frozen below: two 256-byte tables, a separate high and low
register byte and an ``int()`` call per byte. Its hand-written tables are the
high and low halves of the generated one (under inverted names), so they are
rebuilt here instead of being pasted as 512 hex bytes. Both implementations
sign the same payloads and must agree byte for byte.

Run it from the repository root::

    python benchmarks/benchmark_crc.py
"""

import timeit

from modbus_crc import _CRC_TABLE, crc16

# modbus-crc 1.3 called the high half LOW_BYTES and the low half HIGH_BYTES.
LOW_BYTES = bytes(value >> 8 for value in _CRC_TABLE)
HIGH_BYTES = bytes(value & 0xFF for value in _CRC_TABLE)


def crc16_1x(data: bytes) -> bytes:
    """CRC-16/MODBUS as implemented in modbus-crc 1.3."""
    crc_high = 0xFF
    crc_low = 0xFF

    for byte in data:
        index = crc_high ^ int(byte)
        crc_high = crc_low ^ HIGH_BYTES[index]
        crc_low = LOW_BYTES[index]

    return bytes([crc_high, crc_low])


# Payload and repetition count for one timed run (bigger payloads need fewer).
PAYLOADS = [
    ("8-byte frame", b"\x01\x03\x00\x00\x00\x0A\xC5\xCD", 20_000),
    ("1 KiB", bytes(range(256)) * 4, 500),
    ("64 KiB", bytes(range(256)) * 256, 10),
]


def _best_seconds(func, payload: bytes, number: int) -> float:
    """Return the fastest seconds per call over five runs."""
    timer = timeit.Timer(lambda: func(payload))
    return min(timer.repeat(repeat=5, number=number)) / number


def main() -> None:
    print(f"{'payload':<14}{'1.x MB/s':>10}{'now MB/s':>10}{'speedup':>10}")
    for label, payload, number in PAYLOADS:
        assert crc16(payload) == crc16_1x(payload), label
        seconds_1x = _best_seconds(crc16_1x, payload, number)
        seconds_now = _best_seconds(crc16, payload, number)
        mib = max(len(payload), 1) / 1024 / 1024
        print(
            f"{label:<14}{mib / seconds_1x:>10.1f}{mib / seconds_now:>10.1f}"
            f"{seconds_1x / seconds_now:>9.2f}x"
        )


if __name__ == "__main__":
    main()
