# PROVENANCE LEDGER — texture pilot: alligator (2026-09-30)

Status: **PREVIEW ONLY.** Nothing from this pilot is in any pack. It goes into a pack only after Abs0lum's eye says so.
Rules applied: CUSTOM INSTRUCTIONS §9 "ASSET SOURCES" (ruling 2026-09-30: Tier A CC0 / Tier B attribution / Tier C non-commercial).

## 1. Sourced assets (one line each)

| # | Site | Asset (URL / ID) | Author | Licence as shown + licence URL | Downloaded | Tier | What was changed | Used in (pack + file) |
|---|------|------------------|--------|--------------------------------|------------|------|------------------|-----------------------|
| 1 | ambientCG | Leather 008 — https://ambientcg.com/view?id=Leather008 (short link https://ambientcg.com/a/Leather008), file `Leather008_1K-JPG.zip` (md5 e0beb50d2881d3168be5963bc8744e0a) | ambientCG (Lennart Demes) | "All assets are released under the Creative Commons CC0 license, making them free to use without attribution - even in commercial circumstances." (asset page) · CC0 1.0 Universal — https://docs.ambientcg.com/license/ | 2026-09-30 | **A** (CC0) | Only the **Displacement** map is used (as a height pattern): box-filtered to the texel size, a groove mask added, tiled at four plate sizes (belly 2.6, flank 2.4 upright, throat 2.0, head 1.4 / limbs 1.8 model px per plate), recoloured through our own two-tone ramps. The source's colour, normal, roughness and AO maps are not used. | Candidate only: `textures/sf/nba/entity/alligator/alligator.png` (the pack that draws the alligator — today RP-07). **Not shipped.** |

Licence snapshots taken on the download day (sites change their terms):
- `_intake/texture_pilot/ambientcg/LICENSE-ambientcg-2026-09-30.html` (the site's licence page; md5 ab2bcf6101814fd9ace892b3ca9a5a5f)
- `_intake/texture_pilot/ambientcg/ASSETPAGE-Leather008-2026-09-30.html` (the asset's own page: CC0 wording above, no stricter licence, no other owner named; md5 07f2821b7eff5ec306fa2aa4e4b3f1d6)
- `_intake/texture_pilot/ambientcg/API-Leather008-2026-09-30.json` (ambientCG's metadata: released 2018-07-04, "Displacement generated using photogrammetry", tags crocodile / leather / skin; md5 955b1eebefcf8831b58228adae33eaf7)

Asset-page check: the page names the same licence as the site (CC0) and no different owner → nothing to flag.
Re-checked 2026-09-30 10:0x CT through the web reader (link pasted by Abs0lum): same CC0 wording; no creator, stricter licence, attribution requirement or other owner named for Leather 008; release 2018-07-04.

## 2. Generated (original AbsolutRealism work — the recipe is the record)

| Part | Recipe (tool: `tools/texture_pilot_alligator.py`, md5 561bfe270e2643a3fee60971ff7c4a42) |
|------|----------------------------------------------------------------------------------|
| Dorsal armour (back, tail top) | `scutes()`: keeled scutes in straight transverse rows (2.4 px along x 2.2 px across), columns centred on the midline, the middle keels tallest; 15 % Leather008 grain. |
| Crest spikes | dark ramp, tips lighter by height inside the spike; 15 % Leather008 grain. |
| Flank + tail sides | Leather008 plates upright + `countershade()`: dark above, pale below an irregular line (value noise), edge broken into ~1 px blotches. |
| Jaw line | the same countershading on the jaw-level side faces (pale lower half). |
| Head | `tubercles()` (small round bumps, offset rows) 50 % + Leather008 50 %. |
| Limbs | Leather008 55 % + tubercles 45 %. |
| Colours | two-tone ramps per region, picked by eye from reference photos of adult American alligators (visual targets only: never traced, sampled or pasted). |
| Eyes | yellow iris + black slit pupil (the pupil sits where the old art left a dark texel between two yellow ones). |
| Teeth / mouth | flat cream teeth; pale pink-cream mouth with procedural palate ridges (one per model px). |

## 3. Carried over from the old sheet (NOT sourced, NOT original — recorded so nobody mistakes the pilot for a clean-room texture)

The old sheet is the Naturalist creature's own texture (`_build/rp07-1429/textures/sf/nba/entity/alligator/alligator.png`, 128 x 128, md5 d878dbc46cd647a8cc30c82efe0bdcf5), drawn on the Naturalist model (`models/entity/sf/nba/alligator.geo.json`, md5 9d06f11e92d8f33de3c03be6670ae4e0).
- **The cut-out shape (alpha)** is the old sheet's alpha, scaled x4 (nearest), unchanged. The model depends on it: the back and tail crests are thin boxes whose sides are cut into spikes, the teeth are cut out of two thin boxes around the jaws, the feet are flat cut-out claws. Check in the tool: "alpha identical to the old sheet x4: True".
- **Where the eyes, teeth and mouth are**: found from the old sheet's colours, then repainted (no old colour is kept).

Consequence: this texture is bound to the Naturalist model and its cut-outs. It can go wherever that model is allowed to go, under the same rules as the model — not further.

## 4. Commercial gate

Tier A only (CC0) → nothing to replace for a paid release on the texture's own account. Section 3 (the model's cut-outs) follows the model's own status.
- 2026-09-30 · Patrix Java source (FreshLX permission) · Patrix_26.2_256x_basic.zip (1,709,824,419 B, md5 ea9ea0ac021b7d545c887b0069fdda09, from his Drive) · leaf colour tiles, 100 used (11 species, same CTM picks as RP-01 1.3.106) · licence: Patrix port permission · PW-TestRunner RP v0.5.0 textures/blocks/pw_t256/ + pw_t256m/ (test only)
- 2026-09-30 · menagerie P1 (the new animals): 149 creatures + 57 items from his add-on collection (AnF 108, WA 5, WS 1, WWA 8, YSav 19, YTri 8) · licences as shown in RESTRICTED-ASSETS M1-M150 · RP-07 1.4.32 + StripMine BP 1.3.7
- 2026-09-30 · menagerie P3 (his picks): 320 creatures + 72 items from his add-on collection (AnF 211, IFS 1, WA 41, WS 11, WWA 8, YSav 27, YTri 21) · licences as shown in RESTRICTED-ASSETS M151-M471 · RP-07 1.4.33 + StripMine BP 1.3.8
- 2026-09-30 · menagerie R2 (WWA seal lives, AnF spawn weights to vanilla scale, our spawn rules on today's grass): 1 creatures + 0 items from his add-on collection (WWA 1) · licences as shown in RESTRICTED-ASSETS M472-M473 · RP-07 1.4.34 + StripMine BP 1.3.9
