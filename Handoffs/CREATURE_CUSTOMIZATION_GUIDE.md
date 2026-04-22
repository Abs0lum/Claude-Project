# Creature Customization & Variant Design Guide
## PatrixWorld Ecosystem Framework

**Purpose**: Define rules, prompts, and decision trees for creating any creature (vanilla, mythical, or custom) with consistent 16+ variant support and behavior integration.

---

## SECTION 1: PRE-DESIGN DECISION TREE

### Question Set 1: Creature Identity

**Q1.1**: What is the creature's **taxonomic basis**?
- [ ] Real-world animal (species name: _______)
- [ ] Hybrid of 2+ real animals (list: _______)
- [ ] Mythical/Fantasy (origin tradition: _______)
- [ ] Entirely fictional (description: _______)

**Q1.2**: What is its **primary biome/habitat**?
- [ ] Overworld terrestrial (forest/plains/desert/taiga/jungle/savanna/swamp/mountain/badlands)
- [ ] Aquatic (freshwater/saltwater/coastal)
- [ ] Nether
- [ ] End
- [ ] Multiple/Rare spawn

**Q1.3**: Does it **replace a vanilla mob** or is it **entirely new**?
- [ ] Replaces existing (which: _______)
- [ ] New spawn category (neutral/passive/hostile/boss)
- [ ] Variant of existing (base species: _______)

---

### Question Set 2: Behavioral Role

