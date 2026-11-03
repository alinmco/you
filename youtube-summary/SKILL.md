---
name: youtube-summary
description: Preia automat transcrierea (subtitrările) unui clip YouTube și face un sumar structurat. Folosește acest skill de fiecare dată când utilizatorul lipește sau menționează un link YouTube (youtube.com/watch, youtu.be, /shorts/, /live/, m.youtube.com), chiar dacă nu cere explicit un sumar — de ex. „ce zice aici?”, „merită văzut?”, „rezumă-mi”, „tl;dr”, „summarize this video”, sau doar un link simplu. Se aplică și pentru întrebări punctuale despre conținutul unui clip.
---

# YouTube → transcriere → sumar

Utilizatorul vrea să afle rapid ce conține un clip fără să-l urmărească. Un link YouTube lipit singur în conversație înseamnă implicit „fă-mi un sumar”.

## Pasul 1: Preia transcrierea

Rulează scriptul inclus (instalează singur dependențele dacă lipsesc):

```bash
python3 <skill-dir>/scripts/get_transcript.py "<URL>" --timestamps
```

- `--lang ro,en` (implicit) — ordinea limbilor preferate; dacă nu există, ia orice limbă disponibilă.
- `--timestamps` — grupează textul pe blocuri de ~30s cu marcaj `[m:ss]`; folosește-l, ca să poți indica momentele cheie. Fără el iese text continuu (mai compact pentru clipuri foarte lungi).
- Prima linie e un antet: titlu/ID, limba transcrierii, sursa, link scurt.

Pentru mai multe linkuri, rulează scriptul pentru fiecare.

**Dacă eșuează:**
- cod ieșire `2` → clipul nu are subtitrări (nici automate). Spune-i asta utilizatorului direct; nu inventa conținut pe baza titlului.
- cod ieșire `3` → rețeaua blochează YouTube (des întâlnit în containere cloud). Încearcă WebFetch pe pagina clipului pentru titlu/descriere și spune clar că sumarul se bazează doar pe descriere, nu pe transcriere — sau sugerează rularea local.

## Pasul 2: Scrie sumarul

Răspunde în limba utilizatorului (implicit română), indiferent de limba clipului. Transcrierile automate au erori de recunoaștere — corectează tacit nume și termeni evidenți din context, dar nu adăuga informații care nu sunt în clip.

Structura implicită:

```
## <Titlul clipului>
<link> · limba transcrierii: <xx>

**Pe scurt:** 2–3 propoziții cu ideea centrală și concluzia.

**Idei principale**
- [m:ss] idee concretă (cifre, nume, argumente — nu generalități)
- ...  (5–10 puncte, proporțional cu lungimea clipului)

**Concluzii / recomandări practice** (doar dacă clipul are așa ceva)
- ...

**Merită văzut?** o propoziție onestă: pentru cine e util și ce aduce în plus față de sumar.
```

Adaptează după cerere: dacă utilizatorul a pus o întrebare anume („ce spune despre X?”), răspunde întâi la ea, cu marcaje de timp, apoi un sumar scurt. Dacă cere „tl;dr”, dă doar secțiunea „Pe scurt”. Pentru clipuri foarte scurte (shorts), 2–4 rânduri ajung.

Fii fidel sursei: dacă vorbitorul face afirmații discutabile, redă-le ca afirmații ale lui („susține că…”), nu ca fapte.

Nu lipi transcrierea completă în răspuns decât dacă e cerută explicit — e lungă și ascunde sumarul.
