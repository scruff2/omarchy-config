# Optional: Validity 138a:0097 fingerprint reader

This setup was tested on the source laptop's Validity USB reader **138a:0097**
with Omarchy's Quickshell lock and SDDM. It adapts existing userspace drivers;
it does not require a kernel module. Other readers need their own review.
This is independent of the repository's desktop `install.py` and is never
installed automatically with the desktop preferences.

The source laptop's reader already had initialized flash and firmware 1.1
(2020-01-21), ROM 6.7 build 164, sensor VSI 55E FM209-001. The upstream driver
can initialize flash or upload firmware on other devices, but those paths were
not tested here. Review upstream instructions before using this on a reader
without working firmware or with enrollment from another OS. Do not factory
reset a reader just to reproduce these settings.

## Included and excluded

`../../vendor/fingerprint` contains reviewed source files and upstream license
notices, with exact revisions and local changes in its `PROVENANCE.md`.
The files here build an Arch package and configure services and optional login.

No fingerprint templates, sensor pairing material, calibration files, firmware
downloads, system backups, or private runtime state belong in this repository.
In particular, never copy `/var/lib/python-validity`, `/run/python-validity`,
`/var/lib/fprint`, or `/var/lib/validity-0097-backup` into Git. Enrollment must
happen locally on the target laptop, even when using the same account name.
Build output is ignored and is not distributed.

## Build and install the backend

Start with a working Omarchy system and confirm `lsusb -d 138a:0097` finds the
reader. Install dependencies if missing:

```bash
omarchy pkg add base-devel fprintd python-pyusb python-cryptography python-yaml python-dbus python-gobject usbutils
cd hardware/fingerprint  # from the repository root
python ../../vendor/fingerprint/open-fprintd/test_local_security.py
makepkg
sudo bash install-local.sh
fprintd-list "$USER"
```

Read the scripts before running them. They require administrator access.
The package puts source under `/opt/validity-0097`, adds a systemd drop-in that
runs the replacement manager through `fprintd.service`, and adds/enables
`validity-backend.service`. The stock fprintd package and its clients/PAM module
remain installed. Calibration is kept locally under `/var/lib/python-validity`
with restrictive permissions. The sleep hook stops the backend before suspend
and starts it on resume. No packaged Omarchy source is changed.

## Enroll and verify, then enable login

```bash
fprintd-enroll -f right-index-finger "$USER"
fprintd-verify -f right-index-finger "$USER"
```

Touch/lift the right index finger repeatedly during enrollment. In a fresh
verification, it must return `verify-match`. Run verification again using a
different, unenrolled finger; it must return `verify-no-match`. Do not enable
login if the tests do not behave this way.

After those checks pass:

```bash
sudo bash enable-login.sh "$USER"
```

This separate, optional step backs up the previous SDDM and lock fingerprint PAM
files under `/var/lib/validity-0097-backup/TIMESTAMP`. It checks that this version
of Omarchy uses independent `omarchy-lock-password` and
`omarchy-lock-fingerprint` flows. It preserves the password lock file unchanged
and retains SDDM's existing password stack. It adds fingerprint authentication
to SDDM with a short timeout and skips it when the laptop lid is closed.
It does not enable fingerprint authentication for sudo, SSH, or polkit.

Try Super + Ctrl + L and touch the right index finger. Check password unlocking
too. At SDDM you may need to submit the empty password field to begin scanning.
The backend starts at boot; fingerprints cannot unlock an encrypted boot volume
or supply the password for a login keyring.

## Verification and limits

On the source laptop: encrypted sensor communication, calibration, enrollment,
an enrolled-finger match, an unenrolled-finger rejection, and backend restart
with enrollment preserved all passed. Four access-control unit tests passed;
a live D-Bus call from a normal user was rejected when attempting fake backend
registration. SDDM/lock PAM were configured with password fallback retained.

A full reboot, interactive SDDM/lock authentication, and actual suspend/resume
were not tested during this capture. Verify those on the target laptop before
relying on the reader. The older upstream drivers have not had a full security
audit. Hardware initialization, pairing, and firmware compatibility may differ.

Useful checks:

```bash
systemctl status validity-backend.service fprintd.service
journalctl -u validity-backend.service -u fprintd.service
fprintd-list "$USER"
```

## Roll back

Use the exact private backup directory printed by `enable-login.sh`. Restore
its `sddm` to `/etc/pam.d/sddm`. If the backup contains
`omarchy-lock-fingerprint`, restore it to `/etc/pam.d/omarchy-lock-fingerprint`;
otherwise remove the newly created lock fingerprint file. Leave
`/etc/pam.d/omarchy-lock-password` in place.

Then:

```bash
sudo systemctl disable --now validity-backend.service
sudo pacman -R validity-0097-local
sudo systemctl daemon-reload
sudo systemctl restart fprintd.service
```

This restores the stock daemon. Calibration and enrolled templates are
deliberately retained locally. Do not upload them or the private PAM backups.
