#!/usr/bin/env python3
"""art_harvest.py — THE GALLERY harvest (D-C571 v2, his 22:01: "a few thousand pieces of art ... unique pieces that can be
identified and learned about by the player"). Public-domain paintings, CC0 images, from the three collections the
sandbox can reach: the National Gallery of Art (open-data CSVs -> api.nga.gov IIIF), the Met (Open Access, search v1.1
+ objects v1) and the Cleveland Museum of Art (Open Access API). Images are stored resized (long side <= MAX_PX, JPEG
q90) because the workspace is tight; the pack uses <= 1024 px per work.

Catalogue: _intake/art/catalogue.json — one record per work: key, source, id, artist, artist_sort, title, date, year,
medium, dimensions (text), url, image (source URL), file, px (stored), orig_px, licence, department, tags/themes,
wikidata, highlight (museum flag), plus later passes' fields (subject, sitelinks, selected, essay ...).
Resumable: works already in the catalogue (by key) are skipped; failures are logged and retried next run.
Usage: art_harvest.py [--nga] [--met] [--cma] [--all] [--max-px=1280] [--threads=4] [--limit=N] [--year-max=1900]
Complexity: one metadata lookup + one download per work; a thread pool of --threads downloads."""
import csv
import io
import json
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image

ROOT = Path("/home/claude/_intake/art")
CAT = ROOT / "catalogue.json"
OLD = ROOT / "ledger.json"
MET = "https://collectionapi.metmuseum.org/public/collection/v1"
MET_SEARCH = "https://collectionapi.metmuseum.org/public/collection/v1.1/search"
CMA = "https://openaccess-api.clevelandart.org/api/artworks/"
UA = {"User-Agent": "AbsolutRealism-art-harvest/2.0 (personal use; CC0 / public-domain works only)"}
csv.field_size_limit(1 << 30)
LOCK = threading.Lock()
NOT_THE_MASTER = re.compile(r"^(follower|workshop|attributed|imitator|after|circle|style of|copy after|studio of|possibly|"
                            r"manner of|school of|pupil of|assistant|anonymous|unknown)", re.I)


def arg(name, default):
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), None)
    return default if v is None else type(default)(v)


MAX_PX = arg("max-px", 1280)
THREADS = arg("threads", 4)
LIMIT = arg("limit", 0)
YEAR_MAX = arg("year-max", 1900)
YEAR_MIN = 1200


