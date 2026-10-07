# CIVITAS — THE LIVING ECONOMY v1 (DRAFT for Abs0lum's review, 2026-10-02)

**Status:** design proposal, nothing built. It extends the canon (STRATEGY-v4, COMPETITIVE-SOCIETY-v2, CAPITAL-AND-CRAFT-v1,
LIVING-WORLD-v1, CADENCE-AND-CONTROL-v1, SOCIAL-DYNAMICS-v1); it replaces none of it.
**His brief (17:12 CT 10-02):** villages and villagers "operate, grow, and evolve autonomously"; competing markets; how a
business is represented in other towns (employment + a market stand? a franchise supplied by the source business?); what
that does to the economy; story "side quests" he may join or ignore, which "continue their narrative" either way; the world
is a tool for the story-driven game he will add later.

---

## 0 · Where we are (honest status)

- **Designed:** the money system, prices, businesses, competition inside one town, stalls, wagons and roads, friction and
  gossip, the chronicle (canon above, 278 KB of design).
- **Built:** the groundwork the behaviour will stand on (markers, homestead, furniture, seats, hatch, structure pipeline,
  the first cottage). See VILLAGER-PROGRESS-2026-10-02.md.
- **Not built:** any villager or village behaviour. In a survival world today, villagers are vanilla.

---

## 1 · Competing markets

### 1.1 Inside one town (canon, unchanged)
- Several businesses per industry. A second one is chartered when **population ÷ catchment ≥ 2** (the Catchment Law) and
  someone has the capital to open it (the capital gate). Nobody "switches competition on"; growth creates it.
- Every purchase is a small auction in the buyer's head: **choice = price × distance × standing × fondness**. Four ways to
  compete: price, quality (better tools and inputs), location, reputation (friends buy from friends).
- Prices float inside a **Price Band** (per-good floor and ceiling) so nothing spirals.
- Losing is graceful: outcompeted → insolvent → staff released → premises re-let. A shop changes hands; nobody starves.

### 1.2 Between towns (NEW)
- **Each town has its own price for each good**, set by its own stock against its own demand. A forest town has cheap timber;
  a quarry town cheap stone; a coastal town cheap fish (from its biome profile).
- **Haulage costs money and time** (wagon days along built roads; more without roads; nothing moves where no route exists).
- **Arbitrage closes the gaps:** when town B pays more for timber than town A charges plus haulage plus a margin, someone
  ships it. Prices between connected towns drift toward *price at source + haulage*. A broken road reopens the gap — that is
  a shortage, a price spike and a story at the same time.
- **Specialisation emerges:** towns grow the industries their land is good at and import the rest. Nobody assigns it.

---

## 2 · How a business is represented in another town — the Presence Ladder (NEW)

Your examples are both right; they are two rungs of one ladder. A business climbs it one rung at a time when the numbers say
so, and each rung has a different cost, risk, control and effect on the host town.

| Rung | What it is in the world | Who works there | Who owns the stock | Money flow | Capital needed | Control |
|---|---|---|---|---|---|---|
| **1 · Supplier** | Its goods sold in someone else's shop in town B under a supply contract | B's shopkeeper | B's shop (bought wholesale) | wholesale price to the source | none | none over the shop |
| **2 · Market stand** | A stall on B's square on Market Day (or the loggia bay in a village) | an employee who travels with a wagon | the source | sales go home; stall rent to B's treasury | a wagon + stall rent | full, part-time |
| **3 · Agent (factor)** | A desk at B's Exchange, inn or town hall taking orders; goods arrive by wagon | a hired local agent on commission | the source | commission to the agent, rest home | small | orders only |
| **4 · Branch** | A shop building in B with the source's name over the door | a hired manager + staff from B | the source (shipped from home) | wages paid in B, profit sent home | a building (bought or rented) + staff | full |
| **5 · Franchise** | A shop in B owned and run by a B local under the source's name and recipes | the franchisee and his staff | the franchisee (buys from the source at a contract price) | contract price + a royalty share to the source; the franchisee keeps the rest | the franchisee's own | a contract: quality, prices inside a range, supply only from the source |

**When a business climbs a rung (the decision rule):**
- its home market is saturated (it already sells about everything its catchment buys), **and**
- town B's price gap for its good is larger than haulage plus a margin, **and**
- it has the capital the next rung needs (rungs 4 and 5 also need a free building or plot in B).
- Owners differ by trait (CADENCE-AND-CONTROL traits): an ambitious owner climbs early, a cautious one late, a proud one
  never franchises his name.

**Franchise drama is built in:** a franchisee who grows strong can break the contract and become an independent rival
(using the recipes he learned — recipe knowledge is property in CAPITAL-AND-CRAFT), or be bought out, or lose the franchise
for poor quality. Branch managers can be poached by rivals. These are the seeds of side stories.

---

## 3 · What it does to the economy

- **Prices converge** between connected towns; isolated towns keep extreme prices (cheap at home, dear for imports).
- **Local incumbents feel it:** a branch with better goods takes share from B's own shop; B's shop either specialises, cuts
  price, joins as a franchisee, or fails gracefully. Consolidation is visible: famous names appear in many towns.
- **Jobs move:** branches and franchises hire in B; stands and agents move fewer people.
- **Money moves:** branch profits flow home (the source town grows richer); franchise profits stay mostly in B (B grows
  too). A region full of branches of one city becomes dependent on it; a region of franchises stays balanced.
- **Roads become economic arteries:** the Roadwright's network decides who can trade; a road cut is felt everywhere.
- **Stability rules still hold:** the Price Band, the money supply growing only with population, sinks that return money to
  treasuries (rents, fees, taxes → public wages). Expansion cannot print money.

---

## 4 · Autonomous growth and evolution

