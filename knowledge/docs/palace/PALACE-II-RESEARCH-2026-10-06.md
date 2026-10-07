# PALACE II — Research Brief: Real Palace Blueprints, Hidden Circulation, Underground Ways, Nurseries

**Date:** 2026-10-06 · **For:** CIVITAS city palace, BP-02 (`tools/palacegen.py` successor) · **Status:** RESEARCH + PROPOSED DESIGN — nothing built, no pack touched.
**Owner's brief (2026-10-06 18:22):** *"We can enlarge our palaces and castles to make room for our changes, and even entire new rooms for children's beds if you want. You don't have to limit yourself to previously decided sizes. I want these to be blueprinted off of real palaces - all the way down to the secret hallways and doors and secret staircases and underground passages - everything."*

**Scale:** 1 block = 1 m. Imperial figures are converted at 1 ft = 0.3048 m and rounded to whole blocks.
**How to read this:** §1–§3 are **SOURCED** (every claim carries a link; quotations are from the page cited). §4 is **PROPOSED DESIGN** (mine) — every element names the documented feature it imitates, or is marked **[INVENTION]** when no source backs it. §5 lists **myths and weakly sourced claims**, so we do not build legends as fact. This brief extends R3 (`_docs/civitas_research/R3-PALACES-GREAT-HOUSES.md`, 2026-10-03); R3 facts are reused with their original citations rather than re-fetched.

**What the current palace already has (palacegen.py docstring):** one 128 × 128 model cut into four 64 × 64 pieces (NW NE SW SE); frame x = depth from the street, z = frontage; storeys ground 0..4 (clear 5), étage noble 6..13 (clear 8), attic 15..18 (clear 4), roofs from 19; a hidden 2-wide spine corridor behind the state rooms, jib doors (`pw:jib_panel`), three back stairs, the Tesoretto strongroom behind a `pw:secret_painting`, the judges' barrel-wardrobe door, a Duke-of-Athens private stair to the alley, a prison tower (Pozzi / Piombi / bridge of sighs), a baize door. Role beds (1.3.229): `lord | noble | servant | guard | clerk | cell | child`; children's beds today = one per apartment (12 total).

---

## 1. Six palaces with well-documented hidden circulation

### 1.1 Versailles (France) — the apartment grammar and the Queen's door

