"""Test fixtures."""

import json
from builtins import super

import pytest
from napalm.base.test import conftest as parent_conftest
from napalm.base.test.double import BaseTestDouble
from requests.models import HTTPError
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

    REQUESTS = {
        "control/outlets/XX99": {
            "headers": {"Content-Type": "text/html"},
            "status_code": 404,
        }
    }

    def request(self, method, **kwargs):
        address = kwargs["url"].split("/jaws/")[1]
        if self.REQUESTS.get(address):
            return FakeRequest(
                method,
                address,
                self.REQUESTS[address]["headers"],
                self.REQUESTS[address]["status_code"],
            )
        else:
            filename = f"{self.sanitize_text(address)}.json"
            path = self.find_file(filename)
            headers = {
                "Content-Type": "application/json" if method == "GET" else "text/html"
            }
            status_code = 200 if method == "GET" else 204
            return FakeRequest(method, path, headers, status_code)


class FakeRequest:
    """A fake API request."""

    def __init__(self, method, path, headers, status_code):
        self.method = method
        self.path = path
        self.headers = headers
        self.status_code = status_code
        self.text = ""

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HTTPError
        else:
            return True

    def json(self):
        with open(self.path, "r") as file:
            return json.load(file)
