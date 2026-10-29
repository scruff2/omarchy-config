#!/usr/bin/env python3
"""Preview/install selected Omarchy files, with a reversible backup."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
HOME = Path.home()


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_symlink() or target.is_file():
        target.unlink()
    shutil.copy2(source, target, follow_symlinks=False)


def restore(backup):
    entries = json.loads((backup / 'manifest.json').read_text())
    for entry in reversed(entries):
        target = HOME / entry['path']
        if entry['existed']:
            copy(backup / 'files' / entry['path'], target)
        elif target.is_file() or target.is_symlink():
            target.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='write files (default: preview)')
    parser.add_argument('--monitors', action='store_true', help='also copy the original laptop monitor layout')
    parser.add_argument('--restore', type=Path, help='restore a backup created by this installer')
    args = parser.parse_args()
    if args.restore:
        if not args.apply:
            print(f'Would restore {args.restore}; add --apply to proceed.')
        else:
            restore(args.restore.resolve())
            print('Restored. Run hyprctl reload and hyprctl configerrors; restart the Omarchy shell.')
        return

    pairs = [(p, Path('.config') / p.relative_to(ROOT / 'config'))
             for p in sorted((ROOT / 'config').rglob('*')) if p.is_file()]
    if args.monitors:
        pairs.append((ROOT / 'hardware/monitors.lua', Path('.config/hypr/monitors.lua')))
    for _, destination in pairs:
        print(f'Install ~/{destination}')
    print('Build and install ~/.local/lib/hyprland/hyprbars.so')
    if not args.apply:
        print('Preview only. Run ./install.py --apply to install with backups.')
        return
    if os.geteuid() == 0:
        raise SystemExit('Run as your desktop user, without sudo.')
    version = subprocess.check_output(['hyprctl', 'version'], text=True)
    if 'Hyprland 0.56.2 ' not in version:
        raise SystemExit('This snapshot targets Hyprland 0.56.2. Review/update the plugin source before installing on another version.')
    if not Path('/usr/share/omarchy/default/hypr/bootstrap.lua').exists():
        raise SystemExit('The Lua-based Omarchy configuration is required.')

    # Build before changing any desktop files. Work in a temporary directory.
    with tempfile.TemporaryDirectory(prefix='omarchy-config-build-') as temp:
        build = Path(temp) / 'hyprbars'
        shutil.copytree(ROOT / 'vendor/hyprbars', build)
        subprocess.run(['make', '-C', str(build), '-j2'], check=True)
        # Install the plugin first and the main configuration last.
        pairs.sort(key=lambda pair: pair[1] == Path('.config/hypr/hyprland.lua'))
        pairs.insert(0, (build / 'hyprbars.so', Path('.local/lib/hyprland/hyprbars.so')))
        backup = HOME / '.local/state/omarchy-config/backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True)
        entries = []
        for _, relative in pairs:
            target = HOME / relative
            if target.exists() and not target.is_file() and not target.is_symlink():
                raise SystemExit(f'Expected a file: {target}')
            existed = target.exists() or target.is_symlink()
            entries.append({'path': str(relative), 'existed': existed})
            if existed:
                copy(target, backup / 'files' / relative)
        (backup / 'manifest.json').write_text(json.dumps(entries, indent=2) + '\n')
        try:
            for source, relative in pairs:
                copy(source, HOME / relative)
        except Exception:
            restore(backup)
            raise
    print(f'Installed. Backup: {backup}')
    print(f'Restore: ./install.py --apply --restore {backup}')
    print('Log out and back in to load the rebuilt plugin. Then run:')
    print('  hyprctl reload\n  hyprctl configerrors\n  omarchy restart shell')


if __name__ == '__main__':
    main()
