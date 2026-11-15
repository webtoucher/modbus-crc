# Modbus CRC-16

![License](https://img.shields.io/badge/License-BSD%203--Clause-green)
[![Downloads](https://img.shields.io/pypi/dm/modbus-crc.svg?color=orange)](https://pypi.python.org/pypi/modbus-crc)
[![Latest Version](https://img.shields.io/pypi/v/modbus-crc.svg)](https://pypi.python.org/pypi/modbus-crc)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/modbus-crc.svg)](https://pypi.python.org/pypi/modbus-crc)
[![tests](https://github.com/webtoucher/modbus-crc/actions/workflows/tests.yml/badge.svg)](https://github.com/webtoucher/modbus-crc/actions/workflows/tests.yml)

CRC-16 calculation library for Modbus protocol. Tiny, dependency-free and fast: a single
256-entry lookup table, no runtime dependencies, type hints included.

## Algorithm

The checksum is **CRC-16/MODBUS**:

| Parameter             | Value                                     |
|-----------------------|-------------------------------------------|
| Width                 | 16 bits                                   |
| Polynomial            | `0x8005` (reflected: `0xA001`)            |
| Initial value         | `0xFFFF`                                  |
| Reflect in / out      | yes / yes                                 |
| Final XOR             | `0x0000`                                  |
| Check (`"123456789"`)  | `0x4B37`, transmitted as `b'\x37\x4B'`   |
| Byte order on wire    | low byte first                            |

## Installation

Install it with pip:

```shell
$ pip install modbus-crc
```

Or you can add it as dependency in requirements.txt file of your python application:

```
modbus-crc~=2.0
```

## Usage

For signing byte package use `add_crc`:

```python
from modbus_crc import add_crc

signed_package = add_crc(b'\x00\x12\x34\xAB\xCD\xEF')
```

Result is `b'\x00\x12\x34\xAB\xCD\xEF\xD2\xD4'`. For validation signed package use `check_crc`:

```python
from modbus_crc import check_crc

if not check_crc(b'\x00\x12\x34\xAB\xCD\xEF\xD2\xD4'):
    raise SomeException()
```

To get the checksum alone (low byte first, exactly as it is transmitted on the wire), use `crc16`:

```python
from modbus_crc import crc16

crc16(b'\x01\x03\x00\x00\x00\x0A')  # b'\xC5\xCD'
```

Here is a real Modbus RTU request — "read 10 holding registers from slave 1":

```python
add_crc(b'\x01\x03\x00\x00\x00\x0A')  # b'\x01\x03\x00\x00\x00\x0A\xC5\xCD'
```

`check_crc` validates the whole signed frame, so it works with data read straight from
the serial port, without splitting off the trailing bytes:

```python
check_crc(b'\x01\x03\x00\x00\x00\x0A\xC5\xCD')  # True
check_crc(b'\x01\x03\x00\x00\x00\x0A\xC5\xCE')  # False
```

## API

All three functions accept `bytes`, `bytearray` and `memoryview` (declared as `BytesLike`).

| Function                        | Returns | Description                                                     |
|---------------------------------|---------|-----------------------------------------------------------------|
| `crc16(data)`                   | `bytes` | 2-byte checksum of `data`, low byte first                       |
| `add_crc(package)`              | `bytes` | `package` with the checksum appended; input type is normalized  |
| `check_crc(package)`            | `bool`  | `True` if `package` carries a valid trailing checksum           |

Notes:

- `add_crc` always returns `bytes`, even for `bytearray` and `memoryview` input.
- `check_crc(b'')` is `False`: an empty package has no valid checksum.
- Functions are pure: they keep no state between calls. The lookup table is built once,
  at import time.

## Compatibility

- Python **3.9 and newer**, including free-threaded builds. Tested on 3.9 and 3.15 and
  in CI on every version from 3.9 to 3.15.
- No runtime dependencies.
- Type hints are shipped with the package (`py.typed`, PEP 561), so mypy and pyright
  see real signatures instead of `Any`.

## Development

```shell
$ python -m venv .venv
$ .venv\Scripts\activate          # Windows; on POSIX: source .venv/bin/activate
$ pip install -e ".[dev]"          # installs the package and pytest
$ python -m pytest
```

The test suite covers:

- canonical Modbus frames with published checksums,
- an independent bit-by-bit implementation written from the specification, used as an
  oracle against the fast table-driven code (including random payloads up to 1 KiB),
- edge cases: empty package, one-byte packages, `bytearray` / `memoryview` input,
- detection of every single-byte corruption of a signed frame.

Project layout:

```
modbus_crc/__init__.py    the whole library
tests/test_modbus_crc.py  test suite
pyproject.toml            metadata, build config and pytest settings
.github/workflows/        CI: tests on Python 3.9-3.15, sdist/wheel build check
```

To build and verify a release:

```shell
$ pip install build twine
$ python -m build
$ python -m twine check dist/*
```

## Migrating from 1.x

The public API is unchanged, so most projects need no code changes. What did change:

- **Python 3.9+ is required.** Python 2 support and the legacy `setup.py` / `setup.cfg`
  are gone; metadata now lives in `pyproject.toml` (PEP 621).
- **`LOW_BYTES` and `HIGH_BYTES` were removed.** Those were two 256-byte tables with
  inverted naming that leaked from the implementation. The lookup table is now generated
  at import time and is private — use the documented functions instead.
- **`add_crc` always returns `bytes`.** Previously `add_crc(bytearray(...))` returned a
  `bytearray`; the result type is now stable regardless of the input type.
- **`modbus_crc.__version__` is available** and is the single source of truth for the
  package version.
- **The package ships `py.typed`**, so type checkers no longer treat it as untyped.
- **Faster and clearer internals:** one table instead of two, a single 16-bit register
  instead of two byte variables, no `int()` call per byte (over 20% faster per KB on
  CPython 3.11).

## License

Distributed under the BSD 3-Clause license. See [LICENSE.md](LICENSE.md) for details.
