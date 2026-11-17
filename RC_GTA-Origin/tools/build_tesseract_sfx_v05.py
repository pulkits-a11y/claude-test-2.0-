#!/usr/bin/env python3
"""Build the v05 SFX library: 03_SFX/v05/*.wav + 03_SFX/v05/library.json, deterministically.

Why (REVISION_v05.md G9 + S, client doc section 2.7): every caption word gets a soft tick (3 alternating samples,
about -24 dB), every key/hero word a short whoosh into it plus a low thump (about -14 dB), every hard cut in the
hook a swipe, plus named moments (siren whoop, keyboard clatter, an ORIGINAL "critical stop"-style error chord,
glitch stutters, a stamp thud, reverse-cymbal risers, an impact boom + sub drop on the logo, a paper rip, a
flat-line beep, dings, a click ...). The lanes reference these canonical names in hyperframes/<comp>/cues.json;
tools/build_tesseract_audio.py places them.

Sources: the S-files already in 03_SFX/ where one fits (decoded with FFmpeg, resampled to 48 kHz with soxr), every
other sound synthesized here with numpy/scipy (no third-party downloads). Each sound's recipe is written into
library.json next to the file names.

Levels: every file is written at its DEFAULT level, i.e. the file's sample peak = `default_peak_dbfs`, so a layer
at unity gain plays the sound at the level the assembly uses (pre-master; the audio build's master gain, about
-1 dB, comes on top). Variant sets (tick_1-3, hit_1-3) are loudness-matched to each other first (max 100 ms
K-weighted energy), then scaled together so the loudest variant peaks at the default. The defaults were set
against the locked voice (sample peak about -3.8 dBFS on the stereo bus, short-term about -13.5 LUFS stereo):
nothing defaults above -6 dBFS (plan rule: the voice stays on top), caption ticks sit 20 dB under the voice peaks.

Format: 48 kHz (Tesseract's mix rate: no resampling in the engine, so the audio build's model of each layer is
sample-exact), 24-bit PCM WAV, mono unless the sound moves in the stereo field.

Usage:  python3 tools/build_tesseract_sfx_v05.py          (rewrites 03_SFX/v05/; about 10 s)
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter, sosfilt

ROOT = Path(__file__).resolve().parents[1]
SFX_DIR = ROOT / "03_SFX"
OUT = SFX_DIR / "v05"
SR = 48000
FPS = 30


# v05 client override (REVISION_v05.md U2/U5/U6, G5): these stay in the library (harmless) but are not used
NOT_USED_V05 = {"stamp_thud": "NOT USED in v05 (U5: no rubber stamp, no stamp sound).",
                "whoosh_flip": "NOT USED in v05 (U6: no 3D flip; B11 keeps the v04 glitch).",
                "type_on": "NOT USED in v05 (U2: no type-on; pills and the CTA line show their text whole)."}


def log(*a):
    print(*a, flush=True)


# --------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------
def db(x):
    return 20 * math.log10(max(float(x), 1e-12))


def lin(d):
    return 10 ** (d / 20.0)


def tvec(dur):
    return np.arange(int(round(dur * SR))) / SR


def as2d(x):
    x = np.asarray(x, float)
    return x[:, None] if x.ndim == 1 else x


def decode(fname: str, extra_af: str = "") -> np.ndarray:
    """FFmpeg decode of an 03_SFX original at 48 kHz (soxr), float, native channel count (n, ch)."""
    src = SFX_DIR / fname
    ch = int(json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
                                        "stream=channels", "-of", "json", str(src)], capture_output=True, text=True,
                                       check=True).stdout)["streams"][0]["channels"])
    af = "aresample=48000:resampler=soxr:precision=28" + ("," + extra_af if extra_af else "")
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(src), "-af", af, "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, ch).astype(np.float64)
    return x[:, :2]


def fade(x, fin_s=0.0, fout_s=0.0):
    x = as2d(x).copy()
    n = len(x)
    if fin_s > 0:
        k = min(n, int(round(fin_s * SR)))
        x[:k] *= np.linspace(0, 1, k, endpoint=False)[:, None]
    if fout_s > 0:
        k = min(n, int(round(fout_s * SR)))
        x[n - k:] *= np.linspace(1, 0, k)[:, None]
    return x


def bandpass(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], "bandpass", fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


def lowpass(x, fc, order=2):
    return sosfilt(butter(order, fc, "lowpass", fs=SR, output="sos"), x, axis=0)


def highpass(x, fc, order=2):
    return sosfilt(butter(order, fc, "highpass", fs=SR, output="sos"), x, axis=0)


def resonator(x, f, tau):
    """2-pole resonator at f Hz whose impulse response decays with time constant tau (s)."""
    r = math.exp(-1.0 / (tau * SR))
    w = 2 * math.pi * f / SR
    return lfilter([1 - r], [1, -2 * r * math.cos(w), r * r], x, axis=0)


def svf(x, fc, mode="bp", q=0.9):
    """Time-varying state-variable filter (TPT/Zavalishin), fc an array (Hz) per sample. mode bp|lp|hp."""
    x = np.asarray(x, float)
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    out = np.empty_like(x)
    k = 1.0 / q
    ic1 = ic2 = 0.0
    for i in range(len(x)):
        g = math.tan(math.pi * min(fc[i], 0.45 * SR) / SR)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2, a3 = g * a1, g * g * a1
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1, ic2 = 2 * v1 - ic1, 2 * v2 - ic2
        out[i] = v1 if mode == "bp" else (v2 if mode == "lp" else x[i] - k * v1 - v2)
    return out


def norm(x):
    x = np.asarray(x, float)
    return x / max(1e-12, float(np.max(np.abs(x))))


def trim_lead(x, rel_db=-50.0, preroll_s=0.001):
    """Drop leading silence: start `preroll_s` before the first sample within rel_db of the peak."""
    x = as2d(x)
    a = np.max(np.abs(x), axis=1)
    thr = a.max() * lin(rel_db)
    i = int(np.argmax(a > thr))
    return x[max(0, i - int(preroll_s * SR)):]


_KB1 = [1.53512485958697, -2.69169618940638, 1.19839281085285]
_KA1 = [1.0, -1.69065929318241, 0.73248077421585]
_KB2 = [1.0, -2.0, 1.0]
_KA2 = [1.0, -1.99004745483398, 0.99007225036621]


def max_momentary(x, win_s=0.1):
    """Max K-weighted energy over a sliding window (dB, relative): the loudness of a short sound."""
    x = as2d(x)
    y = lfilter(_KB2, _KA2, lfilter(_KB1, _KA1, x, axis=0), axis=0)
    p = np.sum(y * y, axis=1)
    w = max(1, int(win_s * SR))
    c = np.concatenate([[0.0], np.cumsum(p)])
    m = (c[w:] - c[:-w]) / w if len(p) > w else np.array([c[-1] / max(1, len(p))])
    return 10 * math.log10(max(float(m.max()), 1e-20))


# --------------------------------------------------------------------------------------------
# synthesized sounds (deterministic: one RNG seed per sound)
# --------------------------------------------------------------------------------------------
def syn_tick(variant: int):
    rng = np.random.default_rng(1000 + variant)
    t = tvec(0.060)
    p = {1: dict(band=(2500, 7000), tones=[(1850, 0.006, 1.0)], tau=0.004),
         2: dict(band=(3200, 9000), tones=[(2650, 0.005, 1.0)], tau=0.0035),
         3: dict(band=(1500, 5000), tones=[(1200, 0.008, 0.8), (2400, 0.004, 0.5)], tau=0.005)}[variant]
    att = 1 - np.exp(-t / 0.0004)                        # 0.4 ms soft attack: a tick, not a digital click
    noise = norm(bandpass(rng.standard_normal(len(t)), *p["band"])) * np.exp(-t / p["tau"]) * att
    tone = sum(a * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi)) * np.exp(-t / tau) for f, tau, a in p["tones"])
    x = 0.55 * noise + 0.45 * norm(tone * att)
    return fade(x, 0, 0.010), ("band-passed noise %d-%d Hz (decay %.1f ms) + %s, 0.4 ms attack, 60 ms" % (
        p["band"][0], p["band"][1], p["tau"] * 1000,
        " + ".join("%d Hz sine (decay %.0f ms)" % (f, tau * 1000) for f, tau, _ in p["tones"])))


def syn_whoosh_in():
    rng = np.random.default_rng(2001)
    dur = 0.42
    t = tvec(dur)
    u = t / dur
    fc = 450 * (3800 / 450) ** (u ** 1.3)               # band-pass centre sweeps 450 Hz -> 3.8 kHz
    env = u ** 2.4                                        # swells into the word
    a = rng.standard_normal(len(t))
    b = rng.standard_normal(len(t))
    L = svf(0.8 * a + 0.2 * b, fc, "bp", 1.2) * env
    R = svf(0.2 * a + 0.8 * b, fc * 1.04, "bp", 1.2) * env
    pan = 0.35 + 0.3 * u                                  # drifts left -> centre-right
    x = np.stack([L * np.cos(pan * np.pi / 2), R * np.sin(pan * np.pi / 2)], axis=1)
    return fade(x, 0.004, 0.006), ("decorrelated noise through a band-pass (Q 1.2) sweeping 450 Hz -> 3.8 kHz, "
                                   "level swelling as (t/T)^2.4 to its peak at the very end (6 ms release), drifting "
                                   "from left to centre-right; 0.42 s; align END on the key word's frame")


def syn_thump_low():
    rng = np.random.default_rng(2002)
    t = tvec(0.36)
    f = 45 + (110 - 45) * np.exp(-t / 0.03)               # pitch drop 110 -> 45 Hz
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.09) * (1 - np.exp(-t / 0.0015))
    body = np.tanh(1.6 * body) / np.tanh(1.6)              # a little saturation: harmonics for small speakers
    click = norm(lowpass(rng.standard_normal(len(t)), 900)) * np.exp(-t / 0.003)
    x = body + 0.25 * click
    return fade(x, 0, 0.04), ("sine with a pitch drop 110 -> 45 Hz (30 ms), decay 90 ms, tanh drive 1.6 (audible "
                              "harmonics on phones) + a 3 ms low-passed noise click; 0.36 s; align start")


def syn_swipe():
    rng = np.random.default_rng(2003)
    dur, pk = 0.30, 0.12
    t = tvec(dur)
    env = np.where(t < pk, np.exp(-((t - pk) / 0.05) ** 2), np.exp(-((t - pk) / 0.075) ** 2))
    fc = 900 + 5200 * env
    a, b = rng.standard_normal(len(t)), rng.standard_normal(len(t))
    L = svf(0.75 * a + 0.25 * b, fc, "bp", 1.0) * env
    R = svf(0.25 * a + 0.75 * b, fc * 1.05, "bp", 1.0) * env
    u = np.clip(0.15 + 0.7 * t / dur, 0, 1)               # left -> right
    x = np.stack([L * np.cos(u * np.pi / 2), R * np.sin(u * np.pi / 2)], axis=1)
    return fade(x, 0.003, 0.02), ("decorrelated noise, band-pass centre riding the envelope (0.9 -> 6.1 kHz at "
                                  "the peak), fast rise / slower fall around a peak at 0.12 s, panned left -> right; "
                                  "0.30 s; align PEAK on the cut")


def syn_sub_hit():
    rng = np.random.default_rng(2004)
    t = tvec(0.9)
    f = 38 + (72 - 38) * np.exp(-t / 0.05)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.25) * (1 - np.exp(-t / 0.003))
    body = np.tanh(2.0 * body) / np.tanh(2.0)
    knock = norm(lowpass(rng.standard_normal(len(t)), 300)) * np.exp(-t / 0.008)
    x = body + 0.3 * knock
    return fade(x, 0, 0.15), ("sub sine 72 -> 38 Hz (50 ms), decay 250 ms, tanh drive 2.0 (2nd/3rd harmonics so "
                              "phones hear it) + an 8 ms low-passed knock; 0.9 s; align start")


def syn_metal_crunch():
    rng = np.random.default_rng(2005)
    t = tvec(0.8)
    burst = rng.standard_normal(len(t)) * np.exp(-t / 0.025)
    crackle = np.zeros(len(t))
    k = 0.0
    while k < 0.30:                                       # sparse crackle, thinning out
        k += rng.exponential(1 / 450.0)
        i = int(k * SR)
        if i < len(t):
            crackle[i] += rng.lognormal(0, 0.6) * math.exp(-k / 0.12)
    exc = burst + 3.0 * highpass(crackle, 1500)
    modes = [(397, 0.30, 1.0), (523, 0.26, 0.8), (1088, 0.22, 0.7), (1675, 0.18, 0.6), (2470, 0.15, 0.5),
             (3540, 0.12, 0.4), (4960, 0.10, 0.3)]
    ring = sum(a * norm(resonator(exc, f, tau)) for f, tau, a in modes)
    thud = np.sin(2 * np.pi * 60 * t) * np.exp(-t / 0.08) * (1 - np.exp(-t / 0.002))
    x = norm(ring) + 0.5 * norm(bandpass(exc, 800, 6000)) + 0.6 * thud
    x = np.tanh(1.5 * norm(x)) / np.tanh(1.5)
    return fade(x, 0, 0.12), ("a 25 ms noise burst + thinning crackle (450/s, high-passed 1.5 kHz) exciting seven "
                              "inharmonic metal modes (397/523/1088/1675/2470/3540/4960 Hz, 300-100 ms rings), "
                              "plus the raw band-passed scrape and a 60 Hz thud, tanh drive 1.5; 0.8 s; align start")


def syn_error_chord():
    """An ORIGINAL 'critical stop'-style alert chord (not Microsoft's chord.wav): a stacked tritone/fourth voicing
    F#4-C5-F5-B5 with an organ-bell timbre, short ping, decaying sustain."""
    rng = np.random.default_rng(2006)
    dur = 1.0
    t = tvec(dur)
    notes = [369.99, 523.25, 698.46, 987.77]
    partials = [(1.0, 1.0), (2.0, 0.45), (3.0, 0.25), (4.01, 0.12), (5.02, 0.06)]
    env = (1 - np.exp(-t / 0.004)) * (0.6 + 0.4 * np.exp(-t / 0.15)) * np.exp(-np.clip(t - 0.25, 0, None) / 0.35)
    chans = []
    for det in (-3.0, 3.0):                                # +-3 cents L/R: width
        s = np.zeros(len(t))
        for f0 in notes:
            f = f0 * 2 ** (det / 1200.0)
            for m, a in partials:
                s += a * np.sin(2 * np.pi * f * m * t + rng.uniform(0, 2 * np.pi)) * np.exp(-t * (m - 1) * 1.2)
        chans.append(s * env)
    ping = np.sin(2 * np.pi * 2349.3 * t) * np.exp(-t / 0.03) * 0.5
    x = np.stack([chans[0] + ping, chans[1] + ping], axis=1)
    return fade(x, 0.002, 0.08), ("original synthesized alert chord, NOT Microsoft's file: F#4 C5 F5 B5 (stacked "
                                  "tritone / fourth / tritone), each note 5 partials (1, 2, 3, 4.01, 5.02; upper "
                                  "partials decaying faster), 4 ms attack, 150 ms fall to a 60% sustain, release from "
                                  "0.25 s (350 ms), +-3 cents L/R detune, a 30 ms D7 ping on the attack; 1.0 s")


def syn_stamp_thud():
    rng = np.random.default_rng(2007)
    t = tvec(0.6)
    f = 55 + (85 - 55) * np.exp(-t / 0.02)
    ph = 2 * np.pi * np.cumsum(f) / SR
    thud = np.sin(ph) * np.exp(-t / 0.07) * (1 - np.exp(-t / 0.0015))
    slap = norm(bandpass(rng.standard_normal(len(t)), 600, 2500)) * np.exp(-t / 0.010)
    desk = norm(resonator(slap, 180, 0.06))
    paper = norm(bandpass(rng.standard_normal(len(t)), 3000, 8000)) * np.exp(-t / 0.006)
    x = thud + 0.6 * slap + 0.5 * desk + 0.2 * paper
    x = np.tanh(1.4 * norm(x)) / np.tanh(1.4)
    return fade(x, 0, 0.1), ("rubber stamp on paper on a desk: 85 -> 55 Hz thud (70 ms), a 10 ms band-passed "
                             "(0.6-2.5 kHz) slap, a 180 Hz desk resonance (60 ms) and a 6 ms paper tick (3-8 kHz), tanh "
                             "drive 1.4; 0.6 s; align start")


def syn_reverse_cymbal():
    rng = np.random.default_rng(2008)
    dur = 1.3
    t = tvec(dur)
    env = np.exp(-(dur - t) / 0.32)                       # a reversed cymbal decay: rises to the end
    fc = 1500 * (14000 / 1500) ** ((t / dur) ** 2)        # opening low-pass: the 'suck' into the hit
    chans = []
    for c in range(2):
        n = highpass(rng.standard_normal(len(t)), 3000, 2)
        metal = sum(0.15 * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi)) for f in (3150, 4270, 5480, 6930, 8220))
        s = norm(n) + metal * norm(n) * 2.0               # ring-modulated partials: crash-cymbal colour
        chans.append(svf(s, fc, "lp", 0.7) * env)
    x = np.stack(chans, axis=1)
    return fade(x, 0.02, 0.005), ("decorrelated L/R high-passed noise ring-modulated by five inharmonic partials "
                                  "(3.15-8.2 kHz) = crash colour, under a reversed exponential decay (tau 320 ms, peak "
                                  "at the end) and a low-pass opening 1.5 -> 14 kHz; 1.3 s; align END on the reveal")


