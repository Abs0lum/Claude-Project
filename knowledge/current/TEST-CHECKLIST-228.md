# Combined test — BP-02 1.3.228 + RP-04 1.3.159 + RP-01 1.3.125 (program 228, 2026-10-06)

## Install (PS5, your world)
1. Remove from the world: **AR Spiral Stairs Test BP + RP** (0.0.1–0.0.3). The main packs now carry the spirals and the pad (same structure name).
2. Behaviour packs, top to bottom: **BP-02 AbsolutRealism Tectonic BP 1.3.228**, PW-Civitas-Markers BP 0.2.4 (unchanged), your other BPs as before.
3. Resource packs: **RP-13 AbsolutRealism Architecture RP 1.0.0 (NEW: the 8-block ramps + the spiral stairs)**, **RP-04 AbsolutRealism Basic RP 1.3.159**, **RP-01 AbsolutRealism Tectonic RP 1.3.125**, RP-12 1.0.1 (unchanged), the others as before.
4. Script API is now 2.10.0 (BDS 1.26.52 = your v26.52 loads it).

## Checklist (what to look for; one line each)
### Saves and stability
- [ ] Close the game in a town and reopen: the town continues (save on close).
- [ ] No hitches when a tier rises (marks are stepped).
### Civs speak (B5)
- [ ] Bubbles over heads; two friends talk at dusk; a petitioner walks to you and asks; "I'll see to it" — the census checks in 5 days.
- [ ] Talking to a civ stops him and he faces you.
### Growth (B6)
- [ ] Districts look alike within a street (skins); a resting family is skipped after a failed search.
- [ ] `/scriptevent pw:clock prio bakery` builds a bakery first inside the tier.
- [ ] Old houses get mossy/cracked over time; past the bad level the council fines and repairs them (log line).
- [ ] Short gaps between houses get a well, a bench, a hay cart or a lamp post (fillers only).
- [ ] Leaves and logs over a street corridor are cleared (headroom).
### Coins and economy (B7/B8)
- [ ] Silver nickel coins (1 penny; 12 = a gold coin); prices shown in exact coins + nickels; change given in nickels.
- [ ] Market: Notices (deliver goods for a reward); carters walk loads from stores to sites.
- [ ] `/scriptevent pw:clock tax low|normal|high`, `audit`, `board`.
### Names (B9)
- [ ] "Now entering <Town> · <District>" on the action bar; the town earns a title (e.g. Market Town).
### The watch (B10)
- [ ] Ring a bell: children and elders go home (why code "the bell!").
- [ ] Many monsters at night: grown civs band together to fight; the watch carries light at night.
- [ ] Market button "The town's chronicle": the annals and the latest news.
### You (B11)
- [ ] Prices fall as the town likes you (friend 0.9, hero 0.8); talking counts 3 times a day per civ; Give button for gifts.
- [ ] A wedding / tier-up / the monthly holiday: everyone gathers in a ring on the square at dusk, particles, +mood.
- [ ] Dusk speech by the town hall keeper (3 lines) when you stand near the square.
- [ ] Your title in the talk window (Citizen, Burgher, Alderman, Councillor); an Alderman may rename a district by vote.
- [ ] "Show me the way to…": the civ walks you there and waits when you fall behind.
### Role beds (palace)
- [ ] `/scriptevent pw:clock beds`: who sleeps in the lord's chamber, apartments of state (couple + up to 2 children), guard rooms, clerks' lodgings, servants' quarters.
- [ ] Children's beds against the walls in the apartments.
### Spiral stairs
- [ ] `/structure load pw:spiral_pad ~ ~ ~`: walk all six; each ends flush at the floor in front.
- [ ] Palace: gatehouse (A to the lodge, C up the tower), prison tower C, 5 back stairs B, commons B (stair hall), coach house B.
- [ ] Middle floors: step off sideways through the gap beside the step; top: the floor in front.
- [ ] Creative menu: 8 spiral blocks (A/B/C × stone / oak / spruce + plaster).

## Not in this build (queued)
- Castles in the game (design only: A in towers, C in keeps, thatch gables, caphouses).
- Palace II (enlarged, real blueprints, secret passages), diagonal catwalks, furniture import (needs your markup).
- Witnessed deeds are built but OFF; crime factors are measured only.
