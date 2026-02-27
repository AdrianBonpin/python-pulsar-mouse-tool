from dataclasses import dataclass
from typing import Dict, List, Optional

from .constants import (
    ADDR_ANGLE_SNAPPING,
    ADDR_ANGLE_SNAPPING_CHECKSUM,
    ADDR_AUTOSLEEP_TIME,
    ADDR_BUTTON_BACK_CHECKSUM,
    ADDR_BUTTON_BACK_INDEX2,
    ADDR_BUTTON_BACK_INDEX3,
    ADDR_BUTTON_BACK_MODE,
    ADDR_BUTTON_FORWARD_CHECKSUM,
    ADDR_BUTTON_FORWARD_INDEX2,
    ADDR_BUTTON_FORWARD_INDEX3,
    ADDR_BUTTON_FORWARD_MODE,
    ADDR_BUTTON_LEFT_CHECKSUM,
    ADDR_BUTTON_LEFT_INDEX2,
    ADDR_BUTTON_LEFT_INDEX3,
    ADDR_BUTTON_LEFT_MODE,
    ADDR_BUTTON_RIGHT_CHECKSUM,
    ADDR_BUTTON_RIGHT_INDEX2,
    ADDR_BUTTON_RIGHT_INDEX3,
    ADDR_BUTTON_RIGHT_MODE,
    ADDR_BUTTON_WHEEL_CHECKSUM,
    ADDR_BUTTON_WHEEL_INDEX2,
    ADDR_BUTTON_WHEEL_INDEX3,
    ADDR_BUTTON_WHEEL_MODE,
    ADDR_DEBOUNCE_TIME,
    ADDR_DEBOUNCE_TIME_CHECKSUM,
    ADDR_DPI_MODE,
    ADDR_DPI_MODE_CHECKSUM,
    ADDR_DPI_MODE_CT,
    ADDR_DPI_MODE_CT_CHECKSUM,
    ADDR_LED_BREATHE_SPEED,
    ADDR_LED_BREATHE_SPEED_CHECKSUM,
    ADDR_LED_BRIGHTNESS,
    ADDR_LED_BRIGHTNESS_CHECKSUM,
    ADDR_LED_EFFECT,
    ADDR_LED_EFFECT_CHECKSUM,
    ADDR_LED_ENABLED,
    ADDR_LED_ENABLED_CHECKSUM,
    ADDR_LOD_MM,
    ADDR_LOD_MM_CHECKSUM,
    ADDR_LOD_RIPPLE,
    ADDR_LOD_RIPPLE_CHECKSUM,
    ADDR_MODE0_DPI_CHECKSUM,
    ADDR_MODE0_DPI_INDEX1,
    ADDR_MODE0_DPI_INDEX2,
    ADDR_MODE0_DPI_INDEX3,
    ADDR_MODE0_LED_COLOR_B,
    ADDR_MODE0_LED_COLOR_CHECKSUM,
    ADDR_MODE0_LED_COLOR_G,
    ADDR_MODE0_LED_COLOR_R,
    ADDR_MODE1_DPI_CHECKSUM,
    ADDR_MODE1_DPI_INDEX1,
    ADDR_MODE1_DPI_INDEX2,
    ADDR_MODE1_DPI_INDEX3,
    ADDR_MODE1_LED_COLOR_B,
    ADDR_MODE1_LED_COLOR_CHECKSUM,
    ADDR_MODE1_LED_COLOR_G,
    ADDR_MODE1_LED_COLOR_R,
    ADDR_MODE2_DPI_CHECKSUM,
    ADDR_MODE2_DPI_INDEX1,
    ADDR_MODE2_DPI_INDEX2,
    ADDR_MODE2_DPI_INDEX3,
    ADDR_MODE2_LED_COLOR_B,
    ADDR_MODE2_LED_COLOR_CHECKSUM,
    ADDR_MODE2_LED_COLOR_G,
    ADDR_MODE2_LED_COLOR_R,
    ADDR_MODE3_DPI_CHECKSUM,
    ADDR_MODE3_DPI_INDEX1,
    ADDR_MODE3_DPI_INDEX2,
    ADDR_MODE3_DPI_INDEX3,
    ADDR_MODE3_LED_COLOR_B,
    ADDR_MODE3_LED_COLOR_CHECKSUM,
    ADDR_MODE3_LED_COLOR_G,
    ADDR_MODE3_LED_COLOR_R,
    ADDR_MOTION_SYNC,
    ADDR_MOTION_SYNC_CHECKSUM,
    ADDR_POLLING_RATE,
    ADDR_POLLING_RATE_CHECKSUM,
    DPI_MAX,
    DPI_MIN,
    LED_BRIGHTNESS_MAX,
    LED_BRIGHTNESS_MIN,
    LOD_MM_MAX,
    LOD_MM_MIN,
    PollingRateHz,
    LEDEffect,
)
from .payloads import (
    RequestActiveProfilePayload,
    SetActiveProfilePayload,
    build_payload,
    parse_power_details,
)
from .device import Device


