# CIVITAS — MARKER ENTITIES v1 (+ the ladder hatch probe)
**Stamp: 2026-09-22 · ruling 20:24 CT (Abs0lum: "Yes, approve all. If the hatch doesn't work, we'll move to the script driven climbing") · D-C227 / D-C229 · ships in PW-Civitas-Markers BP/RP v0.2.1** (0.2.0 was withdrawn before install, see §4a).
**Amends:** CIVITAS-MARKER-AND-FRAME-SPEC-v1 §1 and CIVITAS-ZONE-GEOMETRY-v2 §1 (the corner number now lives on an ENTITY, not in a block state) · CIVITAS-AUTHORING-WORKFLOW-v1 §8.7 (**save with Include Entities ON**) · CIVITAS-ZONE-TABLE-v1 (unchanged meanings; this doc adds the frozen icon numbers).

---

## §1 · Why markers became entities
Witness 19:46 (F11–F18): zone corners sat in the cells beside the bed and behind the chair, and he could not furnish the room. The blocks already had `collision_box: false`; the real blocker is **one block per cell**. An entity is not part of the block grid, so a marker entity can share a cell with a chair, a bed, a door, a chest — anything.

The reason the corner number had to be carried *by the marker* (ZONE-GEOMETRY-v2 §1.2: a `.mcstructure` is an unordered photograph of space) still holds — it now rides on the entity as a **property** (for rendering) and a **tag** (for reading), and entities are saved inside the structure when it is saved **with entities**.

## §2 · What you do (the same items, one new habit)
1. Take the same marker from the creative menu (`pw:zone_kitchen`, `pw:station_seat`, `pw:port_stair`, `pw:datum` …).
2. **Tap** a block face → the marker goes in the cell in front of that face (exactly where the block would have gone).
3. **Sneak + tap** a block → the marker goes **inside that block's own cell** (the chair, the bed, the table, the doorway).
4. Numbering is unchanged: zone corners count per player per kind (a new kind starts a new ring; `/scriptevent civ:zone close` ends it; `civ:zone status`), stations and ports count per player per role 0–7 (`civ:station reset`). The open ring now survives leaving and reloading the world.
5. **Hit** a visible marker to remove it (in survival you get the item back).

## §3 · Commands (`/scriptevent …`)
| command | what it does |
|---|---|
| `civ:markers hide` / `show` | world-wide: hidden markers are invisible AND lose their hit box, so they never catch a tap meant for the furniture |
| `civ:markers migrate [r]` | converts old marker BLOCKS within r (default 32, ±16 in y) into entities with the same kind and number; the blocks become air (the block ids stay registered, so old saves still load) |
| `civ:markers list [r]` | every marker in range, by kind, with its numbers (`zone kitchen: 0 1 2 3`) |
| `civ:markers check [r]` | lists every NON-marker entity in range — run it before saving (§5) |
| `civ:markers remove` | removes the nearest marker within 3 blocks (works even when hidden) |
| `civ:zone close` / `status` · `civ:station reset` | as before |
| `civ:hatch turn` / `flip` | turns the nearest hatch's hinge 90° / 180° (calibration + preference) |

## §4 · The data each marker carries (what the assembler reads)
Entity `pw:marker`, positioned at the cell's floor centre (x+0.5, y, z+0.5).

| channel | content |
|---|---|
| property `pw:fam` | 0 zone · 1 station · 2 port · 3 datum |
| property `pw:icon` | the **frozen** kind number below |
| property `pw:n` | zone corner number (= ring×16 + idx, exactly as the old block states, 0–63) · station/port index 0–7 · datum 0 |
| property `pw:vis` | shown / hidden |
| tags | `civ:marker`, `civ:<fam>`, `civ:kind:<kind>`, `civ:n:<n>` — the same meaning in words |

### §4a · Collision vs hit box (why 0.2.0 was withdrawn)
Bedrock refuses to place a block where an entity's **collision box** sits, which is why you can't place a block inside a mob. 0.2.0 gave the marker a 0.4 × 0.5 collision box standing on the cell floor, which could have refused a chair in a marked cell. **v0.2.1:** the collision box is **0 × 0 on the cell's floor plane**, so it can't overlap any block. Being able to hit a marker comes from a separate **hit box** (`minecraft:custom_hit_test`, the hoglin pattern), added while markers are shown and removed on `hide`.

