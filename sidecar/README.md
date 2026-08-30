# Context sidecar

Local Python service for the Context device. Hosts talk JSON over localhost. This package does not run inside the Ableton audio thread.

```bash
cd sidecar
CONTEXT_SIDECAR_PORT=8765 PYTHONPATH=src python -m context_sidecar.http
```

Listens on `127.0.0.1` only.

- `GET /health` → `{"ok": true}`
- `POST /intent` → validates `IntentRequest`, echoes it, returns `empty_arrangement` preview
- `POST /analyze`, `/mix-audit`, `/arrange`, `/search`, `/stems`, `/synthesize`, `/dsp`, `/export`

```bash
cd sidecar
PYTHONPATH=src python -m unittest discover -s tests -v
```
