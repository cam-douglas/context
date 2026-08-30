# Agent governance operator setup

Human-only controls that sit outside the in-repo agent policy. Agents must not request secret values here.

## GitHub

- Protect the default branch.
- Require the `agent-governance` workflow to pass before merge.
- Restrict who can edit `AGENTS.md`, `.cursor/hooks/`, `.cursor/cli.json`, `.cursor/permissions.json`, `.cursor/sandbox.json`, `.cursorignore`, and `.github/workflows/agent-governance.yml`.

## Vercel

- Optional until Context has a web surface. No production deploy is authorized by this file.

## Supabase

- Optional until Context persists cloud accounts or telemetry. No remote schema mutation is authorized by this file.

## Plugin distribution (deferred)

Record names only. Values stay in the owner's secret manager.

- Steinberg VST3 commercial license (closed-source VST3)
- Apple Developer ID for AU/VST3 signing
- JUCE license if a JUCE wrapper is chosen
- Cycling '74 Max / RNBO commercial terms for exported binaries

## Cloud generation adapters (deferred)

Wire names in config only. Do not paste keys into the repository.

- `CONTEXT_ENABLE_GENERATION`
- `ELEVENLABS_API_KEY` (if that adapter is later approved)
- Other vendor keys only after Security and owner approval
