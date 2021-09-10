import re


def convert_uptime(uptime):
    """Converts a ServerTech uptime string to a number of seconds."""
    time_regex = (
        r"^(?P<days>\d+) days? (?P<hours>\d+) hours?"
        r" (?P<minutes>\d+) minutes? (?P<seconds>\d+) seconds?$"
    )
    m = re.match(
        time_regex,
        uptime,
    )
    if not m:
        raise ValueError("uptime string was not recognized: regex did not match")
    return (
        int(m.group("days")) * 86400
        + int(m.group("hours")) * 3600
        + int(m.group("minutes")) * 60
        + int(m.group("seconds"))
    )


def parse_hardware(hardware_string):
    """Extract fields from the hardware string."""
    m = re.match(
        r"(?P<cpu_type>[^,;]+), (?P<cpu_freq>\d+) MHz, (?P<ram>\d+)MB RAM, (?P<flash>\d+)MB FLASH",
        hardware_string,
    )
    if not m:
        raise ValueError("hardware string was not recognized: regex did not match")
    return {
        "cpu_type": m.group("cpu_type"),
        "cpu_freq": int(m.group("cpu_freq")),
        "ram": int(m.group("ram")),
        "flash": int(m.group("flash")),
    }


def validate_actions(action, supported_actions):
    """Ensures the inputed action is supported, raises an exception otherwise."""
    if action not in supported_actions:
        raise ValueError(
            f'Action "{action}" is not supported.'
            " the list of valid actions is: {}".format(", ".join(supported_actions))
        )
    return True
