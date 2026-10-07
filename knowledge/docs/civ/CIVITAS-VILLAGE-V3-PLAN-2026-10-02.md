# CIVITAS — VILLAGE V2/V3 PLAN: skins, tiers on the clock, ELEVATION (2026-10-02 22:2x)
Status: BUILT in BP-02 1.3.207 (undelivered), server-probed (villageprobe 0.0.2/0.0.3 13/13; evoprobe 0.0.1 running).
Rulings applied: 20:04 (my discretion, research-based, no questions → ASSUMPTIONs logged), E3 ~60/~200 days, E4 decline yes,
E7 build order, 22:23 "plans must incorporate elevation changes within the village/town and how they deal with it".

## 1. The village as laid (V1, verified)
13 plots on both sides of an east–west street (3 wide, grass path): north side fronts face south, south side fronts face
north; plots packed west→east with one-block gaps; one plot starts per village day (staggered), each rising through its five
stages (plot 1 day, frame 2, walls 2, roof 1). Ground height per plot = median of the footprint's ground; trees over the
plot cleared; the street in front laid when the plot is laid.

## 2. Skins (V2, verified)
Every dwelling/shop in four skins (a–d: woods, roof form gable↔hip for plain rectangles, roof material spruce/oak/thatch,
hearth stone, furniture wood, door). Nothing moves: markers, zones, lids, stage classes identical. The clock picks a skin
per plot from the village seed (`village [seed]`, `plot cottage_s_b`). Farms, lumberyard, quarry, well keep one skin.

## 3. Tiers on the clock (V3)
| tier | reached at age (days) | adds | notes |
|---|---|---|---|
| village | founding | the 13 | |
| village II | 25 | cottage_s ×2, cottage_m, farm_wheat | more households, more bread |
| town | 60 | bakery, cottage_l, cottage_s ×2, lumberyard, inn | a second street opens when the first is full (26 blocks N/S) |
| town II | 120 | butcher, smithy, cottage_m ×2, cottage_s ×2, farm_cattle | second sellers of the same goods = competition (his tier law) |
| city | 200 | town_hall, bakery, cottage_l ×2, cottage_m ×2, cottage_s ×3, quarry, well | 41 plots, 3 streets |
A tier needs its age AND every plot roofed. Decline (E4): no growth; one shop closes every 20 declining days (cobwebs in
the doorway, its station markers removed — villagers will not work there); immigration reopens closed shops first, then
adds a cottage. Tools: `grow`, `decline on|off`, `immigrate [building]`, `log` (the chronicle — the seed of Threads E6).
ASSUMPTION: until the economy (V5) drives prosperity, growth = days + completion and decline is a switch.

## 4. ELEVATION — how a settlement deals with sloping ground (his 22:23)
Principle: the land is terraced to the buildings, the streets are graded to be walkable, and every door is reachable by
steps. Nothing floats, nothing is buried alive, and the downhill side shows stonework.
1. **Plot datum.** Floor (feet 0) = max(median ground of the footprint, street ground at the door) + 1 → a plot never sits
   below its street; drainage reads right.
2. **Terrace before foundations.** For the footprint plus a one-block margin: cut above the floor (the structure's own air
   does the cut inside the footprint), FILL below the floor slab wherever the ground is lower — cobblestone on the outer
   ring and the margin (a retaining face), dirt inside. Uphill ground outside the margin is left as a bank.
3. **Street profile.** Per column: the median ground of the three rows → smoothed so no two neighbouring columns differ by
   more than one block (the high side is cut); low columns filled with dirt; the surface becomes grass path, and each
   one-block rise is a cobblestone step; plants and overhangs cleared three high.
4. **Stoop.** Where the floor slab is above the street cell in front of the door, cobblestone steps climb from the street
   to the slab, one step further out per block (up to 4), in the plot's own clearance column.
5. **Parallel streets** each keep their own profile at their own height; cross-lanes between streets (with steps) are the
   next item; proper stair / ramp blocks (pw:ramp_cobble family) replace block steps once the look is witnessed.
Verification (evoprobe): per finished plot — no air directly under any floor-slab cell; no street step over one block in
its segment; the door's front cells climb by ≤1-block steps. Site: the probe picks the corner with the most relief.

## 5. Next
V4 villagers (day segments, stations from the fixture cells, homes) → V5 economy (production/stock/prices, competition,
roads/wagons, the Presence Ladder, coin + emerald, Threads) → V6 ship (lineup, brief v4, 1.3.207 + fix round).
