# Werkstatt: EmsiBuddy-Zeichentrick-Videos

Hochkant-Videos (1080×1920, 30 fps) mit Strichfiguren, echter Emsi und eigener Musik. Kein Dreh, keine fremden Samples.

## Bauen

```bash
cd werkstatt
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 zeichentrick.py storyboards/<name>.json ../videos/animiert-<name>.mp4
# Vorschau-Standbilder:  ... zeichentrick.py storyboards/<name>.json /tmp/vorschau --stills 2,6,11
```

Braucht Python mit playwright (Chromium), numpy, scipy, ffmpeg.

## Storyboard (JSON)

- `dauer`: Sekunden (15–30).
- `szenen`: Liste mit `von`, `bis` und beliebig vielen dieser Teile:
  - `texte`: `[{text, oben, groesse?, art?: "titel"|"unter"|"klein", rechts?}]`. `<u>Wort</u>` = Honig-Unterstrich.
  - `figuren`: `[{pose, x, y?, kind?, stimmung?, von_x?, dauer?, dann?, schreck?}]`
    - Posen: `steht`, `geht` (mit `von_x` → `x`), `sofa`, `tisch` (Kopf in Händen), `sitzt` (schreibt), `redet`, `jubelt`, `zuckt`, `handy`
    - Stimmungen: `neutral`, `froh`, `schock`, `traurig`, `genervt`, `verwirrt`
    - `kind: true` = kleinere Figur mit Zopf
  - `kulisse`: `["sofa"|"tisch"|"boden"]`
  - `blase`: `{text, oben, links?, zipfel?, ab?}` Sprechblase
  - `uhr`: `{text, oben}` große Uhrzeit
  - `bilder`: `[{datei, x, oben, breite, ab?, huepf?}]` aus `assets/` (Emsi-Posen, Phasen)
  - `logo: true`, `cta: "…"`, `blitz: Sekunde` (Foto-Blitz)
- `ton`: `{musik: "lofi"|"froh"|"ruhig", pausen: [[von,bis]], beat_ab, effekte: [[zeit, name]]}`
  - Effekte: `pop`, `whoosh`, `thud`, `boing`, `scratch`, `tick`, `wahwah`, `glitzer`, `blitz`, `schritte`, `akkord`

## Regeln

Eltern mit „ihr“ ansprechen. Keine erfundenen Zahlen, keine Heilversprechen, keine echten Kinder.
Das Video oder spätestens die Caption erklärt immer kurz das Prinzip: Euer Kind fotografiert seine echte Hausaufgabe
und erklärt sie Emsi. Wer erklärt, versteht es selbst besser. Emsi wächst durch Wissen.