def syn_paper_rip():
    rng = np.random.default_rng(2009)
    dur = 0.55
    t = tvec(dur)
    grains = np.zeros(len(t))
    k = 0.0
    while k < 0.47:
        rate = 600 + 900 * (k / 0.47)                     # tearing speeds up
        k += rng.exponential(1 / rate)
        i = int(k * SR)
        if i < len(t) - 20:
            g = rng.lognormal(0, 0.5) * (2.2 if 0.40 < k < 0.44 else 1.0)   # the final snap
            grains[i:i + 15] += g * rng.standard_normal(15) * np.hanning(15)
    crackle = bandpass(grains, 900, 6000)
    body = norm(bandpass(rng.standard_normal(len(t)), 400, 3000)) * 0.25
    env = np.clip(t / 0.02, 0, 1) * np.clip((dur - t) / 0.08, 0, 1)
    x = (norm(crackle) + body) * env
    return fade(x, 0.002, 0.03), ("dense noise grains (15 samples each, Poisson rate 600 -> 1500/s, a louder snap "
                                  "cluster at 0.40-0.44 s) band-passed 0.9-6 kHz over a band-passed noise body "
                                  "(0.4-3 kHz, -12 dB), 20 ms attack, 80 ms release; 0.55 s; align start")


def syn_flatline_beep():
    t = tvec(1.2)
    x = np.sin(2 * np.pi * 1000 * t) + 0.08 * np.sin(2 * np.pi * 3000 * t)
    return fade(x, 0.008, 0.008), ("monitor flat-line tone: 1 kHz sine + 8% 3rd harmonic, steady, 8 ms attack/release; "
                                   "1.2 s (a cue can shorten it with dur_f)")


