# Optional sudo authentication cache

`99-mark-sudo-timeout` records the proposed preference for the `mark` account:

- Cache sudo authentication for 60 minutes of inactivity.
- Share cached authentication across terminals (`timestamp_type=global`).
- Continue requiring a password when no valid cached authentication exists.

This policy is saved for review and is **not applied to the source laptop**.
The attempt to apply it was rejected by automatic approval review, pending
explicit approval of the 60-minute timeout and sharing across terminals.
The desktop installer does not install this file or modify sudo policy.

Sharing the cache means processes running as Mark can reuse authenticated sudo
access during that window. This setting controls sudo, not graphical Polkit
password prompts such as those used by `pkexec`.

The intended system destination, if separately approved and validated with
`visudo`, is `/etc/sudoers.d/99-mark-sudo-timeout`, owned by root with mode 0440.
The account name must be reviewed before reuse on another laptop.
