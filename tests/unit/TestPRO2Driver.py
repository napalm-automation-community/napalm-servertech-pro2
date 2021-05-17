"""Test driver."""

import unittest

from napalm_servertech_pro2 import pro2
from napalm.base.test.base import TestConfigNetworkDriver


class TestConfigPRO2Driver(unittest.TestCase, TestConfigNetworkDriver):
    @classmethod
    def setUpClass(cls):
        """Executed when the class is instantiated."""
        cls.vendor = "servertech"
        cls.device = pro2.PRO2Driver(
            "127.0.0.1",
            "admin",
            "admin",
            timeout=60,
            optional_args={},
        )
        cls.device.open()
