# Tree Proportions Research: real-world allometry for re-scaling AbsolutRealism tree templates

Date: 2026-10-03. Scope: real proportions (height H, DBH, crown width CW, crown-base height CBH / crown ratio CR, crown-to-DBH ratio) for each in-game species analogue, then per-group targets for 1 block = 1 m.

Status: research only. Nothing here has been checked in game; the targets are proposals for Abs0lum to approve.

Evidence rule: every number in sections 1–2 comes from a source listed at the end. Numbers marked **(derived)** are my arithmetic on sourced equations (checked with Python). Where a source gave no value, this doc says **NOT FOUND**.

---

## 1. Key cross-species finding: crown width scales with DBH

### 1.1 Crown-width-from-DBH equations

| Equation | Species | Coefficients | Source |
|---|---|---|---|
| CW(m) = a + b·DBH(m) | Oak (Q. robur/petraea) | a = 1.71733, b = 15.6159, r² = 0.911 | Hemery et al. 2005 [S1] |
| " | Birch (Betula spp.) | a = 0.97524, b = 16.1512, r² = 0.922 | Hemery et al. 2005 [S1] |
| " | Wild cherry (Prunus avium) | a = 1.7600, b = 15.40, r² = 0.840 | Hemery et al. 2005 [S1] |
| " | Beech (Fagus sylvatica) | a = 1.13312, b = 15.2331 | Hemery et al. 2005 [S1] |
| CW = 0.8304 + 27.82·DBH − 10.68·DBH² (m) | Urban: oak, sycamore, birch, Norway maple pooled | as shown | Martin et al. (NTU) [S2] |
| CW/DBH ratio = 35.9 − 31.19·DBH + 14.19·DBH² | same urban set | as shown | [S2] |
| crown radius = 3.3 m·(DBH/25 cm)^0.8157 (95% quantile, open/urban) | Quercus robur | r25 = 3.3 m, α = 0.8157 | Pretzsch et al. 2015 [S3] |
| LCW(ft) = b0 + b1·D(in) + b2·CR(%) | US stand-grown, 87 spp. | white oak 3.2375/1.5234/0.0455 (+ Hopkins-index term −0.0324); N. red oak 2.8908/1.4077/0.0643; paper birch 2.8399/1.2398/0.0787; white spruce 0.3789/0.8658 (no CR term shown in the extract; check the PDF); red spruce −1.2151/1.6098/−0.0277; black cherry 3.0237/1.1119/0.1112 | Bechtold 2003 [S4] |

Notes from the sources:
- Hemery [S1]: the relationship is close to linear (r² > 0.8) between about 20 and 50 cm DBH. CW/DBH levels off from about 30 cm DBH. At 60 cm DBH the ratio is about 21–22 for walnut and 15–16 for shade-tolerant beech and lime.
- Martin [S2]: mean urban CW/DBH ratios are oak 26.62, sycamore 26.39, Norway maple 25.98 and silver birch 24.88.
- Norway spruce [S5] (5,526 stand-grown trees, Czech Republic): crown-to-bole diameter ratio has a mean of **0.20 m per cm** (a ratio of about 20), SD 0.07, range 0.04–0.67. Sample means: DBH 25.4 cm (range 3.1–112), H 16.1 m (range 2–48.7), CW **3.6 m (range 0.7–11.9 m)**.

### 1.2 What a given trunk can carry (oak) (derived)

| DBH (m) | Hemery CW | Martin (urban) CW | Pretzsch 95% open CW |
|---|---|---|---|
| 0.375 | 7.6 | 9.8 | 9.2 |
| 0.50 | 9.5 | 12.1 | 11.6 |
| 0.75 | 13.4 | 15.7 | 16.2 |
| 1.00 | 17.3 | 18.0 | 20.5 |
| 1.25 | 21.2 | 18.9 | 24.5 |

**Rule of thumb:** crown diameter ≈ 15–25 × DBH for broadleaves, and about 20 × DBH for Norway spruce. Forest-grown trees sit at the low end; open-grown trees sit at the high end.

---

## 2. Species data