def get_json(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == tries - 1:
                print("  !", url[:110], e, flush=True)
                return None
            time.sleep(1.5 * (i + 1))


def get_bytes(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=240) as r:
                return r.read()
        except Exception as e:
            if i == tries - 1:
                print("  !", url[:110], e, flush=True)
                return None
            time.sleep(2 * (i + 1))


def store(img_bytes, f):
    """decode, resize to MAX_PX long side, save JPEG q90; returns (stored px, original px) or None"""
    try:
        im = Image.open(io.BytesIO(img_bytes))
        im.load()
    except Exception:
        return None
    orig = list(im.size)
    im = im.convert("RGB")
    if max(im.size) > MAX_PX:
        s = MAX_PX / max(im.size)
        im = im.resize((max(1, round(im.size[0] * s)), max(1, round(im.size[1] * s))), Image.LANCZOS)
    f.parent.mkdir(parents=True, exist_ok=True)
    im.save(f, "JPEG", quality=90, optimize=True)
    return list(im.size), orig


def load_cat():
    if CAT.exists():
        return json.loads(CAT.read_text())
    cat = {}
    if OLD.exists():                                                        # the 241 of the first pass (full-size files)
        for r in json.loads(OLD.read_text()):
            r = dict(r)
            r["orig_px"] = r.get("px")
            cat[r["key"]] = r
    return cat


def save_cat(cat):
    tmp = CAT.with_suffix(".tmp")
    tmp.write_text(json.dumps(cat, indent=0, ensure_ascii=False))
    tmp.replace(CAT)


def year_of(s):
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return int(s)
    m = re.findall(r"\d{4}", str(s))
    return int(m[-1]) if m else None


# ------------------------------------------------------------------------------------------------ NGA
def nga_jobs(cat):
    d = ROOT / "nga"
    objs = [r for r in csv.DictReader(open(d / "objects.csv", encoding="utf-8")) if r["classification"] == "Painting"]
    imgs = {}
    for r in csv.DictReader(open(d / "published_images.csv", encoding="utf-8")):
        if r["viewtype"] == "primary" and r["openaccess"] == "1":
            imgs.setdefault(r["depictstmsobjectid"], r)
    terms = {}
    for r in csv.DictReader(open(d / "objects_terms.csv", encoding="utf-8")):
        if r["termtype"] in ("Theme", "School", "Style", "Keyword"):
            terms.setdefault(r["objectid"], {}).setdefault(r["termtype"], []).append(r["term"])
    jobs = []
    for o in objs:
        oid = o["objectid"]
        k = f"nga:{oid}"
        if k in cat or oid not in imgs:
            continue
        y = year_of(o["endyear"]) or year_of(o["displaydate"])
        if y is None or y < YEAR_MIN or y > YEAR_MAX:
            continue
        if NOT_THE_MASTER.match(o["attribution"] or ""):
            continue
        im = imgs[oid]
        t = terms.get(oid, {})
        rec = {"key": k, "source": "National Gallery of Art, Washington — Open Access (CC0)", "licence": "CC0 1.0", "id": oid,
               "artist": o["attribution"], "artist_sort": o["attributioninverted"], "title": o["title"], "date": o["displaydate"], "year": y,
               "medium": o["medium"], "dimensions": o["dimensions"], "url": f"https://www.nga.gov/artworks/{oid}", "credit": o["creditline"],
               "image": f"{im['iiifurl']}/full/!{MAX_PX},{MAX_PX}/0/default.jpg", "file": str(ROOT / "nga" / f"{oid}.jpg"),
               "orig_px": [int(im["width"] or 0), int(im["height"] or 0)], "wikidata": o["wikidataid"] or None,
               "themes": t.get("Theme", []), "school": t.get("School", []), "style": t.get("Style", []), "keywords": t.get("Keyword", [])[:12],
               "alt": im.get("assistivetext") or None, "department": o["departmentabbr"]}
        jobs.append(rec)
    return jobs


# ------------------------------------------------------------------------------------------------ MET
MET_DEPTS = {11: "European Paintings", 1: "The American Wing"}


def met_ids(dept):
    ids, offset = [], 0
    while True:
        res = get_json(f"{MET_SEARCH}?q=*&departmentId={dept}&hasImages=true&limit=100&offset={offset}")
        got = (res or {}).get("objectIDs") or []
        ids += got
        total = (res or {}).get("total", 0)
        offset += 100
        if not got or offset >= total:
            break
        time.sleep(0.15)
    return ids


def met_record(oid):
    o = get_json(f"{MET}/objects/{oid}")
    if not o or not o.get("isPublicDomain") or not (o.get("primaryImage") or o.get("primaryImageSmall")):
        return None
    if "Paint" not in str(o.get("classification")) and "Paint" not in str(o.get("objectName")):
        return None
    y = o.get("objectEndDate") or year_of(o.get("objectDate"))
    if y is None or y < YEAR_MIN or y > YEAR_MAX:
        return None
    if NOT_THE_MASTER.match(o.get("artistPrefix") or "") or not o.get("artistDisplayName"):
        return None
    return {"key": f"met:{oid}", "source": "The Metropolitan Museum of Art — Open Access (CC0)", "licence": "CC0 1.0", "id": oid,
            "artist": o.get("artistDisplayName"), "artist_sort": o.get("artistAlphaSort"), "artist_bio": o.get("artistDisplayBio"),
            "title": o.get("title"), "date": o.get("objectDate"), "year": int(y), "medium": o.get("medium"), "dimensions": o.get("dimensions"),
            "url": o.get("objectURL"), "credit": o.get("creditLine"), "image": o.get("primaryImageSmall") or o.get("primaryImage"),
            "file": str(ROOT / "met" / f"{oid}.jpg"), "wikidata": (o.get("objectWikidata_URL") or "").rsplit("/", 1)[-1] or None,
            "artist_wikidata": (o.get("artistWikidata_URL") or "").rsplit("/", 1)[-1] or None, "highlight": bool(o.get("isHighlight")),
            "tags": [t.get("term") for t in (o.get("tags") or [])], "department": o.get("department"), "culture": o.get("culture"),
            "period": o.get("period"), "classification": o.get("classification")}


# ------------------------------------------------------------------------------------------------ CMA
CMA_DEPTS = ["European Painting and Sculpture", "American Painting and Sculpture"]


def cma_jobs(cat):
    jobs = []
    for dept in CMA_DEPTS:
        skip = 0
        while True:
            res = get_json(f"{CMA}?department={urllib.parse.quote(dept)}&type=Painting&cc0=1&has_image=1&limit=100&skip={skip}")
            data = (res or {}).get("data", [])
            for a in data:
                k = f"cma:{a['id']}"
                if k in cat or a.get("share_license_status") != "CC0":
                    continue
                creators = a.get("creators") or []
                desc = (creators[0].get("description") or "") if creators else ""
                if not desc or NOT_THE_MASTER.match(desc):
                    continue
                y = a.get("creation_date_latest") or year_of(a.get("creation_date"))
                if y is None or y < YEAR_MIN or y > YEAR_MAX:
                    continue
                imgs = a.get("images") or {}
                url = (imgs.get("print") or imgs.get("web") or {}).get("url")
                if not url:
                    continue
                jobs.append({"key": k, "source": "The Cleveland Museum of Art — Open Access (CC0)", "licence": "CC0 1.0", "id": a["id"],
                             "artist": desc, "artist_sort": desc, "title": a.get("title"), "date": a.get("creation_date"), "year": int(y),
                             "medium": a.get("technique"), "dimensions": a.get("measurements") or "", "url": a.get("url"), "credit": a.get("creditline"),
                             "image": url, "file": str(ROOT / "cma" / f"{a['id']}.jpg"), "highlight": bool(a.get("is_highlight")),
                             "description": a.get("description"), "did_you_know": a.get("did_you_know"), "artlens": a.get("artlens_description"),
                             "culture": a.get("culture"), "department": a.get("department"), "tombstone": a.get("tombstone")})
            skip += 100
            if not data or skip >= (res or {}).get("info", {}).get("total", 0):
                break
            time.sleep(0.15)
    return jobs


# ------------------------------------------------------------------------------------------------ the pool
def download(rec):
    f = Path(rec["file"])
    if f.exists() and f.stat().st_size > 1000:
        try:
            im = Image.open(f); im.load(); rec["px"] = list(im.size)
            return rec
        except Exception:
            pass
    b = get_bytes(rec["image"])
    if not b:
        return None
    r = store(b, f)
    if not r:
        return None
    rec["px"], orig = r
    if not rec.get("orig_px") or not rec["orig_px"][0]:
        rec["orig_px"] = orig
    return rec


def run_jobs(jobs, cat, label):
    done = fail = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        futs = {ex.submit(download, j): j for j in jobs}
        for fu in as_completed(futs):
            rec = fu.result()
            with LOCK:
                if rec:
                    cat[rec["key"]] = rec
                    done += 1
                else:
                    fail += 1
                if (done + fail) % 50 == 0:
                    save_cat(cat)
                    print(f"  {label}: {done} stored, {fail} failed, {len(cat)} in catalogue, {time.time() - t0:.0f} s", flush=True)
    save_cat(cat)
    print(f"{label}: {done} stored, {fail} failed ({time.time() - t0:.0f} s)", flush=True)


def main():
    cat = load_cat()
    want = {a for a in ("--nga", "--met", "--cma") if a in sys.argv} or ({"--nga", "--met", "--cma"} if "--all" in sys.argv else set())
    if not want:
        print(__doc__); return
    if "--nga" in want:
        jobs = nga_jobs(cat)
        if LIMIT: jobs = jobs[:LIMIT]
        print(f"NGA: {len(jobs)} works to fetch", flush=True)
        run_jobs(jobs, cat, "NGA")
    if "--cma" in want:
        jobs = cma_jobs(cat)
        if LIMIT: jobs = jobs[:LIMIT]
        print(f"CMA: {len(jobs)} works to fetch", flush=True)
        run_jobs(jobs, cat, "CMA")
    if "--met" in want:
        for dept in MET_DEPTS:
            ids = [i for i in met_ids(dept) if f"met:{i}" not in cat]
            if LIMIT: ids = ids[:LIMIT]
            print(f"MET {MET_DEPTS[dept]}: {len(ids)} candidate objects (metadata pass)", flush=True)
            jobs = []
            with ThreadPoolExecutor(max_workers=THREADS) as ex:
                for i, rec in enumerate(ex.map(met_record, ids)):
                    if rec:
                        jobs.append(rec)
                    if i % 200 == 199:
                        print(f"  met metadata {i + 1}/{len(ids)}: {len(jobs)} paintings kept", flush=True)
            print(f"MET {MET_DEPTS[dept]}: {len(jobs)} public-domain paintings to fetch", flush=True)
            run_jobs(jobs, cat, f"MET-{dept}")
    print(f"catalogue: {len(cat)} works", flush=True)


if __name__ == "__main__":
    main()
