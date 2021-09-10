"""Tests for getters."""

import pytest
from requests import HTTPError


@pytest.mark.usefixtures("set_device_parameters")
class TestAdd(object):
    """Test additional methods."""

    def test_set_outlet(self):
        res = self.device.set_outlet("AA01", "on")
        assert res["status"] == "success"

        with pytest.raises(ValueError):
            self.device.set_outlet("AA01", "no")

        with pytest.raises(HTTPError):
            self.device.set_outlet("XX99", "on")

    def test_reboot(self):
        res = self.device.restart("normal")
        assert res["status"] == "success"

        with pytest.raises(ValueError):
            self.device.restart("reboot")
