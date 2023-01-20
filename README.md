# Modbus CRC-16

![License](https://img.shields.io/badge/License-BSD%203--Clause-green)
[![Downloads](https://img.shields.io/pypi/dm/modbus-crc.svg?color=orange)](https://pypi.python.org/pypi/modbus-crc)
[![Latest Version](https://img.shields.io/pypi/v/modbus-crc.svg)](https://pypi.python.org/pypi/modbus-crc)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/modbus-crc.svg)](https://pypi.python.org/pypi/modbus-crc)

CRC-16 calculation library for Modbus protocol

## Installation

Install it with pip:

```shell
$ pip install modbus-crc
```

Or you can add it as dependency in requirements.txt file of your python application:

```
modbus-crc~=1.3
```

## Usage

For signing byte package use `add_crc`:

```python
from modbus_crc import add_crc

signed_package = add_crc(b'\x00\x12\x34\xAB\xCD\xEF')
```

Result is `b'\x00\x12\x34\xAB\xCD\xEF\xD2\xD4`. For validation signed package use `check_crc`:

```python
from modbus_crc import check_crc

if not check_crc(b'\x00\x12\x34\xAB\xCD\xEF\xD2\xD4'):
    raise SomeException()
```

## Testing

```shell
$ python -m unittest discover -v -p "tests.py"
```