### Oak: English/pedunculate oak (Quercus robur)
- H: 20–40 m at maturity; "broad and spreading crown" [S6].
- CW at a given DBH: see 1.2. Q. robur is Pretzsch "allometric type 3", a medium crown size with a steep slope, so its crown keeps widening as the trunk thickens [S3].
- Crown-base height or crown ratio for open-grown oak: **NOT FOUND** as a number.
- Growth stages by age (DBH at age): **NOT FOUND** in the sources read.

### Dark oak analogue: forest-grown sessile oak (Q. petraea)
- Managed high forest keeps stands dense for natural pruning. Rotations run over 120 years, sometimes 250–300. Final crop is at most about 100 trees/ha. At Tronçais, about 200-year rotations carry 120–200 trees/ha [S7].
- (derived) 100–200 trees/ha means about 7–10 m between trees, so forest crowns are roughly 7–10 m wide. The Hemery equation puts that at about 0.35–0.55 m DBH; real 200-year crop trees have larger DBH, so their crowns are compressed below the equation.
- Clear-bole length and crown ratio: **NOT FOUND** as numbers. The sources describe forest-grown oak as having a long clean bole and a high crown. This is the opposite of the "low roofed forest" look; see Conflict C1.

### Birch: silver birch (Betula pendula)
- H: up to 30 m; light canopy [S8].
- Silviculture [S9]: 40 cm DBH in under 40 years and 50 cm in 60 years with early crown release. The spacing needed between target trees at the end of the rotation is about **8, 10 and 12 m for 40, 50 and 60 cm DBH**, so crown width is about 20 × DBH.
- Urban CW/DBH is 24.88 [S2]. Hemery birch gives CW = 0.975 + 16.15·DBH [S1].
- Crown ratio: **NOT FOUND**.

### Spruce: Norway spruce (Picea abies)
- H: 35–55 m, trunk 1–1.5 m; record 62.26 m. Grows up to 1 m/yr for the first 25 years [S10].
- CW: stand-grown mean 3.6 m and **maximum 11.9 m across 5,526 trees** (DBH up to 112 cm) [S5].
- White spruce, US stand-grown [S4] (derived from the coefficients shown): DBH 25 cm → 2.8 m crown; 51 cm → 5.4 m; 76 cm → 8.0 m.
- Live crown ratio: **NOT FOUND**. Kantola & Mäkelä 2004 [S11] could not be read (rate-limited), and the MDPI crown-ratio model paper [S12] gives no species summary table.

### Jungle: tropical rainforest (dipterocarps, Ceiba)
- Sebulu, East Kalimantan [S13]:
  - Emergent layer is 60–70 m tall. Crowns are 20–25 m wide and 20–40 m deep, and do not form a continuous canopy.
  - Emergent *Shorea laevis*: H 70.7 m, DBH 130.5 cm, CW 24.2 m, clear bole 30.5 m, lowest leaf at 45 m. (derived) CR ≈ 0.36 and CW/DBH ≈ 18.5.
  - Large canopy tree *Dipterocarpus crinitus*: H 46.5 m, DBH 127 cm, CW 22.8 × 15.2 m, lowest branch at 18 m. (derived) CR ≈ 0.61 and CW/DBH ≈ 15.
- Poorter et al. 2006 [S14]: tall species build a slender stem and a narrow crown. Crown length is negatively correlated with maximum height at reference heights of 4–14 m.
- Ceiba pentandra [S15]:
  - Height up to 60.4 m verified.
  - Trunk up to 3 m above the buttresses (largest over 5.8 m). Buttresses run 12–15 m up the trunk and spread up to 20 m.
  - Crown on 4–6 major limbs, up to 60 m wide. The BCI "Big tree" averaged a 61.3 m crown, a world record [S16].

### Acacia: umbrella thorn (Vachellia tortilis)
- H: 1.5–18 m, occasionally 21 m. Crown usually flat and spreading [S17].
- H 5–20 m in nature, spread **8–13 m** [S18]. Up to 20 m tall with a flat-topped crown in ssp. heteracantha and spirocarpa [S19].
- Trunk DBH and crown-base height: **NOT FOUND**.

