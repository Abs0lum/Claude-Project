#!/usr/bin/env python3
"""art_catalogue.py — the GALLERY catalogue pass over _intake/art/catalogue.json (after art_harvest.py):
  1. Wikidata enrichment (cached): sitelinks (fame), genre (P136) labels, main subject (P921) labels, English description.
  2. SUBJECT (his A2 equal shares): religious · portrait · landscape · myth_history · genre · still_life — from the Wikidata
     genre first, then the NGA themes, then the Met tags, then title rules (a visible 'subject_by' says which decided).
  3. FRAME CLASS: the real size (cm, from the dimensions text) -> blocks (long side = round(cm / 70), 1..6) and the class
     (w x h blocks) nearest the picture's aspect; the texture size per class (256 px / block up to 4, 1024 px max).
  4. ARTIST: a normalised key + display name + nationality/dates (NGA constituents, Met artistDisplayBio, CMA text).
  5. PERIOD + palace eligibility (A4: the palace hangs pre-1800 work), FAME tier (sitelinks >= 6 or a museum highlight).
Writes the fields back into the catalogue and _docs/palace/GALLERY-CENSUS.md (counts by subject / period / source / class).
Usage: art_catalogue.py [--no-wikidata] [--threads=4]
Complexity: one cached HTTP lookup per Wikidata id; O(n) over the catalogue otherwise."""
import csv
import json
import os
import math
import re
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path("/home/claude/_intake/art")
CAT = Path(os.environ.get("ART_CAT", str(ROOT / "catalogue.json")))
WD = ROOT / "wikidata_cache.json"
UA = {"User-Agent": "AbsolutRealism-art-catalogue/1.0 (personal use)"}
csv.field_size_limit(1 << 30)
LOCK = threading.Lock()
SUBJECTS = ["religious", "portrait", "landscape", "myth_history", "genre", "still_life"]