**Plan.** U-plan corps de logis around the Cour de Marbre / Cour Royale, wings, garden front of 402 m; 2,300 rooms, 67 staircases (R3 §1.1, [Wikipedia – Palace of Versailles](https://en.wikipedia.org/wiki/Palace_of_Versailles)). State rooms are an **enfilade** (rooms opening one into the next on a single axis): the King's apartment runs guard room → first antechamber (public dining) → Œil-de-Bœuf (waiting) → bedchamber with alcove and balustrade → council cabinet → wig cabinet (R3 §1.1, [Wikipedia – Appartement du roi](https://en.wikipedia.org/wiki/Appartement_du_roi)). The Queen's runs guard room → Grand Couvert antechamber → Salon des Nobles → bedchamber ([Wikipedia – Grand appartement de la reine](https://en.wikipedia.org/wiki/Grand_appartement_de_la_reine)).

**Hidden / service features (documented).**
- **The Queen's doors.** "The two doors under hangings on either side of the bed give access to the Queen's private chambers"; "On the morning of 6 October 1789, Marie-Antoinette took the door on the left to escape from the rioters" ([Google Arts & Culture / Château de Versailles – Tour of the Queen's Chamber](https://artsandculture.google.com/story/cgVhVsHRApPWHA)). The passage "dates from the time of Queen Maria-Theresa, and had always been a suite of service rooms", served as "a private means by which the king and queen could communicate", and its entrance is "a door located on the west side of the north wall of the chambre de la reine" ([Wikipedia – Petit appartement de la reine](https://en.wikipedia.org/wiki/Petit_appartement_de_la_reine)). The private rooms behind are "accessible from Marie Antoinette's bedroom from a hidden door… spread over two floors and overlook a courtyard… where Marie Antoinette would… spend time with her children" ([AFAR – Marie Antoinette's rooms reopened](https://www.afar.com/magazine/inside-marie-antoinettes-reopened-apartment-at-versailles)); upper floor: billiard room, dining room, boudoir, and "Six other rooms… reserved for the First Chambermaids and the service" ([Château de Versailles – Marie-Antoinette's private chambers](https://en.chateauversailles.fr/discover/estate/palace/marie-antoinette-private-chambers)); chambermaids' rooms "just over 8 m² to 12 m²", three linking staircases (Billiard, Fleury, Dupes) (R3 §1.1, Versailles press kit).
- **The King's private stair (degré du roi)** ran "from the exterior cour de marbre to the interior cour du roi"; Louis XV's arrière-cabinet with "a small cabinet de la chaise… communicated directly with the degré du roi"; the inner court was renamed **cour des cerfs** — a light well among the private rooms ([Wikipedia – Petit appartement du roi](https://en.wikipedia.org/wiki/Petit_appartement_du_roi)). The private suite had "numerous secret drawers and compartments"; Louis XV had "another, even more private bedroom in the Petits Cabinets on the top of the palace" — "a total of 3 bedrooms" ([Versailles Century – King's private apartments pt 2](https://versaillescentury.com/2016/09/05/versailles-visit-private-apartments-part-2/)); the inner study was "the dispatch room, where… he received his spies and confidential informers" (same source).
- **The private bedchamber (1738)**: "près de 89 m² et plus de 10 m de hauteur sous plafond" ([Versailles press kit, Chambre du Roi, 15 Apr 2026, via P. Cachau](https://www.philippecachau.fr/medias/files/dossier-de-presse-chambre-du-roi-versailles-15-avril-2026-compresse.pdf)) → about **10 × 9 blocks, 10 high**.
- **Flying table** (dumbwaiter precedent): Louis XV wanted "'flying tables', like those at the Château de Choisy, so that tables previously laid on the lower floor could appear in the center of the first-floor dining room", to keep "conversations… [free of] the presence of servants"; cancelled March 1772 for cost; "Traces of a trapdoor remain in the centre of the… parquet floor" ([Wikipedia – Petit Trianon](https://en.wikipedia.org/wiki/Petit_Trianon)). Petit Trianon's levels: ground = service, first = reception, attic = king's rooms and guests (same).
- **Service town**: the Grand Commun, 82 × 76 m, six floors, vaulted 6 m ground floor with kitchens (R3 §1.1).

**Children.** The Queen's bedchamber was the birth room: "19 Princes and Princesses of the Realm were born here" ([Google Arts & Culture](https://artsandculture.google.com/story/cgVhVsHRApPWHA)). The heir lived on the **ground floor of the central block, opening onto the South Parterre**, directly under the state floor — Dauphin's library, great chamber, bedchamber with silk alcove, second antechamber, and a **Lower Gallery** separating his apartment from the Dauphine's ([Château de Versailles – Dauphin's apartment](https://en.chateauversailles.fr/dauphin-appartment); [Dauphin and Dauphine apartments](https://en.chateauversailles.fr/discover/estate/palace/dauphin-and-dauphine-apartments)). The royal children had their own office-holder: the **Governess of the Children of France**, "supported by various deputies or under-governesses… and oversaw a household consisting of dozens of servants and caregivers" ([Wikipedia – Governess of the Children of France](https://en.wikipedia.org/wiki/Governess_of_the_Children_of_France)); Mme de Polignac on appointment "moved into the Governess' apartments" ([Château de Versailles – Madame de Polignac](https://en.chateauversailles.fr/discover/history/great-characters/madame-polignac)). *Not found in this pass:* the exact rooms of the governess's apartment.

### 1.2 Hampton Court (England) — Tudor privy lodgings and the Prince's nursery

**Plan.** Courtyard palace: Base Court (arrivals) → Great Hall → Great Watching Chamber → Presence → Privy Chamber → the king's private lodgings, a guard at every door (R3 §1.2, [HRP – Tudor court](https://www.hrp.org.uk/hampton-court-palace/history-and-stories/the-royal-court-in-the-tudor-period/)). Great Hall 32 × 12 × 14 to the plate; Great Gallery 36 × 7 × 8.5 (R3 §1.2).

**Hidden / service features.** The lodgings ran "the outer, or public chambers, the privy chamber(s) and the innermost or 'secret' lodgings"; beside the king's bedchamber "a door… leads to a **spiral stone staircase rising from the ground floor**" — the king's Wardrobe lay directly below; in an alcove of the bedchamber "a **bricked-up doorway**… once connected the king's secret lodgings directly with Wolsey's gallery and apartments" ([Tudor Travel Guide – Henry VIII's lost apartments](https://thetudortravelguide.com/?p=1274)). Drains: the Great House of Easement "could seat 28 people at one time", its brick chambers filled "head-high" after four weeks ([Mental Floss – Hampton Court privies](https://mentalfloss.com/article/559758/how-to-poop-king-henry-vii-hampton-court-palace)); chutes ran into "brick culverts which ran under the moat and into the river Thames" (R3 §1.2). **Ice house**: "a brick-lined well, which was 30 feet (9.1 m) deep and 16 feet (4.9 m) wide", under a thatched timber house ([Wikipedia – Ice house](https://en.wikipedia.org/wiki/Ice_house_(building))).

**Children (best-documented royal nursery in this brief).** One three-storey range housed "the Princess Mary on the lower level, Henry on the first floor and Katherine of Aragon directly above him" ([Tudor Travel Guide](https://thetudortravelguide.com/?p=1274)) — **the child one floor below the father, the queen one floor above**. For Prince Edward Henry built the **Prince's Lodgings** (1537), "two storeys tall", "overlooking Chapel Court", reached by "a large staircase in the north-west corner of Chapel Court". First floor: "The Prince's Watching Chamber", "The Prince's Presence Chamber", "The Nursery", "The Rocking Chamber", "My Lord Prince's Jakes", "The Prince's Washing Chamber", "The Lodging Next to the Nursery"; lower floor: "lodgings and jakes for Edward's household, and probably a kitchen and laundry". Four "rockers" rocked the prince; Henry "had the Prince's Lodgings swept and soaped down" and "strictly controlled access" ([HRP – Uncovering Edward VI's nursery](https://www.hrp.org.uk/blog/uncovering-edward-vis-nursery-at-hampton-court-palace/)).

### 1.3 Palace of Holyroodhouse (Scotland) — the vice stair of 9 March 1566

**Plan.** "A quadrangle of buildings around a central courtyard" — chapel royal north, king's lodgings west, queen's south ([Tudor Travel Guide – Holyroodhouse](https://thetudortravelguide.com/holyroodhouse-pleasure-palace-of-the-stuarts/)); the James V tower is of "1532… at NW angle", with circular angle turrets; the classical quadrangle was rebuilt 1671–8 ([Historic Environment Scotland LB28022](https://portal.historicenvironment.scot/designation/LB28022)).

**Hidden feature (documented).** The tower stacked the **King's lodgings on the first floor** (outer + inner chamber) and the **Queen's on the second floor** (outer + inner chamber), the queen's side "adjacent… to the Chapel Royal". The conspirators "gained entry to the queen's apartments via the **small vice stair** [which] connected the first with the second floor of the tower"; Mary was "in her cabinet, at our supper", a closet "just **12ft by 12ft**" off her bedchamber; Rizzio was "thrust out of the cabinet through the bedchamber" and stabbed at the entry of the chamber. The tower's original entrance was a forestair "secured via a drawbridge and a yett" ([Tudor Travel Guide – Holyroodhouse](https://thetudortravelguide.com/holyroodhouse-pleasure-palace-of-the-stuarts/)). Mary's rooms are "reached by a narrow, steep and winding staircase"; she "had two rooms in the turrets of her Bedchamber" — one a study/dressing room, one the supper room ([RCT – Explore Mary, Queen of Scots' Chambers](https://rct.uk/resources/explore-mary-queen-of-scots-chambers)). **Block reading:** supper closet 4 × 4 in a corner turret; the vice stair is a tight newel stair between two stacked apartments.

### 1.4 Palazzo Vecchio (Florence) — stair in the wall, rooms behind paintings

**Plan.** Fortress-palace; Salone dei Cinquecento 54 × 23 × 18 m; tower 95 m (R3 §1.5).

**Hidden features (museum's own tour, "Percorsi segreti").** "The narrow stone staircase commissioned by Gualtieri di Brienne and **carved into the thickness of the medieval wall**"; "The Studiolo of Francesco I"; "The Scrittoio of his father Cosimo I, **accessible only thanks to passages concealed behind paintings**"; "The vast space above the ceiling of the Salone dei Cinquecento, where an imposing system of trusses stands out" ([Finestre sull'Arte – Secret Pathways](https://www.finestresullarte.info/en/museums/secret-pathways-of-the-old-palace-returns-after-a-year-and-a-half); [MUS.E Firenze – Secret passages](https://musefirenze.it/en/activities/secret-passages/)). The Studiolo is a "small painting-encrusted **barrel-vaulted** room", "part-office, part-laboratory, part-hiding place", 1570–72 ([Wikipedia – Studiolo of Francesco I](https://en.wikipedia.org/wiki/Studiolo_of_Francesco_I)). The 1342 door: the Duke "had a small door installed in the alleyway, with a narrow staircase leading to the upper floors" so "the ruler himself, spies and special visitors… could enter and leave without being seen"; the Tesoretto had "hidden compartments… and also two hidden doorways" (R3 §2.2). **City scale:** the Vasari Corridor (1565), ~1 km, palace → Uffizi → over the Ponte Vecchio → Pitti (R3 §1.5).
*No dimensions found* for the Studiolo, the Tesoretto or the Brienne stair.

### 1.5 Doge's Palace (Venice) — the Secret Itineraries, Pozzi, Piombi, Bridge of Sighs

**Plan.** ~71 × 75 m around a courtyard; ground = offices and prisons, first = the Doge's modest residence, second = the great councils (R3 §1.4).

**Hidden route, in order (museum leaflet).** Through "a narrow door on the ground floor… the **Pozzi**" ("small wet cells, barely lit by oil lamps, ventilated only through round holes in thick stone walls", each with "a wood litter, a shelf… and a wooden bucket with a lid") → "A narrow staircase takes you up to the two small rooms" of the Ducal Notary and Deputato alla Segreta → Great Chancellor's office → "the large and beautiful **Chamber of the Secret Chancellery**" → Deputy to the Chancellery → **Torture Chamber** → "the so-called **Piombi**" ("6 or 7 cells… formed of wooden partitions to which were nailed sheets of iron") → "directly under the roof to the **attic**" (weapons) → "two long flights of stairs bring one to the **Chamber of the Inquisitors**" → Chamber of the Three Head Magistrates ([Palazzo Ducale – Secret Itineraries leaflet 2019](https://palazzoducale.visitmuve.it/wp-content/uploads/2019/06/itinerari-segreti-ducale-ENG-riv.pdf); [2020 leaflet](https://palazzoducale.visitmuve.it/wp-content/uploads/2020/10/DOWNLOADS-Itinerari-segreti-ducale-ENG-2020.pdf)). The Inquisitors' room "has a **secret entrance behind a wooden wardrobe**" to the Council of Ten; the Chancellery lockers carry chancellors' arms "from 1268" ([Justin Plus Lauren – Secret Itineraries](https://justinpluslauren.com/doges-palace-secret-itineraries-tour-venice/)). Piombi: "in the attic, directly under the roof… covered with slabs of lead", decreed 15 March 1591 because "the pre-existing Wells were too harsh" ([Wikipedia – Piombi](https://en.wikipedia.org/wiki/Piombi)). **Bridge of Sighs**: enclosed stone bridge of 1600, arch span **11 m**, to the New Prisons across the Rio di Palazzo ([Structurae – Bridge of Sighs](https://structurae.net/en/structures/bridge-of-sighs)); it "contains two separate corridors that run next to each other" (R3 §1.4).

### 1.6 Château de Chambord (France) — the double-helix stair and the apartment cell

**Plan.** "128 metres (420 ft) of façade", 56 m high, "440 rooms, 282 fireplaces, and 84 staircases"; "Four rectangular vaulted hallways on each floor form a cross-shape" around the central stair ([Wikipedia – Château de Chambord](https://en.wikipedia.org/wiki/Ch%C3%A2teau_de_Chambord)); the keep is a "Greek cross" giving onto "former living quarters, located in the corners" ([Chambord visitor plan 2022](https://cdn1.chambord.org/fr/wp-content/uploads/sites/2/2022/06/plan-visite-fr-2022-ANGLAIS.pdf)); "cinq niveaux habitables" with "quatre appartements carrés et quatre appartements dans les tours rondes par niveau" ([Académie de Nice – Le château de Chambord](https://www.pedagogie.ac-nice.fr/dsden06/eac/wp-content/uploads/sites/5/2018/04/Le-chateau-de-Chambord.pdf)). Francis I's apartment: "a vast room measuring **80 m²**", wardrobe, closet and oratory; Louis XIV's ceremonial apartment: "the guardhouse, two antechambers and the ceremonial bedroom" ([Chambord visitor plan](https://cdn1.chambord.org/fr/wp-content/uploads/sites/2/2022/06/plan-visite-fr-2022-ANGLAIS.pdf)).
**The stair.** "two flights of steps that wind one above the other around a central core pierced with windows" ([Chambord visitor plan](https://cdn1.chambord.org/fr/wp-content/uploads/sites/2/2022/06/plan-visite-fr-2022-ANGLAIS.pdf)); "The two spirals ascend the three floors without ever meeting"; John Evelyn: "four persons meet, they never come in sight, but by small loopholes" ([Wikipedia – Chambord](https://en.wikipedia.org/wiki/Ch%C3%A2teau_de_Chambord)). *No reliable diameter or step dimensions were found in this pass* — do not invent them.

### 1.7 Supporting cases (one feature each, well documented)

| Place | Documented feature | Source |
|---|---|---|
| **Tower of London**, St Thomas's Tower (Edward I) | Built "so that he could sail his royal barge right up to the Medieval Palace from the River Thames"; "The spiral staircase that leads past Edward's bedchamber goes all the way down to the river below St Thomas's Tower"; private oratory in the bedchamber; garderobe "emptied into the River Thames"; the water gate later "Traitors' Gate" | [HRP – Palace secrets: medieval palace](https://www.hrp.org.uk/media/1239/palace-secrets-medieval-palace.pdf); [Wikipedia – Traitors' Gate](https://en.wikipedia.org/wiki/Traitors%27_Gate) |
| **Passetto di Borgo** (Vatican → Castel Sant'Angelo) | "approximately 800-metre-long" elevated corridor with "two levels: the top level is a standard patrol walkway, and underneath it is the hidden enclosed escape passage"; used by Alexander VI (1494) and Clement VII during the Sack of Rome (1527) | [Wikipedia – Passetto di Borgo](https://en.wikipedia.org/wiki/Passetto_di_Borgo) |
| **Moscow Kremlin**, Tainitskaya ("Secret") Tower | "Built with a secret well inside and a hidden exit to the Moskva River"; the well was backfilled 1930–33 | [Kremlin Museums – Tainitskaya Tower](https://kremlin-architectural-ensemble.kreml.ru/en-Us/architecture/view/taynitskaya-bashnya-moskovskogo-kremlya) |
| **Dover Castle** | Medieval tunnels "constructed in the 13th century after the 1216 siege", the "primary means of access to the spur from the castle"; three passages to three towers meet in a junction under the redan | [Kent HER MKE111638](https://heritage.kent.gov.uk/Monument/MKE111638) |
| **Whitehall Palace** | Riverside terrace and "river gate" steps (Wren, 1691–93) from the palace to the Thames; Henry VIII's vaulted wine cellar survives — moved in 1949 "9 feet… to the West and 19 feet… lower" in a steel-and-concrete case | [British Listed Buildings – Queen Mary's Steps](https://britishlistedbuildings.co.uk/101066636-queen-marys-steps-and-fragment-of-whitehall-palace-st-jamess-ward); [Stuff About London – wine cellar](https://stuffaboutlondon.co.uk/london/henry-viiis-wine-cellar/) |
| **Schönbrunn** (Vienna) | Every stove "was stoked… from a **passage running behind the walls of the rooms**, so that the imperial family was not disturbed"; "a spiral staircase… led down to the empress's private apartments on the ground floor" (removed after 1918); a Children's Room; Great Gallery ">40 m long and almost ten metres wide" | [Schönbrunn audio-guide text 2025](https://www.schoenbrunn.at/fileadmin/content_schoenbrunn/Audioguides/PDFs/Lesetext_PalaceTicket_EN_2025_final.pdf) |
| **Hofburg** (Vienna) | The Augustinian church, court parish from 1634, was "gradually… engulfed" by the palace; its Loreto chapel/Herzgruft holds "the hearts of 54 members of the imperial family" | [Wikipedia – Augustinian Church, Vienna](https://en.wikipedia.org/wiki/Augustinian_Church,_Vienna) |
| **El Escorial** | "Philip II could witness from the bed the liturgy happening in the main altar of the church"; king's chamber = main room, bedroom, study, oratory, on two storeys round the presbytery | [Fascinating Spain – El Escorial](https://www.fascinatingspain.com/articulo/what-to-see-in-madrid/el-escorial-philip-the-prudent/20220627065845067371.html) |
| **Baddesley Clinton** (manor, Warwickshire) | Priests slid "down a rope from the first floor through the old garderobe shaft into the house's **sewers, which run the length of the building**", room for "six or seven people"; another hide "in the roof"; one "in an old privy"; "a small room with a door hidden in the wood panelling"; 1591 raid — "no-one was caught" | [Wikipedia – Baddesley Clinton](https://en.wikipedia.org/wiki/Baddesley_Clinton) |
| **Nicholas Owen's hides** | "he built a more easily discovered outer hiding place, which concealed an inner hiding place"; Hindlip Hall 1606: starved out "after four days" | [Wikipedia – Nicholas Owen](https://en.wikipedia.org/wiki/Nicholas_Owen_(Jesuit)) |
| **Nesvizh** (Radziwiłł) | Documented "utility dungeons and secret passages" and a medieval icehouse whose melt-water hole locals took "to be the entrance to a secret underground passage" | [Gallerix – Castle dungeons: legend and reality](https://en.gallerix.ru/hi/tayny-zamkovyx-podzemeliy-legendy-i-realnost) |

---

## 2. Nurseries and children's quarters — what the sources say

| Case | Where the children slept | Who slept with them | Distance from parents | Source |
|---|---|---|---|---|
| Hampton Court, Princess Mary | Ground level of the king's range | (not stated) | **One floor directly below** the king | [Tudor Travel Guide](https://thetudortravelguide.com/?p=1274) |
| Hampton Court, Prince Edward (1537) | Own two-storey **Prince's Lodgings** off Chapel Court: watching chamber, presence, nursery, rocking chamber, jakes, washing chamber | Four rockers; close servants in "the lodging next to the nursery"; household, kitchen and laundry below | Separate building, controlled access | [HRP blog](https://www.hrp.org.uk/blog/uncovering-edward-vis-nursery-at-hampton-court-palace/) |
| Versailles, the Dauphin | Ground floor of the central block, under the state floor; Lower Gallery between Dauphin and Dauphine | Governess of the Children of France + under-governesses, "dozens of servants and caregivers" | One floor below; the Queen's private rooms were where she "would… spend time with her children" | [Ch. de Versailles](https://en.chateauversailles.fr/dauphin-appartment); [Wikipedia – Governess](https://en.wikipedia.org/wiki/Governess_of_the_Children_of_France); [AFAR](https://www.afar.com/magazine/inside-marie-antoinettes-reopened-apartment-at-versailles) |
| Large houses (general, 19th c.) | "a suite of rooms at the top of a house, including the night nursery, where the children slept, and a day nursery, where they ate and played" | "The nurse (nanny) and nursemaid… slept in the suite too, to be within earshot"; suite with bathroom and "possibly a small kitchen" | Top floor | [Wikipedia – Nursery (room)](https://en.wikipedia.org/wiki/Nursery_(room)) |
| Audley End | "a suite of rooms on the second floor"; five boys and three girls in the 1830s | — | Upper floor | [English Heritage – Audley End nursery](https://www.english-heritage.org.uk/about/search-news/victorian-nursery-unveiled-audley-end/) |
| John Jay Homestead (1811) | Second floor: Night Nursery (sleep), Day Nursery (play and lessons until a schoolhouse was built) | — | Upper floor | [John Jay Homestead](https://johnjayhomestead.org/night-day-nurseries-and-nursery-hall/) |
| Osborne House (exception) | First floor of the Pavilion, the same floor as the Queen's bedroom and sitting room | — | **Same floor**; children visited parents' bedrooms "frequently, at a time when children of aristocrats often lived removed from their parents in nurseries" | [Wikipedia – Osborne House](https://en.wikipedia.org/wiki/Osborne_House) |
| Hierarchy | The nursery maid "reported to the nanny (or nurse)"; governess and wet nurse are separate posts | — | — | [Wikipedia – Nursemaid](https://en.wikipedia.org/wiki/Nursemaid) |

**Pattern to build:** royal children = **a separate lodging one floor below the parents**, with its own guard (watching chamber), presence room, night nursery, day/rocking room, nurses' lodging, privy and washing room, and its own service floor. Noble children = **a nursery room inside the family's apartment**, with the nurse sleeping in the suite "within earshot".

---

## 3. Typical dimensions (sourced where possible)

| Element | Real figure | Blocks | Source |
|---|---|---|---|
| Gallery (state) | Hall of Mirrors 73 × 10.5 × 12.3 m; Schönbrunn Great Gallery >40 × ~10 m; Hampton Court Great Gallery 36 × 7 × 8.5 | 73 × 11 × 12 / 40 × 10 / 36 × 7 × 8 | R3 §1.1–1.2; [Schönbrunn text](https://www.schoenbrunn.at/fileadmin/content_schoenbrunn/Audioguides/PDFs/Lesetext_PalaceTicket_EN_2025_final.pdf) |
| Great hall | Hampton Court 32 × 12, 14 to plate; Doge's Great Council 54 × 25 × 12 | 32 × 12 × 14 | R3 §1.2, §1.4 |
| Royal bedchamber | Versailles private bedchamber ~89 m², >10 m high; Francis I's room at Chambord 80 m² | 10 × 9 × 10 / 9 × 9 | [Versailles press kit 2026](https://www.philippecachau.fr/medias/files/dossier-de-presse-chambre-du-roi-versailles-15-avril-2026-compresse.pdf); [Chambord plan](https://cdn1.chambord.org/fr/wp-content/uploads/sites/2/2022/06/plan-visite-fr-2022-ANGLAIS.pdf) |
| Closet / supper cabinet | Holyrood 12 × 12 ft (3.7 m) | 4 × 4 | [Tudor Travel Guide – Holyrood](https://thetudortravelguide.com/holyroodhouse-pleasure-palace-of-the-stuarts/) |
| Maid's / servant's room | Versailles chambermaids 8–12 m² | 3 × 3 to 3 × 4 | R3 §1.1 |
| Kitchen (mansion) | 18–20 × 25–30 ft, 10–20 ft high (Kerr) | 6 × 8–9, 3–6 high | R3 §2.4 |
| Vaulted service floor | Grand Commun ground floor 6 m | 6 | R3 §1.1 |
| Storey heights | State rooms 8–13 m; service vaults 6 m | 8–12 / 5–6 | R3 §1.11 |
| Wall thickness | Wrocław council chamber walls 1.8–1.9 m; Siena tower walls ~3 m | 2 / 3 | R3 §1.10 |
| Stair in a wall | Brienne stair "carved into the thickness of the medieval wall" (no width given) | needs a 3-thick wall (skin + 1 passage + skin) | [Finestre sull'Arte](https://www.finestresullarte.info/en/museums/secret-pathways-of-the-old-palace-returns-after-a-year-and-a-half) |
| Enclosed bridge | Bridge of Sighs, span 11 m, two parallel corridors | 11 long, 2 × 1-wide corridors | [Structurae](https://structurae.net/en/structures/bridge-of-sighs); R3 §1.4 |
| Escape gallery | Passetto di Borgo ~800 m, two levels | (scaled) | [Wikipedia – Passetto](https://en.wikipedia.org/wiki/Passetto_di_Borgo) |
| Ice house | Hampton Court brick well 9.1 m deep × 4.9 m wide | 9 deep × 5 wide | [Wikipedia – Ice house](https://en.wikipedia.org/wiki/Ice_house_(building)) |
| Sewer hide | Baddesley sewers "run the length of the building", hold 6–7 people | — | [Wikipedia – Baddesley Clinton](https://en.wikipedia.org/wiki/Baddesley_Clinton) |
| Service corridor width | **No source found.** Kerr says only that the kitchen passage "ought… to be wide throughout" | 2 (our existing choice) — **design** | R3 §2.3 |
| Back-stair width | **No source found** ("narrow and gloomy", [Historic Farm – servants' stairs](https://historicfarm.org/re-claiming-the-servants-stairs/)) | our spiral B (4 × 4 well) / A (2 × 2) — **design** | — |
| Spiral stair diameters | **No reliable figure found** (Chambord included) | — | — |

---

## 4. PROPOSED PALACE II PROGRAMME (design — mine, not history)

### 4.1 Why 3 × 3 pieces (192 × 192)

The 128 × 128 palace is full: it holds one apartment sequence, 11 state apartments, a 40 × 14 hall and a 2-wide spine. The documented features need room the 128 model cannot give: (1) **two** apartment sequences (lord and consort) joined by a secret passage — the Versailles 1789 arrangement; (2) a **children's lodging** of 7 rooms plus its service floor (Prince Edward 1537); (3) a **gallery** at Hampton-Court / Schönbrunn scale (36–40 blocks long); (4) a cabinet zone deep enough for an **entresol** (two low floors behind the state rooms, Versailles); (5) walls 3 thick wherever a passage or stair runs inside them (Palazzo Vecchio). **192 × 192 = 9 pieces** (NW N NE / W C E / SW S SE) fits all of this with the court still at a believable 68 × 136. The Versailles-class 4 × 3 (256 × 192) of R3 §5.5 stays the metropolis option. Pieces stay ≤ 64 × 64 and well under 384 high even with two basements (feet −13 to the tower top ~32 = 46).

### 4.2 Section (feet over the court paving; 0 = standing on the court)

| Level | Walking feet | Clear | Use |
|---|---|---|---|
| **B2 — tunnels** | −12 | 4 (−12..−9) | escape tunnel, sewer junction, water gate, chapel crypt passage. Walking level matches the pack's sewers (~12 below the street) **if** the court sits at street level (open question Q3) |
| **B1 — cellars** | −7 | 6 (−7..−2), vaulted (Grand Commun 6 m) | wine cellar, Lower Exchequer strongroom, Pozzi, ice-house access, service tunnel |
| Ground | 0 | 5 (0..4) | guard rooms, offices, **children's lodging**, lord's wardrobe, Lower Gallery |
| Étage noble | 6 | 8 (6..13) | state apartments, gallery, council, chapel tribune |
| ↳ Entresol (cabinet zone only) | 6 and 11 | 4 + 3 | private cabinets, maids' rooms (Versailles "two floors behind the state rooms") |
| Attic | 15 | 4 (15..18) | officials' lodgings, schoolroom, Piombi, petits cabinets |
| Roofs | from 19 | — | as today (gallery and hall vault through the attic) |

Spiral rulings apply: **C grand** (6 × 6 well) for the palace main stairs and towers, **B tower** (4 × 4) for back and service stairs, **A turret** (2 × 2) for defensive towers; mid floors exit through a doorway beside the step, the top floor forward; headroom of at least 2 blocks everywhere; spiral structures are rotated, never mirrored (DECISIONS 2026-10-06). The **secret vice stairs** imitate documented *narrow* stairs (Holyrood, Hampton Court, Brienne) — A turret fits them best, but the 14:21 ruling reserves A for defensive towers → **Q1 for Abs0lum**.

### 4.3 Massing (x = depth from street, z = frontage, both 0..191)

```
x   0..11   GATE RANGE  (gatehouse C+A at z 88..103; porter; guard rooms; public offices; Pozzi in B1 below)
x  12..79   COURT OF HONOUR z 28..163 (68 x 136), raised marble court x 64..79 before the lord's bedchamber
            WEST WING  z 8..27  (government: guard room+armoury G, chancery, exchequer, judges' room 1st, archive attic)
            EAST WING  z 164..183 (noble apartments G/1st/attic; CHAPEL at the inner end x 56..79)
x  80..111  CORPS DE LOGIS z 8..183 (176 wide, 32 deep):
            court wall 80 | state rooms 81..90 (10) | jib partition 91 | HIDDEN SPINE 92..93 | wall 94 |
            CABINET ZONE + ENTRESOL + light courts 95..100 (6) | wall 101 | GALLERY / garden rooms 102..110 (9) | wall 111
x 112..117  CANAL / service alley (6): the "Rio di Palazzo" — Bridge of Sighs and water gate cross here
x 118..191  REAR: privy garden z 28..111 (ice house, garden pavilion = hidden exit) | service court z 112..183
            (kitchen block, little commons, laundry, stables, smithy) | PRISON TOWER at the NW corner across the canal
```

### 4.4 Rooms (block sizes; L along the frontage × D × clear height)

**Étage noble, corps — lord's apartment (west half, Versailles King's sequence + Hampton Court access gradient)**

| Room | Blocks | Imitates | Role beds |
|---|---|---|---|
| Grand staircase (C grand + open well) | 16 × 10 | Queen's Staircase, Versailles | — |
| Guard room (petitions on market day) | 12 × 10 × 8 | Salle des Gardes; Louis XIV took petitions there (R3) | guard × 4 (camp beds) |
| First antechamber / public dining | 14 × 10 × 8 | Grand Couvert | — |
| Grand antechamber (œil-de-bœuf skylight) | 14 × 10 × 8 | Œil-de-Bœuf | — |
| **Lord's state bedchamber**, alcove 4 deep + balustrade, facing the raised marble court (the marble court is centred on this room, Versailles-style; with the rooms above it lands near z 70..79, so the court axis follows the bedchamber, not the frontage centre) | 10 × 10 × 8 | Chambre du Roi, ~89 m² | lord × 1 |
| Council cabinet | 12 × 10 × 8 | Cabinet du Conseil | — |
| Cabinet / study + **Tesoretto** strongroom 3 × 3 behind a `pw:secret_painting` | 8 × 10 + 3 × 3 | Scrittoio "accessible only… behind paintings" | — |
| **Studiolo** — windowless, barrel-vaulted (`pw:roof45` top wedges as in the hall vault) with chest/barrel cupboards | 6 × 4 × 4 | Studiolo of Francesco I | — |
| Garde-robe + chaise closet + private stair head | 6 × 10 | arrière-cabinet + cabinet de la chaise + degré du roi | — |

**Étage noble, corps — consort's apartment (east half, Versailles Queen's sequence)**

| Room | Blocks | Imitates | Role beds |
|---|---|---|---|
| Guard room | 12 × 10 × 8 | Queen's guard room | guard × 2 |
| Antechamber (Grand Couvert) | 14 × 10 × 8 | Antichambre du Grand Couvert | — |
| Salon of Nobles (audiences) | 12 × 10 × 8 | Salon des Nobles | — |
| **Consort's bedchamber** with **two jib doors under hangings, one each side of the bed** | 10 × 10 × 8 | Chambre de la Reine 1789 | lord-spouse (Q2) |
| Private cabinets behind (2 entresol floors, 6 deep): méridienne 5 × 5, library 5 × 5, gold room 5 × 5; upper: billiard 6 × 5, dining 5 × 5, 3 chambermaids' rooms 3 × 4 | — | Marie-Antoinette's private chambers | servant × 3 |
| Supper closet in a corner turret | 4 × 4 | Holyrood 12 × 12 ft cabinet | — |

**Étage noble — public range and the garden side**

| Room | Blocks | Imitates |
|---|---|---|
| Gallery (garden side of the corps, rises through the attic) | 40 × 9 × 12 | Hampton Court Great Gallery / Schönbrunn gallery |
| Great hall (court sittings) — west of the gallery, G + 1st | 32 × 12 × 14 | Hampton Court Great Hall |
| Dining room with **flying table** (a 3 × 1 piston/trapdoor lift from the B1 serving room below) | 10 × 9 × 8 | Choisy / Petit Trianon tables volantes (the trapdoor trace) |
| Chapel (east wing inner end, next to the consort's apartment) — nave at ground, **royal tribune** at the noble floor reached from the consort's guard room; an Escorial-style window from bed to altar is not possible because the lord's bedchamber is far from the chapel, so the link is the tribune door only | 24 × 16 × 14 | Versailles chapel tribune; Holyrood queen's side "adjacent to the Chapel Royal"; Escorial bed-to-altar view (adapted) |

**Ground floor — the CHILDREN'S LODGING (royal), directly below the lord's apartment**

| Room | Blocks | Imitates | Role beds |
|---|---|---|---|
| Watching chamber | 8 × 10 × 5 | "The Prince's Watching Chamber" | guard × 2 |
| Presence chamber | 8 × 10 × 5 | "The Prince's Presence Chamber" | — |
| **Night nursery** | 8 × 10 × 5 | "The Nursery" / night nursery | child × 2 (room for 4: Q4) |
| **Rocking chamber / day nursery** | 8 × 10 × 5 | "The Rocking Chamber" / day nursery | — |
| Nurses' lodging ("next to the nursery") | 5 × 10 × 5 | "The Lodging Next to the Nursery"; nurse + nursemaid "within earshot" | servant × 3 (head nurse, nursemaid, rocker) |
| Washing chamber + jakes | 4 × 4 + 2 × 2 | "Washing Chamber", "Jakes" | — |
| Governess's room | 5 × 5 | Governess of the Children of France | servant × 1 (or clerk — Q5) |
| Schoolroom (attic above, by the children's back stair) | 10 × 8 × 4 | day nursery used "for their schooling" (Jay) | — |
| Lower Gallery (ground, between the children's lodging and the lord's wardrobe) | 30 × 3 × 5 | Versailles Lower Gallery | — |
| Lord's Wardrobe (directly under the bedchamber) | 10 × 10 × 5 | Hampton Court wardrobe under the king's bedchamber | servant × 1 (valet) |

**Noble family apartments (east wing G / 1st, corps attic) — 16 families**

Antechamber 6 × 7 → bedchamber 8 × 7 (2 adult beds + alcove balustrade) → **children's chamber 5 × 7 (2 child beds)** → nurse's closet 3 × 3 (1 servant bed, door into the children's chamber) → cabinet 4 × 7. Length 26 along a 2-wide spine. Imitates the Versailles courtier lodging (antechamber + bedchamber + cabinet, servant closets: Narbonne pattern, R3 §4) plus the nursery rule "nurse… within earshot". 16 families = 32 noble + 32 child + 16 servant beds.

**Government (west wing) and the rest** — keep the current palace's set at R3 §5.4 sizes, enlarged where the frame allows: chancery hall 30 × 8 (clerks' lectern stations), Upper Exchequer audit room 14 × 8 with the chequered table, judges' room 10 × 7 (barrel-wardrobe door to the council cabinet), archive in the attic ("Secret Chancellery"), clerks' lodgings 12 × (3 × 4) in the west attic, guard room + armoury 20 × 8 at ground. Service court as today (kitchen block with buttery hatch and the 2-wide covered passage, little commons, laundry, stables, smithy), the baize door kept.

### 4.5 The hidden network — every element and its model

| # | Element (where) | Built as | Documented model |
|---|---|---|---|
| H1 | **Hidden spine corridor** (corps, G + noble + attic, x 92..93) with a jib door into every state room | 2 wide × 3 high, `pw:jib_panel` doors, bell line | Versailles service rooms behind the Queen's apartment; Kerr's service separation (R3 §2.3) |
| H2 | **Stoking passage** behind the gallery and apartments — every fireplace/stove fed from behind | the same spine on the garden side; furnaces/campfires opening into it | Schönbrunn: stoves "stoked… from a passage running behind the walls" |
| H3 | **The Consort's escape** — jib door LEFT of the consort's bed → private cabinets → H1 → behind the grand antechamber → the lord's bedchamber | jib door in hangings (wool-faced panel), 1-wide link through the cabinets | Versailles, 6 Oct 1789 |
| H4 | **The vice stair** — lord's wardrobe (G) → lord's bedchamber (noble) → consort's supper closet (via entresol) | tight newel stair in a corner turret | Holyrood 1566 "small vice stair"; Hampton Court bedchamber-to-wardrobe spiral |
| H5 | **Children's stair** — children's lodging (G) → lord's garde-robe (noble) → schoolroom (attic) | B tower in the cabinet zone | Hampton Court (Mary below Henry); Versailles Dauphin below the King [link stair = **design**] |
| H6 | **Stair in the wall** (Duke-of-Athens) — alley door → B1 → G → lord's cabinet | 1-wide straight/dog-leg stair inside a **3-thick** wall | Palazzo Vecchio, Brienne stair 1342 |
| H7 | **Tesoretto** behind a painting + **Studiolo** with cupboards behind panels; a **double hide** (outer strongroom found easily, inner 2 × 2 cell behind a second painting) | `pw:secret_painting`, chests | Palazzo Vecchio Scrittoio/Studiolo; Nicholas Owen's outer-and-inner hide |
| H8 | **Wardrobe door** — judges' room → council cabinet | barrel/shelf wall with a walk-through panel | Doge's Inquisitors' "secret entrance behind a wooden wardrobe" |
| H9 | **Secret Itinerary** — Pozzi (B1) → narrow stair → notary + chancellery (G/mezzanine) → torture room → Piombi (attic) → attic armoury → two flights down to the judges' room | B tower + 1-wide passages, iron doors | Doge's Palace itinerary, in the museum's order |
| H10 | **Bridge of Sighs** — judges' room (noble floor) → prison tower across the canal | enclosed 11-long bridge, **two parallel 1-wide corridors** | Doge's Palace 1600 |
| H11 | **Water stair and water gate** — a stair from the lord's tower bedchamber down to B2 and a water gate on the canal (boat to the river/sewer outfall) | A/B spiral + iron-barred arch at canal level | Tower of London, St Thomas's Tower; Traitors' Gate; Whitehall river steps |
| H12 | **Garderobe-shaft drop** — a closet off the garde-robe with a 1 × 1 shaft (ladder) to the B2 sewer junction | ladder shaft (vanilla ladder: custom blocks cannot be climbable, FURNITURE §) | Baddesley Clinton 1591 |
| H13 | **Flying table** — serving room B1 → dining room | 3 × 1 lift (pistons or a trapdoor + dumbwaiter barrel) | Choisy / Trianon tables volantes |
| H14 | **Bricked-up arch** — a visible blocked Tudor arch in the lord's bedchamber alcove (lore, not a way through) | stone arch infill | Hampton Court arch to Wolsey's lodgings |
| H15 | **Chapel tribune door + crypt stair** — consort's guard room → tribune; crypt under the chapel reached from B1 | door + B stair | Versailles tribune; Habsburg Herzgruft |
| H16 | **Baize door** (kept) | warped door, green wool | R3 §2.3 |

### 4.6 Underground passages (B1 / B2)

| # | From → To | Built as | Documented model | Confidence |
|---|---|---|---|---|
| U1 | **Escape tunnel**: H6/H12 foot (B2) → sewer junction → hidden exit **outside the palace walls** (a garden pavilion trapdoor or a culvert mouth on the river/canal bank) | 2 wide × 3 high, vaulted, lit by rare lanterns; iron door with lever on the inside only | Kremlin Tainitskaya "hidden exit to the Moskva River"; Passetto (escape route, but elevated); Baddesley (sewers) | Model documented; **the long tunnel itself is a composite** |
| U2 | **Chapel crypt passage**: B1 under the corps → crypt under the chapel | 2 wide | Herzgruft / palace-engulfed church (Hofburg) | Partial |
| U3 | **Water gate**: H11 foot → canal arch | stair + 1 landing stage | Tower of London | Documented |
| U4 | **Tower communication tunnels**: B2 junction → prison tower, gatehouse, NE tower (three branches meeting under the court) | 2 wide | Dover Castle 13th-c. tunnels, three passages to three towers meeting in a junction | Documented (castle) |
| U5 | **Service tunnel**: kitchen block → B1 serving room under the dining room (food never crosses the court) | 2–3 wide | Kerr's dinner route "must not cross the track of family traffic" + basement "Dinner-Stair… or… a Lift" (R3 §2.3) | Principle documented, **tunnel = design** |
| U6 | **Stables**: no documented palace-to-stables tunnel was found → **[INVENTION]** if built underground; recommended instead as a covered passage at ground level (Kedleston "curved corridors", R3 §1.3) | — | — | Not sourced |
| U7 | **Wine cellar + ice house**: vaulted cellar 12 × 6 (B1); ice house in the privy garden, brick well 9 deep × 5 wide with a drain to the sewer and a 2-door entrance passage | — | Whitehall cellar; Hampton Court ice house | Documented |

### 4.7 Role beds → rooms (existing roles kept; no new role names without approval)

| Role | Rooms in Palace II | Count (proposal) |
|---|---|---|
| `lord` | lord's state bedchamber; (consort: Q2) | 1 (+1) |
| `noble` | 16 family apartments × 2 adults | 32 |
| `child` | royal night nursery 2 (option 4) + 16 children's chambers × 2 | 34 (36) |
| `servant` | nurses (royal 3 + family closets 16), chambermaids 3, valet 1, governess 1, garrets 24 × 2, little commons ~24 | ~96 |
| `guard` | gatehouse 8, lord's guard room 4, consort's 2, watching chamber 2, prison 2, west-wing guard room 6 | 24 |
| `clerk` | clerks' lodgings west attic 12 | 12 |
| `cell` | Pozzi 4 (B1) + Piombi 4 (attic) — never homes | 8 |

About 200 resident beds (today's palace ~100). The job-station limit still binds: villagers find job blocks only "within 16 blocks and 4 blocks height" (R3 §5.1 rule 7) — working servants' beds stay on the floor of their station.

### 4.8 Engine and integration notes (for the build plan, not decided here)

- Hidden passages and the walk graph: service corridors (H1, H2, U5) should be walkable for servants; the escape network (H3, H4, H6, H11, H12, U1, U3) should probably be **no-walk** for ordinary villagers so they do not wander through it → Q6.
- `pw:secret_painting` and `pw:jib_panel` are walk-through (BP-02 1.3.221); the double hide (H7) needs no new block. The flying table (H13) and the tunnel doors are vanilla redstone; the water gate needs canal water at B2.
- A **true double-helix** (Chambord) is **not buildable with designs A/B/C**: the second helix, offset half a turn, would pass about 2 blocks over every tread, under the ≥2-block headroom law (our rise is 4 blocks per turn). It needs a new design D with 8 blocks of rise per turn → its own program if wanted.
- Basements mean the plot must be dug ~14 deep: stage 1 of the five build stages; the B2 level must meet the town sewer (Q3).
- The 3 × 3 palace needs a 192 × 192 plot in the city plan; where the city planner reserves it was not checked here (read-only brief) → Q7.

### 4.9 Open questions for Abs0lum

1. **Q1** Secret vice stairs (H4, H6, H11): A turret (narrow, like the real ones) or B tower (the 14:21 ruling reserves A for defensive towers)?
2. **Q2** Does the consort get a separate bedchamber (Versailles/Holyrood: separate apartments joined by the secret way — needed for H3) and which role: a second `lord` bed or `noble`?
3. **Q3** Is the palace court at street level, so B2 (−12) meets the sewers?
4. **Q4** Royal nursery for 2 children (court rule) or 4?
5. **Q5** Governess: `servant` or `clerk`?
6. **Q6** Escape network walkable by villagers, or player-only (no-walk)?
7. **Q7** Footprint 3 × 3 (192²) as recommended, or the 4 × 3 metropolis (256 × 192)?

---

## 5. Myths and weakly sourced claims — do not build as fact

| Claim | Status | Source / note |
|---|---|---|
| A tunnel from Holyrood (or the Royal Mile) to Edinburgh Castle, the lost piper | **Legend** (ghost lore) | [Great Castles – Edinburgh ghosts](https://www.great-castles.com/edinburghghost.html) |
| Nesvizh's "secret underground passage" entrance | **Myth**: it was the icehouse melt-water hole | [Gallerix](https://en.gallerix.ru/hi/tayny-zamkovyx-podzemeliy-legendy-i-realnost) |
| Castle spiral stairs turn clockwise to favour right-handed defenders | **Challenged**: 85+ anticlockwise examples; "military determinism… is here challenged" | [Medievalists.net – anticlockwise newel stair](https://www.medievalists.net/2012/08/the-rise-of-the-anti-clockwise-newel-stair/) |
| Casanova cut out of the Piombi through the ceiling/roof | **His own account**; historians ask whether "he simply bribed his way out" | [Justin Plus Lauren](https://justinpluslauren.com/doges-palace-secret-itineraries-tour-venice/) |
| Louis XV's hand-worked "elevator" for his mistresses; Louis XVI's spiked iron gate on that stair | **Weakly sourced** in this pass (popular blog only, no primary record) | [Messy Nessy](https://www.messynessychic.com/2018/05/04/how-monarchs-and-their-mistresses-avoided-the-walk-of-shame) |
| "Dozens of invisible doors" at Versailles | **Plausible, uncounted** (blog, R3 §2.2); two doors in the Queen's chamber are confirmed | R3 §2.2; [Google Arts & Culture](https://artsandculture.google.com/story/cgVhVsHRApPWHA) |
| Underground world/tunnels beneath Versailles | **No evidence found**; results were click-bait pages only | (search, 2026-10-06) |
| Hampton Court tunnels (Wolsey etc.) | **None found**; documented underground works are drains and culverts to the Thames | R3 §1.2 |
| Chambord's stair "by Leonardo da Vinci" | **Attribution unproven**; Chambord says "undoubtedly inspired by" | [Chambord visitor plan](https://cdn1.chambord.org/fr/wp-content/uploads/sites/2/2022/06/plan-visite-fr-2022-ANGLAIS.pdf) |
| Hampton Court kitchens "55 rooms, 3,000 sq ft" | **Area implausible** (R3 caveat) | R3 §1.2 |
| Palace-to-stables tunnels; long secret tunnels to distant churches | **Not documented** in any palace studied; build only as labelled invention | — |
| Exact sizes of the Studiolo, the Tesoretto, Chambord's stair, Holyrood's vice stair | **Not found** — sizes in §4 are design choices | — |

---

## Sources

**New in this brief (fetched 2026-10-06)**
- Château de Versailles / Google Arts & Culture – Tour of the Queen's Chamber: https://artsandculture.google.com/story/cgVhVsHRApPWHA
- Wikipedia – Petit appartement de la reine: https://en.wikipedia.org/wiki/Petit_appartement_de_la_reine
- Wikipedia – Petit appartement du roi: https://en.wikipedia.org/wiki/Petit_appartement_du_roi
- Château de Versailles – Marie-Antoinette's private chambers: https://en.chateauversailles.fr/discover/estate/palace/marie-antoinette-private-chambers
- AFAR – Marie Antoinette's rooms reopened: https://www.afar.com/magazine/inside-marie-antoinettes-reopened-apartment-at-versailles
- Versailles press kit, Chambre du Roi (2026), via P. Cachau: https://www.philippecachau.fr/medias/files/dossier-de-presse-chambre-du-roi-versailles-15-avril-2026-compresse.pdf
- Versailles Century – King's private apartments part 2: https://versaillescentury.com/2016/09/05/versailles-visit-private-apartments-part-2/
- Versailles Century – staircases of the King's private apartments: https://versaillescentury.com/2017/06/26/versailles-staircases-kings-private-apartments/
- Wikipedia – Petit Trianon: https://en.wikipedia.org/wiki/Petit_Trianon
- Château de Versailles – Dauphin's apartment: https://en.chateauversailles.fr/dauphin-appartment
- Château de Versailles – Dauphin and Dauphine apartments: https://en.chateauversailles.fr/discover/estate/palace/dauphin-and-dauphine-apartments
- Château de Versailles – Madame de Polignac: https://en.chateauversailles.fr/discover/history/great-characters/madame-polignac
- Wikipedia – Governess of the Children of France: https://en.wikipedia.org/wiki/Governess_of_the_Children_of_France
- Amis de Versailles (PDF): https://amisdeversailles.com/dyn_img/cms/deea733b3b41bdb986daf895f9503eef.pdf
- Tudor Travel Guide – Henry VIII's lost apartments at Hampton Court: https://thetudortravelguide.com/?p=1274
- Historic Royal Palaces – Uncovering Edward VI's nursery: https://www.hrp.org.uk/blog/uncovering-edward-vis-nursery-at-hampton-court-palace/
- Mental Floss – Hampton Court privies: https://mentalfloss.com/article/559758/how-to-poop-king-henry-vii-hampton-court-palace
- Wikipedia – Ice house (building): https://en.wikipedia.org/wiki/Ice_house_(building)
- Tudor Travel Guide – Holyroodhouse: https://thetudortravelguide.com/holyroodhouse-pleasure-palace-of-the-stuarts/
- Royal Collection Trust – Explore Mary, Queen of Scots' Chambers: https://rct.uk/resources/explore-mary-queen-of-scots-chambers
- Royal Collection Trust – The murder of David Rizzio: https://rct.uk/resources/the-murder-of-david-rizzio
- The Freelance History Writer – Mary and the murder of Rizzio: https://thefreelancehistorywriter.com/2015/01/23/mary-queen-of-scots-and-the-murder-of-david-rizzio/
- Historic Environment Scotland – LB28022 Holyroodhouse: https://portal.historicenvironment.scot/designation/LB28022
- Finestre sull'Arte – Secret Pathways of Palazzo Vecchio: https://www.finestresullarte.info/en/museums/secret-pathways-of-the-old-palace-returns-after-a-year-and-a-half
- MUS.E Firenze – Secret passages: https://musefirenze.it/en/activities/secret-passages/
- Wikipedia – Studiolo of Francesco I: https://en.wikipedia.org/wiki/Studiolo_of_Francesco_I
- Palazzo Ducale – Secret Itineraries leaflet (2019): https://palazzoducale.visitmuve.it/wp-content/uploads/2019/06/itinerari-segreti-ducale-ENG-riv.pdf
- Palazzo Ducale – Secret Itineraries leaflet (2020): https://palazzoducale.visitmuve.it/wp-content/uploads/2020/10/DOWNLOADS-Itinerari-segreti-ducale-ENG-2020.pdf
- Justin Plus Lauren – Doge's Palace Secret Itineraries: https://justinpluslauren.com/doges-palace-secret-itineraries-tour-venice/
- Wikipedia – Piombi: https://en.wikipedia.org/wiki/Piombi
- Italy Guides – Doge's Palace prisons: https://www.italyguides.it/en/veneto/venice/st-mark-s-square/doge-s-palace/prisons
- Structurae – Bridge of Sighs: https://structurae.net/en/structures/bridge-of-sighs
- Wikipedia – Château de Chambord: https://en.wikipedia.org/wiki/Ch%C3%A2teau_de_Chambord
- Chambord visitor plan 2022 (English): https://cdn1.chambord.org/fr/wp-content/uploads/sites/2/2022/06/plan-visite-fr-2022-ANGLAIS.pdf
- Académie de Nice – Le château de Chambord: https://www.pedagogie.ac-nice.fr/dsden06/eac/wp-content/uploads/sites/5/2018/04/Le-chateau-de-Chambord.pdf
- Historic Royal Palaces – Palace secrets: the medieval palace (Tower of London): https://www.hrp.org.uk/media/1239/palace-secrets-medieval-palace.pdf
- Wikipedia – Traitors' Gate: https://en.wikipedia.org/wiki/Traitors%27_Gate
- Wikipedia – Passetto di Borgo: https://en.wikipedia.org/wiki/Passetto_di_Borgo
- Kremlin Museums – Tainitskaya Tower: https://kremlin-architectural-ensemble.kreml.ru/en-Us/architecture/view/taynitskaya-bashnya-moskovskogo-kremlya
- Kent Historic Environment Record – Medieval tunnels beneath the Spur, Dover Castle: https://heritage.kent.gov.uk/Monument/MKE111638
- British Listed Buildings – Queen Mary's Steps, Whitehall: https://britishlistedbuildings.co.uk/101066636-queen-marys-steps-and-fragment-of-whitehall-palace-st-jamess-ward
- Stuff About London – Henry VIII's wine cellar: https://stuffaboutlondon.co.uk/london/henry-viiis-wine-cellar/
- Schönbrunn – audio-guide text (2025): https://www.schoenbrunn.at/fileadmin/content_schoenbrunn/Audioguides/PDFs/Lesetext_PalaceTicket_EN_2025_final.pdf
- Wikipedia – Augustinian Church, Vienna: https://en.wikipedia.org/wiki/Augustinian_Church,_Vienna
- Fascinating Spain – El Escorial and Philip II's room: https://www.fascinatingspain.com/articulo/what-to-see-in-madrid/el-escorial-philip-the-prudent/20220627065845067371.html
- Wikipedia – Baddesley Clinton: https://en.wikipedia.org/wiki/Baddesley_Clinton
- Wikipedia – Nicholas Owen (Jesuit): https://en.wikipedia.org/wiki/Nicholas_Owen_(Jesuit)
- Gallerix – Secrets of castle dungeons: legend and reality: https://en.gallerix.ru/hi/tayny-zamkovyx-podzemeliy-legendy-i-realnost
- Wikipedia – Nursery (room): https://en.wikipedia.org/wiki/Nursery_(room)
- English Heritage – Victorian nursery at Audley End: https://www.english-heritage.org.uk/about/search-news/victorian-nursery-unveiled-audley-end/
- John Jay Homestead – Night & Day Nurseries: https://johnjayhomestead.org/night-day-nurseries-and-nursery-hall/
- Wikipedia – Osborne House: https://en.wikipedia.org/wiki/Osborne_House
- Wikipedia – Nursemaid: https://en.wikipedia.org/wiki/Nursemaid
- Historic Farm – Re-claiming the servants' stairs: https://historicfarm.org/re-claiming-the-servants-stairs/
- World History Encyclopedia – Toilets in a medieval castle: https://www.worldhistory.org/article/1239/toilets
- Medievalists.net – The rise of the anti-clockwise newel stair: https://www.medievalists.net/2012/08/the-rise-of-the-anti-clockwise-newel-stair/
- Great Castles – Ghosts of Edinburgh Castle: https://www.great-castles.com/edinburghghost.html
- Messy Nessy Chic – monarchs and mistresses (weak source, §5): https://www.messynessychic.com/2018/05/04/how-monarchs-and-their-mistresses-avoided-the-walk-of-shame

**Reused from R3 (2026-10-03, original citations there):** Wikipedia – Palace of Versailles; Appartement du roi; Grand appartement de la reine; Château de Versailles – Grand Commun; HRP – The royal court in the Tudor period; British History Online – Hampton Court; Little Waldingfield History Society – Great House of Easement; Doge's Palace guide; Visit Florence / Tickets Florence – Palazzo Vecchio; Wikipedia – Vasari Corridor; Our 10 Year Plan – Palazzo Vecchio secret passages; Kerr, *The Gentleman's House* (archive.org); Wikipedia – Servants' quarters; Medieval Heritage – Wrocław Town Hall; Wikipedia – Torre del Mangia; Wikipedia – Kedleston Hall; Minecraft Wiki – Villager.
