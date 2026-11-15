# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2026-11-15

### Fixed

- `add_crc` and `crc16` disagreed on a `memoryview` with a non-byte item format: the
  frame received the raw bytes of the view, while the checksum was computed from its
  items truncated to 8 bits, so `check_crc` rejected the result. Input is now
  normalized once with `memoryview(data).tobytes()` and both functions see the same
  bytes.
- The module docstring and `LICENSE.md` had the CRC polynomial the wrong way round and
  a single-year copyright: they now read `0x8005` (reflected `0xA001`), `2023–2026` and
  the same copyright holder as `pyproject.toml` (`webtoucher`).
- The release workflow extracted the CHANGELOG notes with `python`, which a job without
  `actions/setup-python` does not guarantee; it calls `python3` now.
- The speed claim held only for some interpreters. `benchmarks/benchmark_crc.py` now
  reproduces the comparison, and the README quotes its results per interpreter instead
  of a single number.

### Added

- `benchmarks/benchmark_crc.py`: throughput comparison with the 1.x implementation.
- Free-threaded `3.13t` in the CI matrix, so the compatibility statement is backed by a
  test run.
- `.gitattributes` with `* text=auto eol=lf`.

### Changed

- `BytesLike` is part of `__all__`, as the README always described it.
- `pyproject.toml`: the no-op `zip-safe` flag is gone and the `Programming Language`
  classifiers are back, so PyPI lists the supported versions.
- Test suite: exhaustive checks for every one-byte and two-byte input, all 255
  corruption masks at every byte position, no self-comparing assertions, and the
  exported names are resolved through the module instead of compared with a literal.

## [2.1] - 2026-11-15

### Added

- `Changelog` project URL, so the history is one click away from the PyPI page.
- This changelog.

### Changed

- GitHub Releases are generated from the matching section of this file instead of
  a bare commit list.

## [2.0] - 2026-11-15

### Added

- `modbus_crc.__version__` and an explicit `__all__`.
- `py.typed` marker (PEP 561), so type checkers see real signatures.
- GitHub Actions workflows: tests on Python 3.9-3.15 and a tag-driven release
  pipeline publishing to PyPI and creating a GitHub Release.

### Changed

- Packaging moved from `setup.py` and `setup.cfg` to `pyproject.toml`
  (PEP 621, PEP 639); metadata, build configuration and pytest settings live in one file.
- The CRC lookup table is generated at import time instead of two hand-written
  256-byte tables with inverted naming; the internals are now private.
- `add_crc` always returns `bytes`, also for `bytearray` and `memoryview` input;
  `crc16` and `check_crc` accept any bytes-like object.
- The checksum loop is over 20% faster per KB on CPython 3.11.
- Test suite rewritten: canonical Modbus vectors, an independent bit-wise
  implementation used as an oracle, edge cases and single-byte corruption detection.

### Removed

- `LOW_BYTES` and `HIGH_BYTES` module-level tables.
- Python 2 leftovers: the `coding=utf8` header and the empty `__main__` block.

### Breaking

- Python 3.9 or newer is required. `Requires-Python` is declared now, so older
  interpreters get a clear install error instead of failing at runtime.
- The `LOW_BYTES` and `HIGH_BYTES` module attributes are gone: `from modbus_crc import
  LOW_BYTES` raises `ImportError`.
- `add_crc(bytearray(...))` returns `bytes`, not `bytearray`: code that edits the
  result in place needs `bytearray(add_crc(...))`.

## [1.3] - 2023-01-20

- Packaging fixes only.

## [1.2] - 2023-01-20

- README and metadata updates.

## [1.1] - 2023-01-20

- First published release.
