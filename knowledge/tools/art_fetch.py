#!/usr/bin/env python3
"""art_fetch.py — the ART program's fetcher (D-C571, his 21:30): public-domain paintings for the palace.
Sources (all CC0 / public-domain images, reachable through the sandbox proxy as tested 21:36-21:40 CT 10-04):
  NGA  National Gallery of Art open data (objects.csv + published_images.csv, CC0) -> api.nga.gov IIIF (openaccess=1 only)
  MET  The Met Open Access, search v1.1 (v1 search was retired 2026-10-01) + objects v1; isPublicDomain only
  CMA  Cleveland Museum of Art Open Access API (cc0=1, has_image=1, type=Painting) -> openaccess-cdn print images
  (AIC dropped: www.artic.edu/iiif sits behind a Cloudflare challenge -> 403 for us; Wikimedia 400; Rijksmuseum 410.)
Every file is recorded in _intake/art/ledger.json (source, id, artist, title, date, medium, dimensions, licence, URL,
local file, pixel size) — the provenance ledger line of the standing law. Nothing here is restricted (CC0 / PD).
Usage: art_fetch.py [--per-artist=N] [--total=N] [--only="Name,Name"] [--max-px=2048]
Output: _intake/art/{nga,met,cma}/<id>.jpg (long side <= max-px as served), ledger + thumbnail sheet
(_docs/palace/ART-SHEET-<n>.png) for his review. Complexity: one API/CSV lookup per candidate + one download per kept work."""
import csv
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/home/claude/_intake/art")
LEDGER = ROOT / "ledger.json"
MET = "https://collectionapi.metmuseum.org/public/collection/v1"
MET_SEARCH = "https://collectionapi.metmuseum.org/public/collection/v1.1/search"
CMA = "https://openaccess-api.clevelandart.org/api/artworks/"
UA = {"User-Agent": "AbsolutRealism-art-fetch/1.1 (personal use; CC0 / public-domain works only)"}
csv.field_size_limit(1 << 30)