# ---------------------------------------------------------------- vocabularies
GENRE_MAP = [  # (substring of the Wikidata genre / subject label, subject)
    ("religious", "religious"), ("sacred", "religious"), ("christian", "religious"), ("altarpiece", "religious"), ("devotional", "religious"),
    ("icon", "religious"), ("biblical", "religious"), ("madonna", "religious"), ("crucifixion", "religious"), ("annunciation", "religious"),
    ("nativity", "religious"), ("adoration", "religious"), ("saint", "religious"), ("pietà", "religious"), ("lamentation", "religious"),
    ("self-portrait", "portrait"), ("portrait", "portrait"), ("tronie", "portrait"),
    ("landscape", "landscape"), ("cityscape", "landscape"), ("veduta", "landscape"), ("marine", "landscape"), ("seascape", "landscape"),
    ("townscape", "landscape"), ("topograph", "landscape"), ("architectural painting", "landscape"), ("capriccio", "landscape"), ("riverscape", "landscape"),
    ("history painting", "myth_history"), ("mytholog", "myth_history"), ("allegor", "myth_history"), ("literary", "myth_history"),
    ("battle", "myth_history"), ("nude", "myth_history"), ("classical antiquity", "myth_history"), ("orientalis", "genre"),
    ("genre", "genre"), ("conversation piece", "genre"), ("interior", "genre"), ("everyday", "genre"), ("peasant", "genre"),
    ("still life", "still_life"), ("still-life", "still_life"), ("animal", "still_life"), ("flower", "still_life"), ("hunting", "still_life"),
    ("vanitas", "still_life"), ("fruit", "still_life"), ("game piece", "still_life"), ("equestrian", "still_life"), ("bird", "still_life"),
]
NGA_THEME = {
    "religious": ["saints", "Life of Christ", "Life of the Virgin", "Old Testament", "New Testament", "religious", "Madonna", "Christian", "angels", "biblical", "devotional", "Apocrypha", "Passion"],
    "portrait": ["portrait", "self", "bust facing right", "bust facing left", "group portrait"],
    "landscape": ["landscape", "cityscape", "topographical", "marine", "seascape", "harbor", "river", "ruins", "architecture", "coast"],
    "myth_history": ["classical", "mythology", "history", "allegory", "literature", "fantasy", "nude", "military"],
    "genre": ["daily life", "amusement", "occupation", "social criticism", "music", "family", "peasant", "child", "interior", "games"],
    "still_life": ["still life", "animal", "plant", "botanical", "bird", "mammal", "flower", "fish", "insect", "fruit", "hunting"],
}
MET_TAG = {
    "religious": ["Christ", "Jesus", "Madonna and Child", "Virgin Mary", "Saints", "Angels", "Crucifixion", "Bible", "Nativity", "Annunciation", "Adoration of the Magi", "Holy Family", "Apostles", "Prophets", "Pietà", "Lamentation", "Saint Jerome", "Saint John the Baptist", "Resurrection", "Last Supper", "Baptism", "Mary Magdalene", "Moses", "David", "Adam", "Eve", "Old Testament", "Religion"],
    "portrait": ["Portraits", "Self-portraits", "Men", "Women", "Boys", "Girls", "Profiles"],
    "landscape": ["Landscapes", "Rivers", "Seascapes", "Boats", "Cityscapes", "Ruins", "Harbors", "Mountains", "Trees", "Lakes", "Waterfalls", "Ships", "Beaches", "Sunsets", "Snow", "Bridges", "Canals", "Towns", "Villages", "Piazzas", "Roads", "Forests", "Storms", "Winter", "Streets", "Clouds", "Moon"],
    "myth_history": ["Venus", "Cupid", "Apollo", "Diana", "Jupiter", "Juno", "Mars", "Mercury", "Bacchus", "Hercules", "Minerva", "Psyche", "Ceres", "Flora", "Nymphs", "Satyrs", "Muses", "Allegory", "Mythology", "Battles", "Soldiers", "Kings", "Emperors", "Roman", "Greek", "Trojan War", "Nudes", "Aeneas", "Ulysses", "Orpheus", "Mythical Creatures", "Classical Mythology", "History", "Lucretia", "Cleopatra", "Napoleon", "Antiquity"],
    "genre": ["Interiors", "Music", "Drinking", "Children", "Peasants", "Markets", "Games", "Smoking", "Reading", "Letters", "Kitchens", "Taverns", "Dancing", "Musicians", "Dogs", "Servants", "Lovers", "Eating", "Cooking", "Sewing", "Working", "Fishing", "Cards", "Fairs", "Parties", "Feasts", "Courtship", "Mothers", "Domestic", "Sleeping", "Playing", "Dancers", "Beggars", "Shepherds", "Farms", "Hunting"],
    "still_life": ["Still Life", "Flowers", "Fruit", "Horses", "Birds", "Animals", "Dead Animals", "Cats", "Cattle", "Sheep", "Fish", "Vegetables", "Insects", "Lions", "Vases", "Books", "Musical Instruments", "Skulls", "Game"],
}
TITLE_RULES = [
    ("religious", r"\b(madonna|virgin|christ|jesus|saint\b|st\.|sts\.|holy|annunciation|crucifixion|adoration|nativity|baptism|magdalen|apostle|angel|lamentation|piet[aà]|flight into egypt|rest on the flight|agony|deposition|resurrection|assumption|last judg|moses|judith|susanna|tobias|prodigal|supper|ecce homo|noli me|prophet|baptist|jerome|francis|sebastian|catherine|lucy|peter and|paul\b|magi|shepherds|temple|martyr|trinity|crucifix|altarpiece|evangelist|visitation|presentation|calvary|golgotha|entombment|descent from the cross|salvator|ascension|pentecost|sacrifice of isaac|abraham|jacob|joseph and|david and|samson|delilah|bathsheba|esther|lot and|cain|abel|noah|tower of babel|good samaritan|nicodemus|lazarus|thomas|elijah|elisha|daniel|job\b|isaiah|jonah|tobit|sibyl)\b"),
    ("myth_history", r"\b(venus|cupid|apollo|diana|jupiter|juno|mars\b|mercury|bacchus|bacchante|hercules|minerva|psyche|ceres|flora|nymph|satyr|muse|allegory|triumph of|judgment of paris|rape of|abduction|aeneas|dido|ulysses|odysseus|achilles|troy|trojan|lucretia|cleopatra|alexander|caesar|scipio|socrates|dana[eë]|europa|leda|andromeda|perseus|orpheus|actaeon|adonis|mytholog|battle|siege|death of|oath|sabine|rinaldo|armida|tancred|erminia|orlando|angelica|medoro|fortune|the ages|the seasons|the elements|peace and war|justice|prudence|charity|faith\b|genius|the arts|arcadia|pan\b|galatea|narcissus|endymion|selene|aurora|neptune|amphitrite|vulcan|pluto|proserpin|atalanta|meleager|niobe|medea|jason|argonaut|ariadne|theseus|midas|pygmalion|prometheus|icarus|phaeton|daphne|io\b|callisto|antiope|vertumnus|pomona|zephyr|chloris|graces|parnassus|olympus|titan|giants|roman|greek|antique|classical|emperor|consul|senator|coriolanus|cincinnatus|regulus|horatii|brutus|belisarius|hannibal|cato|seneca|virgil|homer|dante|petrarch|boccaccio|tasso|ariosto|cervantes|don quixote|shakespeare|hamlet|ophelia|macbeth|lear|napoleon|bonaparte|washington crossing|the surrender|declaration)\b"),
    ("still_life", r"\b(still life|flowers|fruit|bouquet|vase of|breakfast|banquet piece|vanitas|game piece|dead game|dead birds|hunting trophies|fish\b|oysters|lemons|grapes|melon|peaches|apples|a horse|horses|stallion|mare\b|a dog|dogs|poodle|spaniel|hound|cattle|cows|cow\b|bull\b|sheep|goats|lion|tiger|leopard|monkey|birds|parrot|hare|rabbit|deer|stag|poultry|hen|rooster|cock\b|swan|peacock|kitchen still|dessert|cheese|bread and|wine glass|roemer|nautilus|shells|insects|butterfl)\b"),
    ("landscape", r"\b(landscape|view of|view from|view near|view on|veduta|river|harbor|harbour|coast|seascape|marine|shipping|ships|storm|canal|piazza|square|bay of|mountain|valley|forest|wood\b|woods|road|village|town|castle|ruins|bridge|mill\b|windmill|winter scene|dunes|beach|shore|sunset|moonlight|panorama|campagna|lake|waterfall|grand canal|venice|rome|tivoli|dordrecht|haarlem|naples|vesuvius|cliff|ravine|glacier|meadow|pasture|marsh|estuary|the thames|the seine|the rhine|the tiber|the arno|grotto|cascade|quay|port\b|pier|lighthouse|rapids|prairie|wilderness|falls|rocky|cathedral|church of|interior of the church|abbey|temple of|colosseum|pantheon|forum|the campo|capriccio|ruin)\b"),
    ("genre", r"\b(merry|company|peasants|tavern|kitchen|market|card players|smokers|drinkers|music party|concert|dance|dancing|skaters|fair\b|kermis|schoolmaster|lacemaker|milkmaid|letter|reading|writing|game of|hot cockles|the swing|blind man|bubbles|soap|toilet of|procuress|interior|courtyard|the visit|sleeping|lesson|children at|fishwife|washerwoman|nursery|spinner|seamstress|cook\b|scullery|maid|servant|fortune teller|musician|lute player|singer|smoking|drinking|feast|wedding|carnival|masquerade|promenade|picnic|bath\b|bathers|the morning|the evening|the doctor|the dentist|surgeon|barber|tailor|shoemaker|blacksmith|cobbler|the old|the young|a boy|a girl|mother and child|family group|gossip|the quarrel|the proposal|conversation|the duet|the music lesson|the letter|breakfast|the meal|the dinner|supper party|skating|haymaking|harvest|gleaners|sower|ploughing|shepherdess|fishermen|hunters|hunt\b|the toilet|the bath)\b"),
    ("portrait", r"\b(portrait|self-portrait|head of a|study of a head|bust of|mr\.|mrs\.|miss\b|madame|mademoiselle|monsieur|signor|signora|don\b|doña|lady\b|lord\b|sir\b|duke|duchess|count|countess|marquis|marquise|marchesa|marchese|baron|baroness|prince|princess|king\b|queen\b|cardinal|bishop|pope\b|doge|captain|colonel|general|admiral|the artist|the painter|the sculptor|young man|young woman|old man|old woman|a man|a woman|a gentleman|a lady|a boy|a girl|his wife|her husband|the artist's|and her|and his|family of|wife of|daughter of|son of|children of|esq)\b"),
]