**Frozen icon table — APPEND-ONLY, never reorder** (saved buildings carry these numbers):

| icon | kind | icon | kind | icon | kind |
|---|---|---|---|---|---|
| 0 | zone threshold | 12 | station anvil | 24 | station rack |
| 1 | zone stable | 13 | station bed | 25 | station seat |
| 2 | zone cellar | 14 | station bench | 26 | station stall |
| 3 | zone storeroom | 15 | station counter | 27 | station store |
| 4 | zone kitchen | 16 | station desk | 28 | station table |
| 5 | zone quarters | 17 | station door | 29 | station yard |
| 6 | zone chamber | 18 | station field | 30 | port passage |
| 7 | zone workfloor | 19 | station hearth | 31 | port sewer |
| 8 | zone shopfloor | 20 | station oven | 32 | port stair |
| 9 | zone yard | 21 | station pen | 33 | port well |
| 10 | zone garden | 22 | station post | 34 | datum |
| 11 | zone commons | 23 | station prep | | |

Zones 0–11 follow the ZONE-TABLE precedence order; stations are alphabetical.

## §5 · Saving buildings — **Include Entities: ON** (amends AUTHORING-WORKFLOW §8.7)
Markers are entities, so a structure saved with entities OFF loses every marker. Save with **Include Entities ON**. That also saves any stray mob or dropped item inside the box, so run `/scriptevent civ:markers check` first and clear what it lists. It never lists players, markers, hatches, or furniture seats.

## §6 · The ladder hatch (PROPOSAL H probe)
Bedrock has no climbable custom block, and climbing an open trapdoor above a ladder is Java-only. So the ladder stays a **vanilla ladder** in the opening cell (native climbing), and the hatch is the **entity** `pw:hatch_lid`:
- **Place:** hold `pw:hatch_lid` (Ladder Hatch) and use it on the **top ladder** of the opening (the space above that ladder must be open). The lid appears **closed**, covering the top of that cell, flush with the floor above.
- **Closed:** `minecraft:is_collidable`, the same recipe vanilla uses for the immobile happy ghast that players stand on. You walk over it, and climbing the ladder you stop under it.
- **Open:** tap the lid (from above or below) → it stands up against the side **opposite the ladder** (the hinge is on the side the ladder faces, ladder `facing_direction` 2/3/4/5 = N/S/W/E), inside the same cell → climb through. Tap again to close. Wooden trapdoor sounds play on each tap.
- **Remove:** hit the lid (you get the item back in survival). Breaking the ladder also removes its lid.
- **Probe assumptions (the witness decides):** (1) players can stand on an `is_collidable` entity (happy-ghast precedent); (2) the open leaf appears on the intended side: entity model space is left-handed (+x = the entity's own left), and yaw 0 faces south, so world = (x, y, −z). If the leaf shows on the wrong side, `civ:hatch flip` fixes that lid and one table fixes them all; (3) tapping reaches the lid's interaction (touch shows "Open / Close").
- **If the probe fails** (can't stand on it, jitter, can't open or close): fallback **H2**, a combined block `pw:ladder_hatch` with script-driven climbing, pre-approved 20:24.

## §7 · What did not change
The manhole hatch (`pw:manhole_cover`, HATCH LAW), the frame posts (stagger resolver v2), all 38 marker/frame/hatch **block** definitions (byte-identical, so old saves load), the zone meanings (ZONE-TABLE-v1), and the numbering rules.

## §8 · Sources
Engine facts checked for this build: `@minecraft/server` 2.0.0 typings (`playerInteractWithBlock.cancel` "the interaction will be cancelled", `getEntitiesAtBlockLocation`, `entityHitEntity`, `dataDrivenEntityTrigger`, `setPropertyOverrideForEntity`; **no `Block.isSolid` in stable**); bedrock-samples 1.26.50 (`happy_ghast` adult_immobile: `is_collidable` + `body_rotation_blocked`; `armor_stand` inert entity; `creaking`/`bee` properties and `bool_property` filters; `first_valid` events; `mojang-blocks.json`: ladder `facing_direction` 0–5); the minecraft.wiki Trapdoor page (climbable trapdoor = Java-only); the bedrock.dev block component list (no climbable component).
