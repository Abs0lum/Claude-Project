# R2 — Material Economy, Wages and Construction Costs for CIVITAS

**Status:** research report, 2026-10-03. Every historical number below is tagged **[SOURCED]** with a URL in the Sources list; every game rule is tagged **[PROPOSED]**. Derived figures (my arithmetic on sourced inputs) are tagged **[DERIVED]**. All arithmetic was checked in Python.

**Scope:** (1) medieval/early-modern wages and prices, (2) building-material supply chains, (3) economic structure of towns, (4) how other games model material economies, (5) a concrete CIVITAS model: materials, production rates, wages, prices, bills of materials, a tier-cost ladder from village to metropolis II, and anti-deadlock rules.

---

## 0. The one-paragraph answer

Medieval building was a **wage economy, not a materials economy**: at Vale Royal Abbey (1278-80) cart hire plus all purchased materials added only about 20 % to the wage bill ([Knoop & Jones](https://historyofeconomicthought.mcmaster.ca/knoop/MediaevalMason.pdf)), and the Caernarfon accounts for 1285-6 show £151 spent on materials against £535 spent *carting* them ([Herefordshire Through Time](https://htt.herefordshire.gov.uk/herefordshires-past/the-medieval-period/castles/building-a-castle/preparation-and-construction)). Stone was cheap at the quarry and ruinous ten miles away: twelve miles of land carriage cost about as much as the stone itself ([Gimpel via Coins and Scrolls](https://coinsandscrolls.blogspot.com/2019/09/osr-medieval-miners-or-goddamn.html?m=1)), and land : river : sea transport cost roughly 8 : 4 : 1 per ton-mile ([Langdon & Claridge](https://static1.squarespace.com/static/5a4d52ff7131a5845cdd5162/t/5a503b02652dea46dba01c55/1515207426683/Claridge+Transport+Medieval+England.pdf)). That is why towns built with whatever was local, and why a palace is expensive: not because stone is dear, but because it needs thousands of paid worker-days of skilled labour, fed and paid every week. The CIVITAS model below therefore prices buildings mostly in **worker-days and wages**, lets **distance** decide whether a settlement is stone, timber or brick, and makes the top tiers expensive by requiring **imported labour and a money supply big enough to pay it**.

---

## 1. Wages and prices, England 1300-1600 (plus continental examples)

### 1.1 Daily wages [SOURCED]

| Trade | c. 1300 | 1351 statute maximum | c. 1390s | 1450s | Notes / source |
|---|---|---|---|---|---|
| Unskilled labourer | 1-1.5 d | 1.5 d (craftsmen's servants) | 3.25 d | 4.4 d | 1307: "1d or 1.5d" ([Ward PDF](https://wardfamily.blog/wp-content/uploads/2022/03/Cost-of-Living-in-14th.-Century-England13872.pdf)); 1390s 3.25 d ([Mittelzeit](https://mittelzeit.blogspot.com/2019/03/prices.html)); decadal 1.7 d (1300s), 2.7 d (1350s), 3.7 d (1400s), 4.4 d (1450s), 6.3 d (1550s) ([Clark](https://faculty.econ.ucdavis.edu/faculty/gclark/papers/Condition.pdf)) |
| Thatcher / thatcher's mate | 2.5 d / 1 d | — | 4.25 d / 2.75 d | 5.5 d / 3.25 d | Dyer's decadal series reproduced in [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Carpenter | 3 d | master 3 d, other 2 d | 4.25 d | 5.8 d (craftsman avg) | [Ward](https://wardfamily.blog/wp-content/uploads/2022/03/Cost-of-Living-in-14th.-Century-England13872.pdf), [Statute of Labourers](https://sourcebooks.web.fordham.edu/seth/statute-labourers.asp), [Clark](https://faculty.econ.ucdavis.edu/faculty/gclark/papers/Condition.pdf) |
| Master carpenter | 6 d | 3 d | — | — | [Ward](https://wardfamily.blog/wp-content/uploads/2022/03/Cost-of-Living-in-14th.-Century-England13872.pdf) |
| Mason | 4 d (rural manors pre-1337) | master freemason 4 d, other masons 3 d | 6 d (£8/yr) | 6 d | Oxford/Cambridge master craftsmen fixed at 6 d/day from 1363 to 1536; London 8 d from 1406 ([Munro](https://www.economics.utoronto.ca/munro5/REH21MunroWageStickiness.pdf)) |
| Master mason (royal works) | 2 s/day (Walter of Hereford, Vale Royal 1278) | — | 1 s/day (Henry Yevele 1369) | — | [Knoop & Jones](https://historyofeconomicthought.mcmaster.ca/knoop/MediaevalMason.pdf) |
| Skilled mason, Vale Royal 1278-80 | 2 s 6 d per week | — | — | — | [Knoop & Jones](https://historyofeconomicthought.mcmaster.ca/knoop/MediaevalMason.pdf) |
| Tiler | — | 3 d, knave 1.5 d | — | — | [Statute](https://sourcebooks.web.fordham.edu/seth/statute-labourers.asp) |
| Mower (per acre or per day) | — | 5 d | — | — | [Statute](https://sourcebooks.web.fordham.edu/seth/statute-labourers.asp) |
| Haymaking | — | 1 d | — | — | [Statute](https://sourcebooks.web.fordham.edu/seth/statute-labourers.asp) |
| Weaver (no food) | — | — | 5 d (1407) | — | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Archer / Welsh infantry | — | — | 3 d / 2 d (1346) | — | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Knight | 2 s (1316) | — | 4 s/day | — | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html), [History Hit](https://www.historyhit.com/money-in-medieval-england/) |

Skill premium: craftsman ÷ labourer fell from **1.93 (1300s)** to **1.33 (1450s)** ([Clark](https://faculty.econ.ucdavis.edu/faculty/gclark/papers/Condition.pdf)); English journeymen "came to earn two-thirds of their masters' wage by the 15th century" ([Munro, MPRA](https://mpra.ub.uni-muenchen.de/11209/)).

Working year: Munro's real-wage series assume **210 paid days a year** ([Munro, MPRA](https://mpra.ub.uni-muenchen.de/11209/)); Exeter Cathedral pay-sheets show actual work weeks of **4.9-5.3 days** rather than six ([Ridolfi](https://link.springer.com/article/10.1007/s11698-026-00331-3)); Antwerp-Lier building workers averaged 210 days (1451-75) rising to 260 (1540s) ([Munro](https://www.economics.utoronto.ca/munro5/REH21MunroWageStickiness.pdf)). Annual: "a labourer made at most £2 a year in 1300 ... 2 pence a day" ([History of England](https://thehistoryofengland.co.uk/resource/medieval-prices-and-wages/)).

Non-wage labour: around 1300 some **105,000 famuli** (permanent manorial servants, ~2 % of the population but a third to a half of demesne labour) were paid mostly in grain; cash rose from ~20 % to 35 % of their pay by the 1380s-1420s; day-labourers' annual earnings "doubled from approximately 25 s to 50 s per year by the 1430s" ([Brewminate](https://brewminate.com/manorial-famuli-wages-and-labor-relations-in-the-middle-ages/)). A carter at Peasenhall in 1296 got 3 s cash a year plus 4.31 quarters of maslin; a day's "basket of consumables" then cost 0.55 d ([LSE](https://www.lse.ac.uk/asset-library/rftw/reappraising-medieval-english-agricultural-wages.pdf)).

**Continental examples [SOURCED]**
- Bruges master building craftsmen: 5 d groot per day in 1349 → 12 d groot by 1387; Antwerp masters 12 d groot Brabant (1442-86); Mechelen 12 d → 13.5 d groot (1434-1540) ([Munro](https://www.economics.utoronto.ca/munro5/REH21MunroWageStickiness.pdf)). At the Black Death English masters' real wages were only a third of Bruges masters'; by the 1480s about 80 % ([Munro, MPRA](https://mpra.ub.uni-muenchen.de/11209/)).
- Florence: masons 13.4 soldi/day (1349) → 16.8 (1350); unskilled 8.4 → 10 soldi; blacksmiths 25-50 soldi; 1 florin = 64 soldi ([Caferro](https://economics.yale.edu/sites/default/files/florence_wages-caferro.pdf)).

### 1.2 Prices [SOURCED]

| Item | Price | Date | Source |
|---|---|---|---|
| Farthing loaf (cheapest bread) | ¼ d; weight slides with wheat: 6 lb 16 s (troy) when wheat is 12 d/quarter | 13th c. onward | [Ward](https://wardfamily.blog/wp-content/uploads/2022/03/Cost-of-Living-in-14th.-Century-England13872.pdf), [Assize of Bread](https://en.wikipedia.org/wiki/Assize_of_Bread_and_Ale) |
| Ale | 0.75-1.5 d/gallon | 14th c. | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Wine (Gascon, London) | 4 d/gallon | 1331 | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Wheat | 6-8 d/bushel (1260); 7.5-8.5 d (1300); 8-16 d (1350) | | [Mittelzeit](https://mittelzeit.blogspot.com/2019/03/prices.html) |
| Oats | 1 s/quarter Somerset, 2 s 2 d London | 1338 | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| 2 chickens; 2 dozen eggs | 1 d each | 14th c. | [History Hit](https://www.historyhit.com/money-in-medieval-england/) |
| Goose | 6 d | 1375 | [History Hit](https://www.historyhit.com/money-in-medieval-england/) |
| Sheep / wether | 17 d; 9-10 d Somerset, 1 s 5 d London | mid-14th c. / 1338 | [History Hit](https://www.historyhit.com/money-in-medieval-england/), [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Pig | 24 d (1338); 2-3 s | 1338 | [History Hit](https://www.historyhit.com/money-in-medieval-england/), [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Cow | 6 s (1285-90); 72 d (1301); 9 s 5 d (mid-14th); 10-12 s (1307) | | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html), [Mittelzeit](https://mittelzeit.blogspot.com/2019/03/prices.html), [Ward](https://wardfamily.blog/wp-content/uploads/2022/03/Cost-of-Living-in-14th.-Century-England13872.pdf) |
| Ox | 13 s 1¼ d | mid-14th c. | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Draught / cart horse | 10-20 s; 144-240 d | 13th c. / 1301 | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html), [Mittelzeit](https://mittelzeit.blogspot.com/2019/03/prices.html) |
| Warhorse | up to £80 (13th c.); £50-80 | | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html), [Ward](https://wardfamily.blog/wp-content/uploads/2022/03/Cost-of-Living-in-14th.-Century-England13872.pdf) |
| Feeding one person on an estate | lord 7 d, esquire 4 d, yeoman 3 d, groom 1 d per day | c. 1380 | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Spade 3 d; axe 5 d; hammer 8 d-2 s 8 d; 2 chisels 8 d; anvil 20 s; bellows 30 s | | 1457-1514 | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Rent: cottage 5 s/yr; craftsman's house 20 s/yr; merchant's house £2-3/yr | | 14th c. | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |

### 1.3 Building and palace costs [SOURCED], with labour-day equivalents [DERIVED]

| Building | Money cost | Source |
|---|---|---|
| Cottage, 1 bay, 2 storeys | £2 (early 14th c.) | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Well-built row house, York | up to £5 | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Craftsman's house with shop, 2-3 bays, tiled | £10-15 (one reconstruction: 6,000 d = 2,400 d materials + 3,600 d labour) | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html), [Ye Olde Tyme News](https://www.yeoldetymenews.com/p/how-affordable-was-life-in-the-middle) |
| Modest hall and chamber, labour only | £12 (1289) | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Merchant's house / house with courtyard | £33-66 / £90+ | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Goldsmiths' Hall, London (hall, kitchen, buttery, 2 chambers) | £136 (1365) | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Large tiled barn | £83 (1309-10) | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Stone gatehouse 40 × 18 ft | £16 13 s 4 d without stone; ~£30 with stone (1313) | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Stonework of a 125-ft church, no tower (contract) | £113 (13th c.) | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Transept of Gloucester Abbey | £781 (1368-73) | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Castle curtain-wall tower | £333-395 (late 14th c.) | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html) |
| Tattershall Castle and college | £450/yr for 13 years (1434-46); ~700,000 bricks | [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html), [Wikipedia](https://en.wikipedia.org/wiki/Tattershall_Castle,_Lincolnshire) |
| Kirby Muxloe Castle | ~£1,000, 1.3 million bricks, >40 men at peak, 1480-84 | [Wikipedia](https://en.wikipedia.org/wiki/Kirby_Muxloe_Castle) |
| Peveril (small tower) / Orford / Dover / Rhuddlan / Château Gaillard | £200 / £1,400 / £7,000 / £9,000 / £15,000-20,000 | [Castles & Manor Houses](https://www.castlesandmanorhouses.com/architecture_08_building.htm) |
| Vale Royal Abbey, first 4 years | £3,000; then £1,000/yr budgeted; 35,000 cartloads of stone | [Wikipedia](https://en.wikipedia.org/wiki/Vale_Royal_Abbey) |
| Harlech Castle | £8,190 | [History of England](https://thehistoryofengland.co.uk/resource/medieval-prices-and-wages/) |
| Beaumaris Castle | £15,000 by 1330, never finished; £270 a week in wages | [Wikipedia](https://en.wikipedia.org/wiki/Beaumaris_Castle) |
| Caernarfon Castle and town walls | £20,000-25,000 (1283-1330); £12,000 by 1292 | [Wikipedia](https://en.wikipedia.org/wiki/Caernarfon_Castle) |
| Edward I's Welsh castles | £80,000 (1277-1304); £95,000 (to 1329) | [Castles & Manor Houses](https://www.castlesandmanorhouses.com/architecture_08_building.htm) |
| Westminster Abbey (Henry III) | >£29,000 by 1261, final "near £50,000"; up to 400 workers on site in summer | [Wikipedia](https://en.wikipedia.org/wiki/Westminster_Abbey) |
| Windsor Castle (Edward III, 1350-77) | £51,000, "over one and a half times Edward's typical annual income of £30,000" | [Wikipedia](https://en.wikipedia.org/wiki/Windsor_Castle) |
| Hampton Court | Wolsey 200,000 crowns (= £50,000); Henry VIII £62,000; William III £131,000 (£113,000 in 1689-94) | [Wikipedia](https://en.wikipedia.org/wiki/Hampton_Court_Palace), [Grunge/HRP](https://www.grunge.com/238645/how-much-it-really-cost-to-build-hampton-court-palace-home-of-king-henry-viii/), [HRP](https://www.hrp.org.uk/media/1871/hcphistory_v2.pdf) |
| Nonsuch Palace | at least £24,000 | [Wikipedia](https://en.wikipedia.org/wiki/Nonsuch_Palace) |
| Versailles | ~80 million livres over 1664-1715, "less than 3 % annually of state expenditure"; of 65 million spent before 1690, 25 million (~40 %) went on the waterworks; ~2,300 rooms, 63,154 m² | [fr.wikipedia](https://fr.wikipedia.org/wiki/Ch%C3%A2teau_de_Versailles), [en.wikipedia](https://en.wikipedia.org/wiki/Palace_of_Versailles) |

Scale references [SOURCED]: a typical baron's income was ~£700/yr, so Beaumaris's £270 weekly wage bill was a third of a baron's annual income and the castle twenty times it ([Wikipedia](https://en.wikipedia.org/wiki/Beaumaris_Castle)); crown revenue at peace c. 1300 was ~£30,000 ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)); castle maintenance ran £20-50 a year at Exeter and Gloucester in the late 12th century ([Castles & Manor Houses](https://www.castlesandmanorhouses.com/architecture_08_building.htm)); Tattershall's 1,296,000 d would have taken a labourer "2,700 years of wages" ([Ye Olde Tyme News](https://www.yeoldetymenews.com/p/how-affordable-was-life-in-the-middle)).

**Labour-day equivalents [DERIVED].** Using the Vale Royal finding that materials and carts were ~20 % on top of wages (wages ≈ 80 % of cost) and a blended site wage of 3 d/day:

| Building | £ | Labour-days (LD) | Crew-years at 210 days |
|---|---|---|---|
| Cottage | 2 | 128 | 0.6 |
| Craftsman's house | 12.5 | 800 | 4 |
| Merchant's house | 50 | 3,200 | 15 |
| Goldsmiths' Hall | 136 | 8,700 | 41 |
| Castle tower | 364 | 23,300 | 111 |
| Gloucester transept | 781 | 50,000 | 238 |
| Harlech | 8,190 | 524,000 | 2,500 |
| Beaumaris | 15,000 | 960,000 | 4,570 |
| Westminster Abbey | 50,000 | 3,200,000 | 15,200 |
| Hampton Court (Henry VIII's works) | 62,000 | 3,970,000 | 18,900 |

Cross-check: Bachrach's reconstruction of the tower of Langeais (992-994; 17.5 × 10 m base, 16 m high, 1.5 m walls, ~1,050 m³ = 2,600 t of limestone) gives **94,930 average working days** in total: procurement 14,250, transport 2,880, unskilled 63,500, mason 12,700, smith 1,600 ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)) — about four times my cost-derived figure for a 14th-century tower, which is the expected gap between 10th-century hand-methods and a late-medieval site with treadwheel cranes that let "a single man hoist a weight of up to 600 kg" ([Wikipedia, Gothic cathedrals](https://en.wikipedia.org/wiki/Construction_of_Gothic_cathedrals)). Beaumaris's £270 a week spread over the first-summer workforce of 1,800 workmen, 450 masons and 375 quarriers works out at **4.1 d per worker-day** [DERIVED], consistent with a mason-heavy mix.

### 1.4 Wages vs materials, and how many people a site employed [SOURCED]

- Vale Royal 1278-80: cart hire and materials "represented an addition of approximately 20 per cent to the wages bill"; on average **135** masons, quarriers, carpenters, smiths, diggers and carters, of whom **15 quarrymen** and **31 carters**; masons fell from 92 (1277) to 53 (1280) ([Knoop & Jones](https://historyofeconomicthought.mcmaster.ca/knoop/MediaevalMason.pdf), [Wikipedia](https://en.wikipedia.org/wiki/Vale_Royal_Abbey)).
- Caernarfon 1285-6: materials £151 5 s 6½ d, transport £535 8 s 8½ d ([Herefordshire Through Time](https://htt.herefordshire.gov.uk/herefordshires-past/the-medieval-period/castles/building-a-castle/preparation-and-construction)).
- Beaumaris 1295-6: Master James of St George asked for "400 masons, both cutters and layers, together with 2,000 less skilled workmen, 100 carts, 60 wagons and 30 boats bringing stone and sea coal; 200 quarrymen; 30 smiths"; up to 3,500 at the summer peak; pay was "very much in arrears" ([World History Encyclopedia](https://www.worldhistory.org/Beaumaris_Castle/), [Wikipedia](https://en.wikipedia.org/wiki/Beaumaris_Castle)).
- An average motte took ~50 people about 40 working days; a stone castle "the best part of a decade" ([Castles & Manor Houses](https://www.castlesandmanorhouses.com/architecture_08_building.htm)); walls rose 20-50 cm a day because lime mortar needs up to a week to set, and work ran about six months a year ([Herefordshire Through Time](https://htt.herefordshire.gov.uk/herefordshires-past/the-medieval-period/castles/building-a-castle/preparation-and-construction)).
- Stone gatehouse 1313: £16 13 s 4 d for everything except stone vs ~£30 with stone — stone ≈ 44 % of that small job [DERIVED from Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html). The craftsman's-house reconstruction above is 40 % materials / 60 % labour ([Ye Olde Tyme News](https://www.yeoldetymenews.com/p/how-affordable-was-life-in-the-middle)).

Design reading: small vernacular buildings are ~40 % materials; big masonry is ~15-20 % materials; monumental finishing (carving, glazing, furnishing — "much of the expenditure was lavished on rich furnishings" at Windsor, [Wikipedia](https://en.wikipedia.org/wiki/Windsor_Castle)) pushes the labour share even higher.

---

## 2. Materials: supply chains and regional building traditions

### 2.1 Quarrying and stone [SOURCED unless marked]

- Vale Royal: **35,000 cartloads** of stone, "over 30 per day", hauled nine miles from the Eddisbury quarries over 1277-81 ([Wikipedia](https://en.wikipedia.org/wiki/Vale_Royal_Abbey)); with 15 quarrymen on average that is **~2 cartloads per quarryman per working day** [DERIVED], with two carters needed per quarryman at that distance.
- Knoop & Jones found "little evidence as to the scale of operations" of medieval quarries; leases show tiny pits of 20-24 ft square ([Knoop & Jones](https://historyofeconomicthought.mcmaster.ca/knoop/MediaevalMason.pdf)).
- Salisbury Cathedral used **~60,000 t of Chilmark stone + 10,000 t of Purbeck marble**, plus 6,500 t more for the tower and spire (c. 1320); the main body took 38 years (1220-58) ([Bath Geological Society](https://bathgeolsoc.org.uk/journal/articles/2012/2012_Salisbury_Cathedral_Rocks.pdf)); it received some 3,000 marble pillars from Dunshay, and a ship's freight of marble from Corfe cost 41 s under Edward I ([Virtual Swanage](https://www.virtual-swanage.co.uk/things-to-do/education-resources/quarrying-in-purbeck)).
- Dressed-stone prices: 1,450 Caen stones for Winchester Castle cost £3 7 s 6 d (1272); 75 shiploads for the Tower of London £332 2 s; at Autun cathedral (1294-5) "more than 10 % of the total cost is absorbed by expenditures on forges" (sharpening tools) ([Gimpel via Coins and Scrolls](https://coinsandscrolls.blogspot.com/2019/09/osr-medieval-miners-or-goddamn.html?m=1)).
- Langeais tower: 1,050 m³ (2,600 t) of limestone; mortar 350 m³ needing 40 m³ of limestone, 225 m³ of sand and **540 m³ of green wood** to burn the lime ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)).

### 2.2 Transport — the rule that makes regions different [SOURCED]

- "The cost of carriage by land for a distance of 12 miles was about equivalent to the cost of the stone" ([Gimpel via Coins and Scrolls](https://coinsandscrolls.blogspot.com/2019/09/osr-medieval-miners-or-goddamn.html?m=1)); "the cost of transporting the stone often rivaling the price of the stone itself" ([Archaeology Mag](https://archaeologymag.com/2024/08/shipwreck-reveals-medieval-lucrative-stone-trade/)).
- Masschaele's ratio of cost per ton-mile, land : river : sea ≈ **8 : 4 : 1**; oxen hauled at 1.5-2 mph, horses 3-4 mph ([Langdon & Claridge](https://static1.squarespace.com/static/5a4d52ff7131a5845cdd5162/t/5a503b02652dea46dba01c55/1515207426683/Claridge+Transport+Medieval+England.pdf)).
- Canterbury fetched stone by boat from France because "it was easier to quarry and bring stone by boat from France, than it was to travel across land on poor roads" ([Canterbury Cathedral](https://learning.canterbury-cathedral.org/how-did-they-build-that/stone/)); cathedral sites used "as many as twenty teams of two oxen each" ([Wikipedia](https://en.wikipedia.org/wiki/Construction_of_Gothic_cathedrals)).

### 2.3 Timber [SOURCED]

- Grundle House (a modest Suffolk farmhouse) used **330 trees**, 10 % elm, half under 9 inches in diameter, only 3 over 18 inches; Norwich Cathedral's roofs used **680 oaks** of ~15 inches; coppice rotation lengthened from 7 years to 10 by 1600 and 15 by 1750 ([Rackham summary](https://kalikellett.com/2018/02/04/trees-and-woodland-in-the-british-landscape-by-oliver-rackham/)). Windsor Castle's works consumed 3,994 oaks ([Gimpel via Coins and Scrolls](https://coinsandscrolls.blogspot.com/2019/09/osr-medieval-miners-or-goddamn.html?m=1)).
- Bayleaf farmstead (Kent, 1405-30): a two-bay open hall, six rooms, 100-130-acre holding, household of 9-10; arch braces 13 ft long weighing nearly four hundredweight ([Weald & Downland](https://www.wealddown.co.uk/buildings/bayleaf-farmstead-chiddingstone/)).
- Timber for the Vale Royal workshops and lodgings cost only 45 s because it came from the local forests ([Wikipedia](https://en.wikipedia.org/wiki/Vale_Royal_Abbey)).

### 2.4 Lime, brick, thatch, tile [SOURCED]

- Lime kilns: "kilns always made 25-30 tonnes of lime in a batch", one-week turnaround (load, 3 days firing, 2 cooling, unload), ~0.5 t of coal per tonne of lime ([Mittelzeit, lime kiln](https://mittelzeit.blogspot.com/2010/04/lime-kiln.html)).
- Brick: Kirby Muxloe's Flemish brickmaker ran "a workshop able to make up to 100,000 bricks a week"; 1.3 million laid for ~£1,000 all-in ([Wikipedia](https://en.wikipedia.org/wiki/Kirby_Muxloe_Castle)) — about 185 d per thousand including laying [DERIVED]; Eton College needed "more than a million bricks" in 1443-4 ([Knoop & Jones](https://historyofeconomicthought.mcmaster.ca/knoop/MediaevalMason.pdf)); Tattershall ~700,000 bricks ([Wikipedia](https://en.wikipedia.org/wiki/Tattershall_Castle,_Lincolnshire)).
- Thatch: thatcher and helper 2½ d/day (1258-9), 5 d (1399), 3 d (1504), 6 d with meat and drink (1594); a four-square job with ridge took five days; a pigeon house of ~30 squares of water reed cost 24 s (1442) ([Thatching Info](https://thatchinginfo.com/thatching-in-the-later-middle-ages/)).

### 2.5 Why towns used local materials — the design lesson

Put the three sourced facts together — stone cheap at the quarry, carriage equal to the stone every 12 miles, land eight times dearer than sea — and the regional traditions in the Historic England / heritage guides (stone belt, timber-and-thatch lowlands, brick in clay country) are simply the cost-minimising answer. **[PROPOSED]** CIVITAS should not script "mountain = stone"; it should price every bill of materials at *delivered* cost and let each settlement pick the cheapest variant. The regional look then emerges and also changes if a river or road is built.

---

## 3. Economic structure of a medieval town [SOURCED]

- Urbanisation: 5.5 % of England's population in towns in 1086, up to 10 % by 1377; ~500 towns by 1350; over 2,200 market and fair charters issued 1200-70; Coventry had over 300 specialist occupations, Durham ~60 ([Wikipedia, Economics of English towns](https://en.wikipedia.org/wiki/Economics_of_English_towns_and_trade_in_the_Middle_Ages)). By 1516 England had 2,464 markets and 2,767 fairs; the great fairs ran in sequence (Stamford in Lent, St Ives at Easter, Boston in July, Winchester in September, Northampton in November) ([Wikipedia, Charter fair](https://en.wikipedia.org/wiki/Charter_fair)).
- Market spacing: Bracton's rule — two markets within six and two-thirds leagues (twenty miles) on the same or consecutive days harm each other, so the newer is suppressed; licence fees were paid to the Crown; revenue came from tolls and stallage — the Earl of Warwick drew £20 a year from market tolls but only 30 s from stallage in 1298 ([Trytel, market rights](http://users.trytel.com/tristan/towns/market/intro07.html)).
- Public works finance: **murage** (wall tax) first granted to Shrewsbury in 1220 at 4 d per boatload, generally under 1 % of goods' value, granted for a few years and renewed, 1,470 grants recorded ([Wikipedia, Murage](https://en.wikipedia.org/wiki/Murage)); Rye got murage in 1329, 1333, 1336, 1343, 1348, 1369 and 1377 and still supplemented it with levies on fish landed and on 200 trees ([Rye News](https://www.ryenews.org.uk/culture/murage-for-town-wall)); **pontage** for bridges and **pavage** for streets were granted by letters patent for limited terms ([Pontage](https://en.wikipedia.org/wiki/Pontage), [Pavage](https://en.wikipedia.org/wiki/Pavage)); statute labour — the Highways Act 1555 required four days' labour a year from each householder, later commuted to money ([Corvée](https://en.wikipedia.org/wiki/Corv%C3%A9e)).
- Regulation: the Assize of Bread and Ale fixed the price of ale and the weight of the farthing loaf against the wheat price ([Assize](https://en.wikipedia.org/wiki/Assize_of_Bread_and_Ale)); the Statute of Labourers (1351) capped wages at 1346 levels and forbade "meat or drink" on top ([Statute](https://sourcebooks.web.fordham.edu/seth/statute-labourers.asp)); the Carpenters' Guild paid a sick member 14 d a week (1333) ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)).
- Money creation: seigniorage "is the profit a government makes from issuing currency ... historically referred to a lord's right to mint coins" ([Wikipedia](https://en.wikipedia.org/wiki/Seigniorage)).

**The wage-fund loop [PROPOSED reading of the sources].** A royal site like Beaumaris was an external money pump: £270 a week flowed in from the Exchequer, was paid as wages, spent on bread, ale and lodging in the town, and returned to the Crown only slowly as tolls and taxes — when the pump stopped, "the men's pay has been and still is very much in arrears ... they have simply nothing to live on" ([World History Encyclopedia](https://www.worldhistory.org/Beaumaris_Castle/)). A self-funding town, by contrast, has only tolls (~1 %), stallage, rents and fines, which is why walls took decades of renewed murage. CIVITAS needs both: a local loop (wages → shops → suppliers → tolls/taxes → treasury) and an external pump (mint/caravan) with a hard limit.

---

## 4. How other games model it — what works and what fails

| Game | Material flow | Wages / money | Construction | What works | What fails |
|---|---|---|---|---|---|
| **MineColonies** (Minecraft Java) | Workers post *requests*; couriers move items between huts and a central Warehouse (2/4/6/8/10 couriers at levels 1-5); "minimum stock" keeps items pre-positioned ([wiki](https://minecolonies.com/wiki/buildings/warehouse/), [guide](https://www.minecraft-guides.com/mod/minecolonies/)) | No wages; happiness and research instead | Builder follows a blueprint, requests materials, can only build up to the Builder's Hut level | Request/courier model scales; min-stock removes micro-management | Builder requests one item type at a time → endless round-trips; level-1 courier carries a single stack ([issue #3594](https://github.com/ldtteam/minecolonies/issues/3594)); crafters and builders compete for the same warehouse stock, so players asked for a *quota* distinct from min-stock to prevent deadlocks ([issue #4855](https://github.com/ldtteam/minecolonies/issues/4855)); builders wall themselves in |
| **Millénaire** | Lumberjacks, miners and farmers gather and deliver to the town hall; villages build autonomously from that stock "all in real-time" | Deniers (bronze/silver/gold) for trade with the player at the town hall | Villagers build when the village has resources and prosperity | Fully real inventories; growth is visibly driven by resource arrival | Lag; buildings "slice through nearby hills and trees" ([HubPages](https://discover.hubpages.com/games-hobbies/Minecraft-Mod-Examination-Millenaire)) |
| **TekTopia** | Villagers produce; Storage is "the heart of the city"; a visiting Merchant exchanges emeralds for villager-made goods ([wiki](https://sites.google.com/view/tektopia/home/getting-started)) | Emeralds buy profession tokens and structure markers | Player builds everything | Clear single sink/source | No villager construction; emerald-only economy is flat |
| **MCA Reborn** | None — blueprint registers rooms; rank system | Tax percentage brings items to storage but lowers reputation ([Apex guide](https://apexminecrafthosting.com/guides/minecraft/mods/minecraft-comes-alive-reborn-mod/)) | Player builds | Rank gating is a clean tier model | No material economy |
| **Banished** | Physical stockpiles with weight capacity (250 units per square; logs 11, stone 15, iron 25); buildings cost logs/stone/iron (Town Hall 62/124/48; Trading Post 100 wood/40 stone/10 iron, 150 work units; Quarry 80 logs/40 stone) ([stockpile](https://banished-wiki.com/wiki/Stock_Pile), [town hall](https://banishedinfo.com/wiki/Town_Hall), [trading post](https://www.banishedventures.com/wiki/tradingpost/), [gamepressure](https://www.gamepressure.com/banished/production-of-resources/z2608d)) | No currency; barter at trading post | Builders consume stockpiled materials; work-unit counters | Materials are honest; proximity matters ("more efficient when built close to a Stock Pile") | One worker per woodcutter hut; demographic death spirals; no price signal, so shortages are discovered only when things stop |
| **Settlers II** | Every road segment has one carrier; goods are physical objects that queue "like a packet-switched computer network"; chains wood→boards, grain→flour→bread, ore+coal→steel→tools ([Blobs in Games](https://simblob.blogspot.com/2006/07/old-classic-settlers-ii.html)) | None | Builder waits for planks and stone delivered by road | Transport *is* the game; bottlenecks are visible | "Hard to manage everything in your head"; no trend information |
| **Caesar III / Pharaoh** | Walkers: a *market buyer* fetches one commodity at a time from a granary/warehouse; a *market trader* random-walks past houses; one granary feeds 2,400 people for a month; half-staffed storage "won't accept new deliveries" ([Syntax 2000](https://www.syntax2000.co.uk/issues/82/caesar.art.txt), [Caesar3Augustus](https://www.caesar3augustus.com/book/farmingindustry/storagedistribution)) | Denarii from taxes; the walker mechanic was chosen because SimCity-style radius effects "were a bit static" ([Wikipedia](https://en.wikipedia.org/wiki/Caesar_III)) | Monuments "require various worker facilities and building materials" and "take time to be built" ([Pharaoh](https://en.wikipedia.org/wiki/Pharaoh_(video_game))) | Distance failure is legible: a buyer who walks too far leaves the trader "spinning her wheels" | Random walkers starve houses off the loop; pipeline fill-up delays |
| **Anno 1404 / 1800** | Tiered houses (8/15/25/40 residents) consume goods; ascension needs materials in the warehouse (1 tool + 1 wood; +4 stone; +3 stone + 3 glass) and only 80 %/60 %/40 % of houses may ascend ([Anno 1404 wiki](https://anno1404.fandom.com/wiki/Population)) | "consumption = money": residents pay tax while supplied; every building has upkeep, so new buildings lower income until supplied ([Steam thread](https://steamcommunity.com/app/916440/discussions/0/1680315447963675297/)) | Instant, from warehouse stock | Ratio-balanced chains; demand pulls money | Storage-full stalls production; one shortage cascades into tax loss ([Chill Place](https://chillplacegaming.com/anno-1800-supply-chains/)) |
| **Dwarf Fortress (40d economy)** | Coins were physical objects "that need to be acquired, hauled, stored, and tidied up"; accounts started at 200 money; dwarves paid rent and bought meals ([DF wiki 40d](https://dwarffortresswiki.org/index.php/40d:Dwarven_economy)) | Wages per job; room prices driven by furniture quality | n/a | A genuinely closed monetary loop | Rooms "far too expensive", evictions, coin clutter; by v0.31 "it never actually activates" and "Toady said he doesn't think it'll turn on" ([DF wiki talk](https://dwarffortresswiki.org/index.php/v0.31_Talk:Dwarven_economy)); "the swordsmen can't afford the swords, so the goblins kill everyone" ([Crooked Timber](https://crookedtimber.org/2014/01/07/dwarf-fortress-a-marxist-analysis/)) |

Lessons carried into §5: (a) requests must be *batched* per building, not per item (MineColonies); (b) reserve stock for construction separately from consumption stock (the quota/min-stock distinction); (c) money must be a ledger number, never a hauled item, except the player's own purse (Dwarf Fortress); (d) distance must be priced, not just walked (Caesar, Settlers); (e) demand should pull money (Anno) so that goods actually move; (f) every chain needs a visible trend/forecast or the player cannot steer it (Settlers, Banished).

---

## 5. PROPOSED CIVITAS MODEL

Everything in this section is **[PROPOSED]** unless a source is cited for the calibration.

### 5.1 Units and time

| Quantity | Rule | Calibration |
|---|---|---|
| Ledger unit | **penny (p)**, integer. 12 p = 1 **gold coin** item. £1 = 240 p = 20 coins. | Keeps the historical L s d ratios; integer math in the ledger; a stack of 64 coins ≈ £3 4 s ≈ 10 days of a labourer's pay |
| Game day (GD) | 1 GD of work = **24 historical labour-days (LD)** ("a game day is a working month") | Makes a cottage a week's job and a palace wing a multi-year one at the owner's 25/60/120/200-day tier pace |
| Worker-day (WD) | one villager working one GD = 24 LD | Used in all bills of materials |
| Game mile | **100 blocks** | Carting formula below |

Wages per GD are therefore 2 × the historical pence-per-day (24 LD ÷ 12 p per coin).

### 5.2 Materials table

| Material | Unit | Base price at source (p) | Produced by | Consumed by |
|---|---|---|---|---|
| Stone (rough) | 1 cartload ≈ 1 t | 2 | Quarry | Masonry, lime kiln (as limestone), roads |
| Lime | 1 cartload of quicklime | 12 | Lime kiln (from 1 stone + fuel) | Mortar: 1 lime per 8 stone laid |
| Timber | 1 felled tree (BIGCANOPY fall) | 3 | Lumberyard (woodcutter) | Framing, fuel, planks |
| Planks | 4 per timber | 3 | Lumberyard (sawyer pair) | Floors, doors, roofs, furniture |
| Thatch | 1 square (100 sq ft) of reed/straw | 10 | Farm (reed cutter) | Cottage and barn roofs |
| Clay | 1 cartload | 1 | Clay pit (brickworks) | Bricks, tiles |
| Brick | 1,000 bricks | 120 | Brickworks (1 clay + ½ timber fuel) | Chimneys, brick variants, palace |
| Tile | 1,000 tiles | 144 | Brickworks (1 clay + ½ timber) | Town-house and shop roofs |
| Iron | 1 bar bundle | 60 | Mine + smithy | Tools, nails, hinges (1 per 100 stone / 50 timber) |
| Toolset | spade + axe + hammer + 2 chisels | 24 | Smithy (¼ iron + ¼ timber) | Every worker, wears out in 60 GD |
| Glass | 1 crate | 240 | Glassworks (city+) | Church, town hall, palace |
| Food (raw) | 1 person-ration | 18 | Farm | Bakery, butcher, inn |
| Food (ration) | 1 person per GD | 36 (= 1.5 d/day historically, between the groom's 1 d and the yeoman's 3 d) | Bakery, butcher, inn | Everyone, every GD |
| Livestock | cow / sheep / pig / draught horse | 120 / 17 / 30 / 180 | Farm | Butcher, carting |

Price sources for calibration: tools, livestock and rents ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)); feeding costs ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)); bricks ([Kirby Muxloe](https://en.wikipedia.org/wiki/Kirby_Muxloe_Castle)); thatch ([Thatching Info](https://thatchinginfo.com/thatching-in-the-later-middle-ages/)).

**Delivered price rule.** `delivered_p = base_p + base_p × (miles / 12) × mode`, where mode = 1 for cart, 0.5 for river/boat, 0.125 for sea — the Gimpel 12-mile rule and the Masschaele 8:4:1 ratio. A stone that costs 2 p at a quarry 12 game-miles (1,200 blocks) away costs 4 p delivered; 36 miles away, 8 p. The settlement always builds the **cheapest delivered variant** of a building (timber/thatch, stone/thatch, stone/tile, brick/tile), so forest settlements go timber and mountain settlements go stone without scripting, and a settlement that builds a road or a river quay changes its own look.

### 5.3 Production rates (per worker per GD = 24 LD)

| Workshop / worker | Output per GD | Inputs per GD | Calibration |
|---|---|---|---|
| Quarryman | 48 stone | 1 toolset / 60 GD | 2 cartloads per quarryman-day at Vale Royal [DERIVED from [Wikipedia](https://en.wikipedia.org/wiki/Vale_Royal_Abbey) and [Knoop & Jones](https://historyofeconomicthought.mcmaster.ca/knoop/MediaevalMason.pdf)] |
| Carter (horse + cart) | `24 × min(3, 9 / miles)` cartloads moved | 1 draught horse, feed 6 p/GD | Vale Royal needed 2 carters per quarryman at 9 miles; oxen 1.5-2 mph vs horses 3-4 mph ([Langdon & Claridge](https://static1.squarespace.com/static/5a4d52ff7131a5845cdd5162/t/5a503b02652dea46dba01c55/1515207426683/Claridge+Transport+Medieval+England.pdf)) |
| Woodcutter | 24 timber (24 BIGCANOPY falls) | tools | 1 tree per LD; regrowth ties to the 7-year coppice ([Rackham](https://kalikellett.com/2018/02/04/trees-and-woodland-in-the-british-landscape-by-oliver-rackham/)) → set tree regrowth ≈ 7 GD |
| Sawyer pair (2 workers) | 96 planks from 24 timber | tools | pit-saw, one tree per LD |
| Lime kiln (2 workers) | 100 lime | 100 stone + 50 timber | 25-30 t per week-long batch ([Mittelzeit](https://mittelzeit.blogspot.com/2010/04/lime-kiln.html)); Langeais wood ratio ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)) |
| Brickworks (4 workers) | 40 brick or 40 tile units | 40 clay + 20 timber | 10,000 bricks a week per small works; Kirby Muxloe's Flemish works did 100,000 ([Wikipedia](https://en.wikipedia.org/wiki/Kirby_Muxloe_Castle)) |
| Clay digger | 20 clay | — | |
| Farmer | 16 raw food | fields; seed 10 % | game pacing (historically 1 farmer fed ~3-5; 80 % of people farmed) |
| Reed cutter | 48 thatch | — | |
| Baker / butcher | 96 rations from 96 raw food | 2 timber fuel | farthing loaf and 1 d/gallon ale ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)) |
| Miner | 4 iron | 4 timber (charcoal) | |
| Smith | 8 toolsets or 2 iron fittings | 2 iron + 2 timber | spade 3 d, axe 5 d ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)) |
| Mason | lays 10 stone | 1.25 lime, 1.5 labourers hoisting and mixing | 20-50 cm of wall a day; Langeais 5 unskilled per mason ([Herefordshire](https://htt.herefordshire.gov.uk/herefordshires-past/the-medieval-period/castles/building-a-castle/preparation-and-construction), [Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)) |
| Carpenter | frames 12 timber or fits 48 planks | 0.1 iron nails | |
| Thatcher | lays 24 thatch | — | 4 squares in 5 days with helper ([Thatching Info](https://thatchinginfo.com/thatching-in-the-later-middle-ages/)) |
| Labourer | 1 generic WD of site work | — | |
| Finishing craftsman (carver, glazier, painter, plumber) | 1 finishing WD | 0.05 glass/iron | only in church, town hall and palace bills |

### 5.4 Wage table (p per GD; coins in brackets)

| Trade | Wage p/GD | Historical anchor |
|---|---|---|
| Labourer, carter, woodcutter, reed cutter, clay digger | 72 (6) | 3 d/day c. 1390 ([Mittelzeit](https://mittelzeit.blogspot.com/2019/03/prices.html)) |
| Farmer | 60 (5) | famuli paid mostly in grain ([Brewminate](https://brewminate.com/manorial-famuli-wages-and-labor-relations-in-the-middle-ages/)); 2.5 d |
| Quarryman, lime burner, miner | 84 (7) | 3.5 d |
| Sawyer, thatcher, brickmaker, baker, butcher, innkeeper | 96 (8) | thatcher 4-5 d ([Thatching Info](https://thatchinginfo.com/thatching-in-the-later-middle-ages/)) |
| Mason, carpenter, smith | 120 (10) | 5 d small towns, 6 d Oxford ([Munro](https://www.economics.utoronto.ca/munro5/REH21MunroWageStickiness.pdf)) |
| Finishing craftsman, master carpenter, town clerk | 144 (12) | 6 d |
| Master mason (site foreman) | 192 (16) | London 8 d ([Munro](https://www.economics.utoronto.ca/munro5/REH21MunroWageStickiness.pdf)) |
| Hired external worker | local wage × 1.5, lodged at an inn (10 beds per inn) | Beaumaris drew labour nationally and paid arrears ([World History Encyclopedia](https://www.worldhistory.org/Beaumaris_Castle/)) |
| Apprentice / child | 36 (3) | servants 1.5 d ([Statute](https://sourcebooks.web.fordham.edu/seth/statute-labourers.asp)) |

A worker's ration costs 36 p of a 72-144 p wage: 25-50 % on food, the balance available for goods, rent (cottage rent 5 s/yr = 1 p/GD) and savings, which is what makes shops profitable and goods move.

### 5.5 Price table for finished goods (p)

| Good | Sell price | Seller | Note |
|---|---|---|---|
| Bread, dozen loaves | 3 | bakery | farthing loaf ([Ward](https://wardfamily.blog/wp-content/uploads/2022/03/Cost-of-Living-in-14th.-Century-England13872.pdf)) |
| Ale, gallon | 1 | inn | ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)) |
| Ration (bread + ale + pottage per GD) | 36 | bakery/inn | |
| Meat ration | 48 | butcher | goose 6 d, pig 2 s ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)) |
| Inn bed per GD | 24 | inn | board 2 s/week ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)) |
| Toolset | 24 | smithy | |
| Cart (planks 20, iron 1) | 240 | carpenter | |
| Linen shirt / woollen garment | 12 / 36 | tailor (city) | ([History Hit](https://www.historyhit.com/money-in-medieval-england/)) |
| Sword / mail shirt | 6 d = 6 / 1,200 | smithy / armourer | ([History Hit](https://www.historyhit.com/money-in-medieval-england/)) |
| Clerk's deed, market stall licence per GD | 12 / 6 | town hall | stallage ([Trytel](http://users.trytel.com/tristan/towns/market/intro07.html)) |

**Dynamic price rule.** `price = base × clamp( sqrt(target_stock / max(stock, 1)), 0.5, 3.0 )`, recomputed each GD per shop; target_stock = 10 GD of local consumption. Shortage triples the price (which is what calls the caravan), glut halves it (which is what makes the settlement export).

### 5.6 Bills of materials and labour

Site labour is derived from the cost method (wages ≈ 80 % of price, blended 4.5 d/LD, 24 LD per WD); finishing labour is the extra skilled labour of monumental work. Coins = materials at base price + wages (site 108 p/WD blended, finishing 144 p/WD).

| Building | Stone | Lime | Timber | Planks | Thatch | Brick | Tile | Iron | Glass | Site WD | Finish WD | Materials p | Wages p | Total coins |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cottage (timber/thatch) | 4 | 1 | 60 | 40 | 6 | — | — | — | — | 5 | — | 372 | 540 | 76 |
| Cottage (stone/thatch) | 60 | 8 | 20 | 30 | 6 | — | — | — | — | 7 | — | 432 | 756 | 99 |
| Town house (2 households, tile) | 30 | 6 | 200 | 160 | — | — | 3 | 1 | — | 22 | — | 1,704 | 2,376 | 340 |
| Shop / workshop (timber) | 20 | 5 | 330 | 200 | — | — | 4 | 1 | — | 33 | — | 2,328 | 3,564 | 491 |
| Shop / workshop (stone) | 250 | 30 | 90 | 160 | — | — | 4 | 1 | — | 38 | — | 2,256 | 4,104 | 530 |
| Farm (house, barn, fields) | 10 | 2 | 200 | 100 | 20 | — | — | — | — | 30 | — | 1,140 | 3,240 | 365 |
| Lumberyard / sawpit | 10 | 2 | 150 | 80 | 10 | — | — | 2 | — | 20 | — | 948 | 2,160 | 259 |
| Quarry (hut, crane, ramp) | 20 | 2 | 120 | 60 | 6 | — | — | 4 | — | 20 | — | 900 | 2,160 | 255 |
| Lime kiln | 120 | 5 | 30 | 10 | — | — | — | — | — | 20 | — | 420 | 2,160 | 215 |
| Brickworks | 60 | 10 | 200 | 100 | — | — | 2 | 4 | — | 45 | — | 1,668 | 4,860 | 544 |
| Market (cross, stalls, tollbooth) | 80 | 10 | 120 | 200 | — | — | 2 | 2 | — | 30 | — | 1,656 | 3,240 | 408 |
| Inn | 120 | 20 | 600 | 500 | — | — | 10 | 3 | — | 133 | — | 5,400 | 14,364 | 1,647 |
| Guildhall (timber town hall) | 60 | 10 | 400 | 400 | — | — | 6 | 4 | — | 125 | — | 3,744 | 13,500 | 1,437 |
| Town hall (stone) | 900 | 120 | 300 | 400 | — | — | 12 | 6 | 10 | 362 | 75 | 9,864 | 49,896 | 4,980 |
| Chapel | 1,300 | 160 | 120 | 100 | — | — | 8 | 4 | 6 | 325 | 50 | 8,064 | 42,300 | 4,197 |
| Church (parish, with tower) | 6,000 | 750 | 680 | 400 | — | — | 25 | 20 | 40 | 1,583 | 500 | 38,880 | 242,964 | 23,487 |
| Town wall, per 100 m with towers | 2,500 | 300 | 100 | 60 | — | — | — | 10 | — | 600 | — | 9,780 | 64,800 | 6,215 |
| Castle tower / keep | 2,600 | 330 | 100 | 120 | — | — | — | 40 | — | 950 | 25 | 12,324 | 106,200 | 9,877 |
| Stone bridge, 5 arches | 4,000 | 500 | 800 | 300 | — | — | — | 30 | — | 1,250 | — | 19,260 | 135,000 | 12,855 |
| Great church / cathedral | 70,000 | 9,000 | 3,000 | 2,000 | — | — | 120 | 200 | 400 | 20,000 | 15,000 | 391,080 | 4,320,000 | 392,590 |
| Palace wing | 15,000 | 2,000 | 2,000 | 4,000 | — | 1,000 | 120 | 150 | 300 | 5,000 | 30,000 | 290,880 | 4,860,000 | 429,240 |
| Palace great hall and gardens | 30,000 | 4,000 | 4,000 | 8,000 | — | 2,000 | 250 | 400 | 800 | 12,083 | 70,000 | 637,200 | 11,384,964 | 1,001,847 |

Anchors: cottage £2-5 ([Hodges](http://faculty.goucher.edu/eng215/medieval_prices.html)) → 76-99 coins (£3.8-5); craftsman's house £10-15 → 491-530 coins (£25; high side, acceptable); Goldsmiths' Hall £136 → stone town hall 4,980 coins (£249 — a larger building); Beaumaris's 960,000 LD and 2,600 t Langeais tower → keep 23,400 LD / 2,600 stone; Salisbury's 70,000 t → cathedral 70,000 stone; Hampton Court's £62,000 of royal works → palace wing + hall ≈ 1.43 M coins (£71,500). Timber per house follows Grundle House (330) and Norwich (680 oaks for a cathedral-class roof) ([Rackham](https://kalikellett.com/2018/02/04/trees-and-woodland-in-the-british-landscape-by-oliver-rackham/)).

### 5.7 Tier-cost ladder

Buildings added per tier (cumulative; the settlement may build more), total materials, worker-days, coins, and the construction crew needed to finish inside the target window. Households: cottage = 1, town house = 2; workers = 1.5 per household.

| Tier | Target day | Window (GD) | Added buildings | Stone | Lime | Timber | Planks | Brick | Glass | WD | Coins (materials + wages) | Cumulative coins | Households / workers | Crew needed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Village (pre-built) | 0 | — | 4 cottages, farm, bakery | 46 | 11 | 770 | 460 | — | — | 83 | 1,160 | 1,160 | 4 / 6 | — |
| Village II | 25 | 25 | +4 cottages, farm, lumberyard, quarry, butcher, market | 156 | 25 | 1,160 | 800 | — | — | 153 | 2,082 | 3,242 | 8 / 12 | 6 |
| Town | 60 | 35 | +6 cottages, 2 town houses, smithy, inn, guildhall, lime kiln, farm | 414 | 60 | 2,320 | 1,770 | — | — | 415 | 5,291 | 8,533 | 18 / 27 | 12 |
| Town II | 120 | 60 | +4 cottages, 6 town houses, chapel, 2 stone shops, farm, lumberyard, brickworks | 2,076 | 274 | 2,290 | 1,820 | — | 6 | 698 | 8,769 | 17,302 | 34 / 51 | 12 |
| City | 200 | 80 | +12 town houses, stone town hall, parish church, 2nd market, 2 shops, 2 farms, quarry, lime kiln | 8,000 | 1,023 | 4,230 | 3,510 | — | 50 | 2,990 | 35,215 | 52,517 | 58 / 87 | 37 |
| Upgraded city | 350 | 150 | +20 town houses, 500 m of wall, stone bridge, keep, 4 shops, 2 farms, inn | 20,840 | 2,594 | 6,760 | 5,260 | — | — | 6,010 | 65,104 | 117,621 | 98 / 147 | 40 |
| Metropolis I | 600 | 250 | +40 town houses, cathedral, palace wing, 500 m more wall, 6 shops, 4 farms, 2 quarries, brickworks, 2 inns | 100,580 | 12,982 | 16,480 | 15,280 | 1,000 | 700 | 74,579 | 875,493 | 993,114 | 178 / 267 | 298 |
| Metropolis II | 1,000 | 400 | +60 town houses, palace great hall and gardens, 2 more palace wings, 8 shops, 6 farms, 2nd bridge, 2 inns | 68,100 | 9,152 | 23,920 | 28,780 | 4,000 | 1,400 | 155,403 | 1,903,306 | 2,896,420 | 298 / 447 | 389 |

Reading the ladder:
- Village → town II needs 6-12 builders out of 12-51 workers (50 % → 24 % of the workforce), which the village can supply itself. City needs 37 of 87 (43 %) — the first tier where hiring or a longer window is normal.
- Metropolis I needs ~300 builders against a local workforce of 267 that must also farm, quarry and keep shop: it **cannot be built from local labour**. Like Beaumaris, it needs ~200 hired workers lodged in inns, paid 1.5× and fed, and ~3,500 coins a day of construction spending for 250 days — or it takes 600-750 days instead of 250. That is the intended expense.
- Cumulative cost to Metropolis II is 2.9 million coins (£145,000-equivalent), between Henry VIII's and William III's Hampton Court spending and well short of Versailles's 80 million livres: the ceiling is still historically modest.
- Per-day flows at Metropolis I [DERIVED]: 402 stone/day (8-9 quarrymen, 11 carters at 3 game-miles or 34 at 9), 66 timber/day (3 woodcutters), 52 lime/day (1 kiln), 40 masons + 60 labourers on the walls, and ~730 rations/day for 178 households plus 200 hired hands (46 farmers). Production is cheap; the site wage bill (~2,700 coins/day) is the cost, exactly as at Vale Royal.

### 5.8 The money loop and the mint

Per GD, in this order:

1. **Pay wages** from the settlement treasury to every employed villager (ledger transfer; coins as items exist only in the player's purse and shop tills the player can open).
2. **Households buy**: 1 ration per person (bakery/butcher/inn), tool replacement, cloth, rent. Shops' tills receive the money.
3. **Shops buy inputs** from farms, lumberyard, smithy at the dynamic price; keepers keep a margin (sell 36, buy 18 for food).
4. **Treasury income**: market toll 2 % of every sale (murage/toll scale: historically ~1 %, [Murage](https://en.wikipedia.org/wiki/Murage)); stallage 6 p per shop per GD; hearth tax 12 p per household per 30 GD; rents on settlement-owned houses; fines from the clerk; sale of surplus materials to caravans.
5. **Construction spend**: the treasury buys the delivered BOM and pays site wages. A building only progresses when both its reserved materials and the day's wages are on hand.
6. **Mint (seigniorage)**: if money in circulation M < 30 × (daily wage bill), the mint may create new pennies up to **50 % of the value of goods produced in the last 10 GD**, and never more than 5 % of M per GD. Coins are backed by real output; a settlement that stops producing stops minting, so there is no inflation spiral, and a settlement that is producing a lot can fund a big site. Minting is logged as a ledger line so the player can audit it.
7. **Sinks**: tool wear (60 GD), food spoilage (rations expire in 3 GD), building maintenance 2 % of build cost per 365 GD (castles cost £20-50 a year on £1,400-7,000 builds, [Castles & Manor Houses](https://www.castlesandmanorhouses.com/architecture_08_building.htm)), caravan purchases (money leaves), luxury imports.

Money-velocity check at Metropolis I [DERIVED]: total wages ≈ 3,700 coins/GD need M ≈ 112,000 coins in circulation; daily production value ≈ 1,750 coins, so the mint can add at most ~875 coins/GD. With taxes and tolls (~400/GD) the treasury's organic inflow is ~1,300/GD against a 3,500/GD construction appetite: the palace proceeds at about a third of the labour-limited pace unless the player adds coins, exports stone and timber by caravan, or the neighbouring settlements lend. That is the "wage fund" constraint working as intended, and it is the knob to tune (mint share 50 % → 75 % roughly halves metropolis time).

### 5.9 Anti-deadlock rules

1. **Batched requests.** A building site reserves its *entire* bill of materials as one request at groundbreaking; couriers fill it in stock-priority order (stone and lime first for masonry, timber first for frames). Never request one item type at a time ([MineColonies #3594](https://github.com/ldtteam/minecolonies/issues/3594)).
2. **Two stock lines per material**: `consumption_stock` (shops, households) and `construction_reserve` (sites). Min-stock protects consumption (10 GD of rations, 5 GD of fuel); the reserve cannot be eaten by shops ([MineColonies #4855](https://github.com/ldtteam/minecolonies/issues/4855)).
3. **Minimum stock triggers imports.** When a material's stock < min for 3 GD, the clerk posts a caravan order to the nearest settlement with a glut; the caravan arrives in `distance_miles / 20` GD (a day's journey ≈ 20 miles, [Trytel](http://users.trytel.com/tristan/towns/market/intro07.html)) and sells at `delivered_price` (§5.2). If no neighbour has stock, a wandering merchant sells at 3× base after 10 GD. Food and tools always import; stone never deadlocks because it is minable on site at 3× price (quarry overtime).
4. **Wage arrears cap.** If the treasury cannot pay a GD's wages, unpaid workers stop on day 3 (Beaumaris), the site pauses, and the clerk auto-sells construction reserve at 50 % to the caravan to restore 5 GD of wages. The player sees the arrears line in the ledger.
5. **Statute labour.** Each household owes 4 WD per 365 GD of unpaid work on walls, roads and bridges only ([Highways Act 1555 via Corvée](https://en.wikipedia.org/wiki/Corv%C3%A9e)); it can never be used on palaces or churches, so it buffers public works without replacing the wage economy.
6. **Labour import gated by inns.** Hired workers ≤ 10 × inns; hired wage 1.5×; they leave when arrears exceed 3 GD or the site completes. This makes inns a real investment and bounds the wage bill.
7. **Price floors and ceilings** (0.5×-3×) on the dynamic price, with the bread assize as the model: ration price fixed, ration *size* flexes with grain stock (shortage = smaller loaves, hunger penalty) ([Assize](https://en.wikipedia.org/wiki/Assize_of_Bread_and_Ale)).
8. **Player can break but not crash it.** Player sales to a shop are capped at 1 GD of that shop's turnover per GD at the dynamic price; player gifts of coins to the treasury are allowed (the royal pump) but logged and taxed 10 %, and never count as production for the mint.
9. **Forecast line.** Each shop and site shows "days of stock at current burn" and "days to completion at current crew and cash" — the trend information Settlers II and Banished lacked.
10. **Hard invariant for the ledger**: `sum(all tills + treasury + player purse + caravans) == minted − sunk` every GD; log a STOP if it drifts, which catches duplication bugs before they inflate the economy.

### 5.10 Implementation order (plan-first)

1. Ledger pennies + wage payment + ration purchase (closes the smallest loop; verify the invariant in §5.9.10 for 10 GD).
2. Delivered-price function and cheapest-variant selection (verify a quarry moved 12 miles doubles stone cost and flips a cottage from stone to timber).
3. Batched BOM requests with two stock lines (verify a chapel reserves 1,300 stone without starving the lime kiln).
4. Dynamic prices + caravan import (verify a 3-GD food shortage triggers a caravan and the price returns to base).
5. Mint rule + sinks (verify M stays within ±20 % of 30 × wage bill over 100 GD).
6. Tier ladder tables as data; hired labour via inns; finishing craftsmen for church/town hall/palace.

Suggested first witness test: a Town II settlement at day 120 should hold roughly 2,000 stone, 2,300 timber and 300 lime in reserve, employ ~12 builders, and show a treasury that neither empties nor balloons over 20 GD.

---

## Sources

- https://www.historyhit.com/money-in-medieval-england/
- https://mittelzeit.blogspot.com/2019/03/prices.html
- https://wardfamily.blog/wp-content/uploads/2022/03/Cost-of-Living-in-14th.-Century-England13872.pdf
- https://www.economics.utoronto.ca/munro5/REH21MunroWageStickiness.pdf
- https://mpra.ub.uni-muenchen.de/11209/
- http://faculty.goucher.edu/eng215/medieval_prices.html
- https://thehistoryofengland.co.uk/resource/medieval-prices-and-wages/
- https://sourcebooks.web.fordham.edu/seth/statute-labourers.asp
- https://faculty.econ.ucdavis.edu/faculty/gclark/papers/Condition.pdf
- https://economics.yale.edu/sites/default/files/florence_wages-caferro.pdf
- https://link.springer.com/article/10.1007/s11698-026-00331-3
- https://www.yeoldetymenews.com/p/how-affordable-was-life-in-the-middle
- https://en.wikipedia.org/wiki/Assize_of_Bread_and_Ale
- https://brewminate.com/manorial-famuli-wages-and-labor-relations-in-the-middle-ages/
- https://www.lse.ac.uk/asset-library/rftw/reappraising-medieval-english-agricultural-wages.pdf
- https://www.worldhistory.org/Beaumaris_Castle/
- https://en.wikipedia.org/wiki/Beaumaris_Castle
- https://www.castlesandmanorhouses.com/architecture_08_building.htm
- https://en.wikipedia.org/wiki/Caernarfon_Castle
- https://www.autodesk.com/blogs/construction/castle-medieval-construction/
- https://htt.herefordshire.gov.uk/herefordshires-past/the-medieval-period/castles/building-a-castle/preparation-and-construction
- https://historyofeconomicthought.mcmaster.ca/knoop/MediaevalMason.pdf
- https://en.wikipedia.org/wiki/Vale_Royal_Abbey
- https://en.wikipedia.org/wiki/Windsor_Castle
- https://en.wikipedia.org/wiki/Westminster_Abbey
- https://en.wikipedia.org/wiki/Nonsuch_Palace
- https://en.wikipedia.org/wiki/Hampton_Court_Palace
- https://www.grunge.com/238645/how-much-it-really-cost-to-build-hampton-court-palace-home-of-king-henry-viii/
- https://www.hrp.org.uk/media/1871/hcphistory_v2.pdf
- https://fr.wikipedia.org/wiki/Ch%C3%A2teau_de_Versailles
- https://en.wikipedia.org/wiki/Palace_of_Versailles
- https://en.wikipedia.org/wiki/Tattershall_Castle,_Lincolnshire
- https://en.wikipedia.org/wiki/Kirby_Muxloe_Castle
- https://en.wikipedia.org/wiki/Construction_of_Gothic_cathedrals
- https://bathgeolsoc.org.uk/journal/articles/2012/2012_Salisbury_Cathedral_Rocks.pdf
- https://www.virtual-swanage.co.uk/things-to-do/education-resources/quarrying-in-purbeck
- https://archaeologymag.com/2024/08/shipwreck-reveals-medieval-lucrative-stone-trade/
- https://static1.squarespace.com/static/5a4d52ff7131a5845cdd5162/t/5a503b02652dea46dba01c55/1515207426683/Claridge+Transport+Medieval+England.pdf
- https://coinsandscrolls.blogspot.com/2019/09/osr-medieval-miners-or-goddamn.html?m=1
- https://learning.canterbury-cathedral.org/how-did-they-build-that/stone/
- https://kalikellett.com/2018/02/04/trees-and-woodland-in-the-british-landscape-by-oliver-rackham/
- https://www.wealddown.co.uk/buildings/bayleaf-farmstead-chiddingstone/
- https://thatchinginfo.com/thatching-in-the-later-middle-ages/
- https://mittelzeit.blogspot.com/2010/04/lime-kiln.html
- https://en.wikipedia.org/wiki/Economics_of_English_towns_and_trade_in_the_Middle_Ages
- https://en.wikipedia.org/wiki/Charter_fair
- http://users.trytel.com/tristan/towns/market/intro07.html
- https://en.wikipedia.org/wiki/Murage
- https://www.ryenews.org.uk/culture/murage-for-town-wall
- https://en.wikipedia.org/wiki/Pontage
- https://en.wikipedia.org/wiki/Pavage
- https://en.wikipedia.org/wiki/Corv%C3%A9e
- https://en.wikipedia.org/wiki/Seigniorage
- https://www.minecraft-guides.com/mod/minecolonies/
- https://github.com/ldtteam/minecolonies/issues/3594
- https://minecolonies.com/wiki/buildings/warehouse/
- https://github.com/ldtteam/minecolonies/issues/4855
- https://discover.hubpages.com/games-hobbies/Minecraft-Mod-Examination-Millenaire
- https://sites.google.com/view/tektopia/home/getting-started
- https://apexminecrafthosting.com/guides/minecraft/mods/minecraft-comes-alive-reborn-mod/
- https://banished-wiki.com/wiki/Stock_Pile
- https://banishedinfo.com/wiki/Town_Hall
- https://www.banishedventures.com/wiki/tradingpost/
- https://www.gamepressure.com/banished/production-of-resources/z2608d
- https://simblob.blogspot.com/2006/07/old-classic-settlers-ii.html
- https://www.syntax2000.co.uk/issues/82/caesar.art.txt
- https://www.caesar3augustus.com/book/farmingindustry/storagedistribution
- https://en.wikipedia.org/wiki/Caesar_III
- https://en.wikipedia.org/wiki/Pharaoh_(video_game)
- https://anno1404.fandom.com/wiki/Population
- https://chillplacegaming.com/anno-1800-supply-chains/
- https://steamcommunity.com/app/916440/discussions/0/1680315447963675297/
- https://dwarffortresswiki.org/index.php/40d:Dwarven_economy
- https://dwarffortresswiki.org/index.php/v0.31_Talk:Dwarven_economy
- https://crookedtimber.org/2014/01/07/dwarf-fortress-a-marxist-analysis/