**Q2.1**: What is its **primary game function**?
- [ ] Passive (just exists, drops nothing/basic items)
- [ ] Neutral (doesn't attack unless provoked)
- [ ] Hostile (attacks player on sight)
- [ ] Boss (rare/difficult/special mechanic)
- [ ] Utility (provides resource/service)

**Q2.2**: What **drops** does it provide?
- [ ] None (decorative only)
- [ ] Standard (meat, wool, hide, drops corresponding to base species)
- [ ] Specialty (rare item, crafting component, magical drop)
- [ ] Multi-tier (drops vary by biome/variant)

**Q2.3**: **Can it be tamed?**
- [ ] No (wild only)
- [ ] Yes — conditional (describe taming mechanic: _______)
- [ ] Yes — with item (which: _______)

**Q2.4**: **Can it be ridden/used as mount?**
- [ ] No
- [ ] Yes — saddle required (standard Minecraft saddle)
- [ ] Yes — special tack required (describe: _______)
- [ ] Yes — with passengers (how many extra: _______)

**Q2.5**: **Speed/Abilities when ridden**:
- [ ] Slow (horse equivalent: walk/trot)
- [ ] Fast (horse: gallop)
- [ ] Very fast (strider/other special)
- [ ] Flight (elytra, glide, hover)
- [ ] Water-specific (swim speed)
- [ ] Other (describe: _______)

---

### Question Set 3: Visual Design Parameters

**Q3.1**: **Primary color palette** (list 3-5 dominant colors):
- Base color 1: _____
- Base color 2: _____
- Accent color: _____
- Rare/variant color: _____

**Q3.2**: **Body structure**:
- [ ] Quadruped (4 legs)
- [ ] Biped (2 legs)
- [ ] Winged (describe wing type: _______)
- [ ] Aquatic (fins, tail, gills)
- [ ] Segmented/Modular (describe: _______)
- [ ] Other (describe: _______)

**Q3.3**: **Distinguishing features** (what makes it recognizable?):
- Horns/Antlers: [ ] Yes [ ] No — description: _____
- Spikes/Spines: [ ] Yes [ ] No — description: _____
- Distinctive tail: [ ] Yes [ ] No — description: _____
- Mane/Fur pattern: [ ] Yes [ ] No — description: _____
- Facial markings: [ ] Yes [ ] No — description: _____
- Other (describe): _____

**Q3.4**: **Scale/Size relative to player**:
- [ ] Tiny (bat-sized, < 0.5m)
- [ ] Small (cat-sized, 0.5-1m)
- [ ] Medium (cow-sized, 1-2m)
- [ ] Large (horse-sized, 2-3m)
- [ ] Huge (elephant-sized, > 3m)
- [ ] Boss-scale (varies)

---

## SECTION 2: VARIANT GENERATION FRAMEWORK

### Real-World Animal Variants (16+ options per species)

**Approach**: Research actual genetic/geographic variation in the real animal, then translate to Minecraft textures.

**Example — Horses (16+ variants from real-world breeding)**:

| Variant Type | Real-World Basis | Minecraft Variant |
|---|---|---|
| 1. Solid Colors | Bay (brown/black mane) | Brown body, black mane/tail |
| 2. | Chestnut (reddish) | Reddish-brown, lighter mane |
| 3. | Black (ebony) | Pure black with sheen |
| 4. | Palomino (golden) | Gold body, white mane |
| 5. | Gray (dappled) | Light gray with dappled spots |
| 6. | Roan (mixed) | Brown + white hairs mixed |
| 7. | Cremello (cream) | Pale cream/tan |
| 8. Coat Patterns | Tobiano (patches) | Large white patches + brown |
| 9. | Overo (splashed) | Dark base + random white splashes |
| 10. | Appaloosa (spots) | Base color + dark spotted blanket |
| 11. | Paint (large patches) | Distinct brown & white sections |
| 12. | Dun (dilute + stripe) | Tan/olive with dark stripe & bars |
| 13. | Buckskin (golden + darker) | Golden with dark mane/tail/legs |
| 14. | Grullo (dark dilute) | Slate-gray with dark stripe |
| 15. Rare/Special | Champagne | Light golden with metallic sheen |
| 16. | Pearl | Opalescent, color-shifting effect |

**Template for any animal**:

1. **Solid color variations** (5-7): Research natural color ranges (fur, feather, scale hues)
2. **Pattern variations** (4-6): Research coat patterns (spots, stripes, patches, dappling)
3. **Geographic variants** (2-3): Research regional subspecies (size, color differences)
4. **Age/Sex variants** (1-2): Research juvenile vs adult, male vs female dimorphism

---

### Mythical/Fictional Variants (16+ options per species)

**Approach**: Establish internal lore rules, then create variants that follow them.

**Example — Dragon (16+ variants by element/affinity)**:

| Variant | Affinity | Color Scheme | Special Feature |
|---|---|---|---|
| 1. Flame Dragon | Fire | Crimson/gold | Lava trails, ember particles |
| 2. Frost Dragon | Ice | Pale blue/white | Snow aura, icy sheen |
| 3. Storm Dragon | Lightning | Storm-gray/violet | Electrical marks, crackling |
| 4. Forest Dragon | Nature | Deep green/brown | Vine-covered, leafy texture |
| 5. Void Dragon | Shadow | Black/purple | Darkness aura, cosmic speckles |
| 6. Light Dragon | Radiance | White/gold | Glowing runes, ethereal |
| 7. Aquatic Dragon | Water | Teal/blue | Scales like fish, water ripples |
| 8. Magma Dragon | Volcanic | Orange/red/black | Obsidian plates, lava cracks |
| 9-16. | Hybrid combinations | Mix of above | Blend 2+ affinities |

---

## SECTION 3: TEXTURE VARIANT CREATION PROCESS

### Step 1: Research Phase (per species)
- Gather 30+ reference images of real animal (or mythical sources)
- Document color variations, pattern distributions, regional differences
- Identify 16-24 distinct variation possibilities

### Step 2: Master Texture (512x resolution)
- Create 512×512px base (or appropriate size) Patrix-quality texture
- Hand-author each variant as unique texture file: `creature_name_variant_1.png` through `_variant_16.png`
- Include PBR maps for each: `_variant_1_n.png` (normal), `_variant_1_s.png` (specular)

### Step 3: Downsampling Tiers
- 512x → 256x (bilinear resample with quality check)
- 256x → 128x (bilinear resample with quality check)
- 128x → 64x (bilinear resample with quality check)
- 64x → 32x (careful resample, hand-touch pixelation if needed)

### Step 4: PBR Map Generation
- **Normal maps (_n)**: Per-pixel surface orientation
  - Flat areas (body): smooth normal
  - Textured areas (fur, scales): bumpy normal
  - Generate via smart filters or hand-paint
- **Specular maps (_s)**: Reflectivity/roughness
  - Scales/wet fur: high reflectivity (lighter pixels)
  - Dry fur/matte: low reflectivity (darker pixels)
  - Eyes: high reflectivity (shine spots)

### Step 5: Integration
- Place all variants in resolution-tier folder structure:
  ```
  /textures/entity/creature_name/
  ├── 32x/
  │   ├── variant_1.png
  │   ├── variant_1_n.png
  │   ├── variant_1_s.png
  │   └── ... (16 variants × 3 files = 48 files)
  ├── 64x/
  ├── 128x/
  ├── 256x/
  └── 512x/
  ```

---

## SECTION 4: RIDABILITY & TAMABILITY IMPLEMENTATION

### Ridability Decision Matrix

**Can this creature be ridden?**

```
START
  ↓
Is creature size ≥ 1.5m tall?
  ├─ NO → Not ridable (too small for player)
  └─ YES ↓
      Does creature have 4+ legs (stable platform)?
        ├─ NO → Check for other rideable surface (dragon back, llama style)
        │       ├─ YES → Continue
        │       └─ NO → Not ridable
        └─ YES ↓
            Is it a domesticable species (docile baseline)?
              ├─ NO → Ridable only if tamed first
              └─ YES → Ridable with saddle
                  ↓
            Does it have special speed/abilities?
              ├─ NO → Standard mount (horse speed tier)
              └─ YES → Special mount type (flying, water, fast, etc.)
```

### Tamability Decision Matrix

**Can this creature be tamed?**

```
START
  ↓
Is it naturally aggressive/hostile?
  ├─ YES → Requires special taming item or condition
  │        └─ What triggers taming? (rare item, ritual, task completion)
  └─ NO → Can be tamed
      ↓
  What is the taming mechanism?
    ├─ Food-based (feed specific item until hearts appear)
    │   └─ Which food item? (carrot, golden apple, special crafted item)
    ├─ Interaction-based (right-click with specific item)
    ├─ Ritual-based (complex multi-step interaction)
    └─ Automatic (passive mobs auto-tame on approach)
      ↓
  What taming indicator shows success?
    ├─ Color change (collar, marking)
    ├─ Name tag persistence
    ├─ Behavior change (follows player, responds to commands)
    └─ Particle effect or sound
```

### Mount Behavior Specification

**If ridable, define**:

| Parameter | Options | Notes |
|---|---|---|
| **Speed tier** | Walk / Trot / Gallop / Flying / Teleporting | In blocks/second |
| **Jump height** | 0.5 / 1.0 / 1.5 / 2.0+ blocks | How high can it jump while ridden |
| **Can jump while moving** | Yes / No | Affects gameplay feel |
| **Fall damage reduction** | None / Reduced / Immunity | Does rider take fall damage? |
| **Water behavior** | Sinks / Swims / Floats | Can it be ridden in water? |
| **Control method** | Reins / Steering / Auto-follow | How does player control direction |
| **Passenger capacity** | 1 (player only) / 2+ | Can others ride as passengers? |
| **Dismount mechanic** | Sneak / Jump / Damage / Command | How does player get off? |

---

## SECTION 5: CREATURE TEMPLATE CHECKLIST

**Use this for every new creature:**

- [ ] **Identity**: Real/Mythical/Hybrid? Base species? Biome?
- [ ] **Role**: Passive/Neutral/Hostile/Boss/Utility?
- [ ] **Drops**: What does it give when defeated?
- [ ] **Tamability**: Taming method? Taming item?
- [ ] **Ridability**: Can it be ridden? Mount type (normal/flying/water)?
- [ ] **Color palette**: 3-5 dominant colors identified
- [ ] **Body structure**: Quadruped/Biped/Winged/Aquatic/Other?
- [ ] **Distinguishing features**: 2-3 unique visual traits
- [ ] **Size**: Tiny/Small/Medium/Large/Huge/Boss-scale?
- [ ] **Real-world research**: 30+ reference images gathered
- [ ] **Variant strategy**: 16+ variant ideas documented
- [ ] **Master textures (512x)**: All 16 variants hand-authored + PBR
- [ ] **Downsampled tiers**: 256x, 128x, 64x, 32x generated + quality-checked
- [ ] **Integration**: All files placed in correct folder structure
- [ ] **Testing**: Spawn in-game, verify rendering across resolutions

---

## SECTION 6: BIOME VARIANT DISPATCHER (Future)

**Optional**: Math-based variant selection per biome to simulate natural ecosystem distribution.

```javascript
// Example: Horses spawn with variant based on biome
if (biome === "plains") {
  // Grassland horses: browns, palominos, bays (warm earth tones)
  variant = randomFromSet([brown, chestnut, palomino, roan])
}
if (biome === "taiga") {
  // Cold climate: grays, duns, darker tones
  variant = randomFromSet([gray, dun, cremello, black])
}
if (biome === "desert") {
  // Arid climate: tans, creams, light colors
  variant = randomFromSet([buckskin, palomino, cremello])
}
```

This requires a behavior pack script, but makes the world feel more cohesive.

---

## SECTION 7: EXAMPLE — CREATING A CUSTOM CREATURE FROM SCRATCH

**Scenario**: You want to add a "Stone Golem" (mythical, not ridable, hostile).

**Step 1: Answer Decision Tree**

Q1.1: Mythical (golem folklore)
Q1.2: Mountain biome
Q1.3: Entirely new spawn category (hostile)
Q2.1: Hostile (attacks on sight)
Q2.2: Specialty (drops rare gemstone, crafting component)
Q2.3: Not tamable
Q2.4: Not ridable
Q3.1: Gray, dark charcoal, with golden accents
Q3.2: Biped (humanoid shape)
Q3.3: Cracks across body, glowing eyes, runes etched
Q3.4: Large (2-3m, taller than player)

**Step 2: Variant Strategy (16 types)**

| Type | Basis | Description |
|---|---|---|
| 1-4 | Stone type | Granite gray, basalt black, marble white, slate blue-gray |
| 5-8 | Age/Weathering | Fresh/sharp, weathered, moss-covered, crystal-embedded |
| 9-12 | Elemental infusion | Standard, flaming cracks, icy sheen, electric runes |
| 13-16 | Rare variants | Obsidian (rare), emerald-streaked (very rare), gilded (legendary), void (unique) |

**Step 3: Master Texture (512x)**
- Hand-paint 16 variants of stone golem (512×512 each)
- Create _n maps (cracks = bumpy, smooth areas = flat)
- Create _s maps (metallic runes = shiny, stone = matte)

**Step 4: Downsample** → 256x, 128x, 64x, 32x

**Step 5: Integrate** → Place in `/textures/entity/stone_golem/{32x,64x,128x,256x,512x}/`

**Step 6: Behavior Pack** (future)
- Define spawn rules (mountains, rare)
- Define attack behavior
- Define drops (gemstone, crafting item)

---

## SECTION 8: NOTES FOR FUTURE EXPANSION

- This guide applies to mobs, mounts, and creatures
- Armor variants (if applicable) follow same 16+ rule
- Custom creatures uploaded later should be processed through this framework
- Biome-based variant dispatch (Section 6) is optional but recommended for immersion
- PBR quality at all tiers ensures VV completeness across all resolutions

---

**End of Creature Customization Guide**

*Next Steps*: Use this framework to design all Minecraft animals, research real-world variants, then author textures.