# the curated list: Renaissance -> Baroque -> Rococo / Neoclassical ("classical" read as the classical tradition — A3).
# (name as the museums index it, surname key used to confirm the artist in fuzzy search results)
ARTISTS = [
    ("Leonardo da Vinci", "leonardo"), ("Sandro Botticelli", "botticelli"), ("Raphael", "raphael"), ("Titian", "titian"),
    ("Giovanni Bellini", "bellini"), ("Fra Angelico", "angelico"), ("Fra Filippo Lippi", "lippi"), ("Pietro Perugino", "perugino"),
    ("Carlo Crivelli", "crivelli"), ("Lorenzo Lotto", "lotto"), ("Tintoretto", "tintoretto"), ("Paolo Veronese", "veronese"),
    ("Bronzino", "bronzino"), ("Andrea del Sarto", "sarto"), ("Giovanni di Paolo", "giovanni di paolo"), ("Giorgione", "giorgione"),
    ("Domenico Ghirlandaio", "ghirlandaio"), ("Benozzo Gozzoli", "gozzoli"), ("Cima da Conegliano", "cima"),
    ("Pieter Bruegel the Elder", "bruegel"), ("Lucas Cranach the Elder", "cranach"), ("Hans Holbein the Younger", "holbein"),
    ("Hans Memling", "memling"), ("Gerard David", "gerard david"), ("Joachim Patinir", "patinir"), ("Petrus Christus", "christus"),
    ("Rogier van der Weyden", "weyden"), ("Jan van Eyck", "eyck"), ("Albrecht Dürer", "dürer"), ("Quentin Massys", "massys"),
    ("El Greco", "greco"), ("Caravaggio", "caravaggio"), ("Rembrandt", "rembrandt"), ("Johannes Vermeer", "vermeer"),
    ("Peter Paul Rubens", "rubens"), ("Anthony van Dyck", "dyck"), ("Velázquez", "velázquez"), ("Murillo", "murillo"),
    ("Zurbarán", "zurbarán"), ("Claude Lorrain", "claude lorrain"), ("Nicolas Poussin", "poussin"), ("Canaletto", "canaletto"),
    ("Francesco Guardi", "guardi"), ("Giovanni Battista Tiepolo", "tiepolo"), ("Georges de La Tour", "la tour"),
    ("Frans Hals", "frans hals"), ("Jacob van Ruisdael", "ruisdael"), ("Meindert Hobbema", "hobbema"), ("Aelbert Cuyp", "cuyp"),
    ("Jan Steen", "steen"), ("Pieter de Hooch", "hooch"), ("Gerard ter Borch", "borch"), ("Jan van Goyen", "goyen"),
    ("Salomon van Ruysdael", "ruysdael"), ("Philips Wouwerman", "wouwerman"), ("Willem Claesz Heda", "heda"),
    ("Jan Davidsz de Heem", "heem"), ("Rachel Ruysch", "ruysch"), ("Ambrosius Bosschaert", "bosschaert"),
    ("Jan Brueghel the Elder", "brueghel"), ("Adriaen van Ostade", "ostade"), ("Nicolaes Maes", "maes"), ("Jan Lievens", "lievens"),
    ("Guido Reni", "reni"), ("Annibale Carracci", "carracci"), ("Domenichino", "domenichino"), ("Guercino", "guercino"),
    ("Orazio Gentileschi", "gentileschi"), ("Luca Giordano", "giordano"), ("Sebastiano Ricci", "ricci"), ("Bernardo Strozzi", "strozzi"),
    ("Jean-Baptiste-Siméon Chardin", "chardin"), ("Jean Honoré Fragonard", "fragonard"), ("Antoine Watteau", "watteau"),
    ("François Boucher", "boucher"), ("Jacques-Louis David", "jacques-louis david"), ("Jean-Auguste-Dominique Ingres", "ingres"),
    ("Thomas Gainsborough", "gainsborough"), ("Joshua Reynolds", "reynolds"), ("George Stubbs", "stubbs"),
    ("Joseph Wright of Derby", "wright"), ("Bernardo Bellotto", "bellotto"), ("Hubert Robert", "hubert robert"),
    ("Claude-Joseph Vernet", "vernet"), ("Jean-Baptiste Greuze", "greuze"), ("Élisabeth Louise Vigée Le Brun", "vigée"),
    ("Thomas Lawrence", "lawrence"), ("Henry Raeburn", "raeburn"), ("George Romney", "romney"), ("Richard Wilson", "richard wilson"),
    ("Pompeo Batoni", "batoni"), ("Angelica Kauffman", "kauffman"), ("Anton Raphael Mengs", "mengs"),
]
NOT_THE_MASTER = re.compile(r"^(follower|workshop|attributed|imitator|after|circle|style of|copy after|studio of|possibly|"
                            r"manner of|school of|pupil of|assistant)", re.I)


