# Context session export

## Write a cloned Live Set

```bash
cd sidecar
PYTHONPATH=src .venv/bin/python -c "
from context_sidecar.export import export_session
print(export_session(
    '/tmp/context-export',
    midi_path='../fixtures/empty.mid',
    stem_paths=['../fixtures/silence.wav'],
    slug='Context',
))
"
```

Or `POST http://127.0.0.1:8765/export` with `dest_dir`, optional `source_als`, `arrangement`, `stem_paths`, `midi_path`.

## Integrity rules

- Source `.als` is cloned, never overwritten.
- Existing tracks stay. Context adds `Context …` tracks.
- Output: `*.als`, `*.als.json`, staged `Samples/Context/`, optional `*-render.wav`.

## Open in Live

File → Open the written `.als`. Do not replace the user's original set until they confirm Live loads it.