### Cherry: Japanese cherry (Prunus serrulata 'Kanzan')
- Ultimate H 8–12 m, spread over 8 m, reached in 20–50 years. Vase-shaped when young, spreading later [S20].
- Hemery wild-cherry equation [S1] (derived): a 9 m crown needs about 0.47 m DBH; the current 13.5 m crown needs about 0.76 m.

### Mangrove: red mangrove (Rhizophora mangle)
- H 10–20 m, up to 40 m on optimal sites. DBH typically 10–30 cm, up to 70 cm [S21].
- Commonly about 6 m, up to 24 m [S22].
- 5–20 m tall (occasionally 30 m); bole 20–70 cm. **Stilt roots 2–4.5 m tall** in salt water. Crown "round-topped, bushy". Large trees are branch-free for 9–12 m [S23].
- CW: **NOT FOUND**.

### Pale oak: veteran pollard oak
- Classic pollards were cut at **2–3 m**, giving a lower, spreading form with horizontal branches [S24].
- Veteran girth and crown numbers: **NOT FOUND** in the sources read.

---

## 3. Diagnosis of the current templates

The core problem is that **the crowns are 1.5–2× wider than their visible trunk can carry.** A wide crown on a thin stem reads as "canopy floating high on a skinny trunk", even when CBH is realistic.

| Group | Current | Real relationship | Mismatch |
|---|---|---|---|
| oak_young | CW 5.7 on 0.375 m trunk | 0.375 m DBH carries 7.6–9.8 m | Fine. The trunk is slightly heavy for its crown. |
| oak_mature | **CW 17.5 on 0.5 m** | 0.5 m → 9.5–12 m; 17.5 m needs about 1.0 m DBH | Crown about 1.5–1.8× too wide, or trunk 2× too thin |
| oak_old | **CW 19.7 on 0.5 m** | needs about 1.15 m DBH | Same, worse |
| oak_elder | CW 21.3 on 2×2 (about 1.5–2 m) | 1.25 m DBH → 19–24.5 m | Consistent |
| dark_oak_elder | CW 19.9 on 2×2, CBH 2.8 | Forest oak crowns about 7–10 m (spacing-derived) | Wide for a dense forest, but this is a stylistic call (C1) |
| pale_oak_elder | CW 16.2 on 2×2, CBH 3.8 | Pollard cut at 2–3 m | CBH slightly high; otherwise plausible |
| birch_* | CW 3.4 / 8.6 / 8.3 | 8.6 m needs about 0.47 m DBH | Fine if the visible trunk is about 0.4–0.5 m |
| spruce_mature/old/elder | **CW 11.9 / 14.7 / 15.8** | Stand-grown mean 3.6 m, maximum 11.9 m out of 5,526 trees | **Crowns about 2–3× too wide.** This is the biggest outlier. |
| jungle_mature/old | CR 0.26, CW 21 on 1×1 | Canopy CR about 0.61, emergent about 0.36; 21 m CW needs about 1.1–1.4 m DBH | **Crown too shallow and too high; trunk far too thin** |
| jungle_elder | CR 0.22, CW 23 on 3×3 | Emergent crown 20–40 m deep | Crown too shallow |
| acacia | H 12.1, **CBH 8.4**, CW 15 | H 5–20, spread 8–13 | Crown about 15% too wide; bare trunk long (CBH number NOT FOUND) |
| cherry | H 11, CW 13.5 | H 8–12, spread over 8 | Crown about 40% too wide for a 1×1 trunk |
| mangrove | H 13.4, CW 13.5 | Commonly 6–20 m; roots 2–4.5 m | CW not sourced; probably wide |

---

## 4. Recommended targets (1 block = 1 m)

"Trunk" means the visible trunk diameter in metres. Each crown width is set at about 18–22 × trunk, following Hemery, Martin and Sharma; open-grown and plains trees go toward 22, forest trees toward 18.