def arg(name, default):
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), None)
    return default if v is None else type(default)(v)


def get_json(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == tries - 1:
                print("  !", url[:100], e, flush=True)
                return None
            time.sleep(1.5 * (i + 1))


# ---------------------------------------------------------------- 1. wikidata
def wd_fetch(q):
    j = get_json(f"https://www.wikidata.org/wiki/Special:EntityData/{q}.json")
    if not j or "entities" not in j or q not in j["entities"]:
        return q, None
    e = j["entities"][q]
    cl = e.get("claims", {})
    ids = lambda p: [c["mainsnak"]["datavalue"]["value"]["id"] for c in cl.get(p, []) if "datavalue" in c["mainsnak"]]
    return q, {"sitelinks": len(e.get("sitelinks", {})), "genre": ids("P136"), "subject": ids("P921")[:6], "depicts": ids("P180")[:8],
               "label": e.get("labels", {}).get("en", {}).get("value"), "desc": e.get("descriptions", {}).get("en", {}).get("value"),
               "movement": ids("P135")[:3], "creator": ids("P170")[:2]}


def wd_label(q):
    j = get_json(f"https://www.wikidata.org/wiki/Special:EntityData/{q}.json")
    try:
        return q, j["entities"][q]["labels"]["en"]["value"]
    except Exception:
        return q, None


def enrich_wikidata(cat, threads):
    cache = json.loads(WD.read_text()) if WD.exists() else {}
    need = sorted({r["wikidata"] for r in cat.values() if r.get("wikidata") and r["wikidata"] not in cache})
    print(f"wikidata: {len(need)} ids to fetch ({len(cache)} cached)", flush=True)
    with ThreadPoolExecutor(max_workers=threads) as ex:
        for i, (q, v) in enumerate(ex.map(wd_fetch, need)):
            cache[q] = v
            if i % 200 == 199:
                WD.write_text(json.dumps(cache))
                print(f"  wikidata {i + 1}/{len(need)}", flush=True)
    # labels for the genre / subject / depicts ids
    labels = cache.setdefault("_labels", {})
    ids = set()
    for q, v in cache.items():
        if q.startswith("Q") and v:
            ids.update(v.get("genre", []), v.get("subject", []), v.get("depicts", []), v.get("movement", []))
    need = sorted(i for i in ids if i not in labels)
    print(f"wikidata labels: {len(need)} to fetch", flush=True)
    with ThreadPoolExecutor(max_workers=threads) as ex:
        for q, lab in ex.map(wd_label, need):
            labels[q] = lab
    WD.write_text(json.dumps(cache))
    return cache


# ---------------------------------------------------------------- 2. subject
def classify(rec, wd, labels):
    score = {s: 0 for s in SUBJECTS}
    by = None
    # (a) wikidata genre labels, then depicts / main subject labels
    if wd:
        for q in wd.get("genre", []):
            lab = (labels.get(q) or "").lower()
            for sub, s in GENRE_MAP:
                if sub in lab:
                    score[s] += 6
        if max(score.values()) > 0:
            by = "wikidata genre"
        else:
            for q in wd.get("subject", []) + wd.get("depicts", []):
                lab = (labels.get(q) or "").lower()
                for sub, s in GENRE_MAP:
                    if sub in lab:
                        score[s] += 2
            if max(score.values()) > 0:
                by = "wikidata depicts"
    # (b) NGA themes
    if max(score.values()) == 0 and rec.get("themes"):
        for t in rec["themes"]:
            for s, words in NGA_THEME.items():
                if t in words:
                    score[s] += 3 if s in ("religious", "myth_history", "portrait", "still_life") else 2
        if max(score.values()) > 0:
            by = "nga theme"
    # (c) Met tags
    if max(score.values()) == 0 and rec.get("tags"):
        for t in rec["tags"]:
            for s, words in MET_TAG.items():
                if t in words:
                    score[s] += 3 if s in ("religious", "myth_history", "still_life") else 2
        if max(score.values()) > 0:
            by = "met tag"
    # (d) title rules (always added at a lower weight: they break ties and cover the rest)
    title = (rec.get("title") or "").lower()
    for s, rx in TITLE_RULES:
        if re.search(rx, title):
            score[s] += 1
            if by is None:
                by = "title"
    if max(score.values()) == 0:
        return "portrait" if re.search(r"^[A-Z][a-z]+ [A-Z]", rec.get("title") or "") else "genre", "default"
    best = max(SUBJECTS, key=lambda s: (score[s], -SUBJECTS.index(s)))
    return best, by


# ---------------------------------------------------------------- 3. frame class
SIDES = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 3.5, 4, 5, 6]
CLASSES = [(w, h) for w in SIDES for h in SIDES if 0.4 <= w / h <= 2.5 and max(w, h) >= 1]   # quarter steps to 2, halves above (a 1.5 x 2 fits a 2 x 2 slot)
CM = re.compile(r"(\d+(?:[.,]\d+)?)\s*[×x]\s*(\d+(?:[.,]\d+)?)\s*(?:[×x]\s*\d+(?:[.,]\d+)?\s*)?cm", re.I)


