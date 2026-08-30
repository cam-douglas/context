# Security note (localhost host)

- `SidecarClient` connects only to `127.0.0.1` with a 1s timeout.
- No secrets, no remote bind, no `.als` write.
- Drop folder is the user Documents directory (owner-visible files only).
- Verdict: **PASS** for this local host. Distribution signing is out of scope.
