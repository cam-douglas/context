# Blocker: Stable Audio Open weights are gated

## Resolution

Verified 2026-08-30. Owner accepted the Hugging Face license. `snapshot_download("stabilityai/stable-audio-open-1.0")` wrote 7 weight files (15.6 GB) under `~/Library/Application Support/Context/models`. A real compose wrote a 705644-byte stereo 44.1 kHz WAV with RMS 4583 and `backend` `stable-audio-open-1.0`. No stand-in. DDIM scheduler is used because the default SDE scheduler hit a recursion error on MPS.
