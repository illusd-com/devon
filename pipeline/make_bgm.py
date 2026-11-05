#!/usr/bin/env python3
"""Generate original BGM tracks into pipeline/bgm/ (requires numpy)."""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "bgm")
os.makedirs(OUT, exist_ok=True)
SR = 44100

def write_wav(path, mono, sr=SR):
    import wave, struct
    stereo = np.column_stack([mono, mono]) if mono.ndim == 1 else mono
    stereo = np.clip(stereo, -1, 1)
    with wave.open(path, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        data = (stereo * 32767).astype(np.int16)
        w.writeframes(data.tobytes())

def soft_pad(secs=45, root=220.0):
    t = np.linspace(0, secs, int(SR * secs), endpoint=False)
    env = np.minimum(1.0, t / 2) * np.minimum(1.0, (secs - t) / 3)
    wave = 0.15 * np.sin(2 * np.pi * root * t)
    wave += 0.08 * np.sin(2 * np.pi * root * 1.5 * t)
    wave += 0.05 * np.sin(2 * np.pi * root * 2 * t)
    return wave * env

tracks = {
    "calm_c": 196.0,
    "warm_f": 174.6,
    "soft_am": 220.0,
    "bright_d": 293.7,
    "night_e": 164.8,
}
for name, root in tracks.items():
    path = os.path.join(OUT, f"{name}.wav")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        print("skip", name)
        continue
    write_wav(path, soft_pad(48, root))
    print("wrote", path)
