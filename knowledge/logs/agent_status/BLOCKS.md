[02:59 CT] BLOCKS started: reading law + locating painting/bed/inn/root/banner sources
[03:04 CT] item1 PAINTINGS mechanism found (entity file x = world x, z flipped; 10-05 fix assumed 180 deg -> E/W slabs sit 15/16 off the wall); next: patch geo + render check
[03:05 CT] item1 PAINTINGS staged (RP-12 + LITE pw_frames.geo.json, 408/408 facings flush+outward in check render); next: item2 bed legs
[03:10 CT] item2 BED: mechanism = engine bed legs' head-facing face reads the leg 'up' uv slot, which is 100% transparent in every RP-04 bed colour (Java-layout leg copied without Java's leg rotation) + the 16 _n maps are still Java layout; fixing textures (engine geometry has no overlap)
[03:11 CT] item2 BED staged: RP-04 textures/entity/bed 16 colour + 16 _n (relaid to engine layout) + 16 _mers; renders viewed (hollow head-end legs -> solid); next: item4 texture warnings
[03:12 CT] item4 WARNINGS staged: 5 BP-02 block files -> single keys + RP-04 terrain_texture.json +1 key (pw_acacia_log_top_single); full BP-02 scan: 0 other array-key refs; next: item5 banner
[03:13 CT] item5 BANNER done: pw_companion.js banner reads globalThis.__PW_BUILD one tick after boot (+ RP-04 1.3.159 const); needs 1-line main.js proposal; node --check OK; next: item3 inn redesign
[03:17 CT] item3 INN: read pipeline (civ_roster -> civ_variants -> civ_stages -> weather_overlays -> civ_village_data/art_slots); writing tools/inn_v2.py (new file, mine): 17 deep x 12 front, 2 guest floors x 4 rooms x 4 beds (1-block gaps)
[03:20 CT] item3 INN generated: 4 skins + 5 stages + _w/_r each, table entries, ruling test PASS (8 rooms x 4 beds, 1-block gaps); plans f-5/0/4/8/12 viewed; next: geo_ref_check + test suites + README
DONE: 5 items staged in _staging/blocks231 (paintings RP-12, bed legs RP-04, inn v2 BP-02 8x4 beds, 8 texture warnings, PW-C2 banner); geo_ref_check 0; suites 29/29; awaiting lead assembly + his witness
