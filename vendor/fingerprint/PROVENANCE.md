# Validity fingerprint sources

This is a local adaptation of two existing userspace drivers, not a newly
reverse-engineered sensor protocol. Only tracked source files were copied from
the upstream checkouts. No runtime sensor data or installed state is included.

## python-validity

- Upstream: https://github.com/uunicorn/python-validity
- Revision: `a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920`
- License: see `python-validity/LICENSE` and individual file headers.
- Included: Python package, D-Bus entry point/config, upstream README and license.
- Local change: calibration state lives under `/var/lib/python-validity` with
  mode 0700, rather than under the temporary `/run` tree.

## open-fprintd

- Upstream: https://github.com/uunicorn/open-fprintd
- Revision: `b7073730bccca36e84484e3fcb4f8253ea038d07`
- License: see `open-fprintd/COPYING` and individual file headers.
- Included: Python package, D-Bus entry points/config, upstream README and license.
- Local changes: reject non-root backend registration, suspend/resume control,
  and raw sensor commands; restrict cross-user enrollment listing; add four
  access-control tests.

The upstream Python files contain public protocol constants, initialization
blobs, firmware download URLs, and cryptographic constants. These are upstream
source, not keys or biometric data extracted from this laptop. No proprietary
firmware installer or extracted firmware is bundled.

The packaging and Omarchy integration live in `hardware/fingerprint` at the
repository root. The security changes are limited improvements, not an audit
of either upstream project or of fingerprint authentication as a whole.
