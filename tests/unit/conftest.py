"""Test fixtures."""

import json
from builtins import super

import pytest
from napalm.base.test import conftest as parent_conftest
from napalm.base.test.double import BaseTestDouble
from napalm_servertech_pro2 import pro2


@pytest.fixture(scope="class")
def set_device_parameters(request):
    """Set up the class."""

    def fin():
        request.cls.device.close()

    request.addfinalizer(fin)

    request.cls.driver = pro2.PRO2Driver
    request.cls.patched_driver = PatchedPRO2Driver
    request.cls.vendor = "servertech"
    parent_conftest.set_device_parameters(request)


def pytest_generate_tests(metafunc):
    """Generate test cases dynamically."""
    parent_conftest.pytest_generate_tests(metafunc, __file__)


class PatchedPRO2Driver(pro2.PRO2Driver):
    """Patched ServerTech PRO2 Driver."""

    def __init__(self, hostname, username, password, timeout=60, optional_args={}):
        """Patched PRO2Driver constructor."""
        super().__init__(hostname, username, password, timeout, optional_args)
        self.patched_attrs = ["api"]

    def close(self):
        pass

    def is_alive(self):
        return {"is_alive": True}

    def open(self):
        self.api = FakePRO2Api()


class FakePRO2Api(BaseTestDouble):
    """ServerTech fake API."""

    def request(self, method, **kwargs):
        filename = f'{self.sanitize_text(kwargs["url"].split("/jaws/")[1])}.json'
        path = self.find_file(filename)
        return FakeRequest(method, path)


class FakeRequest:
    """A fake API request."""

    def __init__(self, method, path):
        self.method = method
        self.path = path

    def raise_for_status(self):
        return True

    def json(self):
        with open(self.path, "r") as file:
            return json.load(file)