def syn_ding():
    rng = np.random.default_rng(2010)
    t = tvec(1.2)
    f0 = 1318.5
    parts = [(1.0, 1.0, 0.9), (2.0, 0.25, 0.5), (2.76, 0.4, 0.35), (5.4, 0.12, 0.15)]
    x = sum(a * np.sin(2 * np.pi * f0 * m * t + rng.uniform(0, 2 * np.pi)) * np.exp(-t / tau) for m, a, tau in parts)
    strike = norm(bandpass(rng.standard_normal(len(t)), 3000, 9000)) * np.exp(-t / 0.002) * 0.3
    x = (x + strike) * (1 - np.exp(-t / 0.0008))
    return fade(x, 0, 0.1), ("small bell: E6 (1318.5 Hz) with bell partials 1/2/2.76/5.4 (decays 0.9/0.5/0.35/0.15 s) "
                             "+ a 2 ms strike noise; 1.2 s; align start")


def syn_click():
    rng = np.random.default_rng(2011)
    t = tvec(0.12)

    def one(t0, f, a):
        u = np.clip(t - t0, 0, None)
        on = (t >= t0).astype(float)
        n = norm(bandpass(rng.standard_normal(len(t)), 2000, 6000)) * np.exp(-u / 0.0015) * on
        r = np.sin(2 * np.pi * f * u) * np.exp(-u / 0.004) * on
        return a * (0.6 * n + 0.4 * r)
    x = one(0.0, 3200, 1.0) + one(0.055, 3600, 0.6)
    return fade(x, 0, 0.01), ("mouse click: press (band-passed 2-6 kHz noise, 1.5 ms + a 3.2 kHz 4 ms ring) and "
                              "release 55 ms later at 60% (3.6 kHz ring); 0.12 s; align start (press on the frame)")


