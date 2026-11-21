"""EmsiBuddy-Zeichentrick aus einem Storyboard bauen: Bild (zeichentrick.html) + Ton (sfx.py) -> MP4.
Aufruf: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 zeichentrick.py storyboards/<name>.json out.mp4 [--stills 1,5,9]

Ton im Storyboard: "ton": {"musik": "lofi"|"froh"|"ruhig", "pausen": [[von,bis],...], "beat_ab": s,
                          "effekte": [[zeit, "pop"|"whoosh"|"thud"|"boing"|"scratch"|"tick"|"wahwah"|"glitzer"|"blitz"|"schritte"|"akkord"], ...]}
"""
import json, subprocess, sys, pathlib, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sfx import *

HERE = pathlib.Path(__file__).resolve().parent

def build_audio(story, path):
    D = story["dauer"]; ton = story.get("ton", {}); mx = Mix(D)
    mood = ton.get("musik", "froh"); pausen = ton.get("pausen", []); beat_ab = ton.get("beat_ab", 99)
    B = 60 / {"lofi": 88, "froh": 100, "ruhig": 72}[mood]
    prog = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [53, 57, 60]), (43, [55, 59, 62])]
    def frei(t): return not any(a <= t < b for a, b in pausen)
    bar = 0
    while bar * 4 * B < D:
        root, tri = prog[bar % 4]; t0 = bar * 4 * B
        if frei(t0): mx.put(t0, pad([m + 12 for m in tri], 4 * B + .3, 900 if mood == "ruhig" else 1400), .07)
        if mood != "ruhig":
            if frei(t0): mx.put(t0, bass(root - 12, B * 1.6), .25)
            for k in range(8):
                tt = t0 + k * B / 2
                if tt < D - .3 and frei(tt):
                    mx.put(tt, pluck(tri[[0, 1, 2, 1, 0, 2, 1, 2][k]] + 12, .26), .11, pan=(-.22 if k % 2 else .22))
                    if tt >= beat_ab: mx.put(tt, hat(), .035, pan=.3)
            for k in range(4):
                tt = t0 + k * B
                if tt >= beat_ab and tt < D - .3 and frei(tt):
                    mx.put(tt, kick() if k % 2 == 0 else snap(), .42 if k % 2 == 0 else .13)
        bar += 1
    fx = {"pop": lambda: (pop(84), .15), "whoosh": lambda: (whoosh(.5), .12), "thud": lambda: (thud(), .5),
          "boing": lambda: (boing(67, .55), .14), "scratch": lambda: (scratch(), .3), "blitz": lambda: (hp(rng.standard_normal(int(.06*SR)), 2500) * env(int(.06*SR), .001, .015), .2)}
    for t, name in ton.get("effekte", []):
        if name in fx: x, g = fx[name](); mx.put(t, x, g)
        elif name == "tick":
            for i in range(6): mx.put(t + i * .5, tick() if i % 2 == 0 else tock(), .16, pan=.3 if i % 2 == 0 else -.3)
        elif name == "wahwah":
            for j, m in enumerate((55, 54, 53)): mx.put(t + j * .6, wahwah(m, .55), .13)
            mx.put(t + 1.8, wahwah(52, 1.0, fall=True), .13)
        elif name == "glitzer":
            for j, m in enumerate((72, 76, 79, 84)): mx.put(t + j * .05, bell(m, .3), .07)
        elif name == "schritte":
            for i in range(4): mx.put(t + i * .42, step(), .35)
        elif name == "akkord":
            for j, m in enumerate((60, 64, 67, 72, 76)): mx.put(t + j * .015, bell(m, 1.4), .07)
    mx.write(path, fade_out=1.0, reverb=.22 if mood == "ruhig" else .14)

def main():
    story_path, out = sys.argv[1], sys.argv[2]
    story = json.load(open(story_path)); D = story["dauer"]; fps = 30
    stills = [float(x) for x in sys.argv[sys.argv.index("--stills") + 1].split(",")] if "--stills" in sys.argv else None
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.add_init_script("window.STORY=" + json.dumps(story))
        pg.goto((HERE / "zeichentrick.html").as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
        if stills:
            for t in stills: pg.evaluate(f"render({t})"); pg.screenshot(path=f"{out}-{t}.png")
            b.close(); return
        silent = out + ".video.mp4"
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", silent], stdin=subprocess.PIPE)
        for i in range(int(D * fps)):
            pg.evaluate(f"render({i / fps})"); ff.stdin.write(pg.screenshot(type="jpeg", quality=92))
        ff.stdin.close(); ff.wait(); b.close()
    wav = out + ".wav"; build_audio(story, wav)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", silent, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(silent); os.remove(wav)

if __name__ == "__main__":
    main()
