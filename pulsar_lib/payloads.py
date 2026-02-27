import ctypes
from dataclasses import dataclass
from typing import ClassVar

from .constants import (
    PAYLOAD_HEADER,
    Command,
    DeviceEvent,
)


def checksum(*values):
    return ctypes.c_uint8(0x55 - sum(values)).value


def build_payload(command, *,
                  index02=0x00,
                  index03=0x00,
                  index04=0x00,
                  index05=0x00,
                  index06=0x00,
                  index07=0x00,
                  index08=0x00,
                  index09=0x00,
                  index10=0x00,
                  index11=0x00,
                  index12=0x00,
                  index13=0x00,
                  index14=0x00,
                  index15=0x00):
    payload = [
        PAYLOAD_HEADER,
        command,
        index02,
        index03,
        index04,
        index05,
        index06,
        index07,
        index08,
        index09,
        index10,
        index11,
        index12,
        index13,
        index14,
        index15,
    ]
    return bytearray([*payload, checksum(*payload)])


class Payload:
    payload: ClassVar[bytearray]
    
    def __bytes__(self):
        return bytes(self.payload)

    def __eq__(self, other):
        return self.payload == other.payload


class RestorePayload(Payload):
    @property
    def payload(self):
        return build_payload(Command.RESTORE)

    @classmethod
    def from_payload(cls, payload):
        inst = cls()
        assert payload == inst.payload
        return cls()


class RequestActiveProfilePayload(Payload):
    @property
    def payload(self):
        return build_payload(Command.ACTIVE_PROFILE_GET)

    @classmethod
    def from_payload(cls, payload):
        inst = cls()
        assert payload == inst.payload
        return inst


class SetActiveProfilePayload(Payload):
    def __init__(self, profile):
        self.payload = build_payload(
            Command.ACTIVE_PROFILE_SET,
            index05=0x01,
            index06=profile,
        )

    @property
    def profile(self):
        return self.payload[6]

    @classmethod
    def from_payload(cls, payload):
        profile = payload[6]
        inst = cls(profile)
        assert inst.payload == payload
        return inst


class CurrentActiveProfilePayload(Payload):
    def __init__(self, profile):
        self.payload = build_payload(
            Command.ACTIVE_PROFILE_GET,
            index05=0x01,
            index06=profile,
        )

    @property
    def profile(self):
        return self.payload[6]

    @classmethod
    def from_payload(cls, payload):
        profile = payload[6]
        inst = cls(profile)
        assert inst.payload == payload
        return inst


class DeviceEventPayload(Payload):
    EVENT_FUNCTION: ClassVar[int]
    
    @property
    def payload(self):
        return build_payload(
            Command.DEVICE_EVENT,
            index05=0x0a,
            index06=self.EVENT_FUNCTION,
        )

    @classmethod
    def from_payload(cls, payload):
        inst = cls()
        assert payload == inst.payload
        return inst


class Unknown1DeviceEventPayload(DeviceEventPayload):
    EVENT_FUNCTION = DeviceEvent.UNKNOWN_1


class DPIModeDeviceEventPayload(DeviceEventPayload):
    EVENT_FUNCTION = DeviceEvent.DPI_MODE


class PowerDeviceEventPayload(DeviceEventPayload):
    EVENT_FUNCTION = DeviceEvent.POWER


DEVICE_EVENT_CLASSES = [
    Unknown1DeviceEventPayload,
    DPIModeDeviceEventPayload,
    PowerDeviceEventPayload,
]
DEVICE_EVENT_TYPES = {}
for c in DEVICE_EVENT_CLASSES:
    func = c.EVENT_FUNCTION
    assert func not in DEVICE_EVENT_TYPES
    DEVICE_EVENT_TYPES[func] = c


class RequestPowerDetailsPayload(Payload):
    @property
    def payload(self):
        return build_payload(Command.POWER)

    @classmethod
    def from_payload(cls, payload):
        inst = cls()
        assert payload == inst.payload
        return inst


def from_payload(payload):
    assert len(payload) == 17
    assert payload[16] == checksum(*payload[0:16])
    command = payload[1]
    if command == Command.POWER:
        if payload == RequestPowerDetailsPayload().payload:
            return RequestPowerDetailsPayload()
        else:
            raise NotImplementedError
    elif command == Command.RESTORE:
        return RestorePayload()
    elif command == Command.STATUS:
        raise NotImplementedError
    elif command == Command.DEVICE_EVENT:
        settings_type = payload[6]
        return DEVICE_EVENT_TYPES[settings_type].from_payload(payload)
    elif command == Command.MEM_SET:
        raise NotImplementedError
    elif command == Command.MEM_GET:
        raise NotImplementedError
    elif command == Command.ACTIVE_PROFILE_SET:
        return SetActiveProfilePayload.from_payload(payload)
    elif command == Command.ACTIVE_PROFILE_GET:
        if payload == RequestActiveProfilePayload().payload:
            return RequestActiveProfilePayload()
        else:
            return CurrentActiveProfilePayload.from_payload(payload)
    else:
        raise NotImplementedError


@dataclass
class PowerDetails:
    battery_percentage: int
    battery_millivoltage: int
    power_connected: bool


def parse_power_details(data):
    return PowerDetails(
        battery_percentage=data[6],
        battery_millivoltage=int.from_bytes(data[8:10], byteorder='big'),
        power_connected=bool(data[7]),
    )


def bool_to_int(value):
    if value == 0:
        return False
    elif value == 1:
        return True
    else:
        raise ValueError


def int_to_bool(value):
    if value == 0:
        return False
    elif value == 1:
        return True
    else:
        raise ValueError