def inverse(dict_obj):
    return {v: k for k, v in dict_obj.items()}


def dpi_int_to_raw(dpi):
    if not (DPI_MIN <= dpi <= DPI_MAX):
        raise ValueError
    quo, rem = divmod(dpi, 50)
    if rem:
        raise ValueError('DPI must be multiple of 50')
    factor12800, factor50 = divmod(quo-1, 256)

    index2 = factor50
    index3 = factor12800 << 2 | factor12800 << 6
    return bytearray([index2, index2, index3])


def dpi_raw_to_int(raw):
    raw = bytearray(raw)
    if len(raw) != 3:
        raise ValueError
    if raw[0] != raw[1]:
        raise ValueError
    factor50 = raw[1] + 1

    nib1 = raw[2] & 0b00001111
    nib2 = raw[2] >> 4
    if nib1 != nib2:
        raise ValueError
    if nib1 != (nib1 & 0b1100):
        raise ValueError
    factor12800 = nib1 >> 2
    return (factor50*50) + (factor12800*12800)


def color_to_int(value):
    value = value.removeprefix('#')
    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )


def int_to_color(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'


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


@dataclass
class ModeAddresses:
    dpi_index1: int
    dpi_index2: int
    dpi_index3: int
    dpi_checksum: int
    led_color_r: int
    led_color_g: int
    led_color_b: int
    led_color_checksum: int


ADDR_MODE = [
    ModeAddresses(
        ADDR_MODE0_DPI_INDEX1,
        ADDR_MODE0_DPI_INDEX2,
        ADDR_MODE0_DPI_INDEX3,
        ADDR_MODE0_DPI_CHECKSUM,
        ADDR_MODE0_LED_COLOR_R,
        ADDR_MODE0_LED_COLOR_G,
        ADDR_MODE0_LED_COLOR_B,
        ADDR_MODE0_LED_COLOR_CHECKSUM),
    ModeAddresses(
        ADDR_MODE1_DPI_INDEX1,
        ADDR_MODE1_DPI_INDEX2,
        ADDR_MODE1_DPI_INDEX3,
        ADDR_MODE1_DPI_CHECKSUM,
        ADDR_MODE1_LED_COLOR_R,
        ADDR_MODE1_LED_COLOR_G,
        ADDR_MODE1_LED_COLOR_B,
        ADDR_MODE1_LED_COLOR_CHECKSUM),
    ModeAddresses(
        ADDR_MODE2_DPI_INDEX1,
        ADDR_MODE2_DPI_INDEX2,
        ADDR_MODE2_DPI_INDEX3,
        ADDR_MODE2_DPI_CHECKSUM,
        ADDR_MODE2_LED_COLOR_R,
        ADDR_MODE2_LED_COLOR_G,
        ADDR_MODE2_LED_COLOR_B,
        ADDR_MODE2_LED_COLOR_CHECKSUM),
    ModeAddresses(
        ADDR_MODE3_DPI_INDEX1,
        ADDR_MODE3_DPI_INDEX2,
        ADDR_MODE3_DPI_INDEX3,
        ADDR_MODE3_DPI_CHECKSUM,
        ADDR_MODE3_LED_COLOR_R,
        ADDR_MODE3_LED_COLOR_G,
        ADDR_MODE3_LED_COLOR_B,
        ADDR_MODE3_LED_COLOR_CHECKSUM),
]


class PulsarX2V2Mini:
    LED_EFFECTS = {
        'off',
        'breathe',
        'steady',
    }

    def __init__(self, dev: Device):
        self.dev = dev
        self.settings: Dict[int, int] = {}
        self._profile: Optional[int] = None

    def get_power(self):
        self.dev.clear_read_buffer()
        payload = build_payload(0x04)
        self.dev.write(payload)
        while True:
            resp = self.dev.read()
            if resp[1] == 0x04:
                break
        return parse_power_details(resp)

    def read_settings(self):
        min_addr = 0x00
        max_addr = 0xb8
        current = min_addr
        settings = {}
        while current <= (max_addr + 10):
            length = 10
            payload = build_payload(
                0x08,
                index04=current,
                index05=length,
            )
            self.dev.write(payload)
            resp = self.dev.read()
            assert resp[4] == current
            assert resp[5] == length
            for (k, v) in enumerate(resp[6:6+length], current):
                settings[k] = v
            current += 10
        self.settings = settings

    def read_profile(self):
        self.dev.write(RequestActiveProfilePayload())
        resp = self.dev.read()
        # Parse the response bytes to get profile number
        # Response format: [header, command, ..., profile, ..., checksum]
        # Profile is at index 6
        if len(resp) > 6:
            self._profile = resp[6]
        else:
            raise ValueError(f"Invalid profile response: {resp}")

    @property
    def profile(self) -> int:
        if self._profile is None:
            self.read_profile()
        return self._profile

    @profile.setter
    def profile(self, value: int):
        from .payloads import checksum
        inst = SetActiveProfilePayload(value)
        self.dev.write(inst)
        resp = self.dev.read()
        assert resp.profile == inst.profile
        self._profile = inst.profile

    def restore(self):
        payload = build_payload(0x09)
        self.dev.write(payload)
        resp = self.dev.read()
        assert resp == payload
        self.settings.clear()

    @property
    def is_on(self) -> bool:
        payload = build_payload(0x03)
        self.dev.write(payload)
        while True:
            resp = self.dev.read()
            if resp[1] == 0x03:
                break
        return int_to_bool(resp[6])

    @property
    def polling_rate(self) -> int:
        return inverse(PollingRateHz)[self.settings[ADDR_POLLING_RATE]]

    @polling_rate.setter
    def polling_rate(self, rate: int):
        from .payloads import checksum
        val = PollingRateHz[rate]
        self._mem_set({
            ADDR_POLLING_RATE: int(val),
            ADDR_POLLING_RATE_CHECKSUM: checksum(val),
        })

    def _mem_set(self, addresses: Dict[int, int]):
        from .payloads import checksum
        length = len(addresses)
        if not (1 <= length <= 10):
            raise ValueError('must not be longer than 10')
        start_address = min(addresses)
        indexes = [
            'index06',
            'index07',
            'index08',
            'index09',
            'index10',
            'index11',
            'index12',
            'index13',
            'index14',
            'index15',
        ]
        kwargs = {
            'index04': start_address,
            'index05': length,
        }
        for index, address in zip(indexes, range(start_address, start_address+length)):
            kwargs[index] = addresses[address]

        payload = build_payload(0x07, **kwargs)
        # Note: is_on check removed - mouse can still accept commands even if is_on reports False
        self.dev.write(payload)
        resp = self.dev.read()
        self.settings.update(addresses)

    @property
    def dpi_mode(self) -> int:
        return self.settings[ADDR_DPI_MODE]

    @dpi_mode.setter
    def dpi_mode(self, value: int):
        from .payloads import checksum
        if not isinstance(value, int):
            raise TypeError
        if not (0 <= value <= 3):
            raise ValueError
        self._mem_set({
            ADDR_DPI_MODE: value,
            ADDR_DPI_MODE_CHECKSUM: checksum(value),
        })

    @property
    def lod_mm(self) -> int:
        return self.settings[ADDR_LOD_MM]

    @lod_mm.setter
    def lod_mm(self, value: int):
        from .payloads import checksum
        if not isinstance(value, int):
            raise TypeError
        if not (LOD_MM_MIN <= value <= LOD_MM_MAX):
            raise ValueError
        self._mem_set({
            ADDR_LOD_MM: value,
            ADDR_LOD_MM_CHECKSUM: checksum(value),
        })

    @property
    def debounce_time(self) -> int:
        return self.settings[ADDR_DEBOUNCE_TIME]

    @property
    def motion_sync(self) -> bool:
        return bool(self.settings[ADDR_MOTION_SYNC])

    @motion_sync.setter
    def motion_sync(self, enabled: bool):
        from .payloads import checksum
        value = 1 if enabled else 0
        self._mem_set({
            ADDR_MOTION_SYNC: value,
            ADDR_MOTION_SYNC_CHECKSUM: checksum(value)
        })

    @property
    def lod_ripple(self) -> bool:
        return bool(self.settings[ADDR_LOD_RIPPLE])

    @lod_ripple.setter
    def lod_ripple(self, enabled: bool):
        from .payloads import checksum
        value = 1 if enabled else 0
        self._mem_set({
            ADDR_LOD_RIPPLE: value,
            ADDR_LOD_RIPPLE_CHECKSUM: checksum(value)
        })

    @property
    def angle_snapping(self) -> bool:
        return bool(self.settings[ADDR_ANGLE_SNAPPING])

    @angle_snapping.setter
    def angle_snapping(self, enabled: bool):
        from .payloads import checksum
        value = 1 if enabled else 0
        self._mem_set({
            ADDR_ANGLE_SNAPPING: value,
            ADDR_ANGLE_SNAPPING_CHECKSUM: checksum(value)
        })

    @property
    def led_effect(self) -> LEDEffect:
        return LEDEffect(self.settings[ADDR_LED_EFFECT])

    @led_effect.setter
    def led_effect(self, value):
        from .payloads import checksum
        raw = LEDEffect(value)
        self._mem_set({
            ADDR_LED_EFFECT: raw,
            ADDR_LED_EFFECT_CHECKSUM: checksum(raw),
        })

    @property
    def led_brightness(self) -> int:
        return self.settings[ADDR_LED_BRIGHTNESS]

    @led_brightness.setter
    def led_brightness(self, value: int):
        from .payloads import checksum
        if not isinstance(value, int):
            raise TypeError
        if not (LED_BRIGHTNESS_MIN <= value <= LED_BRIGHTNESS_MAX):
            raise ValueError
        self._mem_set({
            ADDR_LED_BRIGHTNESS: value,
            ADDR_LED_BRIGHTNESS_CHECKSUM: checksum(value),
        })

    @property
    def led_breathe_speed(self) -> int:
        return self.settings[ADDR_LED_BREATHE_SPEED]

    @property
    def autosleep_time(self) -> int:
        return self.settings[ADDR_AUTOSLEEP_TIME] * 10

    @property
    def led_enabled(self) -> bool:
        return bool(self.settings[ADDR_LED_ENABLED])

    @led_enabled.setter
    def led_enabled(self, enabled: bool):
        from .payloads import checksum
        value = 1 if enabled else 0
        self._mem_set({
            ADDR_LED_ENABLED: value,
            ADDR_LED_ENABLED_CHECKSUM: checksum(value)
        })

    def get_dpi(self, mode: int) -> int:
        addrs = ADDR_MODE[mode]
        return dpi_raw_to_int(
            bytearray([
                self.settings[addrs.dpi_index1],
                self.settings[addrs.dpi_index2],
                self.settings[addrs.dpi_index3],
            ])
        )

    def set_dpi(self, mode: int, dpi: int):
        from .payloads import checksum
        raw = dpi_int_to_raw(dpi)
        addrs = ADDR_MODE[mode]
        self._mem_set({
            addrs.dpi_index1: raw[0],
            addrs.dpi_index2: raw[1],
            addrs.dpi_index3: raw[2],
            addrs.dpi_checksum: checksum(*raw),
        })

    @property
    def dpi(self) -> int:
        return self.get_dpi(self.dpi_mode)

    @dpi.setter
    def dpi(self, value: int):
        return self.set_dpi(self.dpi_mode, value)

    @property
    def dpi_mode_count(self) -> int:
        return self.settings[ADDR_DPI_MODE_CT]

    def get_led_color(self, mode: int) -> str:
        addrs = ADDR_MODE[mode]
        return int_to_color(
            addrs.led_color_r,
            addrs.led_color_g,
            addrs.led_color_b,
        )

    @property
    def led_color(self) -> str:
        return self.get_led_color(self.dpi_mode)

    def set_led_color(self, mode: int, color: str):
        from .payloads import checksum
        addrs = ADDR_MODE[mode]
        r, g, b = color_to_int(color)
        self._mem_set({
            addrs.led_color_r: r,
            addrs.led_color_g: g,
            addrs.led_color_b: b,
            addrs.led_color_checksum: checksum(r+g+b),
        })

    @led_color.setter
    def led_color(self, color: str):
        self.set_led_color(self.dpi_mode, color)

    def get_all_settings(self) -> dict:
        power = self.get_power()
        
        modes = []
        for i in range(self.dpi_mode_count):
            modes.append({
                'dpi_mode': i,
                'led_color': self.get_led_color(i),
                'dpi': self.get_dpi(i),
            })

        settings = {
            'dpi_modes': modes,
            'active_profile': self.profile,
            'active_dpi_mode': self.dpi_mode,
            'angle_snapping_enabled': self.angle_snapping,
            'autosleep_seconds': self.autosleep_time,
            'debounce_milliseconds': self.debounce_time,
            'lod': {
                'mm': self.lod_mm,
                'ripple_enabled': self.lod_ripple,
            },
            'motion_sync_enabled': self.motion_sync,
            'polling_rate_hz': self.polling_rate,
        }
        
        led = {
            'enabled': self.led_enabled,
        }
        if self.led_enabled:
            led['effect'] = self.led_effect.name.lower() if self.led_effect else None
            settings['led_color'] = self.led_color
            if self.led_effect == LEDEffect.BREATHE:
                led['breathe_speed'] = self.led_breathe_speed
            elif self.led_effect == LEDEffect.STEADY:
                led['brightness'] = self.led_brightness
        else:
            led['effect'] = None
        led['effect'] = led.get('effect')
        settings['led'] = led
        
        return {
            'power': {
                'connected': power.power_connected,
                'battery_percent': power.battery_percentage,
                'battery_millivolts': power.battery_millivoltage,
            },
            **settings
        }