| Group | H | CBH | CW | Trunk | Justification |
|---|---|---|---|---|---|
| oak_young | 9 | 2.5–3 | 6 | 0.3 | 0.3 m DBH → about 6.4 m [S1] |
| oak_mature | 14 | 3.5–4 | 11–12 | 0.6 (or a full 1×1 cell) | 0.6 m → 11–14 m [S1–S3]; 14 m is the low end of oak's 20–40 m mature range [S6], scaled down |
| oak_old | 16 | 4 | 14–15 | 0.8–1.0 | 0.8 m → 14–17 m |
| oak_elder | 20–22 | 4–5 | 20 | 1.2–1.5 (2×2) | 1.25 m → 19–24.5 m; already consistent |
| dark_oak_elder | 15 | 3–4 | 14–16 | 1.0–1.5 (2×2) | Keep the low "roofed" style but match CW to the trunk (see C1) |
| pale_oak_elder | 12–13 | 2.5–3 | 14–16 | 1.2–1.5 (2×2) | Pollard cut at 2–3 m, low spreading form [S24] |
| birch_young | 8 | 2 | 3–3.5 | 0.15–0.2 | Hemery birch: 0.15 m → 3.4 m |
| birch_mature | 16–17 | 5 | 8 | 0.4 | 0.4 m → about 8 m [S9] |
| birch_old | 19–20 | 6 | 9–10 | 0.5 | 0.5 m → about 10 m [S9] |
| spruce_young | 8–9 | 0.5–1 | 3–3.5 | 0.15–0.2 | Ratio about 20 [S5] |
| spruce_mature | 20–23 | 2–4 | 5–6 | 0.3–0.4 | Stand-grown mean 3.6 m at 25 cm DBH [S5]; white spruce 5.4 m at 51 cm [S4] |
| spruce_old | 26–28 | 3–5 | 6.5–7.5 | 0.5 | Above the stand mean, well below the 11.9 m maximum |
| spruce_elder | 30–32 | 3–5 | 8–9 | 0.75–1.0 (2×2) | Real mature trunk is 1–1.5 m [S10] |
| jungle_young | 12 | 4–5 | 5–6 | 0.3 | Slender stem and narrow crown for tall species [S14] |
| jungle_mature (canopy) | 26–28 | 10–11 | 16–18 | 1.0 (1×1 full or 2×2) | Canopy CR about 0.6 and CW/DBH about 15 [S13] |
| jungle_old | 30 | 12–14 | 18–20 | 1.2 (2×2) | Same |
| jungle_elder (emergent) | 32–35 | 18–20 | 22–24 | 2–3 (3×3, buttressed) | Emergent CR about 0.36–0.45 and crown 20–25 m [S13]; Ceiba-style buttresses [S15] |
| acacia | 8–10 | NOT FOUND (style: 4–5) | 10–12 | 0.3–0.4 | Spread 8–13 m [S18]; flat-topped [S17] |
| cherry | 8–9 | 2–2.5 | 9 | 0.45 | Kanzan 8–12 m H, spread over 8 m [S20]; Hemery cherry 0.47 m → 9 m [S1] |
| mangrove | 10–12 | 4–5 (above roots) | 8–10 (not sourced) | 0.3–0.4 + roots 2–4 m tall | H, DBH and root height from [S21–S23] |

### Conflicts and decisions for Abs0lum
- **C1:** Real forest-grown oak (Q. petraea) has a long clear bole and a narrow, high crown. A realistic dark oak forest would therefore look *more* like "canopy high on a trunk", not less. Proposal: keep dark oak low and stylised, but tie its crown width to its trunk.
- **C2:** Two separate fixes exist: shrink the crowns, or thicken the visible trunks (0.5 → 0.75–1.0 m). The table uses some of both. Thicker trunks keep the big-canopy look while restoring believable proportions. Both changes are template and geometry edits and need checking in game.
- **C3:** Spruce crown ratio. Real forest spruce self-prunes, but no CR number was found. The CBH values above are proposals, not sourced figures.

---

