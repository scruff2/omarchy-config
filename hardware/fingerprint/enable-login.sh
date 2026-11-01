#!/bin/bash
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Run this setup with sudo.' >&2; exit 1; }
target_user=${1:?Usage: sudo bash enable-login.sh YOUR_USERNAME}
id "$target_user" >/dev/null
test -x /usr/bin/omarchy-hw-laptop-closed
# Omarchy intentionally runs TWO independent PAM contexts: passwordPam uses
# omarchy-lock-password, fingerprintPam uses omarchy-lock-fingerprint. Either
# may unlock. The separate fingerprint file below matches the stock Omarchy
# setup script; the existing password stack must remain byte-for-byte intact.
lock_source=/usr/share/omarchy/shell/plugins/lock/Service.qml
grep -q 'config: "omarchy-lock-password"' "$lock_source"
grep -q 'config: "omarchy-lock-fingerprint"' "$lock_source"
grep -q 'pam_unix.so' /etc/pam.d/omarchy-lock-password
password_hash=$(sha256sum /etc/pam.d/omarchy-lock-password)
grep -Eq '^auth[[:space:]]+include[[:space:]]+system-login' /etc/pam.d/sddm
fprintd-list "$target_user" | grep -q 'right-index-finger'
backup_dir="/var/lib/validity-0097-backup/$(date +%Y%m%d-%H%M%S)"
install -d -m700 "$backup_dir"
cp -a /etc/pam.d/sddm "$backup_dir/sddm"
if [[ -e /etc/pam.d/omarchy-lock-fingerprint ]]; then
  cp -a /etc/pam.d/omarchy-lock-fingerprint "$backup_dir/omarchy-lock-fingerprint"
fi
if ! grep -q 'pam_fprintd.so' /etc/pam.d/sddm; then
  sed -i '1a auth [success=1 default=ignore] pam_exec.so quiet /usr/bin/omarchy-hw-laptop-closed\nauth sufficient pam_fprintd.so max_tries=3 timeout=10' /etc/pam.d/sddm
fi
cat > /etc/pam.d/omarchy-lock-fingerprint <<'EOF'
#%PAM-1.0
auth required pam_fprintd.so
account include system-local-login
EOF
chmod 644 /etc/pam.d/omarchy-lock-fingerprint
test "$password_hash" = "$(sha256sum /etc/pam.d/omarchy-lock-password)"
grep -Eq '^auth[[:space:]]+include[[:space:]]+system-login' /etc/pam.d/sddm
echo "Fingerprint login configured. Original PAM files saved in $backup_dir"