- **Every town has goals** weighted by its people: feed everyone, house newcomers, improve buildings, connect to neighbours,
  grow its trade. The town hall (clerk / mayor) spends the treasury on the top goal it can afford.
- **Growth ladder (canon tiers):** minimal village → village → town → city, by population and wealth thresholds. Each step
  unlocks building types (STRUCTURE-PROGRAM-v1) and businesses (Catchment Law).
- **Buildings evolve through stages and renovations:** every building is a set of authored stages; the village clock moves a
  building forward when its owner can afford the next stage. Each villager's house is different (your 13:31 ruling).
- **Population:** arrivals come when a town is prosperous and has housing (the Immigrant Faucet); children grow up; people
  move away from failing towns. Decline is possible and graceful: houses empty, shops close, a hamlet can shrink.
- **All of it runs on the village clock in in-game time** (your V2): near you villagers walk and work for real; far away the
  town runs as numbers; when you return it catches up before you see it; closing the game pauses everything.

---

## 5 · Stories you can join or ignore — Threads (NEW)

- **A Thread is a live situation the simulation produces, not a scripted quest:** a rivalry turning bitter, a franchisee
  planning to break away, a shortage after a bridge fails, an inheritance dispute, a debt the baker cannot pay, a branch
  manager stealing stock, a courtship between rival families.
- **Each Thread has:** the people involved, what is at stake, the paths it can take, and a default course with a timeline —
  what happens if nobody outside steps in.
- **You hear about Threads the way a stranger would:** tavern gossip (the gossip graph), a notice on the town-hall board,
  a villager who knows you (fondness) asking for help, or simply noticing an empty shop.
- **If you join**, your actions become inputs (deliver the missing timber, testify, lend money, take a side, expose the
  thief). **If you ignore it**, it resolves on its own by the same rules and the outcome is written in the town's chronicle.
  The world never waits for you.
- **Later, for your story game:** the chronicle and the open Threads are the data a story layer reads; authored story beats
  can be planted as special Threads that use the same machinery.

---

## 6 · Performance and the Bedrock budget

- Ledger in world dynamic properties (32,767 bytes per string; batched writes; daily rollups that forget detail).
- One simulation function for live play, catch-up and the test skip tool, so testing the skip tests offline progress.
- Cognitive level of detail: only villagers near you run full behaviour; distant ones are tallies.
- Budget per tick measured on the workspace server before anything ships (the scanner lesson: never let a background job
  take the whole time slice).

---

## 7 · Build order (proposal)

| Step | What | You can see it |
|---|---|---|
| 1 | Village clock + time tool + buildings advancing through stages (already approved) | skip / step a village and watch it build |
| 2 | Metabolism: the ledger, day segments, villagers walking to their stations, eating, working | a village living a day |
| 3 | Production and stock; prices inside one town; stalls and Market Day | shops with stock, prices changing |
| 4 | Competition inside a town (Catchment Law, buyer choice, graceful failure) | a second bakery opening, one failing |
| 5 | Roads and wagons between towns; inter-town prices; arbitrage | wagons on roads, prices converging |
| 6 | The Presence Ladder (supplier → stand → agent → branch → franchise) | a famous name spreading |
| 7 | Population growth, tiers, decline | a hamlet becoming a town |
| 8 | Threads + chronicle | side stories you can join |

Each step ships with a TestRunner lineup and a BDS run before it reaches you.

---

## 8 · Questions for Abs0lum

```
E1  The Presence Ladder (supplier, market stand, agent, branch, franchise): all five / remove some  -> answer:
E2  Franchisees may break away and become rivals (with what they learned): yes / no  -> answer:
E3  Growth pace in in-game days, roughly: (a) village -> town ~60 days, town -> city ~200 (my pick)  (b) faster  (c) slower  -> answer:
E4  Decline: towns can shrink and buildings can stand empty (never sudden death): yes / no  -> answer:
E5  Money you use: (a) emeralds are the coin (vanilla-compatible)  (b) a CIVITAS coin item  (c) both, exchangeable  -> answer:
E6  Threads reach you by: tavern gossip, the town-hall notice board, villagers who know you asking: all / pick  -> answer:
E7  Build order 1-8 above: yes / changes  -> answer:
```


---
## Rulings 2026-10-02 19:05 (Abs0lum)
- E5 = (b) a CIVITAS coin item is the money; (c) exchange with emeralds is allowed.
- E6 = all three channels (tavern gossip, town-hall notice board, villagers who know you).
- E7 = yes, build order 1-8; step 7 includes IMMIGRATION toward the city (villagers from weaker villages, especially those born after spawn, and from initial spawn).
- Tier vision (18:59): village v1 (minimum requirements: sparse, practical homes) -> v2 -> v3/v4 for village AND town before city; homes diversify and upgrade by tier. City = the spot several towns chose as a market hub, grown by trade, foot traffic and fame (plus the grown-up-town feeling).
- E1-E4 answered 19:09 (see below).
- 19:06: towns get a SECOND, upgraded phase before city: the town where several sellers of the SAME goods compete. That
  competition is what CAUSES the city (the market hub). Tier ladder now: village v1 (minimum) -> village v2 (v3/v4 maybe) ->
  town -> town II (multiple sellers of the same goods) -> city (market hub).

## Rulings 2026-10-02 19:09 (Abs0lum)
- E1 = all five rungs of the Presence Ladder (supplier, market stand, agent, branch, franchise): "all five are necessary - this needs to follow realism."
- E2 = yes: franchisees may break away and become rivals (with what they learned).
- E3 = (a): village -> town ~60 in-game days, town -> city ~200.
- E4 = yes: decline is real (towns shrink, buildings stand empty), never sudden death.
- All E1-E7 now answered; the draft's questions section is closed.