def cm_of(rec):
    d = rec.get("dimensions") or ""
    if not d:
        return None
    pick = None
    for seg in re.split(r"[;\n]", d):
        m = CM.search(seg)
        if not m:
            continue
        low = seg.lower()
        if "frame" in low and "unframed" not in low:
            continue
        pick = (float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", ".")))
        if any(k in low for k in ("unframed", "painted surface", "overall", "image")):
            break
    return pick                                                  # (height, width) as museums list them


def ppb_of(L):
    """pixels per block: 256 up to 4 blocks, then whatever keeps the long side at 1024 (a multiple of 8)"""
    return 256 if L <= 4 else int(1024 / L) // 8 * 8


def frame_class(rec):
    hw = cm_of(rec)
    px = rec.get("px") or [1, 1]
    if hw and hw[0] > 5 and hw[1] > 5:
        h_cm, w_cm = hw
        ratio = w_cm / h_cm
        if abs(math.log(ratio) - math.log(px[0] / max(1, px[1]))) > 0.45:   # the text does not describe the picture (a wrong pair)
            ratio = px[0] / max(1, px[1])
            long_cm = max(h_cm, w_cm)
        else:
            long_cm = max(h_cm, w_cm)
        source = "cm"
    else:
        ratio = px[0] / max(1, px[1])
        long_cm = 100.0
        source = "px"
    L = long_cm / 60.0                                            # 1 block = 60 cm: a little larger than life ("lifelike and grand")
    L = max(1.0, min(6.0, round(L * 4) / 4 if L <= 2 else round(L * 2) / 2 if L <= 4 else float(round(L))))
    cands = [c for c in CLASSES if max(c) == L]
    best = min(cands, key=lambda c: abs(math.log(c[0] / c[1]) - math.log(ratio)))
    ppb = ppb_of(L)
    return {"w": best[0], "h": best[1], "L": L, "ppb": ppb, "tex": [int(best[0] * ppb), int(best[1] * ppb)], "ratio": round(ratio, 3), "cm": [round(x, 1) for x in hw] if hw else None, "by": source}


# ---------------------------------------------------------------- 4. artist
def nga_constituents():
    d = ROOT / "nga"
    cons = {r["constituentid"]: r for r in csv.DictReader(open(d / "constituents.csv", encoding="utf-8"))}
    by_obj = {}
    for r in csv.DictReader(open(d / "objects_constituents.csv", encoding="utf-8")):
        if r["roletype"] == "artist" and r["role"] in ("artist", "painter"):
            by_obj.setdefault(r["objectid"], []).append((int(r["displayorder"] or 0), cons.get(r["constituentid"])))
    return {k: sorted(v, key=lambda x: x[0])[0][1] for k, v in by_obj.items() if v and sorted(v, key=lambda x: x[0])[0][1]}


def artist_key(name, wikidata=None):
    """one key per painter across the three museums: the Wikidata id when the museum gives one (q1234), else the full
    name (never the surname alone — 'johnson' once merged David, Joshua and Eastman Johnson into one life)"""
    if wikidata and re.match(r"^Q\d+$", str(wikidata)):
        return str(wikidata).lower()
    s = re.sub(r"\(.*?\)", "", name or "").strip()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:48] or "anonymous"


