# CIVITAS — ZONE TABLE v1
**Stamp: 2026-09-22 · ruling 17:20 CT (Abs0lum: "I accept these") · D-C219 · companion to
MARKER-AND-FRAME-SPEC-v1 §5 (precedence) and ZONE-GEOMETRY-v2 (the ring).**

The twelve `pw:zone_<kind>` markers shipped in PW-Civitas-Markers 0.1.8 (`/give @s pw:zone_…`
lists exactly these). Until this table, `chamber` and `commons` were used in the specs but never
defined; both readings below were proposed 2026-09-22 17:03 and accepted 17:20. The markers pack
and the behaviour code (access rules, trespass, gossip privacy, pathing) read their semantics
from HERE.

## The table

| rank | kind (`pw:zone_…`) | what it is | examples | who may enter | talk is |
|---|---|---|---|---|---|
| 1 | **threshold** | the transition strip at an opening — the doorway and its approach; greetings, queuing, doorway talk | the 3×2 inside a shop door; the 11×2 apron outside the loggia | anyone the room beyond admits | public |
| 2 | **stable** | animal housing | stalls, byre, coop | staff / household | private |
| 3 | **cellar** | below-grade storage | vaults, root cellar, the brewer's cask room | staff / household | private (conspirators' venue) |
| 4 | **storeroom** | stock storage, above grade | the baker's flour room, the shop's back store | staff — customers may not | private |
| 5 | **kitchen** | the hearth room where food is prepared; **a home's main room IS kitchen when the hearth is there** | cottage hearth room, inn kitchen | household / staff | private |
| 6 | **quarters** | a household's private living space — bedrooms, lofts, the family's main room; nobody from another household | the loft bedroom (ruled: quarters, not chamber); the cottage's main room when the hearth is not in it | that household only | private (gossip does not leave) |
| 7 | **chamber** | **a building-owned single room that is not a household's** — let, assigned, or official | inn guest rooms, the clerk's office, the council chamber, a physician's consulting room | by the building's rule — guests / officials / staff | private |
| 8 | **workfloor** | where the trade's work happens, out of the customer's reach | smithy floor, bakery back room, joiner's shop | staff | semi-private |
| 9 | **shopfloor** | the customer-facing trade floor | the shop, the bar side of the inn, the counter room | customers welcome | public (propagates) |
| 10 | **yard** | open-air working ground attached to a premises | forecourt, work yard, drying yard, the smith's coal yard | semi-public — customers to the front, staff to the back | public |
| 11 | **garden** | cultivated open-air plot | kitchen garden, orchard strip, herb beds | household / staff | private |
| 12 | **commons** | **a shared or public gathering room or covered space** — the room you walk into that belongs to everyone | inn common room, the loggia, the market-hall floor, the green | anyone | public |

**Precedence (MARKER-AND-FRAME-SPEC §5, unchanged):** `threshold > stable > cellar > storeroom >
kitchen > quarters > chamber > workfloor > shopfloor > yard > garden > commons` — smallest area
wins by default; this order settles overlaps where area would give the wrong answer.

## The three rulings in one line each
- **Chambers vs quarters:** quarters belong to a household; a chamber belongs to the building. A bed
  makes neither — ownership does. The inn's beds are chambers; the innkeeper's own bed is quarters.
- **The loft bedroom is quarters.**
- **Is commons the main room you walk into?** Only in a public building. In a home the room you walk
  into is **quarters** (or **kitchen** if it is the hearth room), with a **threshold** strip at the
  door; commons is for rooms that belong to everyone.

## Consequences for the behaviour code (pre-registered, nothing built)
- Access: `chamber` needs a third access class beside customer/staff/household — **guest** (the
  person the building assigned the room to) — the trespass rule reads "not assigned" as a
  high-surprise event exactly like a stranger in quarters.
- Gossip privacy: chamber = private, commons = public (same propagation rule as shopfloor).
- Pathing: a villager crossing an inn goes commons → threshold → chamber; never through another guest's chamber.
- Authoring: a cottage = threshold + (kitchen | quarters) + storeroom/cellar as built; an inn =
  threshold + commons + kitchen + storeroom + chambers ×N + the innkeeper's quarters.
