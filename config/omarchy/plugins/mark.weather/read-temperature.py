#!/usr/bin/python
"""Listen for an Aranet4 advertisement; never connect or change sensor settings."""
import fcntl
import json
import os
from pathlib import Path
import struct
import re
import time

import dbus
import dbus.mainloop.glib
from gi.repository import GLib

# Override for another sensor without changing the reader.
ADDRESS = os.environ.get('ARANET_ADDRESS', 'EC:C2:AC:8D:8B:4D').upper()
if not re.fullmatch(r'(?:[0-9A-F]{2}:){5}[0-9A-F]{2}', ADDRESS):
    print(json.dumps({'ok': False, 'error': 'Invalid Aranet Bluetooth address'}))
    raise SystemExit
cache_dir = Path.home() / '.cache' / 'aranet-bar' / ADDRESS.replace(':', '')
cache_dir.mkdir(parents=True, exist_ok=True)
lock = (cache_dir / 'lock').open('w')
fcntl.flock(lock, fcntl.LOCK_EX)
cache = cache_dir / 'reading.json'
try:
    previous = json.loads(cache.read_text())
except (OSError, ValueError):
    previous = {}
now = time.time()
if 0 <= now - previous.get('attempted_at', 0) < 900:
    print(json.dumps(previous))
    raise SystemExit

result = {'ok': False, 'attempted_at': now, 'error': 'Sensor unavailable'}
loop = GLib.MainLoop()
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
adapter = None
started = False

def receive(path, props):
    if not str(path).upper().endswith('DEV_' + ADDRESS.replace(':', '_')):
        return
    data = bytes(props.get('ManufacturerData', {}).get(0x0702, []))
    if len(data) < 21 or not data[0] & 0x20:
        return
    co2, temp, pressure, humidity, battery, status, interval, age = struct.unpack_from('<HHHBBBHH', data, 8)
    if age > max(900, interval * 2) or not 0 <= temp / 20 <= 60:
        return
    result.update(ok=True, temperature_f=temp / 20 * 1.8 + 32,
                  temperature_c=temp / 20, humidity=humidity, co2=co2,
                  battery=battery, observed_at=time.time(), age=age)
    result.pop('error', None)
    loop.quit()

def changed(interface, props, invalidated, path=None):
    if interface == 'org.bluez.Device1':
        receive(path, props)

def added(path, interfaces):
    if 'org.bluez.Device1' in interfaces:
        receive(path, interfaces['org.bluez.Device1'])

try:
    manager = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.freedesktop.DBus.ObjectManager')
    objects = manager.GetManagedObjects()
    for path, interfaces in objects.items():
        if interfaces.get('org.bluez.Adapter1', {}).get('Powered', False):
            adapter = dbus.Interface(bus.get_object('org.bluez', path), 'org.bluez.Adapter1')
            break
    if adapter is None:
        raise RuntimeError('Bluetooth is off')
    bus.add_signal_receiver(changed, signal_name='PropertiesChanged',
                            dbus_interface='org.freedesktop.DBus.Properties', path_keyword='path')
    bus.add_signal_receiver(added, signal_name='InterfacesAdded',
                            dbus_interface='org.freedesktop.DBus.ObjectManager')
    adapter.SetDiscoveryFilter(dbus.Dictionary({'Transport': dbus.String('le'),
                              'DuplicateData': dbus.Boolean(True)}, signature='sv'))
    adapter.StartDiscovery()
    started = True
    GLib.timeout_add_seconds(30, lambda: (loop.quit(), False)[1])
    loop.run()
except Exception as exc:
    result['error'] = str(exc)
finally:
    if started:
        try:
            adapter.StopDiscovery()
        except dbus.DBusException:
            pass
payload = json.dumps(result)
temporary = cache.with_suffix('.tmp')
temporary.write_text(payload)
os.replace(temporary, cache)
print(payload)
