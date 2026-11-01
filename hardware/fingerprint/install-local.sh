#!/bin/bash
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Run this installer with sudo.' >&2; exit 1; }
cd -- "$(dirname -- "$(realpath -- "$0")")"
lsusb -d 138a:0097 | grep -q . || { echo 'Validity 138a:0097 reader not found.' >&2; exit 1; }
pacman -U ./validity-0097-local-0.1-2-any.pkg.tar.zst
install -d -m700 /var/lib/python-validity
if [[ -f /run/python-validity/calib-data.bin && ! -f /var/lib/python-validity/calib-data.bin ]]; then
  install -m600 /run/python-validity/calib-data.bin /var/lib/python-validity/calib-data.bin
fi
systemctl daemon-reload
systemctl reload dbus
systemctl restart fprintd.service
systemctl enable --now validity-backend.service
systemctl --no-pager status validity-backend.service
