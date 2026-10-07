#!/usr/bin/env python3
"""art_essays.py — the ESSAY program's batching for the Connoisseur's Book (D-C571 v2, his A2: "the artist, the date of the
piece, a description of the artist and his life and, a description, interpretation, and critique of the piece").
  make   -> _intake/art/essays/in/works-<nnn>.json (tier B, ~60 works each: the facts + the museum's own text + Wikidata
            depicts / genre / description) and famous-<nnn>.json (tier A: famous works, ~24 each, with a 768 px contact
            copy of the picture for the writer to look at) and artists-<nnn>.json (~50 artists each with their works)
  merge  -> _intake/art/essays.json {key: {d, i, c}} + bios.json {artist_key: bio} from every out/*.json written by the
            writers; reports coverage. Idempotent: re-running `make` skips works / artists already covered.
Usage: art_essays.py make | merge | status"""
import json
import os
import sys
from pathlib import Path

from PIL import Image

ROOT = Path("/home/claude/_intake/art")
CAT = Path(os.environ.get("ART_CAT", str(ROOT / "catalogue.json")))
IN, OUT = ROOT / "essays/in", ROOT / "essays/out"
CONTACT = ROOT / "essays/contact"
ESSAYS, BIOS = ROOT / "essays.json", ROOT / "bios.json"
WORKS_PER, FAMOUS_PER, ARTISTS_PER = 60, 24, 50


def facts(r):
    fr = r.get("frame") or {}
    return {"key": r["key"], "title": r.get("title"), "artist": r.get("artist_display") or r.get("artist"), "artist_key": r.get("artist_key"),
            "nationality": r.get("artist_nat"), "artist_dates": r.get("artist_dates"), "date": r.get("date"), "year": r.get("year"),
            "medium": r.get("medium"), "size_cm": fr.get("cm"), "subject": r.get("subject"), "period": r.get("period"),
            "museum": r["key"].split(":")[0].upper(), "url": r.get("url"), "credit": r.get("credit"),
            "museum_text": r.get("description") or r.get("alt") or None, "did_you_know": r.get("did_you_know"),
            "wikidata_description": r.get("wd_desc"), "depicts": [d for d in (r.get("wd_depicts") or []) if d], "genre": [g for g in (r.get("wd_genre") or []) if g],
            "themes": r.get("themes") or r.get("tags") or [], "sitelinks": r.get("sitelinks", 0), "famous": bool(r.get("famous"))}


def make():
    cat = json.loads(CAT.read_text())
    done = json.loads(ESSAYS.read_text()) if ESSAYS.exists() else {}
    bios = json.loads(BIOS.read_text()) if BIOS.exists() else {}
    IN.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True); CONTACT.mkdir(parents=True, exist_ok=True)
    for f in IN.glob("*.json"):
        f.unlink()
    recs = [r for r in cat.values() if "frame" in r and Path(r["file"]).exists() and r["key"] not in done]
    famous = sorted([r for r in recs if r.get("famous")], key=lambda r: -r.get("sitelinks", 0))
    rest = sorted([r for r in recs if not r.get("famous")], key=lambda r: (r.get("artist_key") or "", r.get("year") or 0))
    nf = nw = 0
    for i in range(0, len(famous), FAMOUS_PER):
        batch = []
        for r in famous[i:i + FAMOUS_PER]:
            c = CONTACT / f"{r['key'].replace(':', '_')}.jpg"
            if not c.exists():
                im = Image.open(r["file"]).convert("RGB"); im.thumbnail((768, 768)); im.save(c, "JPEG", quality=82)
            d = facts(r); d["image"] = str(c)
            batch.append(d)
        (IN / f"famous-{nf:03d}.json").write_text(json.dumps(batch, ensure_ascii=False, indent=1)); nf += 1
    for i in range(0, len(rest), WORKS_PER):
        (IN / f"works-{nw:03d}.json").write_text(json.dumps([facts(r) for r in rest[i:i + WORKS_PER]], ensure_ascii=False, indent=1)); nw += 1
    # artists
    arts = {}
    for r in cat.values():
        if "frame" not in r:
            continue
        a = arts.setdefault(r.get("artist_key") or "anonymous", {"artist_key": r.get("artist_key") or "anonymous", "name": r.get("artist_display") or r.get("artist"),
                                                                 "nationality": r.get("artist_nat"), "dates": r.get("artist_dates"), "works": []})
        if len(a["works"]) < 12:
            a["works"].append(f"{r.get('title')} ({r.get('date') or '?'}; {r['key'].split(':')[0].upper()})")
    todo = sorted([a for k, a in arts.items() if k not in bios and k != "anonymous"], key=lambda a: a["artist_key"])
    na = 0
    for i in range(0, len(todo), ARTISTS_PER):
        (IN / f"artists-{na:03d}.json").write_text(json.dumps(todo[i:i + ARTISTS_PER], ensure_ascii=False, indent=1)); na += 1
    print(f"batches: {nf} famous ({len(famous)} works), {nw} works ({len(rest)}), {na} artists ({len(todo)}); already done {len(done)} essays, {len(bios)} lives")


def merge():
    essays = json.loads(ESSAYS.read_text()) if ESSAYS.exists() else {}
    bios = json.loads(BIOS.read_text()) if BIOS.exists() else {}
    n_e = n_b = 0
    for f in sorted(OUT.glob("*.json")):
        try:
            j = json.loads(f.read_text())
        except Exception as e:
            print("  !", f.name, e); continue
        if f.name.startswith("artists"):
            for k, v in j.items():
                if isinstance(v, str) and len(v) > 40:
                    bios[k] = v.strip(); n_b += 1
        else:
            for k, v in j.items():
                if isinstance(v, dict) and (v.get("d") or v.get("i") or v.get("c")):
                    essays[k] = {q: v[q].strip() for q in ("d", "i", "c", "s") if v.get(q)}; n_e += 1
    ESSAYS.write_text(json.dumps(essays, ensure_ascii=False, indent=0))
    BIOS.write_text(json.dumps(bios, ensure_ascii=False, indent=0))
    cat = json.loads(CAT.read_text())
    n = sum(1 for r in cat.values() if "frame" in r)
    # the writers' subject corrections go back into the catalogue (subject_by = "writer")
    fixed = 0
    for k, v in essays.items():
        s = v.get("s")
        if k in cat and s in ("religious", "portrait", "landscape", "myth_history", "genre", "still_life") and cat[k].get("subject") != s:
            cat[k]["subject"] = s; cat[k]["subject_by"] = "writer"; fixed += 1
    if fixed:
        tmp = CAT.with_suffix(".tmp"); tmp.write_text(json.dumps(cat, indent=0, ensure_ascii=False)); tmp.replace(CAT)
    print(f"merged {n_e} essays + {n_b} lives -> {len(essays)} / {n} works have essays, {len(bios)} lives; {fixed} subjects corrected by the writers")


def status():
    cat = json.loads(CAT.read_text())
    essays = json.loads(ESSAYS.read_text()) if ESSAYS.exists() else {}
    bios = json.loads(BIOS.read_text()) if BIOS.exists() else {}
    n = sum(1 for r in cat.values() if "frame" in r)
    arts = {r.get("artist_key") for r in cat.values() if "frame" in r}
    print(f"{len(essays)} / {n} essays; {len(bios)} / {len(arts)} lives; in: {len(list(IN.glob('*.json')))} batches, out: {len(list(OUT.glob('*.json')))} files")


if __name__ == "__main__":
    {"make": make, "merge": merge, "status": status}[sys.argv[1]]()
