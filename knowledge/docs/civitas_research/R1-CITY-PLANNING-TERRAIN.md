# R1 — City Planning on Real Terrain: Research for the CIVITAS Settlement Generator

**Date:** 2026-10-03  
**Scope:** How real pre-industrial towns grew, zoned themselves and built on slopes, and what that implies for a Bedrock settlement generator at 1 block = 1 metre with fixed 13-wide street prefabs, 1-in-7 ramps, 7–20 m buildings and eight growth tiers.  
**Reading convention:** every paragraph is tagged **SOURCED** (fact with URL; numbers as the source gives them, my unit conversions marked "≈"), **COMPUTED** (a ratio I derived from two sourced numbers) or **PROPOSED** (my rule, with its derivation). Nothing PROPOSED or COMPUTED is a historical claim.

---

## 1. How real towns grew: stages, sizes, streets, plots, blocks

### 1.1 Stages and populations (SOURCED)

- **Hamlet → village.** Geographers put a village at "between 500 and 2,500 inhabitants"; in Italy a settlement "inhabited by less than 2000 people is usually described as 'village'"; by the old UK rule "a hamlet earned the right to be called a village when it built a church" ([Wikipedia: Village](https://en.wikipedia.org/wiki/Village)). A hamlet is "often fewer than 100" people ([Wikipedia: Settlement hierarchy](https://en.wikipedia.org/wiki/Settlement_hierarchy)). Owen's English hill-*town* definition "excludes villages with fewer than 2000 occupants and cities with more than 10,000" ([Wikipedia: Hill town](https://en.wikipedia.org/wiki/Hill_town)).
- **Village → market town.** "Domesday Book of 1086 lists 50 markets in England. Some 2,000 new markets were established between 1200 and 1349"; markets were spaced "a day's worth of travelling (approximately 10 kilometres)" apart; the form was "a wide main street or central market square" ([Wikipedia: Market town](https://en.wikipedia.org/wiki/Market_town)). Seigneurial town-founding peaked in the 12th–13th centuries; by the later 13th century saturation made many planted towns fail ([ORB: planted towns](https://the-orb.arlima.net/encyclop/culture/towns/townint5.html)).
- **Town sizes.** 13th-century German towns averaged "2,000-3,000 residents" and "only 50 cities exceeded 5,000"; typical walled cities enclosed "between 50 and 200 acres" (≈20–80 ha), Cologne "almost 1,000 acres" (≈405 ha); 14th-century London reached 30,000, Paris "70,000-80,000" ([Encyclopedia.com](https://www.encyclopedia.com/history/news-wires-white-papers-and-books/urban-fortifications-and-public-places)). Monpazier (1284/85) was built for "between 2000 and 2500 inhabitants" on "about 400 by 220 metres" ([michaeldelahaye.com](https://www.michaeldelahaye.com/monpazier.html); [French Moments](https://frenchmoments.eu/monpazier-dordogne/)).
- **City sizes.** Of "approximately 1,450 cities" in 14th-century Europe, ~60% were "small towns (2,000-6,000)", ~300–330 "regional centers (4,000-12,000)" and ~210 "large cities (8,000-12,000+)"; in 800 CE only 36 cities exceeded 2,000; "density increases with city population size" (Cesaretti et al., 173 walled cities) ([Jedwab et al., GWU](https://www2.gwu.edu/~iiep/assets/docs/papers/2020WP/JedwabIIEP2020-9.pdf)). In 1300 "there were just 5 cities over 100,000 in all of Europe: Paris, Milan, and Grenada at around 150,000, and Florence and Venice at around 100,000"; "most 'cities' are in the 8000 to 25000 population range"; 87 major cities averaged ~22,000, the next 118 ~12,000 ([Medium: Medieval population geography](https://medium.com/migration-issues/notes-on-medieval-population-geography-fd062449364f)).
- **Metropolis trajectory.** Florence: 1125 25,000; 1280 80,000; early 1300s ~100,000; the 1285–1333 circuit ran 8,500 m, enclosed 430 ha with 12 gates and was "five times larger than the previous enclosure" ([Castelli Toscani](https://castellitoscani.com/en/florence-city-walls/)); another source gives 630 ha and a series 2nd c. ~10,000 → 10th c. ~2,500 → early 13th c. ~50,000 → 1350 25–30,000 ([Florence Inferno](https://www.florenceinferno.com/florence-town-walls/)). Paris's Philip Augustus wall (1190–1213) "enclosed an area of 253 hectares", 77 towers at 60 m, 15 gates ([Wikipedia: Wall of Philip II Augustus](https://en.wikipedia.org/wiki/Wall_of_Philip_II_Augustus)).
- **Growth beyond the wall.** A *faubourg* is "an agglomeration forming around a throughway leading outwards from a city gate", named after the street inside the gate, usually on lower ground, later annexed and re-walled ([Wikipedia: Faubourg](https://en.wikipedia.org/wiki/Faubourg)); Bristol "had large suburbs ... in all directions" by the 13th century with successive wall lines ([ORB](https://the-orb.arlima.net/encyclop/culture/towns/townint5.html)).
- **Density (COMPUTED).** Monpazier 2,250 / 8.8 ha ≈ 256/ha; Florence 100,000 / 430 ha ≈ 233/ha (≈159/ha on 630 ha); Cologne ~40,000 / 405 ha ≈ 99/ha. A hobbyist synthesis built on the Paris tax list of 1292 and Russell/Pirenne gives "around 150 per hectare (61 per acre)" and bands village 20–1,000 (typically 50–300), town 1,000–8,000, city 8,000–12,000 ([Medieval Demographics Made Easy](https://gamingballistic.com/wp-content/uploads/2018/11/Medieval-Demographics-Made-Easy-1.pdf)) — secondary, not primary. Timgad's "15,000 planned" over its 12.6 ha core would be ~1,190/ha, so that figure must describe the later expanded city; not used.

### 1.2 Street widths and hierarchy (SOURCED)

| Context | Main / through | Secondary / cross | Lanes | Source |
|---|---|---|---|---|
| Roman Twelve Tables | 8 Roman ft (≈2.37 m) straight, double at curves; rural public roads ~12 Roman ft; measured 1.1–7.0 m | | | [Wikipedia: Roman roads](https://en.wikipedia.org/wiki/Roman_roads) |
| Roman colonies | Carthage axes 40 ft (11.76 m); Rimini cardo/decumanus ~9 m | Carthage 24 ft (7.06 m); Turin 5–8 m; Norba 4 m | | [MIT Press: Orthogonal Town Planning ch. 6](https://mitp-arch.mitpress.mit.edu/pub/s1g1tf3w) |
| Roman principal roads (Davies, ~500 routes) | average 6.5 m | | | [Designing Buildings](https://www.designingbuildings.co.uk/wiki/The%20history%20of%20the%20dimensions%20and%20design%20of%20roads,%20streets%20and%20carriageways) |
| Medieval organic towns | 12–15 ft (≈3.7–4.6 m) | 8–10 ft (≈2.4–3 m) | | [Encyclopedia.com](https://www.encyclopedia.com/history/news-wires-white-papers-and-books/urban-fortifications-and-public-places) |
| *Via regia*, England 1114–18 | room for "two waggons" to pass and "16 armed knights to ride side by side" | | | [Designing Buildings](https://www.designingbuildings.co.uk/wiki/The%20history%20of%20the%20dimensions%20and%20design%20of%20roads,%20streets%20and%20carriageways) |
| Bastides | 6–10 m "so a chariot could pass"; Monpazier's two principal streets 8 m for carts to pass on market days | alleys 5–6 m | 2–2.5 m | [Wikipedia: Bastide](https://en.wikipedia.org/wiki/Bastide); [michaeldelahaye.com](https://www.michaeldelahaye.com/monpazier.html) |
| Bern (1191) | Gerechtigkeitsgasse "around 26 meters, reduced to 18 meters after the construction of the arcades", 260 m long | | narrow cross alleys | [Wikipedia: Gerechtigkeitsgasse](https://en.wikipedia.org/wiki/Gerechtigkeitsgasse) |
| Savannah (1733) | 75 ft (≈22.9 m); 45–120 ft between wards | 37½ ft (≈11.4 m) | 22½ ft (≈6.9 m) | [NPS](https://www.nps.gov/articles/savannah-georgia-the-lasting-legacy-of-colonial-city-planning-teaching-with-historic-places.htm); [Wikipedia: Oglethorpe Plan](https://en.wikipedia.org/wiki/Oglethorpe_Plan) |
| Edinburgh New Town (1767) | George Street "115 feet wide" (Skrine 1813); central street 100 ft | outer and cross streets 80 ft (≈24.4 m) | mews 30 ft (≈9.1 m) | [Georgian Cities](https://18thc-cities.sorbonne-universite.fr/The-New-Town-of-Edinburgh-James.html); [Designing Buildings](https://www.designingbuildings.co.uk/wiki/The%20history%20of%20the%20dimensions%20and%20design%20of%20roads,%20streets%20and%20carriageways) |
| Manhattan 1811 | avenues 100 ft (≈30.5 m); 15 cross streets 100 ft | 60 ft (≈18.3 m) | | [MCNY: Greatest Grid](https://thegreatestgrid.mcny.org/greatest-grid/making-the-plan/12) |
| Paris, Rue Rambuteau (1838) | 13 m, "an important dimension for the time" | | | [Wikipedia: Rue Rambuteau](https://en.wikipedia.org/wiki/Rue_Rambuteau) |
| Eixample (1859) | 20, 30 and 60 m | | | [Wikipedia: Cerdà Plan](https://en.wikipedia.org/wiki/Cerd%C3%A0_Plan) |
| English bye-laws 1877 / London 1894 | 36 ft (≈11 m) min, 24 ft (≈7.3 m) carriageway; 40 ft from 1894 | | back streets 13–16 ft (≈4–4.9 m); footway ≤ 1 in 24 | [Designing Buildings](https://www.designingbuildings.co.uk/wiki/The%20history%20of%20the%20dimensions%20and%20design%20of%20roads,%20streets%20and%20carriageways) |

**Where our prefabs sit (COMPUTED):** the 13-block corridor equals Rue Rambuteau (13 m) and the 1877–94 bye-law street (11–12.2 m); the 7-block roadway is the bye-law 24-ft carriageway (7.3 m) and the Carthage colonial street (7.06 m); the 5-block side roadway matches bastide alleys (5–6 m) and Turin's Roman streets (5–8 m). The corridor is 2–3× any medieval organic main street and about half a Georgian or Cerdà avenue. What we lack is the 2–5 m lane class every pre-industrial town had.

### 1.3 Plots: frontage and depth (SOURCED)

- Hungerford (c. 1250): plots "about 11 yards wide (which was two rods or poles)", "approximately 110 yards" deep, "¼ acre"; about 130 plots along a 700-yard High Street; width "dictated by the maximum practical length of an oak house beam" ([Hungerford Virtual Museum](https://www.hungerfordvirtualmuseum.co.uk/index.php/10-themes/954-burgage-plots)). COMPUTED: ≈9.8 m frontage × 101 m depth.
- Alnwick: Conzen found properties "roughly 28 feet wide" (≈8.5 m); plots were "usually laid out to a standard width of two or three perches" (perch 16½ ft ≈ 5.03 m) ([Alnwick Civic Society](https://alnwickcivicsociety.org.uk/2020/09/11/rods-poles-and-perches/)). Winchester's 9th-century properties were "each about two perches in width"; Wells was laid out in "chequers" of "around 170 metres square" ([Haslam](https://www.academia.edu/38721877/The_articulation_of_burgages_and_streets_in_early_medieval_towns_pt_2)).
- Scottish burghs: Perth 5.5–6.4 m; St Andrews 8.5–11.6 m; Edinburgh "7.6m in width and 137m in length"; Aberdeen 5.5–6.0 m; depths c. 130 m (long) and c. 73 m (short) ([Coleman](https://scispace.com/pdf/the-archaeology-of-burgage-plots-in-scottish-medieval-towns-g1tih1rxk1.pdf)).
- Bastides: "8 m (26 ft) by 24 m (79 ft) being a common size" ([Wikipedia: Bastide](https://en.wikipedia.org/wiki/Bastide)). Wrocław (c. 1232): "Each plot was 60 feet wide (18.78 meters), with a depth of 120 feet (37.56 meters) for the shorter frontages and 240 feet (75 meters) for the longer ones"; 36 plots around a 213 × 178 m square; "Eleven streets lead to the market: two to each corner" ([Wikipedia: Market Square, Wrocław](https://en.wikipedia.org/wiki/Market_Square,_Wroc%C5%82aw)).
- Savannah lots "60 feet in width and 90 feet in depth" (≈18.3 × 27.4 m), ten per tything; trust lots 180 × 60 ft ([NPS](https://www.nps.gov/articles/savannah-georgia-the-lasting-legacy-of-colonial-city-planning-teaching-with-historic-places.htm)). Manhattan: "A standard lot became 100 feet deep (half of the block depth) and 20 or 25 feet wide" ([RentHop](https://www.renthop.com/blog/how-long-is-a-block/)).
- Back lanes "ran parallel to the main street at the other end of burgage plots" and "divided the village from ... the open fields" ([Wikipedia: Back lane](https://en.wikipedia.org/wiki/Back_lane)).

### 1.4 Block sizes in planned towns (SOURCED)

| Plan | Block between parallel streets | Notes | Source |
|---|---|---|---|
| Roman colonies | Norba, Cosa 1 actus (32.5–37 m) × ~82 m; Rimini 74 × 110; Piacenza 80 square; Bologna 113.66 × 80; Parma 45 × 55; Florence 60 square; Verona 75–80; Aosta 70–80 within 724 × 572 m; Carthage 35.28 × 141.12 (1 × 4 actus) | actus = 120 Roman ft ≈ 35.5 m; Polybius' via principalis 100 ft | [MIT Press ch. 6](https://mitp-arch.mitpress.mit.edu/pub/s1g1tf3w) |
| Timgad (AD 100) | insulae "around 70 by 70 Roman feet (21 by 21 m)" in a 355 m square | forum 8 insulae, theatre 4, baths 7 | [Socks Studio](https://socks-studio.com/2017/06/21/a-perfect-grid-the-roman-town-of-timgad-the-african-pompeii/) |
| Monpazier (1284) | 400 × 220 m; streets parallel to the long sides; "Four transversal streets divide Monpazier into rectangular blocks" | bastide squares 50–55 m per side (Tournay 70 × 72) | [French Moments](https://frenchmoments.eu/monpazier-dordogne/); [Wikipedia: Bastide](https://en.wikipedia.org/wiki/Bastide) |
| Kraków (1257) | square 3.79 ha; "three, evenly spaced streets set at right angles" from each side | | [Wikipedia: Main Square, Kraków](https://en.wikipedia.org/wiki/Main_Square,_Krak%C3%B3w) |
| Laws of the Indies (1573) | plaza 200 × 300 to 530 × 800 *pies*, ideal 600 × 400 (≈167 × 111 m; range ≈56 × 84 to 148 × 223 m), length ≥ 1.5 × width; four streets from the middles of the sides and two from each corner, sheltered from "the four principal winds"; "In cold places, the streets shall be wide and in hot places narrow" | | [HUD PDF](https://www.huduser.gov/portal/sites/default/files/pdf/The-Laws-of-the-Indies.pdf); [TU Delft IPHS](https://journals.open.tudelft.nl/iphs/article/download/2720/2931/7656) |
| Savannah ward (1733) | 675 ft (≈206 m) square, ≈10 acres; 4 tythings × 10 lots + 4 trust lots around a square; "approximately 50% developable area and 50% public area"; 6 wards first, 24 eventually | | [Wikipedia: Oglethorpe Plan](https://en.wikipedia.org/wiki/Oglethorpe_Plan); [NPS](https://www.nps.gov/articles/savannah-georgia-the-lasting-legacy-of-colonial-city-planning-teaching-with-historic-places.htm) |
| Edinburgh New Town | ridge street linking two squares, two parallel main streets downhill, two mews between | | [Wikipedia: New Town](https://en.wikipedia.org/wiki/New_Town,_Edinburgh) |
| Manhattan 1811 | "all blocks are 200 feet north to south" (≈61 m); east–west 620–920 ft (≈190–280 m); streets 1–155 | ~20 streets or 6–7 avenues per mile | [MCNY](https://thegreatestgrid.mcny.org/greatest-grid/making-the-plan/12); [RentHop](https://www.renthop.com/blog/how-long-is-a-block/) |
| Eixample (1859) | 113.3 m squares, 15 m chamfers, 1.24 ha; 1,100 ha; height cap 16 m | pitch ≈133 m | [Wikipedia: Cerdà Plan](https://en.wikipedia.org/wiki/Cerd%C3%A0_Plan) |

**Pattern (COMPUTED):** pre-industrial blocks cluster at 35–80 m between parallel streets; a bastide block is two 24 m lots back-to-back (≈48 m); 19th-century grids run 61 m (Manhattan) to 113 m (Eixample). A bastide had "usually between one and eight streets" ([Wikipedia: Bastide](https://en.wikipedia.org/wiki/Bastide)).

---

## 2. Districts and zoning (SOURCED)

- **Centre = market, church, civic.** Laws of the Indies: the church gets "a complete block so as to avoid having other buildings nearby" (Ord. 119); the contagious hospital is sited so "no harmful wind blowing through it may cause harm to the rest of the town" (Ord. 121); "slaughter houses, fisheries, tanneries, and other business which produce filth shall be so placed that the filth can easily be disposed of" (Ord. 122); a commons "large enough that although the population may experience a rapid expansion, there will always be sufficient space" (Ord. 129); farm lots "as many in number as the lots in the town" (Ord. 130) ([HUD PDF](https://www.huduser.gov/portal/sites/default/files/pdf/The-Laws-of-the-Indies.pdf)). Each Savannah settler got "one town lot, a five acre garden plot" and "a 45-acre farm" ([NPS](https://www.nps.gov/articles/savannah-georgia-the-lasting-legacy-of-colonial-city-planning-teaching-with-historic-places.htm)).
- **Clean trades in, dirty trades out.** "Luxury trades occupied the best locations, while poorer ones or those that were handicapped by noise and bad smells or presented a fire hazard were relegated to the periphery"; near the gates "the makers of saddles and those of pack-saddles ... the vendors of victuals brought in from the country"; on the periphery "the dyers, the tanners, and almost outside the city limits, the potters"; market streets ran "up to one mile long" ([Encyclopaedia Iranica: Bāzār ii](https://iranicaonline.org/articles/bazar-ii)). Tunis: the perfumers' souk (1240) "is located just behind the Al-Zaytuna Mosque", cloth on its west façade, while the dyers' souk "is located on the outskirts of the medina ... because dyeing is considered a polluting activity" ([Wikipedia: Souks of Tunis](https://en.wikipedia.org/wiki/Souks_of_Tunis)). Fez: main souk streets "run from the city's main gates to the area of the city's main mosque", produce and butchers at the gate end, spices (150–170 shops) by the mosque; residential *derbs* branch off, "many of them leading to dead-ends" ([Wikipedia: Tala'a Kebira](https://en.wikipedia.org/wiki/Tala%27a_Kebira)). The Chouara tannery lies "along the Oued Fes"; Fez had 86 tanneries under the Almohads, ~100 under the Marinids ([Wikipedia: Chouara Tannery](https://en.wikipedia.org/wiki/Chouara_Tannery)).
- **Europe, same logic via waste rules.** "Medieval laws restricted them [slaughterhouses, tanneries, dye works] to specific districts near rivers, often downstream from the drinking supply"; "Blacksmiths, fullers, and lime burners were sometimes pushed outside the walls" ([Popular Archaeology](https://popular-archaeology.com/article/inside-a-medieval-city-public-health-housing-and-everyday-regulations/)). York's tanners sat upstream near the river's entrance but could not wash skins "above Pudding Holes because of 'corruption of the water of Ouse'"; in 1371 butchers got a pier "downstream of the Friars for washing their entrails"; Norwich surcharged "barkers, dyers, calaundrers, parchementmakers, tewers, sadelers, brewers, wasshers of shepe" — towns regulated *where waste went* more than where shops stood ([Jørgensen](https://dolly.jorgensenweb.net/files/Jorgensen_Responses_to_urban_river_pollution_postprint.pdf)). Guild streets were normal: "a 'Tanners street,' a 'Saddlers street,' etc." ([Medieval Spell](https://www.medieval-spell.com/Medieval-Towns/)). York's Shambles (400 ft) still had 31 butchers in 1885; its shade kept meat fresh and offal "thrown into the street runnels that had a natural slope" washed away ([Wikipedia: The Shambles](https://en.wikipedia.org/wiki/The_Shambles)).
- **Edge:** back lanes mark the field boundary ([Wikipedia: Back lane](https://en.wikipedia.org/wiki/Back_lane)); faubourgs grow along the roads from each gate ([Wikipedia: Faubourg](https://en.wikipedia.org/wiki/Faubourg)).

---

## 3. Building on slopes

### 3.1 Terraces and retaining walls (SOURCED)

- Inca *andenes*: "retaining wall, which might rise about 2 metres (6.6 ft) above the slope", foundation "about 1 metre deep", fill in ~1 m layers of large stones, sand/gravel, topsoil; Colca Valley platforms average "3 metres wide"; ~1,000,000 ha terraced ([Wikipedia: Andén](https://en.wikipedia.org/wiki/And%C3%A9n)). Tipón's 13 main terraces have walls "from 1 metre to 5 metres, with an average height of 2.5 metres to 3 metres" ([Wikipedia: Tipón](https://en.wikipedia.org/wiki/Tip%C3%B3n)). Inca roads "about one to four meters wide" ([Wikipedia: Inca technology](https://en.wikipedia.org/wiki/Inca_technology)). Machu Picchu has "approximately 200 structures" on a terraced ridge in ~2,000 mm/yr rain ([Machu Picchu Soul](https://machupicchusoul.com/blog/machu-picchu-terraces/)); the ">60% underground" claim appears only as a reader comment in the source reached — unverified ([Années de Pèlerinage](https://www.annees-de-pelerinage.com/machu-picchu-architecture-explained/)).
- Cinque Terre: "6,720,000 meters" of dry-stone wall, "8,400,000 cubic meters", ~2,000 ha ([Le Cinque Terre](https://www.lecinqueterre.org/eng/murettiasecco.php)); "3,163 linear metres of wall per hectare", "2 metres high" ([Cinque Terre Consorzio](https://www.cinqueterre.it/en/the-cinque-terre/storia/)). COMPUTED: mean terrace width ≈ 3.2 m.
- Bench-terrace design: hand-built terraces suit "7 degrees to 25 degrees (or 12.3% to 46.6%)"; benches 2.5–5 m (hand) or 3.5–8 m (machine); riser "should not exceed 1.8 m to 2 m"; batter 0.5:1 for stone; VI = S·Wb/(100 − S·U); max 100 m drainage length ([Sheng](https://topsoil.nserl.purdue.edu/isco/isco12/VolumeIV/BenchTerraceDesignMadeSimple.pdf); [FAO](https://www.fao.org/4/ad083e/ad083e07.htm)). COMPUTED: a 4 m stone bench on 30% needs a 1.41 m riser; 3 m on 45% needs 1.74 m.
- Modern limits: IBC permit for retaining structures "over 4 ft (1.2 m)"; unreinforced segmental walls "up to 3 to 4 ft (1.0 – 1.2 m)"; terraced walls independent only if setback "at least equal to twice the height of the lower wall (D > 2H1)" ([CMHA](https://www.cmha.org/resource/srw-faq-001/)). San Diego: steep hillside = "natural gradient of at least 25 percent ... and a vertical elevation of at least 50 feet"; "maximum height for a single retaining wall ... shall be 10 feet"; above that, stepped walls "no individual wall height exceeding 6 feet" with "a minimum horizontal distance of 3 feet" between; some communities ban building on "steep hillsides fifty percent or greater" ([San Diego PDF](https://www.sandiego.gov/sites/default/files/legacy/development-services/pdf/industry/landdevmanual/ldmsteephillsides.pdf)). Phoenix's hillside ordinance starts at 10% slope and cuts density from 1.80 dwellings/acre (10–14.9%) to 0.20 (35%+) ([Phoenix ZO §710](https://phoenix.municipal.codes/ZO/710)).

### 3.2 Hill, cliff, cave and stilt settlements (SOURCED)

- Doctrine: Lynch — "on a gentle slope the building lines can follow the horizontal contours, on a steep slope the building line should 'plunge' across the contour"; Norberg-Schulz — a promontory "suggests a cluster-like arrangement"; "In Italy, hill towns comprised about half of the important towns in the Middle Ages" ([Wikipedia: Hill town](https://en.wikipedia.org/wiki/Hill_town)). Italian builders let "roads to curve around slopes, stairways to climb between houses", with "retaining walls to hold back the earth, and buildings to rise at different levels" ([Architecture & Tradition](https://www.architectureandtradition.com/p/what-made-the-italian-hill-town-so)).
- Positano rises "from sea level to elevations over 400 meters"; "many staircases ... connect the upper districts with the valley" ([Wikipedia: Positano](https://en.wikipedia.org/wiki/Positano)). Santorini: people "built staircase downhill, and then dug cave houses into the rather soft tufa"; a *yposkafo* "consisted of a single room" with a cistern, homes of "the poor and the crew members of ships" ([Showcaves](https://www.showcaves.com/english/gr/topics/Santorini.html)), dug "deep enough to be anchored into the underlying rock" ([Hole in the Donut](https://holeinthedonut.com/2018/08/21/cave-architecture-of-santorini-oia/)).
- Cuenca's Hanging Houses (15th c.) overhang "the ravine of the river Huécar" on "wooden balconies" ([Wikipedia](https://en.wikipedia.org/wiki/Hanging_Houses_of_Cuenca)). Bonifacio (828): cliff-tops "at about 70 meters"; buildings "placed on the very lip of the precipice, appear to overhang it" ([Wikipedia: Bonifacio](https://en.wikipedia.org/wiki/Bonifacio,_Corse-du-Sud)). Lhasa's Potala rises "117 metres on top of Marpo Ri ... more than 300 m in total above the valley floor", 400 × 350 m, 13 storeys, "sloping stone walls averaging 3 m. thick, and 5 m. ... at the base" ([Wikipedia: Architecture of Lhasa](https://en.wikipedia.org/wiki/Architecture_of_Lhasa); [Potala Palace](https://en.wikipedia.org/wiki/Potala_Palace)) — a building whose battered walls *are* the retaining structure.
- *Diaojiaolou*: "Typically two to three storeys high"; on mountainsides "the front ... is held up by pillars but the rear of the house is suspended on wooden poles, making it level with the mountainside"; the open ground floor is stable/storage ([Asia Cultural Travel](https://www.asiaculturaltravel.co.uk/diaojiaolou/)); built "close to the mountain or above the water" with "only supporting wood pillars and no foundation" ([ChinaBlog](https://chinablog.cc/diaojiaolou-stilted-building-in-southwestern-china/)). Fenghuang's stand "on the stilts of different heights", front "a storied building built on the ground", rear "a bungalow", built against "the spring floods" ([Zhangjiajie Tourism](https://www.cn-zhangjiajie.com/view-40-348.html); [China Highlights](https://www.chinahighlights.com/fenghuang/)).
- Stair streets give "access up and down a slope that is too steep for automobiles"; New York 102, Pittsburgh "over 700", Rue Foyatier "over 250 steps", San Francisco 600 ([Wikipedia: Step street](https://en.wikipedia.org/wiki/Step_street)). San Francisco's old rule: "no new street shall exceed 25 percent grade"; steepest paved 31.5–37% ([Datapointed](https://www.datapointed.net/2009/11/the-steeps-of-san-francisco/)); world extremes 34.8–41% ([Wikipedia: Grade](https://en.wikipedia.org/wiki/Grade_(slope)); [steepest roads list](https://en.wikipedia.org/wiki/List_of_steepest_roads_and_streets)). Stair codes "prefer an angle of around 37°"; "around 7° for ramps" is the ramp/stair boundary ([InspectApedia](https://inspectapedia.com/Stairs/Stair-Angle-Slope-Specifications.php)). ADA ramps 1:12 (8.33%), 30 in rise per run, 60 in landings ([Express Ramps](https://expressramps.com/learn/codes/ada-ramp-slope)). Accessible trails: 1:20 any distance; 1:12 for 200 ft; 1:10 for 30 ft; 1:8 for 10 ft; never steeper than 1:8 ([FSTAG 2013](https://www.fs.usda.gov/sites/default/files/FSTAG-2013-Update.pdf)).

### 3.3 Cart-road grades and switchbacks (SOURCED)

| Standard | Grade / geometry | Source |
|---|---|---|
| Roman roads | "Gradients of 10%–12% are known in ordinary terrain, 15%–20% in mountainous country"; roads cut "through the hill, rather than with a serpentine pattern of switchbacks" | [Wikipedia: Roman roads](https://en.wikipedia.org/wiki/Roman_roads) |
| Hardknott Pass (Roman AD 110 route) | "1 in 3 (about 33%)" | [Wikipedia: Hardknott Pass](https://en.wikipedia.org/wiki/Hardknott_Pass) |
| Telford, Holyhead Road | aim "maximum gradient would not exceed 1 in 20"; Nant Ffrancon 1 in 22 | [Cycling North Wales](https://www.cyclingnorthwales.co.uk/pages/thom_tel_rd.htm) |
| Telford, Glencoe | "averaging 1 in 20"; 5–6 m wide | [Roads.org.uk](https://www.roads.org.uk/articles/three-generations-a82/telfords-road) |
| Macadam roads, US 1901 | "most highway engineers specify a maximum grade of 1 to 30"; tractive force per ton: level 38 lb, 1 in 100 58 lb, 1 in 30 104 lb, 1 in 10 238 lb | [Georgia Geological Survey 1901](https://epd.georgia.gov/document/publication/b-8-preliminary-report-roads-and-materials-georgia-1901/download) |
| Alpine carriage roads | Simplon 1801–1805; Stelvio 1820–25, "48 mostly tight hairpin turns" on 28 km, climbing 1,871 m | [Wikipedia: Simplon](https://en.wikipedia.org/wiki/Simplon_Pass); [Stelvio](https://en.wikipedia.org/wiki/Stelvio_Pass) |
| IRC 52:2019 hill roads | mountainous ruling 5%, limiting 7%, exceptional 8%; steep 7/8/10%; hairpin inner radius ≥ 14 m, 11–12 m wide, ≤ 2.5% grade in the bend, ≥ 60 m (90 preferred) between hairpins; carriageways 3.75 / 7.0 m | [Infralens](https://infralens.in/code/IRC-52-2019); [Testbook](https://testbook.com/civil-engineering/hill-roads) |
| IRC plain/rolling | ruling 3.3%, limiting 5%, exceptional 6.7% | [EssaySauce](https://www.essaysauce.com/architecture-essays/gradients-special-consideration-for-hill-roads/) |
| US highways | 6%, exceptionally 7% | [Wikipedia: Grade](https://en.wikipedia.org/wiki/Grade_(slope)) |
| Hairpins, EU/Swiss/Italian | inner radius 5.30 m (Directive 2002/7/EC) to 6.05 m; outer 12.50 m; "less than 20 km/h"; 7–8.5 m wide | [MDPI](https://www.mdpi.com/2412-3811/7/9/112) |
| Trails (USFS) | climbing turns on ≤ 15–20% side-slope, radius 4–6 m; switchbacks where steeper, radius 1.5–3 m, platform ≤ 5%, tread widened 0.5–1 m; fill below the turn "at least as much as excavated from the upper side" | [FHWA/USFS](https://www.fhwa.dot.gov/environment/recreational_trails/publications/fs_publications/00232839/page10.cfm) |
| Street corners | 1.5 m curb radii preferred; > 5 m "should be the exception" | [GDCI](https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/corner-radii/) |

### 3.4 Where our 1-in-7 ramp sits (COMPUTED)

1 in 7 = 14.29% = 8.1°; the 4-block ramp section is locally 25% (14°), San Francisco's historical new-street cap.

| Reference | Grade | Ours ÷ reference |
|---|---|---|
| Macadam max (1 in 30) | 3.3% | 4.3× steeper |
| Telford, IRC mountainous ruling | 5% | 2.9× |
| IRC mountainous limiting | 7% | 2.0× |
| ADA ramp | 8.3% | 1.7× |
| IRC steep exceptional | 10% | 1.4× |
| Roman ordinary terrain | 10–12% | 1.2–1.4× |
| Ramp/stair boundary (7°), FSTAG max (1:8) | 12.3–12.5% | 1.15× |
| **Our ramp** | **14.3%** | 1.0 |
| Roman mountain roads | 15–20% | 0.7–0.95× |
| SF new-street cap | 25% | 0.57× |
| Hardknott / steepest paved streets | 33–41% | 0.35–0.43× |

A 1-in-7 street is steeper than any engineered carriage road of the last three centuries and just above the grade where real design switches from ramps to stairs, but inside the Roman mountain range and far below tolerated street extremes. It is credible as a side street or short connector, not as a sustained main-street grade.

---

## 4. Rules for the generator (PROPOSED unless marked)

Units: blocks (= metres). Corridor C = 13. Ramp unit U = 7 blocks per 1 block rise. S = terrain slope (rise/run) over the footprint considered.

### 4.1 Block size and street pitch

- **Pitch between parallel streets (centre to centre): P = 60** from Town upward. Derivation: a double-loaded block = two building depths (7–20) + 2–3 yard each = 20–46; plus C = 13 → 33–59. 60 fits the deepest buildings and keeps the 47-block clear interior inside the historical 35–80 m band (Roman colonies, bastides ≈48, Manhattan 61) and under Eixample's 113.
- **Village tiers:** one or two parallel streets only; give each house a 20–30 garden strip behind (Hungerford's 100 m burgage depth, scaled) and a 5-wide back lane only when a second row is needed.
- **Cross-street spacing along a street: L = 60–90** (block long side 1–1.5× short side; Monpazier's four transverse streets over 400 m ≈ 80–100 m; Roman strigas 1:2–1:4). Use 90 while filling, insert mid-block cross streets to reach 60 on tier-up.
- **Lane class (new prefab recommended):** a 5-wide pedestrian lane/stair without sidewalks (1-wide drain instead of a sewer) reproduces the 2–5 m class (andrones, bastide alleys, bye-law back streets) and lets blocks split at 30 without spending a 13-wide corridor.

### 4.2 When to open a new cross street

Open a T or crossroads when any of these holds:
1. Buildable frontage on both sides of a segment is ≥ 80% occupied and the segment exceeds 90.
2. A new platform cannot be reached from an existing sidewalk within 20 blocks of walking; then add a *derb*-style cul-de-sac ≤ 60 long ending in a 13 × 13 turning square.
3. A tier-up needs more frontage than the network offers (4.9). Order of additions: extend the main street → parallel back street at pitch 60 → cross streets at 60–90 → second main street (grid). This is Monpazier's sequence (longitudinal streets first, transverse second) and Bern's (three parallel streets, cross alleys later).
4. Growth reaches an edge/gate: start a faubourg — one street continuing the main axis outside the edge, houses both sides — then connect it back with cross streets later.

### 4.3 Street direction relative to contours

- **S ≤ 1/14 (7%)**: free orientation; align to the regional road or river. Streets may run straight up-slope with one ramp unit per 14 blocks (sustained 7%, IRC limiting, below Roman 10–12%).
- **1/14 < S ≤ 1/7**: main streets along contours (flat); side streets perpendicular at natural grade, one ramp unit per 7–14 blocks; earthwork minimal (Lynch's gentle-slope rule).
- **1/7 < S ≤ 0.45**: terrace-and-switchback regime. All through corridors run along contours on flat benches; vertical links are switchback legs along the contour (4.6) or stair streets across it (4.7). No 13-wide corridor runs perpendicular to the contour. This is the FAO bench-terrace band (12–47%) and the band where hill towns let stairs "plunge" while roads curve.
- **S > 0.45**: no streets; cave/stilt/cliff buildings reached by stairs. Above S ≈ 1.0 nothing but the lip row of the bench above.

### 4.4 Maximum grade per street class

| Class | Sustained grade | Max continuous ramp | Notes |
|---|---|---|---|
| Main (7-wide roadway) | ≤ 1 in 14 (ramp unit every 14) | 42 (3 units), then ≥ 14 flat | IRC limiting 7%; keeps frontages usable |
| Side (5-wide roadway) | ≤ 1 in 7 | 42 (6 units, rise 6), then 13 flat landing | native prefab grade; Roman mountain range |
| Switchback leg | exactly 1 in 7 | 42 per leg | 4.6 |
| Lane / stair street | 1 rise per 1–2 run (50–100%) | 14 risers, then 3-deep landing | 37° stair preference; landing per ADA/FSTAG |
| T, crossroads, elbow | 0 | — | IRC ≤ 2.5% in hairpins; trail platforms ≤ 5% |

Frontages sit only on flat pieces; ramp segments carry no doors.

### 4.5 Terracing per building

- **Platform:** footprint + 1-block margin on three sides, flush with the sidewalk at the front.
- **ΔH = S × (depth + 1)** across the platform:
  - ΔH ≤ 2: one level; cut ≤ 2 (FAO riser; Inca ≈ 2 m), fill ≤ 2 behind a 1-wide stone wall.
  - 2 < ΔH ≤ 4: split level, two steps ≤ 2 each (uphill cut, downhill fill); the house gets a one-storey offset.
  - 4 < ΔH ≤ 6: stilts (4.7) or cave house; no fill.
  - ΔH > 6: no building; stair or garden terrace instead.
- **Walls:** single wall ≤ 3 (San Diego 10 ft; Tipón 2.5–3 m average); taller retention stepped in ≤ 2 lifts with ≥ 3-block setbacks (San Diego ≥ 3 ft; CMHA D > 2H → use 4 when space allows). Garden terraces: wall ≤ 2, bench 3–5 (Inca 3 m; FAO 2.5–5 m).
- **Bench arithmetic (COMPUTED):** bench = 13 + depth (7–20) + 2 = 22–35; natural rise between adjacent benches = S × bench — on 30% with a 33 bench ≈ 10, far above a 3 wall. So above S ≈ 1/7 a bench is *street bench (13, wall ≤ 3) + building stepping down behind it*, the Positano/Oia section where one roof is the next terrace. A flat 13 corridor alone has cross-fall 3.9 on 30% (cut 2, fill 2) and 5.9 on 45% (3 wall each side) — the practical ceiling for the prefab.

### 4.6 Switchback geometry in blocks

- **Form:** elbow + optional straight + elbow → two parallel legs. **Leg separation** centre-to-centre 20 (13 corridor + 7 gap for a 2–3 wall and a 5 stair short-cut); pair footprint 33 wide. Zero gap (26) for metropolis cores; 13 gap (39) if a house row goes between legs.
- **Rise per leg:** legs run along the contour at 1 in 7. The ground along a contour is level, so a leg rising R sits R/2 below grade at its low end and R/2 above at its high end if centred on its mid-level (plus half-corridor cross-fall 6.5·S). With walls ≤ 3: **R ≤ 6 per leg → leg = 42 (6 units)**; a hairpin pair climbs 12 in a 55 × 33 footprint; a stack of n pairs climbs 12n.
- **Flat pieces:** both elbows flat; one flat 7 piece as a landing before each elbow (IRC ≤ 2.5% in bends; FSTAG resting intervals). Successive hairpins ≥ 42 apart (IRC 60 m, scaled to our shorter legs).
- **Reality check:** real cart hairpins have 5.3–14 m inner radii and 7–12 m widths; our right-angle elbow has radius 0 and relies on the landing — fine at villager speed, equivalent to the 1.5–3 m trail switchback.
- **Connector choice:** rise ≤ 3 → one straight 1-in-7 side ramp (21) across the contour if S ≤ 1/7, else a stair street; rise 4–12 → one hairpin pair; rise > 12 → stair street always, hairpin stack only at City tier and above (footprint and sewer cost).

### 4.7 Stilt, cave and cliff houses

- **Stilts (diaojiaolou rule):** 4 < ΔH ≤ 6 (S ≈ 0.25–0.45 for a 15-deep house), or any bench within 2 blocks of water level. Rear on the bench at sidewalk level; front on 1-wide posts (height ΔH ≤ 6) standing on stone footings; open under-floor is storage/stable.
- **Cave house (Santorini rule):** S > 0.45 in diggable stone/tuff/terracotta: a one-room house cut 7–10 into the slope, façade wall only, flat roof = terrace of the house above, stair-street access; stack ≤ 3.
- **Cliff-lip house (Bonifacio/Cuenca rule):** where a bench ends in a drop ≥ 10 with S > 1.0 beyond, the last row may stand flush with the lip and cantilever 1–2 blocks of balcony; nothing below.
- **No-build:** S > 1.0 elsewhere; any platform needing > 3 of fill.

### 4.8 District assignment (from Town tier)

1. **Square** at the first crossroads of the main street: 20–33 per side at Town (bastide 50–55 m scaled), up to 55 × 83 at City+ (Indies minimum 200 × 300 *pies*), ratio 1:1.5. Church on its own block beside the square; civic hall on the square.
2. **Prestige ring** (first 60 blocks of main street): cloth, spices/apothecary, goldsmith, scribe, inns (Tunis/Fez/Iranica).
3. **Market-craft ring** (60–150 out, and cross streets): bakers, carpenters, masons, tailors, shoemakers.
4. **Gate ring** (last 60 before each edge): saddlers, carters, livestock, produce market, travellers' taverns.
5. **Noxious band:** smiths, potters, lime/charcoal burners outside the built edge downwind (east if no wind convention), ≥ 40 from the square; tanners, dyers, slaughter yards, fulling on the *downstream* bank outside the core; butchers' retail may stay central on a narrow shaded lane with a sloped runnel (Shambles); pest-house and cemetery downwind at the edge (Ord. 121).
6. **Fields and commons:** one farm plot per town house (Ord. 130); 5-block garden strips behind village houses (Savannah gardens scaled); a ≥ 30 commons band reserved for growth (Ord. 129); back lanes mark the field edge.
7. **Castle/palace:** highest point within 150 of the square (Potala logic); else the square's long side.

### 4.9 Tier targets: real anchors, game targets, scale factor

**Real anchors (SOURCED §1; "houses" = population ÷ 5, an assumption not sourced here):**

| Tier | Real population | Real area | Real houses | Real through streets (grid-equivalent, 70 m pitch, COMPUTED) |
|---|---|---|---|---|
| Village | 100–500 (typ. 300) | 2–5 ha | ~60 | 1 + back lane |
| Village II | 500–1,000 | 5–8 ha | ~160 | 2–3 |
| Town | 1,000–2,500 (Monpazier; German avg 2,000–3,000) | 8–12 ha | ~450 | 4–8 ("one to eight" in bastides) |
| Town II | 2,500–6,000 (Jedwab small towns) | 15–40 ha | ~900 | 8–16 |
| City | 6,000–12,000 (regional centres / large cities) | 40–80 ha (typical walled 20–80) | ~2,000 | 16–30 |
| Upgraded city | 12,000–30,000 (Florence 1125; major cities avg 22,000) | 80–250 ha (Paris 1213 = 253) | ~4,400 | 30–60 |
| Metropolis I | 30,000–60,000 (Cologne ~40,000 / ≈405 ha) | 250–450 ha | ~9,000 | 60–120 |
| Metropolis II | 80,000–150,000 (Florence/Venice; Paris/Milan 1300) | 430–650 ha (Florence 1333) | ~20,000 | 120–250 |

**Game targets (PROPOSED).** The game holds hundreds to low thousands of structures in total, so I set a global budget of ≈1,500 loaded structures, a per-settlement cap of 450 at Metropolis II, and a compressive power law B_game = 10 × (P_real/300)^0.655 fitted to those end-points. Gross land per building: 600 m² in village tiers, 400 m² from Town up (streets and squares included) → ≈17–25 buildings/ha, deliberately below real densities (Monpazier ≈33 lots/ha; Savannah ≈10) because our streets are wide.

| Tier | Buildings | Footprint (ha / side) | Through streets (pitch 60) | Junctions | Villagers | Scale vs real houses |
|---|---|---|---|---|---|---|
| Village | 10 | 0.6 / one street ≈ 90 long | 1 (+ back lane) | 0–1 | 10 | 1:6 |
| Village II | 20 | 1.2 / ~110 | 2–3 | 1–2 | 20 | 1:8 |
| Town | 35 | 1.4 / ~120 | 4–6 incl. square | 4 | 30 | 1:13 |
| Town II | 60 | 2.4 / ~155 | 6–8 | 9 | 50 | 1:15 |
| City | 100 | 4.0 / ~200 | 8–10 | 16 | 60 | 1:20 |
| Upgraded city | 165 | 6.6 / ~260 | 10–12 | 25 | 100 | 1:27 |
| Metropolis I | 265 | 10.6 / ~325 | 12–14 | 36 | 120 | 1:34 |
| Metropolis II | 450 | 18 / ~425 | 14–16 (+ lanes) | 49–64 | 200 | 1:44 |

Notes: "through streets" are named 13-wide corridors; add about as many 5-wide lanes from Town II up if the lane prefab exists; street pieces ≈ 2 × junctions. Villagers fall from 1.0 per building (village) to ≈0.45 (metropolis) to hold ≤ 200 entities per loaded settlement; the UI shows the real anchor ("≈100,000 citizens") while 200 are simulated — these entity figures are performance hypotheses for PS5/Realms, not sourced, and need witness verification. Keep real *proportions* even where counts are compressed: square ≈ 1–1.5% of footprint at Town (Monpazier ≈ 2,000 m² of 88,000), public space 25–50% (Savannah's 50% is the generous end), streets 20–30%. A 425-block metropolis is ~7 × 7 chunks; if that cannot stay loaded, build it as Savannah-style wards of ~200 × 200 (60–80 buildings each) generated and ticked independently — Savannah grew from 6 to 24 wards.

### 4.10 To verify in-game

1. Villager pathing on the 1-in-7 ramp (locally 25%) — real design would make this a stair.
2. Hairpin navigability at 20 centre-to-centre and sewer turning inside the elbow.
3. Measured entity/structure cost per tier on PS5 before fixing the villager column.

---

## Sources

- https://en.wikipedia.org/wiki/Village
- https://en.wikipedia.org/wiki/Settlement_hierarchy
- https://en.wikipedia.org/wiki/Hill_town
- https://en.wikipedia.org/wiki/Market_town
- https://the-orb.arlima.net/encyclop/culture/towns/townint5.html
- https://www.encyclopedia.com/history/news-wires-white-papers-and-books/urban-fortifications-and-public-places
- https://www.michaeldelahaye.com/monpazier.html
- https://frenchmoments.eu/monpazier-dordogne/
- https://en.wikipedia.org/wiki/Monpazier
- https://www.travelfranceonline.com/monpazier-bastide-in-perigord/
- https://en.wikipedia.org/wiki/Bastide
- https://www2.gwu.edu/~iiep/assets/docs/papers/2020WP/JedwabIIEP2020-9.pdf
- https://medium.com/migration-issues/notes-on-medieval-population-geography-fd062449364f
- https://castellitoscani.com/en/florence-city-walls/
- https://www.florenceinferno.com/florence-town-walls/
- https://en.wikipedia.org/wiki/Wall_of_Philip_II_Augustus
- https://en.wikipedia.org/wiki/Faubourg
- https://gamingballistic.com/wp-content/uploads/2018/11/Medieval-Demographics-Made-Easy-1.pdf
- https://handwiki.org/wiki/History:Medieval_demography
- https://en.wikipedia.org/wiki/Roman_roads
- https://mitp-arch.mitpress.mit.edu/pub/s1g1tf3w
- https://socks-studio.com/2017/06/21/a-perfect-grid-the-roman-town-of-timgad-the-african-pompeii/
- https://www.designingbuildings.co.uk/wiki/The%20history%20of%20the%20dimensions%20and%20design%20of%20roads,%20streets%20and%20carriageways
- https://en.wikipedia.org/wiki/Gerechtigkeitsgasse
- https://en.wikipedia.org/wiki/Kramgasse
- https://en.wikipedia.org/wiki/Z%C3%A4hringerstadt
- https://www.nps.gov/articles/savannah-georgia-the-lasting-legacy-of-colonial-city-planning-teaching-with-historic-places.htm
- https://en.wikipedia.org/wiki/Oglethorpe_Plan
- https://18thc-cities.sorbonne-universite.fr/The-New-Town-of-Edinburgh-James.html
- https://en.wikipedia.org/wiki/New_Town,_Edinburgh
- https://thegardenstrust.org/wp-content/uploads/2016/07/Lewis.pdf
- https://thegreatestgrid.mcny.org/greatest-grid/making-the-plan/12
- https://www.renthop.com/blog/how-long-is-a-block/
- https://en.wikipedia.org/wiki/Casimir_Goerck
- https://en.wikipedia.org/wiki/Rue_Rambuteau
- https://en.wikipedia.org/wiki/Cerd%C3%A0_Plan
- https://www.hungerfordvirtualmuseum.co.uk/index.php/10-themes/954-burgage-plots
- https://alnwickcivicsociety.org.uk/2020/09/11/rods-poles-and-perches/
- https://www.academia.edu/38721877/The_articulation_of_burgages_and_streets_in_early_medieval_towns_pt_2
- https://scispace.com/pdf/the-archaeology-of-burgage-plots-in-scottish-medieval-towns-g1tih1rxk1.pdf
- https://en.wikipedia.org/wiki/Market_Square,_Wroc%C5%82aw
- https://en.wikipedia.org/wiki/Main_Square,_Krak%C3%B3w
- https://en.wikipedia.org/wiki/Back_lane
- https://www.huduser.gov/portal/sites/default/files/pdf/The-Laws-of-the-Indies.pdf
- https://journals.open.tudelft.nl/iphs/article/download/2720/2931/7656
- https://iranicaonline.org/articles/bazar-ii
- https://en.wikipedia.org/wiki/Souks_of_Tunis
- https://en.wikipedia.org/wiki/Tala%27a_Kebira
- https://en.wikipedia.org/wiki/Chouara_Tannery
- https://popular-archaeology.com/article/inside-a-medieval-city-public-health-housing-and-everyday-regulations/
- https://dolly.jorgensenweb.net/files/Jorgensen_Responses_to_urban_river_pollution_postprint.pdf
- https://www.medieval-spell.com/Medieval-Towns/
- https://en.wikipedia.org/wiki/The_Shambles
- https://en.wikipedia.org/wiki/And%C3%A9n
- https://en.wikipedia.org/wiki/Tip%C3%B3n
- https://en.wikipedia.org/wiki/Inca_technology
- https://machupicchusoul.com/blog/machu-picchu-terraces/
- https://www.annees-de-pelerinage.com/machu-picchu-architecture-explained/
- https://www.lecinqueterre.org/eng/murettiasecco.php
- https://www.lecinqueterre.org/eng/terrazzamenti.php
- https://www.cinqueterre.it/en/the-cinque-terre/storia/
- https://topsoil.nserl.purdue.edu/isco/isco12/VolumeIV/BenchTerraceDesignMadeSimple.pdf
- https://www.fao.org/4/ad083e/ad083e07.htm
- https://www.cmha.org/resource/srw-faq-001/
- https://www.sandiego.gov/sites/default/files/legacy/development-services/pdf/industry/landdevmanual/ldmsteephillsides.pdf
- https://phoenix.municipal.codes/ZO/710
- https://www.architectureandtradition.com/p/what-made-the-italian-hill-town-so
- https://en.wikipedia.org/wiki/Hilltowns_in_Italy
- https://en.wikipedia.org/wiki/Positano
- https://www.showcaves.com/english/gr/topics/Santorini.html
- https://holeinthedonut.com/2018/08/21/cave-architecture-of-santorini-oia/
- https://en.wikipedia.org/wiki/Hanging_Houses_of_Cuenca
- https://en.wikipedia.org/wiki/Bonifacio,_Corse-du-Sud
- https://en.wikipedia.org/wiki/Architecture_of_Lhasa
- https://en.wikipedia.org/wiki/Potala_Palace
- https://www.asiaculturaltravel.co.uk/diaojiaolou/
- https://chinablog.cc/diaojiaolou-stilted-building-in-southwestern-china/
- https://www.cn-zhangjiajie.com/view-40-348.html
- https://www.chinahighlights.com/fenghuang/
- https://www.topchinatravel.com/china-attractions/fenghuang-ancient-town.htm
- https://en.wikipedia.org/wiki/Step_street
- https://www.datapointed.net/2009/11/the-steeps-of-san-francisco/
- https://en.wikipedia.org/wiki/Grade_(slope)
- https://en.wikipedia.org/wiki/List_of_steepest_roads_and_streets
- https://inspectapedia.com/Stairs/Stair-Angle-Slope-Specifications.php
- https://expressramps.com/learn/codes/ada-ramp-slope
- https://www.fs.usda.gov/sites/default/files/FSTAG-2013-Update.pdf
- https://en.wikipedia.org/wiki/Hardknott_Pass
- https://www.cyclingnorthwales.co.uk/pages/thom_tel_rd.htm
- https://www.roads.org.uk/articles/three-generations-a82/telfords-road
- https://epd.georgia.gov/document/publication/b-8-preliminary-report-roads-and-materials-georgia-1901/download
- https://en.wikipedia.org/wiki/Simplon_Pass
- https://www.myswitzerland.com/en-id/experiences/the-first-highway-over-the-alps-simplon-pass/
- https://en.wikipedia.org/wiki/Stelvio_Pass
- https://en.wikipedia.org/wiki/Great_St_Bernard_Pass
- https://infralens.in/code/IRC-52-2019
- https://testbook.com/civil-engineering/hill-roads
- https://www.essaysauce.com/architecture-essays/gradients-special-consideration-for-hill-roads/
- https://civilguidelines.com/articles/gradients-roads-types.html
- https://www.mdpi.com/2412-3811/7/9/112
- https://www.fhwa.dot.gov/environment/recreational_trails/publications/fs_publications/00232839/page10.cfm
- https://globaldesigningcities.org/publication/global-street-design-guide/designing-streets-people/designing-for-motorists/corner-radii/
- https://roman-empire.net/architecture/roman-roads
- https://en.wikipedia.org/wiki/Hlavn%C3%A1_ulica
