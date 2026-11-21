"""Kleine Synth-Bibliothek für EmsiBuddy-Videos (Musik + Geräusche, ohne fremde Samples).
Stil wie marketing/brag-output/work/audio.py im App-Repo."""
import numpy as np, wave
from scipy.signal import fftconvolve, butter, lfilter

SR = 48000
rng = np.random.default_rng(7)

def note(n): return 440 * 2 ** ((n - 69) / 12)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(t / a, 1) * np.exp(-np.maximum(t - a, 0) / d)
def lp(x, f): b, a = butter(2, f / (SR / 2)); return lfilter(b, a, x)
def hp(x, f): b, a = butter(2, f / (SR / 2), 'high'); return lfilter(b, a, x)

class Mix:
    def __init__(self, dur):
        self.dur = dur; self.N = int(SR * (dur + 1)); self.buf = np.zeros((2, self.N))
    def put(self, t, x, g=1.0, pan=0.0):
        i = int(t * SR)
        if i >= self.N or i < 0: return
        x = x[:self.N - i]; l = g * np.sqrt(.5 * (1 - pan)); r = g * np.sqrt(.5 * (1 + pan))
        self.buf[0, i:i + len(x)] += x * l; self.buf[1, i:i + len(x)] += x * r
    def write(self, path, fade_out=1.2, reverb=.14):
        mix = self.buf
        ir = rng.standard_normal((2, int(1.0 * SR))) * np.exp(-np.arange(int(1.0 * SR)) / SR / .25)
        ir = np.stack([lp(ir[0], 4500), lp(ir[1], 4500)])
        wet = np.stack([fftconvolve(mix[c], ir[c])[:self.N] for c in range(2)]); wet /= np.abs(wet).max() + 1e-9
        out = mix + reverb * np.abs(mix).max() * wet
        t = np.arange(self.N) / SR; fade = np.ones(self.N)
        m = t > self.dur - fade_out; fade[m] = np.clip((self.dur - t[m]) / fade_out, 0, 1) ** 1.5
        out = np.tanh(out * 1.4 / (np.abs(out).max() + 1e-9)) * fade
        out = out / (np.abs(out).max() + 1e-9) * .89
        out = out[:, :int(self.dur * SR)]
        pcm = (out.T * 32767).astype('<i2')
        with wave.open(path, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

# --- Instrumente
def kick():
    n = int(.28 * SR); t = np.arange(n) / SR; f = 45 + 85 * np.exp(-t / .03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .09)
def snap():
    n = int(.12 * SR); return hp(lp(rng.standard_normal(n), 5200), 1400) * env(n, .001, .03)
def hat():
    n = int(.05 * SR); return hp(rng.standard_normal(n), 7500) * env(n, .001, .012)
def pluck(m, d=.32):
    n = int(1.0 * SR); t = np.arange(n) / SR; f = note(m)
    return (np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*2*f*t)*np.exp(-t/.08) + .18*np.sin(2*np.pi*4*f*t)*np.exp(-t/.03)) * env(n, .003, d)
def bell(m, d=.5):
    n = int(1.6 * SR); t = np.arange(n) / SR; f = note(m)
    return np.sin(2*np.pi*f*t + 1.2*np.sin(2*np.pi*3.01*f*t)*np.exp(-t/.12)) * env(n, .002, d)
def bass(m, l):
    n = int(l * SR); t = np.arange(n) / SR; f = note(m)
    return lp(np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*2*f*t), 600) * np.minimum(t/.01, 1) * np.exp(-t/(l*.7))
def pad(ms, l, cut=1400):
    n = int(l * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for m in ms:
        for det in (-.06, .05): x += np.sin(2*np.pi*note(m+det)*t + rng.uniform(0, 6))
    a = np.minimum(t/.5, 1) * np.minimum((l-t)/.5, 1); return lp(x, cut) * a / len(ms)

# --- Geräusche
def pop(m=79):
    n = int(.09 * SR); t = np.arange(n) / SR; f = note(m) * (1 + .5*np.exp(-t/.012))
    return np.sin(2*np.pi*np.cumsum(f)/SR) * env(n, .002, .025)
def whoosh(l, up=True):
    n = int(l * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); k = 8
    for j in range(k):
        s = slice(j*n//k, (j+1)*n//k); fr = (j+1)/k if up else 1-j/k
        out[s] = lp(x, 500 + 3000*fr)[s]
    shape = (t/l)**2 if up else (1 - t/l)**2
    return out * shape
def step():
    n = int(.08 * SR); return lp(rng.standard_normal(n), 400) * env(n, .002, .02) + .5*kick()[:n]*.3
def thud():
    n = int(.35 * SR); t = np.arange(n) / SR
    return lp(rng.standard_normal(n), 250) * env(n, .004, .08) + np.sin(2*np.pi*70*t)*np.exp(-t/.08)
def boing(m=60, l=.5):
    n = int(l * SR); t = np.arange(n) / SR; f = note(m) * (1 + .9*np.sin(2*np.pi*7*t)*np.exp(-t/.15)) * (1 + t*1.5)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * env(n, .003, .18)
def scratch(l=.45):
    n = int(l * SR); t = np.arange(n) / SR
    f = 900 * np.exp(-t/.12) + 120
    saw = 2*((np.cumsum(f)/SR) % 1) - 1
    return hp(saw + .4*rng.standard_normal(n), 300) * env(n, .002, .12)
def tick(m=88): return bell(m, .05)[:int(.12*SR)]
def tock(m=81): return bell(m, .05)[:int(.12*SR)]
def wahwah(m, l=.55, fall=False):
    n = int(l * SR); t = np.arange(n) / SR; f = note(m) * (1 - (.06*t/l if fall else 0*t))
    ph = np.cumsum(f) / SR; saw = sum(np.sin(2*np.pi*k*ph)/k for k in range(1, 7))
    wah = .5 + .5*np.sin(2*np.pi*2.2*t - np.pi/2)
    return lp(saw, 900) * (.5 + .5*wah) * np.minimum(t/.03, 1) * np.minimum((l-t)/.08, 1)
def breath(l=3.0, inhale=True):
    n = int(l * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    sh = np.sin(np.pi * t / l) ** 2
    return lp(hp(x, 300), 1800 if inhale else 1200) * sh
