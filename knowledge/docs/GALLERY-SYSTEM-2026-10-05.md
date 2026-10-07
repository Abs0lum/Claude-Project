# THE GALLERY — system note (D-C571 v2; BP-02 1.3.222 · RP-12 1.0.0) — for ARCHITECTURE absorption

## Data flow (build time)
1. `tools/art_harvest.py --all` → `_intake/art/catalogue.json` (one record per work; images stored 1,280 px JPEG at
   `_intake/art/{nga,met,cma}/<id>.jpg`). Sources: NGA open-data CSVs (`_intake/art/nga/*.csv`) + api.nga.gov IIIF;
   Met search v1.1 + objects v1 (isPublicDomain, Paintings, 1200–1900); Cleveland API (cc0, Painting). Resumable by key.
2. `tools/art_catalogue.py` → Wikidata enrichment (cache `_intake/art/wikidata_cache.json`: sitelinks, genre, depicts,
   description), SUBJECT (wikidata genre → NGA themes → Met tags → title rules; the writers' "s" overrides on merge),
   FRAME CLASS (`frame`: w × h in quarter / half / whole blocks, ppb, tex px; 1 block = 60 cm), ARTIST (key = Wikidata id
   `q…` when known else the full name; nationality, dates), PERIOD, FAME (sitelinks ≥ 6 or a museum highlight),
   palace_ok (≤ 1800). Census → `_docs/palace/GALLERY-CENSUS.md`.
3. `tools/art_essays.py make | merge | status` → batches for the writers (`_intake/art/essays/in/*.json`, briefs
   `PROMPT-works.md / PROMPT-famous.md / PROMPT-artists.md`), outputs merged into `essays.json` {key: {d, i, c, s}} and
   `bios.json` {artist_key: paragraph}; merged batch files move to `out_merged/`.
4. `tools/build_rp12_gallery.py OUT [--scale=0.5]` → RP-12: `textures/gallery/<kid>.jpg` (framed; `compose()`),
   `entity/pw_art_<kid>.entity.json`, `models/entity/pw_frames.geo.json` (one geometry per class: four facing bones
   n / e / s / w, picture on the facing face, frame strips on the edges), `render_controllers/pw_art.render.json`
   (part_visibility by `pw:facing`), the book icon + item_texture + lang. `kid` = key lowercased, non-alnum → `_`
   (`nga:1236` → `nga_1236`, `cma:1944.90` → `cma_1944_90`).
5. `tools/build_bp02_222.py` → BP-02: `entities/pw_art/<kid>.json` (static, hitbox w × h, property pw:facing),
   `scripts/pw_gallery.js` (from `tools/bp02_src/`), `scripts/pw_gallery_data.js` (WORKS rows + ARTISTS + SUBJECTS +
   SOURCES), `scripts/pw_gallery_text.js` (TEXT + BIOS), CIV_BUILDINGS `art` slots (`tools/art_slots.py`: offline wall
   scan per template; the palace by room), the clock hooks (hang at the furnished stage; a 200-tick sweep for older
   buildings), the book item + recipe.

## Runtime
- `pw_gallery.js`: registry = world dynamic property `pw:gallery_used` (a 0/1 string, one char per WORKS index);
  `pick(subject, w, h, palaceOnly, rng)` prefers the larger fitting classes; `hangBuilding(dim, b, def, seed)` is
  RESUMABLE (`b.artNext`, `b.artDone`, `b.art` = count) because a spawn needs a TICKING chunk (loaded is not enough);
  a failed spawn gives the work back. Slots are rotated with the building (floats: r1 (X,Z) → (sz − Z, X); facing + r).
- Interaction: `playerInteractWithEntity` (before-event, cancelled) → with the book: the essay form; empty hand: the
  label in the action bar. `itemUse` of the book in the air: the catalogue (nearby / by subject / by artist).
- Commands: `/scriptevent pw:gallery status | test [n] | testat x y z [n] | hang <key> | unused | reset`.

## Invariants / limits
- Texts are data: a rebuild of 222 with new essays changes no behaviour (a load gate suffices).
- Pack sizes: RP-12 174 MB (256 px per block, 1024 max), LITE 56 MB (128 px per block). One of the two is installed.
- The palace hangs ≤ 1800 only (A4); other buildings anything; cap per family in `art_slots.CAP`.
- Never hang through the clock without the registry (a repeat is a bug: LC-GAL-4).

## Open (as of 2026-10-05 06:xx)
- Witness: LC-GAL-1 (lazy texture loading), LC-GAL-2 (JPEG textures), LC-GAL-3 (north / west faces not mirrored).
- The secret painting block could carry a real work; room-subject rules for the palace are in build_bp02_222.palace_subject.