# --------------------------------------------------------------------------------------------
# S-file based sounds
# --------------------------------------------------------------------------------------------
def s13_strokes():
    """Single keystrokes of the S13 typing file: onsets from a 1 ms peak envelope (as the audio build does)."""
    x = decode("S13_v3) Type (A B C ).wav")
    m = np.max(np.abs(x), axis=1)
    w = SR // 1000
    n = len(m) // w
    env = 20 * np.log10(m[: n * w].reshape(n, w).max(axis=1) + 1e-12)
    pk = env.max()
    thr, low = pk - 20, pk - 32
    on, armed = [], True
    for i in range(n):
        if armed and env[i] > thr:
            j = i
            while j > 0 and env[j - 1] > low:
                j -= 1
            on.append(j / 1000)
            armed = False
        elif not armed and env[i] < low and np.all(env[i:i + 20] < low):
            armed = True
    out = []
    for k, o in enumerate(on):
        nxt = on[k + 1] if k + 1 < len(on) else n / 1000
        a, b = o - 0.004, min(o + 0.080, nxt - 0.004)
        out.append(fade(x[int(a * SR): int(b * SR)], 0.001, 0.010))
    return out, on


def place(strokes, times, gains_db, dur):
    y = np.zeros((int(round(dur * SR)), strokes[0].shape[1]))
    for k, (tt, g) in enumerate(zip(times, gains_db)):
        s = strokes[k % len(strokes)] * lin(g)
        i = int(round(tt * SR))
        L = max(0, min(len(s), len(y) - i))
        y[i:i + L] += s[:L]
    return y


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    lib = {}

    def add(name, files_data, recipe, align, peak_db, group, cls, source, notes="", variants=False, match=False):
        """files_data: [(filename, signal)]. Signals are scaled so the (loudest variant's) sample peak = peak_db."""
        sigs = [as2d(s) for _, s in files_data]
        if match and len(sigs) > 1:                        # equal loudness first (variants)
            ref = max_momentary(sigs[0])
            sigs = [s * lin(ref - max_momentary(s)) for s in sigs]
        k = lin(peak_db) / max(float(np.max(np.abs(s))) for s in sigs)
        entries = []
        for (fn, _), s in zip(files_data, sigs):
            y = s * k
            if y.shape[1] == 2 and np.allclose(y[:, 0], y[:, 1]):
                y = y[:, :1]
            sf.write(str(OUT / fn), y.astype(np.float32), SR, subtype="PCM_24")
            back, sr_ = sf.read(str(OUT / fn), always_2d=True)
            a = np.max(np.abs(back), axis=1)
            entries.append({"file": fn, "duration_s": round(len(back) / SR, 4), "channels": back.shape[1],
                            "sample_peak_dbfs": round(db(a.max()), 2), "peak_s": round(int(np.argmax(a)) / SR, 4),
                            "max_momentary_100ms_db": round(max_momentary(back), 2)})
        if name in NOT_USED_V05:
            notes = (notes + " " if notes else "") + NOT_USED_V05[name]
        lib[name] = {"files": [e["file"] for e in entries], "variants": "rotate" if variants else None,
                     "align": align, "default_peak_dbfs": peak_db, "group": group, "class": cls,
                     "dropout_mute": cls in ("riser", "ambience"), "source": source, "recipe": recipe,
                     "notes": notes, "file_info": entries}
        if not variants:
            lib[name]["variants"] = None
        log("  %-16s %-6s %5.1f dBFS  %s" % (name, align, peak_db, ", ".join("%s %.2fs" % (e["file"], e["duration_s"])
                                                                             for e in entries)))

    # ---- caption sounds (A5) ------------------------------------------------------------------------
    ticks = [syn_tick(v) for v in (1, 2, 3)]
    add("tick", [("tick_%d.wav" % (i + 1), s) for i, (s, _) in enumerate(ticks)],
        "synthesized (numpy): " + " | ".join("tick_%d: %s" % (i + 1, r) for i, (_, r) in enumerate(ticks)),
        "start", -24.0, "A5", "pop", "synthesized",
        "Every caption word that is not key/hero (cues.json word_pops). The three variants rotate in edit order, so "
        "two neighbouring words never share a sample. Doc 2.7: 'a soft tick or click at -24 dB'.", True, True)
    s, r = syn_whoosh_in()
    add("whoosh_in", [("whoosh_in.wav", s)], "synthesized (numpy): " + r, "end", -16.0, "A5", "riser", "synthesized",
        "Key/hero words (cues.json key_words): ends on the word's entry frame, the thump starts there. Doc 2.7: "
        "'a short whoosh into it plus a low thump at -14 dB': the thump carries the -14, the whoosh sits 2 dB under it "
        "(broadband noise reads louder than a low thump at the same peak).")
    s, r = syn_thump_low()
    add("thump_low", [("thump_low.wav", s)], "synthesized (numpy): " + r, "start", -14.0, "A5", "hit", "synthesized",
        "Key/hero words (cues.json key_words), on the entry frame.")
    # ---- transitions / sweeps (A4) ----------------------------------------------------------------------
    s, r = syn_swipe()
    add("swipe", [("swipe.wav", s)], "synthesized (numpy): " + r, "peak", -16.0, "A4", "sweep", "synthesized",
        "Hard cuts in the hook (cues.json hook_cuts, B1-B2); the swipe's peak on the cut frame.")
    x = decode("S02_Siren.mp3", "highpass=f=300")
    x = fade(x[int(0.5 * SR): int(1.3 * SR)], 0.010, 6 / FPS)
    add("siren_whoop", [("siren_whoop.wav", x)], "S02_Siren.mp3 (the plan's S02/S14 slice): 48 kHz, high-pass 300 Hz "
        "(FFmpeg, 2-pole), slice 0.5-1.3 s, 10 ms de-click fade-in, 6f fade-out", "start", -14.0, "A4", "hit",
        "03_SFX/S02_Siren.mp3", "Police siren sweep (doc: 0:00 with sub_hit on frame 0, and 0:03.6).")
    x = decode("S10_Flip.wav")
    add("whoosh_flip", [("whoosh_flip.wav", trim_lead(x))], "S10_Flip.wav at 48 kHz, leading silence trimmed (1 ms "
        "pre-roll)", "peak", -12.0, "A4", "sweep", "03_SFX/S10_Flip.wav", "3D flip / spin whoosh; its peak (about "
        "0.36 s in) on the flip's midpoint.")
    x = decode("S15_23 Whip Hit.wav")
    add("whip", [("whip.wav", fade(trim_lead(x)[: int(0.40 * SR)], 0, 0.08))], "S15_23 Whip Hit.wav at 48 kHz, "
        "leading silence trimmed, cut at 0.40 s with an 80 ms fade (only 0.2-0.3 s is audible)", "peak", -12.0, "A4",
        "sweep", "03_SFX/S15_23 Whip Hit.wav", "Whip-zooms; the peak on the whip's midpoint.")
    x = decode("S17_Spinback (2).wav")
    add("rewind", [("rewind.wav", trim_lead(x))], "S17_Spinback (2).wav at 48 kHz (= the plan's S17), leading "
        "silence trimmed", "start", -12.0, "A4", "sweep", "03_SFX/S17_Spinback (2).wav", "Tape rewind / spinback.")
    x = decode("S18_Riser Faster.wav")
    add("riser", [("riser.wav", trim_lead(x, -60))], "S18_Riser Faster.wav at 48 kHz (= the plan's S18), ends at its "
        "peak", "end", -12.0, "A4", "riser", "03_SFX/S18_Riser Faster.wav", "Short riser; its end on the hit frame.")
    s, r = syn_reverse_cymbal()
    add("reverse_cymbal", [("reverse_cymbal.wav", s)], "synthesized (numpy): " + r, "end", -14.0, "A4", "riser",
        "synthesized", "Doc 2.7: 'a reverse-cymbal riser into each big reveal (31.5 s, 53.0 s, 1:15.5)': ends ON its "
        "frame.")
    strokes, onsets = s13_strokes()
    rng = np.random.default_rng(3001)
    times, tt_ = [], 0.0
    while tt_ < 1.85:
        times.append(tt_)
        tt_ += float(rng.uniform(0.055, 0.140)) + (0.18 if rng.random() < 0.12 else 0.0)
    gains = [float(rng.uniform(-4.0, 0.0)) for _ in times]
    order = [int(rng.integers(0, len(strokes))) for _ in times]
    clat = place([strokes[i] for i in order], times, gains, 2.0)
    add("keyboard_clatter", [("keyboard_clatter.wav", fade(clat, 0, 0.15))],
        "%d single keystrokes sliced from S13_v3) Type (A B C ).wav (onsets %s s) re-sequenced over 2.0 s: gaps "
        "55-140 ms (+180 ms pauses 12%% of the time), per-stroke level -4..0 dB, random stroke order (seed 3001), "
        "150 ms fade-out" % (len(strokes), [round(o, 3) for o in onsets]), "start", -20.0, "A4", "ambience",
        "03_SFX/S13_v3) Type (A B C ).wav", "Typing bed under the CRT (doc: 4.5-6.4 s); 2.0 s, shorten with dur_f.")
    # ---- hits / events (A3) -----------------------------------------------------------------------------
    burst = place(strokes, [0.0, 0.068, 0.131, 0.205], [0.0, -2.0, -1.0, -3.0], 0.32)
    add("type_on", [("type_on.wav", fade(burst, 0, 0.03))], "4 keystrokes of S13 (file order) at 0/68/131/205 ms, "
        "0/-2/-1/-3 dB; 0.32 s", "start", -20.0, "A3", "hit", "03_SFX/S13_v3) Type (A B C ).wav",
        "One typed burst (place one per burst of typed text).")
    s, r = syn_click()
    add("click", [("click.wav", s)], "synthesized (numpy): " + r, "start", -20.0, "A3", "pop", "synthesized",
        "UI click (the CTA's 'Follow' button).")
    s, r = syn_sub_hit()
    add("sub_hit", [("sub_hit.wav", s)], "synthesized (numpy): " + r, "start", -8.0, "A3", "hit", "synthesized",
        "Sub-bass hit (doc: frame 0 with the siren whoop).")
    s, r = syn_metal_crunch()
    add("metal_crunch", [("metal_crunch.wav", s)], "synthesized (numpy): " + r, "start", -10.0, "A3", "hit",
        "synthesized", "Doc hook beat 4: 'metal crunch on the flip'.")
    s, r = syn_error_chord()
    add("error_chord", [("error_chord.wav", s)], "synthesized (numpy): " + r, "start", -12.0, "A3", "hit",
        "synthesized", "Doc 2.7: the Windows 95 'critical stop' chord (7.5 s): an ORIGINAL chord in that role. "
        "03_SFX/S03a_Windows Error.wav is the old S03 error sound; it is not used for this name.")
    x = decode("S03b_Glitch, Flicker, Text (14).wav")
    add("glitch_stutter", [("glitch_stutter.wav", trim_lead(x))], "S03b_Glitch, Flicker, Text (14).wav at 48 kHz, "
        "leading silence trimmed", "start", -10.0, "A3", "hit", "03_SFX/S03b_Glitch, Flicker, Text (14).wav",
        "Hard glitch stutter (doc: 8.8 s, 32.0 s).")
    x = decode("S08a_Glitch, Impact.wav")
    add("glitch_impact", [("glitch_impact.wav", trim_lead(x))], "S08a_Glitch, Impact.wav at 48 kHz (= the plan's "
        "S08a, B8's glitch impact)", "start", -8.0, "A3", "hit", "03_SFX/S08a_Glitch, Impact.wav",
        "The X4 glitch impact (the S08a sound).")
    s, r = syn_stamp_thud()
    add("stamp_thud", [("stamp_thud.wav", s)], "synthesized (numpy): " + r, "start", -8.0, "A3", "hit", "synthesized",
        "Rubber stamp landing (doc: 30.4 s).")
    x = decode("S01_Cinematic Hit 1.wav")
    add("impact_boom", [("impact_boom.wav", fade(trim_lead(x)[: int(2.5 * SR)], 0, 20 / FPS))],
        "S01_Cinematic Hit 1.wav at 48 kHz, trimmed to 2.5 s with a 20f fade (its tail fills the 0.4 s logo "
        "silence)", "peak", -6.0, "A3", "hit", "03_SFX/S01_Cinematic Hit 1.wav",
        "Big impact (doc: on 'Grand Theft Auto' 53.5 s, with sub_drop); its peak on the slam frame.")
    x = decode("S09_Sub Drop.mp3")
    add("sub_drop", [("sub_drop.wav", fade(trim_lead(x)[: int(2.5 * SR)], 0, 20 / FPS))],
        "S09_Sub Drop.mp3 decoded by FFmpeg at 48 kHz (encoder delay skipped), trimmed to 2.5 s with a 20f fade "
        "(the plan's S09 trim)", "start", -8.0, "A3", "hit", "03_SFX/S09_Sub Drop.mp3", "Bass drop (doc: 53.5 s).")
    s, r = syn_paper_rip()
    add("paper_rip", [("paper_rip.wav", s)], "synthesized (numpy): " + r, "start", -14.0, "A3", "hit", "synthesized",
        "Calendar page rip (doc: MAR 1995 -> NOV 1997).")
    s, r = syn_flatline_beep()
    add("flatline_beep", [("flatline_beep.wav", s)], "synthesized (numpy): " + r, "start", -20.0, "A3", "tone",
        "synthesized", "Flat-line monitor beep on 'dull.' (doc).")
    s, r = syn_ding()
    add("ding", [("ding.wav", s)], "synthesized (numpy): " + r, "start", -18.0, "A3", "hit", "synthesized",
        "Small ding per phrase (doc B17).")
    hits = []
    for fn in ("S06a_Hit 1.mp3", "S06b_Hit 2.mp3", "S06c_Hit 3.mp3"):
        x = trim_lead(decode(fn))
        hits.append(fade(x[: int(0.8 * SR)], 0, 8 / FPS))
    add("hit", [("hit_%d.wav" % (i + 1), h) for i, h in enumerate(hits)],
        "S06a/S06b/S06c (the plan's stamp hits) decoded by FFmpeg at 48 kHz, leading silence trimmed, cut at 0.8 s with "
        "an 8f fade (the plan's S06 trim), loudness-matched (max 100 ms K-weighted energy)", "peak", -10.0, "A3", "hit",
        "03_SFX/S06a_Hit 1.mp3, S06b_Hit 2.mp3, S06c_Hit 3.mp3",
        "Short hits (doc: 'ram.', 'chase.', 'let go.'); 'hit' rotates hit_1 -> hit_2 -> hit_3 in edit order, "
        "'hit_2' picks one; the peak on the frame.", True, True)

    doc = {
        "_what": "v05 SFX library (REVISION_v05.md G9 + S, client doc 2.7). Lanes name these in "
                 "hyperframes/<composition>/cues.json; tools/build_tesseract_audio.py places them.",
        "made_by": "tools/build_tesseract_sfx_v05.py (deterministic; re-run to rebuild)",
        "format": "48 kHz, 24-bit PCM WAV; mono unless the sound moves in the stereo field (Tesseract plays a mono "
                  "file at full level on both channels)",
        "not_used_v05": sorted(NOT_USED_V05),
        "levels": "Each file is written at its default level: its sample peak = default_peak_dbfs (pre-master; the "
                  "assembly's master gain, about -1 dB, comes on top). The audio build plays a cue at "
                  "default_peak_dbfs, or at the cue's gain_db (an absolute sample-peak level in dBFS, capped at "
                  "-4 dBFS) when the cue gives one. Variant sets are loudness-matched, the loudest at the default.",
        "align": "start = the file's first sound on the cue frame (leading silence trimmed to 1 ms); peak = the "
                 "file's sample peak (peak_s) on the frame; end = the file's last sample at the frame's start.",
        "groups": {"A3": "SFX hits & impacts", "A4": "Risers, whooshes & textures", "A5": "Caption pops & key words"},
        "classes": "pop/hit/tone: never touched by dropouts. sweep: transitions on cuts. riser/ambience "
                   "(dropout_mute true): silenced inside every cues.json `dropouts` window they overlap (2-6 f before a "
                   "big word), like the music bed would be.",
        "sounds": lib,
    }
    (OUT / "library.json").write_text(json.dumps(doc, indent=1) + "\n")
    log("wrote %s (%d names, %d files)" % ((OUT / "library.json").relative_to(ROOT), len(lib),
                                           sum(len(v["files"]) for v in lib.values())))


if __name__ == "__main__":
    build()
