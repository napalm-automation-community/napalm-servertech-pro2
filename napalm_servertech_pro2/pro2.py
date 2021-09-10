"""NAPALM driver for ServerTech PRO2 PDUs"""
import json

import requests
from napalm.base import NetworkDriver
from napalm.base.exceptions import ConnectionException
from netaddr import IPNetwork
from requests.auth import HTTPBasicAuth

from napalm_servertech_pro2.constants import (
    CONFIG_ITEMS,
    LOCAL_USER_LEVELS,
    SUPPORTED_OUTLET_ACTIONS,
    SUPPORTED_RESTART_ACTIONS,
)
from napalm_servertech_pro2.utils import (
    convert_uptime,
    parse_hardware,
    validate_actions,
)


class PRO2Driver(NetworkDriver):
    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout
        self.optional_args = optional_args if optional_args else dict()
        self.verify = bool(self.optional_args.get("verify", True))
        self.api = None

        self.platform = "pro2"

    def _req(self, path, method="GET", json=None, raise_err=True):
        url = f"https://{self.hostname}/jaws{path}"
        try:
            req = self.api.request(method, url=url, json=json, verify=self.verify)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if raise_err:
                raise err
            else:
                return {"err": str(err)}
        if "application/json" in req.headers.get("Content-Type"):
            return req.json()
        else:
            return {
                "status": "success",
                "status_code": req.status_code,
                "content": req.text,
            }

    def open(self):
        """Open a connection to the device."""
        self.api = requests.Session()
        self.api.auth = HTTPBasicAuth(self.username, self.password)
        self.api.verify = self.verify

        try:
            req = self.api.request(
                "GET",
                url=f"https://{self.hostname}/jaws/monitor/system",
                verify=self.verify,
            )
            req.raise_for_status()
        except requests.exceptions.ConnectionError:
            self.api = None
            raise ConnectionException

    def close(self):
        self.api.close()

    def is_alive(self):
        return {"is_alive": True if self.api else False}

    def get_config(self, retrieve="all", full=False, sanitized=False):
        if sanitized:
            # There is no way to ask the API not to reveal secrets
            raise NotImplementedError("driver cannot retrieve sanitized configurations")
        config = {}
        for item in CONFIG_ITEMS:
            res = self._req(f"/config/{item}", raise_err=False)
            if "err" not in res:
                config[item] = res
        config_types = {
            "running": json.dumps(config),
            "candidate": "",
            "startup": json.dumps(config),
        }
        if retrieve != "all" and retrieve in config_types:
            return {k: (config_types[k] if k == retrieve else "") for k in config_types}
        else:
            return config_types

    def get_environment(self):
        ret = {k: {} for k in ("fans", "temperature", "power", "cpu", "memory")}

        fans = self._req("/monitor/sensors/fan", raise_err=False)
        if "err" not in fans:
            for fan in fans:
                ret["fans"][fan["name"]] = {
                    "status": True if fans["status"] == "Normal" else False
                }

        temps = self._req("/monitor/sensors/temp", raise_err=False)
        if "err" not in temps:
            for temp in temps:
                if temp["status"] == "Not Found":
                    continue
                config = self._req(f"/config/sensors/temp/{temp['id']}")
                t = temp["temperature_celsius"]
                # thresholds are gathered from configuration
                alert = config["thresholds_celsius"][2]
                critical = config["thresholds_celsius"][3]
                ret["temperature"][temp["name"]] = {
                    "temperature": t,
                    "is_alert": True if t > alert else False,
                    "is_critical": True if t > critical else False,
                }

        cords = self._req("/monitor/cords", raise_err=False)
        for cord in cords:
            utilized = (cord["power_capacity"] / 100) * cord["power_utilized"]
            ret["power"][cord["name"]] = {
                "status": True if cord["status"] == "Normal" else False,
                "capacity": float(cord["power_capacity"]),
                "output": float(utilized),
            }

        system = self._req("/config/info/system", raise_err=False)
        ram = parse_hardware(system["hardware"])["ram"]

        # used RAM can't be retrieved: rather than putting 0 or -1 (inaccurate values),
        # we just assume that it is used at 100%
        ret["memory"] = {
            "available_ram": ram,
            "used_ram": ram,
        }

        return ret

    def get_facts(self):
        info_system = self._req("/config/info/system")
        system = self._req("/config/system")
        network = self._req("/config/network")
        units = self._req("/config/info/units")[0]
        outlets = self._req("/monitor/outlets")

        uptime = convert_uptime(info_system["uptime"])

        return {
            "uptime": uptime,
            "vendor": "ServerTech",  # TODO: try to find a way to get the actual vendor
            "model": units["model_number"],
            "hostname": system["location"],
            "fqdn": network["dhcp_fqdn_name"],
            "os_version": info_system["firmware"],
            "serial_number": units["product_serial_number"],
            "interface_list": [outlet["id"] for outlet in outlets],
        }

    def get_interfaces(self):
        ports = self._req("/monitor/outlets")
        net = self._req("/config/info/network")

        ports.append(
            {
                "id": "NET",
                "name": "management",
                "speed": int(net["speed"].split(" ")[0]),
                "status": "Normal" if net["link"] == "Up" else False,
                "state": "On",
                "mac_address": net["ethernet_mac_address"].replace("-", ":"),
                "mtu": 1500,
            }
        )

        return {
            port["id"]: {
                "is_up": True if port["status"] == "Normal" else False,
                "is_enabled": True if port["state"] == "On" else False,
                "description": port["name"],
                "last_flapped": -1.0,
                "speed": port.get("speed", 0),
                "mtu": port.get("mtu", 0),
                "mac_address": port.get("mac_address", ""),
            }
            for port in ports
        }

    def get_interfaces_ip(self):
        net = self._req("/config/info/network")

        ips = {
            4: IPNetwork(f"{net['ipv4_address']}/{net['ipv4_subnet_mask']}"),
            6: IPNetwork(net["ipv6_auto_config_address"]),
        }

        return {
            "net": {
                f"ipv{v}": {str(addr.ip): {"prefix_length": addr.prefixlen}}
                for v, addr in ips.items()
            }
        }

    def get_users(self):
        users = self._req("/config/users/local")

        return {
            user["username"]: {
                "level": LOCAL_USER_LEVELS.get(user["access_level"], 0),
                "password": user["password_secure"],
                "sshkeys": [],
            }
            for user in users
        }

    def set_outlet(self, outlet_id, action):
        """
        Change the status of an outlet

        :param outlet_id: a string
        :param action: a string (values can be: on, off, reboot)
        :return: a dict
        """
        validate_actions(action, SUPPORTED_OUTLET_ACTIONS)

        outlet = self._req(
            f"/control/outlets/{outlet_id}", "PATCH", json={"control_action": action}
        )

        return outlet

    def restart(self, action):
        """
        Restarts the PDU

        :param action: a string (see SUPPORTED_RESTART_ACTIONS for valid values)
        :return: a dict
        """
        validate_actions(action, SUPPORTED_RESTART_ACTIONS)

        restart = self._req("/restart", "PATCH", json={"action": action})

        return restart
