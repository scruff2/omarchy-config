# My Omarchy configuration

Personal desktop customizations for [Omarchy](https://omarchy.org/), collected so
another laptop can use the same setup without repeating the original editing
sessions. Intended public repository: `scruff2/omarchy-config` on GitHub.

## What this setup changes

- Traditional title bars with circular close, maximize, and minimize buttons.
  The maximize square uses `▢` for clear edges and better visual centering.
- Double-click a title bar to toggle maximization. Maximized windows use the
  working area without outer gaps or rounded corners.
- A bottom bar with window buttons, workspaces, a centered clock, and system
  controls. Click a window button to activate it or restore a minimized window.
- Click the weather cloud to see outdoor weather and the Aranet4 indoor
  temperature. Indoor readings refresh every 15 minutes; failures silently hide
  the indoor row. No separate temperature label occupies the bar.
- Minimize moves a window to the hidden `special:minimized` workspace. The helper
  records its original workspace in the user's temporary runtime directory.
- Super + middle-click closes the focused window.
- Right Alt toggles Voxtype dictation when Voxtype is installed and configured.
- Terminal preferences for Alacritty, Ghostty, Foot, and Kitty. These retain
  Omarchy's dynamic theme includes.

## Compatibility and dependencies

Captured on Omarchy **4.0.6-1**, Hyprland **0.56.2**, on October 28, 2026.
This uses Omarchy's **Lua-based** Hyprland configuration and Quickshell bar.
It is not a drop-in setup for older Omarchy releases with different formats.

Start with a working Omarchy installation. Required tools include Python 3,
GNU Make, a C++23 compiler, pkg-config, and development headers for Hyprland,
pixman, libdrm, libinput, libudev, Wayland, and xkbcommon. The packaged Omarchy
environment normally supplies many of these; install missing build dependencies
through its package manager. JetBrainsMono Nerd Font is used by the terminals.
Voxtype is optional and needs its own microphone/model setup.

The title bars require Hyprbars. Its source and upstream license are included
under `vendor/hyprbars`, along with provenance for the local Lua adaptation.
The installer compiles it against the target laptop's installed headers rather
than distributing this laptop's compiled binary. Hyprland plugins depend on the
compositor ABI; rebuild after a Hyprland update and review source compatibility.
The installer currently stops on versions other than 0.56.2.

## Install on another laptop

After this repository has been published:

```bash
git clone https://github.com/scruff2/omarchy-config.git
cd omarchy-config
./install.py                 # preview the selected files
./install.py --apply         # build plugin, back up files, install
```

Run as your normal desktop user, without sudo. The preview writes nothing.
The installer backs up each existing destination and records missing destinations
so restoration can also remove newly installed files. It does not install OS
packages, change system files, or automatically restart the desktop.

Log out and back in after installing, then check:

```bash
hyprctl reload
hyprctl configerrors
omarchy restart shell
```

Verify title-bar controls, taskbar restoration, keyboard shortcuts, and terminals.
This snapshot has been checked on the source laptop; a fresh laptop installation
still needs this verification. Other existing personal configuration files are
left in place, but the files listed by the preview are replaced in full.

## Aranet4 indoor temperature

The user-owned `mark.weather` plugin extends Omarchy's weather popup. Click the
cloud icon to show the indoor Fahrenheit reading above the outdoor weather.
Hover over the indoor reading for Celsius, humidity, CO₂, battery percentage,
and the last reception time. The row disappears silently if a refresh fails or
the received data becomes stale, and returns after a successful refresh.

The reader listens for Bluetooth LE advertisements for up to 30 seconds every
15 minutes. It does not connect, pair, request a measurement, or change the
sensor's own measurement interval. The sensor must have **Smart Home
integrations** enabled so advertisements include readings. Bluetooth must be
powered on and the sensor in range. This implementation supports Aranet4.

Dependencies on Arch/Omarchy are `bluez`, `python-dbus`, and `python-gobject`,
in addition to the existing Quickshell installation. If missing, install with
`omarchy pkg add bluez python-dbus python-gobject`.

The default address in `config/omarchy/plugins/mark.weather/read-temperature.py`
identifies the source laptop's Aranet4. For a different sensor, set its `ADDRESS`
default before installation, or export `ARANET_ADDRESS` in the desktop session's
environment and restart the shell. Find the address with `bluetoothctl devices`.
Runtime readings and the shared refresh lock stay under `~/.cache/aranet-bar/`
and are not included in this repository. Each sensor gets its own cache.

The installer includes the weather plugin automatically and backs it up like
other configuration files. Restart with `omarchy restart shell` after installation:
changes to nested popup components may remain cached until the shell restarts.
This popup was visually verified on the source laptop with a live Aranet4 reading.

The copied weather base (`BarWidget.qml`, `Panel.qml`, and `Model.js`) comes from
the installed Omarchy 4.0.6-1 shell, with the popup extended to include
`IndoorTemperature.qml`. Keep the clone reviewed against upstream weather changes
when updating Omarchy. Advertisement decoding follows the
[Aranet4-Python implementation](https://github.com/Anrijs/Aranet4-Python).

## Monitor layout

Monitor settings are **not installed by default**. Keep the new laptop's working
`~/.config/hypr/monitors.lua`. The original layout is saved in
`hardware/monitors.lua`: an HDMI display above the laptop display, with different
scaling on each. Review and adapt output names, scaling, and positions before
using `./install.py --apply --monitors`.

## Optional fingerprint reader

The source laptop's **Validity 138a:0097** reader works with a local adaptation
of existing userspace drivers. Source, licenses, an Arch package recipe,
access-control tests, setup instructions, and rollback steps are saved under
[hardware/fingerprint](hardware/fingerprint/README.md). Installation is a
separate administrator action; the desktop installer does not enable it.
Fingerprint templates, pairing material, calibration, firmware downloads, and
private system backups are excluded. Enroll and verify fingers locally on each
laptop before enabling login.

## Restore

The installer prints a backup path under
`~/.local/state/omarchy-config/backups/`. To undo an installation:

```bash
./install.py --apply --restore /path/to/the/printed/backup
```

Log out and back in, reload Hyprland, check configuration errors, and restart the
shell. Restoring the plugin file requires a new desktop session to load it.
Backups contain your previous local configuration; keep them private.

## Themes and scope

This repository preserves layout and configuration preferences. It does not
bundle the selected stock theme, wallpaper images, installed applications,
browser profiles, credentials, dictation models, fingerprint enrollment, or
installed system state. Optional fingerprint service source is saved separately
and is not installed by the desktop installer. The source laptop uses the stock Tokyo Night theme. Select it separately with
`omarchy theme set "Tokyo Night"` (check available names on the target installation).
Generated theme files stay managed by Omarchy.

## Maintain this repository

After changing a preference, copy only the relevant reviewed file into `config/`,
inspect `git diff`, update this explanation, and commit/push. Do not copy your
entire home directory or `.config` directory. Exclude credentials, private URLs,
personal screenshots, generated runtime state, and backup files.

The main Hyprland file still loads Omarchy defaults first, so package defaults
can improve independently. After Omarchy updates, check this setup before
reapplying it, especially the Hyprbars plugin and custom bar module.
