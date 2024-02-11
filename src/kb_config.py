from dataclasses import dataclass


@dataclass
class KB:
    vendor: float
    pid: float
    key_set: set[str]
    added = False
    name: str


keyboards: list[KB] = [
    KB(vendor=0x514c, pid=0x8842, key_set=set(), name="bluetoothboard"),
    KB(vendor=0x1189, pid=0x8890, key_set=set(), name="firstboard"),

    # bluetooth max : F8:3B:26:D3:A3:24
    KB(vendor=0x07d7, pid=0x0000, key_set=set(), name="footboard-ble")
]
