"""Test utils."""

import pytest
from napalm_servertech_pro2 import utils


def test_convert_uptime():
    uptime = "11 days 4 hours 8 minutes 6 seconds"
    assert utils.convert_uptime(uptime) == 965286.0

    uptime = "133 days 1 hour 12 minutes 15 seconds"
    assert isinstance(utils.convert_uptime(uptime), float)

    uptime = "0 days 0 hours 0 minutes 1 second"
    assert utils.convert_uptime(uptime) == 1.0

    with pytest.raises(ValueError):
        utils.convert_uptime("hello")


def test_parse_hardware():
    hardware = "AAAAA (000), 123 MHz, 2048MB RAM, 2048MB FLASH"
    assert utils.parse_hardware(hardware) == {
        "cpu_type": "AAAAA (000)",
        "cpu_freq": 123,
        "ram": 2048,
        "flash": 2048,
    }


def test_validate_actions():
    supported_actions = ["foo", "bar"]
    assert utils.validate_actions("foo", supported_actions) is True

    with pytest.raises(ValueError):
        utils.validate_actions("oof", supported_actions)


def test_server_version():
    headers = {"Server": "ServerTech-AWS/v8.0k"}
    assert utils.server_version(headers) == "8.0k"

    headers = {"Server": "lol"}
    assert utils.server_version(headers) is None

    assert "8.0v" > "8.0m"

    assert "8.0k" < "8.0m"
