"""Generate rights-clear fixture audio and MIDI. Stdlib only."""

from __future__ import annotations

import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAMPLE_RATE = 44100
CHANNELS = 2
SECONDS = 1


def write_silence_wav(path: Path) -> None:
    frames = SAMPLE_RATE * SECONDS
    with wave.open(str(path), "w") as handle:
        handle.setnchannels(CHANNELS)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(b"\x00\x00" * CHANNELS * frames)


def write_empty_midi(path: Path) -> None:
    # Format 0, one track, 480 ticks per quarter. One bar of 4/4, no notes.
    ticks_per_quarter = 480
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, ticks_per_quarter)
    # delta 0, meta end-of-track
    track_events = b"\x00\xff\x2f\x00"
    track = b"MTrk" + struct.pack(">I", len(track_events)) + track_events
    path.write_bytes(header + track)


def main() -> None:
    write_silence_wav(ROOT / "silence.wav")
    write_empty_midi(ROOT / "empty.mid")


if __name__ == "__main__":
    main()
