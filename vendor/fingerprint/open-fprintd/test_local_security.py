import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from openfprintd.manager import Manager
from openfprintd.device import Device, PermissionDenied


class AccessTests(unittest.TestCase):
    def test_unprivileged_backend_rejected(self):
        manager = SimpleNamespace(devices={})
        bus = Mock()
        bus.get_unix_user.return_value = 1000
        with self.assertRaises(PermissionDenied):
            Manager.RegisterDevice(manager, '/fake', ':1.123', bus)
        self.assertEqual(manager.devices, {})

    def test_unprivileged_power_controls_rejected(self):
        bus = Mock()
        bus.get_unix_user.return_value = 1000
        for method in (Manager.Suspend, Manager.Resume):
            with self.assertRaises(PermissionDenied):
                method(SimpleNamespace(devices={}), ':1.123', bus)

    def test_unprivileged_raw_commands_rejected(self):
        device = SimpleNamespace(bus=Mock(), target=Mock())
        device.bus.get_unix_user.return_value = 1000
        with self.assertRaises(PermissionDenied):
            Device.RunCmd(device, '00', ':1.123', device.bus)
        device.target.RunCmd.assert_not_called()

    def test_root_raw_command_allowed(self):
        device = SimpleNamespace(bus=Mock(), target=Mock())
        device.bus.get_unix_user.return_value = 0
        Device.RunCmd(device, '00', ':1.123', device.bus)
        device.target.RunCmd.assert_called_once_with('00', signature='s')


if __name__ == '__main__':
    unittest.main()
