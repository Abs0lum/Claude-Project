# TEXTURE SOURCES — licence survey for creature textures (2026-09-30)

Rules applied: CUSTOM INSTRUCTIONS §9 ASSET SOURCES (Tier A CC0 · Tier B attribution · Tier C non-commercial · NOT ALLOWED: no licence, forbids redistribution, personal/editorial only, content the site does not own). A pack other players download IS redistribution.
Method: each site's own licence page read on 2026-09-30 through the web reader (links pasted by Abs0lum); dated copies saved in `_intake/texture_sources/` where the page could be saved. Quotes below are the licence wording as read. **Nothing here has been downloaded or used yet** except ambientCG Leather008 (see `_docs/texture_pilot/PROVENANCE.md`).

## Verdicts

| Site | Licence as read (quote) | Verdict | Why |
|------|------------------------|---------|-----|
| **ambientCG** | "All assets are released under the Creative Commons CC0 license … even in commercial circumstances." | **Tier A** | CC0; already in use (Leather008). |
| **Poly Haven** | CC0: "You can use our assets for any purpose, including commercial work"; may be "include[d] in a product you sell"; credit not required. | **Tier A** | CC0; logos / example renders excluded (we would not use those). |
| **TextureCan** | "under the Creative Commons CC0 1.0 Universe License"; "can be used for any purposes, including commercial use"; "allowed to be redistributed together with your projects and 3D assets". | **Tier A** | CC0 + redistribution inside projects stated. Their note: brand names / logos inside a texture stay the user's responsibility. |
| **3DTextures.me** | "All textures on this site are licensed as CC0 … You can redistribute them (share them around or include them when sharing your own project)." Only limit: don't claim to be the author. | **Tier A** | CC0. Has Skin Lizard 002, Dragon Scales 001/002, Stylized Scales 001-003 (full PBR sets). |
| **ShareTextures** | "custom CC0-based license"; "Free to use for personal, educational, or commercial projects"; "No asset redistribution on other websites, in plugins, or **as part of collections** without our written permission"; "CC0 only applies to assets downloaded directly from our site". | **FLAG — ask them first** | A resource pack is literally a texture collection; the custom clause may cover it. Usable only with their written OK (or if you read "collections" as asset packs sold/shared as assets — your call). |
| **AITextured** | "Free for personal & commercial projects; no resell/redistribution of raw files; no AI/ML training without our written permission"; forbids "re-packaging as standalone assets"; credit appreciated, not required; they "retain all rights not expressly granted". | **FLAG — likely allowed for heavily changed work, raw files never** | Our use turns a texture into a creature's own painted sheet (recoloured, re-cut to its UV) — not the raw file. But the pack's PNGs are extractable. Safest: use it as a height / pattern source only (like Leather008), never ship its colour map as-is, or email them for a yes. Has fur (spotted, coarse, striped, mottled), reptile / crocodile / snake scales, feathers, hides. |
| **FreePBR** | "free to use in your games / 3d … As long as you don't use these commercially"; commercial = $19 VIP; "don't redistribute these PBR file sets on other sites, file sharing sites, email". | **Tier C (free suite only)**, raw sets never shipped | Non-commercial free use is stated; the redistribution ask is about the file sets themselves. Commercial gate: replace or buy the $19 licence. |
| **CGAxis** | Games only "provided that the Assets are contained within a proprietary format and displayed within the game during play"; "strictly prohibited from sharing or reselling these PBR materials in the exact form they were downloaded"; credit "models by CGAXIS.com" required. | **NOT ALLOWED** | Minecraft packs store textures as plain PNG anyone can open — not a proprietary format. |
| **Texturing.xyz** | Prohibited: distributing Materials "as part of a texture pack, material pack, clip-art collection". | **NOT ALLOWED** | A resource pack is a texture pack. |
| **RenderHub** | Personal Use Only licence = non-commercial, no sharing; Extended licence allows games, but "you may not redistribute … a Digital Asset … unless the modified Digital Asset becomes part of a larger Creation"; not "competitive with the original". | **NOT RECOMMENDED** (per asset, paid, grey) | Every asset needs the paid Extended licence, and a texture inside a texture pack is close to the "competitive" line. Only with a written OK per asset. |
| **3D Jungle** | Footer: "received from an open source … use for non commercial purposes". Agreement §4 "License to use" (read from Abs0lum's screenshots 11:23): "4.1 The Seller is not the creator of the Goods posted on the Seller's Website and does not own the copyright to these Goods. 4.2 Payment for Download Access … does not grant an exclusive or personal license to use these products. 4.3 All Products posted … solely for informational purposes, and all copyrights belong to their owners." | **NOT ALLOWED (confirmed)** | The site grants no licence at all and says it does not own the copyright; the real owners are unknown = §9 "no licence / cannot be found". |
| **Textures.com** | (read from Abs0lum's screenshots 11:24) Own video game: "allowed … to create your own free or commercial video game … also … with a Free account", no credit. BUT: "you are not allowed to resell (or give away for free) our images as a competing product, even when you modify the images. Competing products are for example textures, texture packs, materials, shaders"; "redistribution of the materials is not allowed"; not under open-source licences; Special Content (PBR materials, scans) may not be bundled even when modified. | **NOT ALLOWED** | Our packs are resource / texture packs for someone else's game (Minecraft), handed to other players — exactly the "texture packs … give away for free" case, even modified. |

## What this means for the creature texture work
- **Tier A to build from now:** ambientCG, Poly Haven, TextureCan, 3DTextures.me. Animal-relevant: leathers / hides (ambientCG, Poly Haven "Textiles & Leather"), scales (3DTextures.me Skin Lizard 002, Dragon Scales, ambientCG Leather008), organic (Poly Haven "Organic").
- **Fur and feathers are the gap in Tier A.** Options: (1) procedural fur / feather generators of our own (recipe = original work), (2) AITextured as a pattern / height source only, after your call, (3) written permission from AITextured or ShareTextures.
- **Method stays the pilot's:** a source texture's height or pattern, recoloured and re-cut onto each creature's own texture layout; the creature's cut-out shapes kept; one ledger line per source.

## Paid libraries checked for a later release (2026-09-30 11:4x, links pasted by Abs0lum)
| Library | Licence as read (quote) | Release route? |
|---------|------------------------|----------------|
| **Poliigon** | Assets may not be used "in design software or games where the users have direct or indirect access to the assets"; game mods / resource packs "make it possible for others to access Poliigon assets and therefore is not allowed"; no redistribution "even if they've been modified". | **NO** — mods / resource packs named as not allowed. |
| **Adobe Substance 3D Assets** | Distribute "only as modified into a Modified Work or as incorporated into a Larger Work" if that work "without inclusion of the Substance 3D Asset(s), would qualify as an original work of authorship" and "the primary value … does not lie with the Substance 3D Asset(s) itself"; not in "any way that allows a third party to use, download, extract, or access the Substance 3D Asset(s) on a stand-alone basis". | **MAYBE (grey)** — a creature texture painted from an asset is a Modified Work inside a Larger Work (the pack), but pack PNGs can be extracted; would need Adobe's confirmation before relying on it. |

## Snapshots saved (download day)
`_intake/texture_sources/`: texturecan-terms (2fd4c48b…), 3dtextures-about (b66b1bb9…), aitextured-terms (afe64d95…), sharetextures-license (e5d80a27…), polyhaven-license (cd9ac4fc…), cgaxis-tos (3ebb20ac…), freepbr-about (1716386d…), all -2026-09-30.html. ambientCG: `_intake/texture_pilot/ambientcg/`.

## 2026-10-01 — BLOCK PBR ROUND (RP-04 1.3.145 · RP-05 1.3.52 · RP-10 1.3.44 · RP-11 1.3.36 · RP-01 1.3.108 · RP-03 1.3.61 · RP-08 1.4.10)
- Patrix 26.2 256x basic (Drive `Patrix_26.2_256x_basic.zip`; FreshLX permission, §9 "port freely"): `_n` / `_s` maps (block
  textures + OptiFine CTM tiles) converted by Lesson #156 into texture-set normal / MERS layers for the block textures whose
  picture matches a Patrix source (thumbnail match d < 10; report `_docs/blocks/PBR-ROUND.json`, `PBR-PHASE6.json`); the vanilla
  grass block sides' tint mask from Patrix `ctm/patrix/grass/block/side_overlay/1..16`. Patrix 26.2 128x basic = fallback.
- Derived (own work, from our own colour images): normal + MERS for block textures with no Patrix match (luminance height +
  material class table in tools/pbr_round.py).
- Mojang `bedrock-samples/resource_pack/textures/blocks/grass_side.tga` was READ (fetched 17:56) to learn the tint-mask
  format; it is not shipped.

## 2026-10-01 evening — resolution tier round + sand depth test
- UP to 256 (109 textures: dirt, coarse dirt, podzol side, rooted dirt, mud, packed mud, muddy mangrove roots side,
  farmland dry/wet, oak log, log_oak): colour + normal + MERS from the Patrix Java source 26.2 256x basic pack
  (`_intake/patrix262_basic`, FreshLX permission; same-layout match checked by layout correlation >= 0.6, colour graded
  to ours by per-channel mean/std; MERS by Lesson #156). Packs: RP-04 1.3.147, RP-10 1.3.45, RP-05 1.3.53, RP-01 1.3.109.
- DOWN to 64 (15 End decor textures): our own images resampled (no new source). RP-04 1.3.147, RP-03 1.3.62.
- PW-SandTest A / B 1.0.0: sand normals are own work — A integrated from our current sand normal maps (Frankot-Chellappa,
  low-pass), B from our own sand colour images' luminance (tools/sand_vv_preview.py). Colour + MERS = RP-04's own files.
- AR Spiral Stairs Test RP 0.0.1 (2026-10-06): textures/blocks/pw_spiral/pw_sp_<palette>_<part> = copies of RP-04 1.3.159's
  Patrix-derived tiles (polished_andesite_v0, stone_bricks/_v1/_v2, oak_planks_v0/_v2, spruce_planks_v0, smooth_stone_v1,
  stripped_oak/dark_oak/spruce_log) + their MER / normal maps; pw_sp_oak_soffit = oak_planks_v2 turned 90 deg (colour + MER;
  normal map left out — a turned normal map needs its vectors turned). Patrix Java source (FreshLX permission): not restricted.