def artist_of(rec, ngac):
    src = rec["key"].split(":")[0]
    if src == "nga":
        c = ngac.get(str(rec["id"]))
        if c:
            dates = f"{c['beginyear']}–{c['endyear']}" if c.get("beginyear") else ""
            return {"artist_display": c["preferreddisplayname"], "artist_key": artist_key(c["preferreddisplayname"], c.get("wikidataid")),
                    "artist_nat": c.get("nationality") or "", "artist_dates": dates, "artist_wikidata": c.get("wikidataid") or None,
                    "artist_bio": f"{c.get('nationality') or ''}, {dates}".strip(", ")}
        return {"artist_display": rec["artist"], "artist_key": artist_key(rec["artist"]), "artist_nat": "", "artist_dates": "", "artist_bio": ""}
    if src == "met":
        bio = rec.get("artist_bio") or ""
        nat = bio.split(",")[0] if bio else ""
        m = re.search(r"(\d{4})[–-](\d{4})", bio)
        return {"artist_display": rec["artist"], "artist_key": artist_key(rec["artist"], rec.get("artist_wikidata")), "artist_nat": nat,
                "artist_dates": f"{m.group(1)}–{m.group(2)}" if m else "", "artist_bio": bio}
    # cma: "Rembrandt van Rijn (Dutch, 1606–1669)"
    m = re.match(r"(.*?)\s*\((.*?)\)", rec["artist"] or "")
    name = m.group(1) if m else (rec["artist"] or "")
    inside = m.group(2) if m else ""
    nat = inside.split(",")[0] if inside else ""
    md = re.search(r"(\d{4})[–-](\d{4})", inside)
    return {"artist_display": name, "artist_key": artist_key(name), "artist_nat": nat, "artist_dates": f"{md.group(1)}–{md.group(2)}" if md else "", "artist_bio": inside}