def get_json(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == tries - 1:
                print("  !", url[:100], e)
                return None
            time.sleep(1.5 * (i + 1))


def get_bytes(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                return r.read()
        except Exception as e:
            if i == tries - 1:
                print("  !", url[:100], e)
                return None
            time.sleep(2 * (i + 1))


def load_ledger():
    return json.loads(LEDGER.read_text()) if LEDGER.exists() else []


def save_ledger(L):
    LEDGER.write_text(json.dumps(L, indent=1, ensure_ascii=False))


def keep(img, f):
    """decode-check, write, return pixel size (None if not an image)"""
    try:
        im = Image.open(io.BytesIO(img)); im.load()
    except Exception:
        return None
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(img)
    return list(im.size)


# ---------------------------------------------------------------- NGA (local CSV index -> IIIF)
_NGA = {}


def nga_index():
    if _NGA:
        return _NGA
    d = ROOT / "nga"
    objs = [r for r in csv.DictReader(open(d / "objects.csv", encoding="utf-8")) if r["classification"] == "Painting"]
    imgs = {}
    for r in csv.DictReader(open(d / "published_images.csv", encoding="utf-8")):
        if r["viewtype"] == "primary" and r["openaccess"] == "1":
            imgs.setdefault(r["depictstmsobjectid"], r)
    _NGA["objs"], _NGA["imgs"] = objs, imgs
    print(f"NGA index: {len(objs)} paintings, {len(imgs)} open-access primary images")
    return _NGA


def fetch_nga(artist, key, max_per, have, max_px):
    ix = nga_index()
    kept = []
    cands = [o for o in ix["objs"] if key in (o["attribution"] or "").lower() and not NOT_THE_MASTER.match(o["attribution"] or "")]
    cands.sort(key=lambda o: -(len(o["dimensions"] or "")))                 # a crude "bigger first" (dimension strings)
    for o in cands:
        if len(kept) >= max_per:
            break
        k = f"nga:{o['objectid']}"
        if k in have or o["objectid"] not in ix["imgs"]:
            continue
        im = ix["imgs"][o["objectid"]]
        url = f"{im['iiifurl']}/full/!{max_px},{max_px}/0/default.jpg"
        img = get_bytes(url)
        if not img:
            continue
        px = keep(img, ROOT / "nga" / f"{o['objectid']}.jpg")
        if not px:
            continue
        kept.append({"key": k, "source": "National Gallery of Art, Washington — Open Access (CC0)", "licence": "CC0 1.0",
                     "id": o["objectid"], "artist": o["attribution"], "title": o["title"], "date": o["displaydate"], "medium": o["medium"],
                     "dimensions": o["dimensions"], "url": f"https://www.nga.gov/collection/art-object-page.{o['objectid']}.html",
                     "image": url, "file": str(ROOT / "nga" / f"{o['objectid']}.jpg"), "px": px, "year": o["endyear"]})
        print(f"  nga {o['objectid']}: {o['attribution']} — {o['title'][:48]} ({o['displaydate']}) {px[0]}x{px[1]}")
        time.sleep(0.3)
    return kept


# ---------------------------------------------------------------- MET (search v1.1 -> objects v1)
def fetch_met(artist, key, max_per, have, max_px):
    q = urllib.parse.quote(artist)
    res = get_json(f"{MET_SEARCH}?q={q}&artistOrCulture=true&hasImages=true&departmentId=11&limit=40")
    ids = (res or {}).get("objectIDs") or []
    kept = []
    for oid in ids:
        if len(kept) >= max_per:
            break
        if f"met:{oid}" in have:
            continue
        o = get_json(f"{MET}/objects/{oid}")
        if not o or not o.get("isPublicDomain") or not (o.get("primaryImage") or o.get("primaryImageSmall")):
            continue
        if "Paint" not in str(o.get("classification")):
            continue
        name = (o.get("artistDisplayName") or "").lower()
        if key not in name or NOT_THE_MASTER.match(o.get("artistPrefix") or ""):
            continue                                                      # the search is fuzzy; keep the master's own works
        url = o.get("primaryImageSmall") or o.get("primaryImage")         # web-large (~1500 px long side) is enough for 1024 textures
        img = get_bytes(url)
        if not img:
            continue
        px = keep(img, ROOT / "met" / f"{oid}.jpg")
        if not px:
            continue
        if max(px) < 900 and o.get("primaryImage") and url != o["primaryImage"]:
            img2 = get_bytes(o["primaryImage"])
            if img2:
                px2 = keep(img2, ROOT / "met" / f"{oid}.jpg")
                px = px2 or px
        kept.append({"key": f"met:{oid}", "source": "The Metropolitan Museum of Art — Open Access (CC0)", "licence": "CC0 1.0",
                     "id": oid, "artist": o.get("artistDisplayName"), "title": o.get("title"), "date": o.get("objectDate"),
                     "medium": o.get("medium"), "dimensions": o.get("dimensions"), "url": o.get("objectURL"), "image": url,
                     "file": str(ROOT / "met" / f"{oid}.jpg"), "px": px, "year": o.get("objectEndDate"),
                     "tags": [t.get("term") for t in (o.get("tags") or [])]})
        print(f"  met {oid}: {o.get('artistDisplayName')} — {str(o.get('title'))[:48]} ({o.get('objectDate')}) {px[0]}x{px[1]}")
        time.sleep(0.3)
    return kept


# ---------------------------------------------------------------- CMA (open access API -> CDN print image)
def fetch_cma(artist, key, max_per, have, max_px):
    q = urllib.parse.quote(artist)
    res = get_json(f"{CMA}?artists={q}&cc0=1&has_image=1&type=Painting&limit=20")
    kept = []
    for a in (res or {}).get("data", []):
        if len(kept) >= max_per:
            break
        k = f"cma:{a['id']}"
        if k in have:
            continue
        creators = a.get("creators") or []
        desc = (creators[0].get("description") or "") if creators else ""
        role = (creators[0].get("role") or "") if creators else ""
        if key not in desc.lower() or NOT_THE_MASTER.match(desc) or (role and role.lower() != "artist"):
            continue
        if a.get("share_license_status") != "CC0":
            continue
        imgs = a.get("images") or {}
        url = (imgs.get("print") or imgs.get("web") or {}).get("url")
        if not url:
            continue
        img = get_bytes(url)
        if not img:
            continue
        px = keep(img, ROOT / "cma" / f"{a['id']}.jpg")
        if not px:
            continue
        kept.append({"key": k, "source": "The Cleveland Museum of Art — Open Access (CC0)", "licence": "CC0 1.0", "id": a["id"],
                     "artist": desc, "title": a.get("title"), "date": a.get("creation_date"), "medium": a.get("technique"),
                     "dimensions": (a.get("measurements") or ""), "url": a.get("url"), "image": url,
                     "file": str(ROOT / "cma" / f"{a['id']}.jpg"), "px": px, "year": a.get("creation_date_latest")})
        print(f"  cma {a['id']}: {desc[:40]} — {str(a.get('title'))[:48]} ({a.get('creation_date')}) {px[0]}x{px[1]}")
        time.sleep(0.3)
    return kept


def sheet(L, per_row=10, cell=160):
    rows = (len(L) + per_row - 1) // per_row
    img = Image.new("RGB", (per_row * cell, rows * (cell + 30) + 10), (30, 30, 34))
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    for i, r in enumerate(L):
        try:
            im = Image.open(r["file"]).convert("RGB")
            im.thumbnail((cell - 10, cell - 10))
        except Exception:
            continue
        x, y = (i % per_row) * cell + 5, (i // per_row) * (cell + 30) + 5
        img.paste(im, (x + (cell - 10 - im.width) // 2, y + (cell - 10 - im.height) // 2))
        d.text((x, y + cell - 8), f"{i}: {(r['artist'] or '')[:24]}", fill=(230, 230, 230), font=font)
        d.text((x, y + cell + 4), (r["title"] or "")[:26], fill=(180, 180, 190), font=font)
    out = Path("/home/claude/_docs/palace") / f"ART-SHEET-{len(L)}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    return out


def main():
    per = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--per-artist=")), "4"))
    total = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--total=")), "200"))
    max_px = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--max-px=")), "2048"))
    only = next((a.split("=", 1)[1].split(",") for a in sys.argv if a.startswith("--only=")), None)
    L = load_ledger()
    have = {r["key"] for r in L}
    artists = [a for a in ARTISTS if not only or a[0] in only]
    for artist, key in artists:
        if len(L) >= total:
            break
        print(artist, flush=True)
        got = fetch_nga(artist, key, per, have, max_px)
        if len(got) < per:
            got += fetch_met(artist, key, per - len(got), have, max_px)
        if len(got) < per:
            got += fetch_cma(artist, key, per - len(got), have, max_px)
        L.extend(got)
        have.update(r["key"] for r in got)
        save_ledger(L)
    print(f"ledger: {len(L)} works; sheet {sheet(L)}", flush=True)


if __name__ == "__main__":
    main()
