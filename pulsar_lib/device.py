import usb
import usb.core
import usb.util

from .constants import (
    VENDOR_ID,
    WIRELESS_1KHZ_DEVICE_ID,
    WIRED_DEVICE_ID,
    INTERFACES,
)


class Device:
    VENDOR_ID = 0x3554
    WIRELESS_1KHZ_DEVICE_ID = 0xf508
    WIRED_DEVICE_ID = 0xf507

    INTERFACES = {
        0: {'endpoint': 0x81, 'length': 8},
        1: {'endpoint': 0x82, 'length': 17},
        2: {'endpoint': 0x83, 'length': 7},
    }

    def __init__(self):
        self.interface = 1
        info = self.INTERFACES[self.interface]
        self.length = info['length']
        self.endpoint = info['endpoint']
        self.device = None
        self._connect()

    def _connect(self):
        for device_id in (self.WIRED_DEVICE_ID, self.WIRELESS_1KHZ_DEVICE_ID):
            self.device = usb.core.find(idVendor=self.VENDOR_ID, idProduct=device_id)
            if self.device is not None:
                break
        
        if self.device is None:
            raise RuntimeError("No Pulsar mouse found")
        
        # Set configuration first
        try:
            self.device.set_configuration()
        except Exception as e:
            print(f"Note: Could not set configuration: {e}")
        
        # Detach kernel driver if needed
        try:
            if self.device.is_kernel_driver_active(self.interface):
                self.device.detach_kernel_driver(self.interface)
        except Exception as e:
            print(f"Note: Could not detach kernel driver: {e}")
        
        # Claim interface
        try:
            usb.util.claim_interface(self.device, self.interface)
        except Exception as e:
            print(f"Note: Could not claim interface: {e}")

    def is_connected(self):
        try:
            for device_id in (self.WIRED_DEVICE_ID, self.WIRELESS_1KHZ_DEVICE_ID):
                dev = usb.core.find(idVendor=self.VENDOR_ID, idProduct=device_id)
                if dev is not None:
                    return True
            return False
        except Exception:
            return False

    def write(self, payload):
        if not isinstance(payload, bytes):
            payload = bytes(payload)
        res = self.device.ctrl_transfer(
            0x21,  # Host-to-device
            0x09,  # Set report
            0x0208,  # wValue
            self.interface,
            payload,
            timeout=1000)
        assert res == len(payload)

    def _read(self):
        data = self.device.read(self.endpoint, self.length, timeout=1000)
        return data.tobytes()

    def clear_read_buffer(self):
        """Clear any stale data from the read buffer"""
        try:
            while True:
                self.device.read(self.endpoint, self.length, timeout=1)
        except usb.core.USBTimeoutError:
            pass

    def read(self, expect=None):
        while True:
            resp = self._read()
            if expect is None:
                return resp
            from .payloads import from_payload
            inst = from_payload(resp)
            if isinstance(inst, expect):
                return inst

    def close(self):
        """Release USB interface and cleanup"""
        if self.device:
            try:
                usb.util.release_interface(self.device, self.interface)
            except:
                pass
            try:
                usb.util.dispose_resources(self.device)
            except:
                pass
            self.device = None

    def __del__(self):
        self.close()
