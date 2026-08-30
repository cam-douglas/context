# Engineering evidence

Date: 2026-08-28

- Sidecar tests: `PYTHONPATH=src python -m unittest discover -s tests -v` → 44 OK.
- HTTP: `127.0.0.1` only. `/health`, `/intent`, `/analyze`, `/mix-audit`, `/arrange`, `/search`, `/stems`, `/synthesize`, `/dsp`, `/export`.
- Fixtures: `fixtures/silence.wav`, `fixtures/empty.mid`.
- Max Project: `max/context/` unfrozen. Live C-5 UNVERIFIED.
- Generation/Demucs default off. MusicGen/AudioLDM 2 blocked.
- Export never writes `.als`.
