# Context security findings (phase 0)

## SEC-001

- Severity: medium (operational, not product exploit)
- Title: Bootstrap blocked on missing protected control-plane files
- Evidence: bootstrap error; Write to AGENTS.md denied
- Remediation: owner runs `docs/handover/apply-missing-control-plane-files.sh`
- Status: open, owner-owned

## SEC-002

- Severity: info
- Title: MusicGen weights excluded from commercial path
- Evidence: AudioCraft LICENSE_weights CC-BY-NC
- Status: accepted control, no remediation

No high or critical product findings in the phase-0 tree. Sidecar HTTP is not implemented yet, so T1 is a future implementation check.