## Sources
- [S1] Hemery, Savill & Pryor 2005, "Applications of the crown diameter–stem diameter relationship…" (Forest Ecology and Management): https://benfieldgroup.uk/wp-content/uploads/2021/09/Hemery_et_al_2005_kd_paper.pdf ; summary: https://gabrielhemery.com/blog/2011/05/23/estimating-tree-crown-size/ ; https://www.sciencedirect.com/science/article/abs/pii/S0378112705003373
- [S2] Martin et al., "Defining the allometry of stem and crown diameter of urban trees" (Urban Forestry & Urban Greening): https://irep.ntu.ac.uk/id/eprint/37525/1/14692_Martin.pdf
- [S3] Pretzsch et al. 2015, "Crown size and growing space requirement of common tree species in urban centres, parks, and forests": https://www.sciencedirect.com/science/article/pii/S1618866715000473
- [S4] Bechtold 2003, "Crown-diameter prediction models for 87 species of stand-grown trees" (USDA FS): https://www.srs.fs.usda.gov/pubs/ja/ja_bechtold004.pdf
- [S5] Sharma, Vacek et al. 2017, "Modelling tree crown-to-bole diameter ratio for Norway spruce and European beech" (Silva Fennica): https://www.silvafennica.fi/article/1740
- [S6] Woodland Trust, English oak: https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/british-trees/a-z-of-british-trees/english-oak/
- [S7] Management of sessile oak (Journal of Forestry Research 2025): https://link.springer.com/article/10.1007/s11676-025-01868-1
- [S8] Woodland Trust, silver birch: https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/british-trees/a-z-of-british-trees/silver-birch/
- [S9] "Towards Silviculture Guidelines to Produce Large-Sized Silver Birch Logs in Western Europe" (Forests 2021): https://www.mdpi.com/1999-4907/12/5/599
- [S10] Wikipedia, Picea abies: https://en.wikipedia.org/wiki/Picea_abies
- [S11] Kantola & Mäkelä 2004, Crown development in Norway spruce (not readable; rate-limited): https://link.springer.com/article/10.1007/s00468-004-0319-x
- [S12] Generalized nonlinear mixed-effects crown ratio models for Norway spruce and beech: https://www.mdpi.com/1999-4907/9/9/555
- [S13] "Tree size in a mature dipterocarp forest stand in Sebulu, East Kalimantan": https://kyoto-seas.org/pdf/23/4/230404.pdf
- [S14] Poorter et al. 2006, "Architecture of 54 moist-forest tree species" (Ecology): https://ibifbolivia.org.bo/wp-content/uploads/2022/09/2006-Poorter-et-al.-Architecture-of-54-spp-Ecology.pdf
- [S15] Wikipedia, Ceiba pentandra: https://en.wikipedia.org/wiki/Ceiba_pentandra
- [S16] Smithsonian figshare, BCI "Big tree" crown 61.3 m (title only): https://smithsonian.figshare.com/articles/media/The_BCI_Big_tree_had_a_world-record_average_crown_diameter_of_61_3_m_This_tree_is_illustrated_on_the_cover_of_i_The_First_100_Years_of_Research_on_Barro_Colorado_Island_Plant_and_Ecosystem_Science_i_/22823111
- [S17] FAO, Manual on taxonomy of Acacia species: https://www.fao.org/4/q2934e/q2934e05.htm
- [S18] Krugerpark, Umbrella thorn: https://www.krugerpark.co.za/africa_umbrella_thorn.html
- [S19] Winrock, Acacia tortilis fact sheet: https://winrock.org/factnet/fact-net-fact-sheets/acacia-tortilis-fodder-tree-for-desert-sands/ ; Wikipedia: https://en.wikipedia.org/wiki/Vachellia_tortilis
- [S20] RHS, Prunus serrulata 'Kanzan': https://www.rhs.org.uk/plants/151367/prunus-serrulata-kanzan/details
- [S21] USDA FS (Allen 2002), Rhizophora mangle: https://www.fs.usda.gov/psw/publications/allen/psw_2002_allen009.pdf
- [S22] Wikipedia, Rhizophora mangle: https://en.wikipedia.org/wiki/Rhizophora_mangle
- [S23] Useful Tropical Plants, Rhizophora mangle: https://tropical.theferns.info/viewtropical.php?id=Rhizophora+mangle
- [S24] Ancient Tree Forum, pollard article (QJF Oct 2012): https://www.ancienttreeforum.org.uk/wp-content/uploads/2017/03/Pollard-article-QJF-Oct-2012.pdf