# ---------------------------------------------------------------- 5. period / fame
def period_of(y):
    if y is None:
        return "unknown"
    return "gothic" if y < 1400 else "renaissance" if y < 1600 else "baroque" if y < 1750 else "rococo_neoclassical" if y < 1800 else "nineteenth"


def main():
    threads = arg("threads", 4)
    cat = json.loads(CAT.read_text())
    print(f"catalogue: {len(cat)} works", flush=True)
    cache = enrich_wikidata(cat, threads) if "--no-wikidata" not in sys.argv else (json.loads(WD.read_text()) if WD.exists() else {})
    labels = cache.get("_labels", {})
    ngac = nga_constituents()
    counts = {"subject": {}, "by": {}, "period": {}, "source": {}, "class": {}, "famous": 0, "palace": 0}
    for k, r in cat.items():
        wd = cache.get(r.get("wikidata") or "") if r.get("wikidata") else None
        r["sitelinks"] = wd["sitelinks"] if wd else 0
        r["wd_genre"] = [labels.get(q) for q in wd.get("genre", [])] if wd else []
        r["wd_desc"] = wd.get("desc") if wd else None
        r["wd_depicts"] = [labels.get(q) for q in (wd.get("depicts", []) + wd.get("subject", []))][:8] if wd else []
        r["subject"], r["subject_by"] = classify(r, wd, labels)
        r["frame"] = frame_class(r)
        r.update(artist_of(r, ngac))
        try:
            r["year"] = int(r["year"])
        except Exception:
            r["year"] = None
        r["period"] = period_of(r["year"])
        r["famous"] = bool(r["sitelinks"] >= 6 or r.get("highlight"))
        r["palace_ok"] = bool(r["year"] and r["year"] <= 1800)
        for f, v in (("subject", r["subject"]), ("by", r["subject_by"]), ("period", r["period"]), ("source", k.split(":")[0]), ("class", f"{r['frame']['w']}x{r['frame']['h']}")):
            counts[f][v] = counts[f].get(v, 0) + 1
        counts["famous"] += r["famous"]
        counts["palace"] += r["palace_ok"]
    # one key per painter: a name-keyed record joins a Wikidata-keyed painter of the same display name (CMA gives no ids)
    q_of_name = {}
    for r in cat.values():
        if r["artist_key"].startswith("q"):
            q_of_name.setdefault(re.sub(r"[^a-z]", "", (r["artist_display"] or "").lower()), r["artist_key"])
    for r in cat.values():
        if not r["artist_key"].startswith("q"):
            q = q_of_name.get(re.sub(r"[^a-z]", "", (r["artist_display"] or "").lower()))
            if q:
                r["artist_key"] = q
    tmp = CAT.with_suffix(".tmp"); tmp.write_text(json.dumps(cat, indent=0, ensure_ascii=False)); tmp.replace(CAT)
    artists = {}
    for r in cat.values():
        artists.setdefault(r["artist_key"], {"display": r["artist_display"], "n": 0, "nat": r["artist_nat"], "dates": r["artist_dates"]})["n"] += 1
    lines = [f"# GALLERY CENSUS — {len(cat)} works, {len(artists)} artists ({time.strftime('%Y-%m-%d %H:%M')} CT)", ""]
    for f in ("subject", "by", "period", "source", "class"):
        lines.append(f"## {f}")
        for v, n in sorted(counts[f].items(), key=lambda x: -x[1]):
            lines.append(f"- {v}: {n}")
        lines.append("")
    lines += [f"famous (sitelinks >= 6 or museum highlight): {counts['famous']}", f"palace-eligible (<= 1800): {counts['palace']}", "",
              "## top artists", *[f"- {a['display']} ({a['nat']}, {a['dates']}): {a['n']}" for a in sorted(artists.values(), key=lambda a: -a["n"])[:40]]]
    Path("/home/claude/_docs/palace/GALLERY-CENSUS.md").write_text("\n".join(lines))
    print("\n".join(lines[:60]), flush=True)


if __name__ == "__main__":
    main()
