# AbsolutRealism — Fog & Lighting Stacking Dossier
### How every Vibrant Visuals visual layer composes, with AbsolutRealism's real values

> Purpose: a definitive model of *how the layers stack* so our cubemap overlay and any future tuning are correct. Sourced from Microsoft Learn, Minecraft Wiki, bedrock.dev, cross-referenced against AbsolutRealism v1.2.52's actual 51 fogs / 10 atmospherics / 10 lighting / 10 color-grading files.

---

## 0. The single most important fact

There is **not one fog system**. There are **three independent fog systems** plus the atmosphere model plus the lighting model, and they are evaluated in a **specific order**, some **replacing**, some **averaging**, some **multiplying**. Nearly every "fog looks wrong" or "sky looks wrong" bug in a layered pack like AbsolutRealism comes from a misunderstanding of *which* of these is in play and *how it combines*, not from a single wrong value.

The pipeline, end to end:

```
LIGHTING (sun/moon/ambient/sky illuminance + color)
        │  feeds color & intensity into ↓
ATMOSPHERE (rayleigh + mie scattering → sky/horizon color)
        │  produces the sky + the COLOR that fog inherits ↓
DISTANCE FOG (render-distance haze, the "air" fog)  ── stack-resolved
VOLUMETRIC FOG (ray-marched medium, light shafts)   ── stack-resolved, uses the color above
        │  final scene ↓
CUBEMAP (our overlay) — composited as skybox, optionally fed THROUGH atmosphere/volumetric
        │  final image ↓
COLOR GRADING + TONE MAPPING (ACES) — applied LAST to everything
```

Read that as: **light defines color → atmosphere turns it into sky → fog inherits that color and obscures distance → cubemap sits in the sky → color-grading re-grades the entire composited frame.** Whatever you change, it is re-graded by the last stage. This is why AbsolutRealism's ACES + saturation grade affects *our cubemap too* (the D-056 double-grade discovery).

---

## 1. The Active Fog Stack (the most misunderstood mechanic)

Bedrock resolves fog through a **stack**, evaluated top-to-bottom, **per fog-property**, until a value is found. From Microsoft Learn / bedrock.dev, bottom → top:

1. **Engine Default** — hard-coded fallback (implicit bottom).
2. **Data Default** — the `default` biome entry's referenced fog definition.
3. **Biome layer** — the fog of the biome(s) around the player, **averaged** by proximity.
4. **Command layer** — `/fog push|pop|remove`, its own internal top-to-bottom sub-stack.

### The crucial non-obvious rules

- **Per-property resolution, not per-file.** When the engine needs (say) `volumetric.density.air.max_density`, it walks the stack from the top and takes the **first layer that defines that specific property**. A biome fog that omits a property does **not** blank it — it *falls through* to the next layer down. This means AbsolutRealism's 51 fog files are **sparse overlays on top of each other and the vanilla default**, not complete replacements.
- **`remove_all_prior_fog`** (default `false`) on the `default` biome entry: when `true`, wipes every fog definition from packs *below* this one — making this pack the new fog floor. **If any AbsolutRealism fog or a pack above it sets this true, lower packs' fog contributions vanish.** This is a prime suspect for "fog suddenly different when I reorder packs."
- **`inherit_from_prior_fog`** (default `false`): when `true`, this biome's fog is read *on top of* the prior fog rather than replacing the matched property — a soft merge.
- **Biome layer is an AVERAGE.** Standing near a biome border, your fog is the **proximity-weighted mean** of the surrounding biomes' fog settings. AbsolutRealism has 106 client_biome files → 106 potential fog blends. A single mis-tuned biome fog bleeds into its neighbors at the border.
- **Resource-pack order matters for fog definitions.** Higher-priority packs' fog files override same-identifier definitions in lower packs. In the canonical config, Atmospheric Effects RP is **pack #2 from the bottom** — so any pack above it that ships a `fogs/` folder or a `default` fog entry can override AbsolutRealism's fog. (Verified: PBR/Basic/Flora/mobs/Items/Trees/Terrain/Ores are texture/model packs and do **not** ship fog/biome JSON, so in the canonical order AbsolutRealism's fog is safe — but this is exactly the fragility that load-order juggling breaks.)

### AbsolutRealism's real fog values (sampled)

| Biome fog | air max_density | uniform | air scattering RGB | distance air fog_start→end |
|---|---|---|---|---|
| basalt_deltas | 0.05 | (height-graded 128→250) | [0.075, 0.056, 0.05] | 10 → 96 (fixed) |
| beach | 0.04 | true | [0.0079, 0.0118, 0.0153] | 0.3 → 1.0 (render-relative) |
| birch_forest | 0.045 | true | [0.0079, 0.0118, 0.0153] | 0.3 → 1.0 (render-relative) |

Two distinct **distance-fog idioms** are already in use: `render_distance_type: "render"` (fog_start/end as *fractions of render distance* — 0.3→1.0) vs `"fixed"` (absolute blocks — 10→96). Mixing these across biomes at a border produces non-linear haze transitions. Worth auditing all 51 for consistency.

---

## 2. The two fog systems that are NOT the stack: render-distance vs volumetric

These coexist and are **additive in perceived obscuration**:

### 2a. Distance (render-distance) fog — `minecraft:fog_settings > distance`
- The classic horizon haze. `fog_start`/`fog_end` (blocks or render-fraction), `fog_color`.
- **This is what tints the horizon and hides chunk edges.** It is *not* volumetric; it's a cheap depth-based color lerp.
- `render_distance_type: "render"` → distances scale with the player's render-distance setting (a player on render distance 8 vs 24 gets very different absolute fog). `"fixed"` → absolute blocks regardless of settings.

### 2b. Volumetric fog — `minecraft:fog_settings > volumetric` (Vibrant Visuals only)
- A **ray-marched participating medium**. This is what does light shafts / god rays, glow, and the "thick soup" look.
- `density.air.max_density`: 0.0 = none, 1.0 = near-opaque. **AbsolutRealism uses ~0.04–0.05 in air** — tuned for atmospheric *terrain depth*, NOT for the sky to be drowned in it.
- `uniform: true` → density constant at all heights. `false` → ramps between `max_density_height` (full) and `zero_density_height` (none). **AbsolutRealism mixes both idioms** (beach/birch uniform; basalt height-graded 128→250).
- `media_coefficients.air.scattering [R,G,B]` — per-channel light spread per block. `absorption [R,G,B]` — light lost per block. **Critical engine limitation (Microsoft Learn):** Vibrant Visuals does **not** support tinted absorption — it collapses the RGB absorption to a single luminance value via `L = 0.2126R + 0.7152G + 0.0722B`. So per-channel `absorption` is cosmetic; only its luminance matters. Scattering *is* per-channel.
- `henyey_greenstein_g` (1.21.90+) — the phase function asymmetry. g→1 = sharp forward scatter (tight light shafts/god rays); g→0 = isotropic (even glow); g<0 = back-scatter. **This is the actual god-ray control**, not the cubemap boolean.
- **At Y≥320 volumetric fog is not rendered at all** (Minecraft Wiki). High-altitude builds escape volumetric entirely — relevant to AbsolutRealism's sky work and to why high-altitude screenshots look different.

> **The D-085 regression, fully explained:** enabling `affected_by_volumetric_scattering: true` on our cubemap made the *skybox itself* a surface inside this ~0.045-density, `uniform:true` medium across the entire sky-dome path length. AbsolutRealism tuned that density for *terrain* depth; applied to the sky dome it integrates to near-opaque → "fog so thick I can't see anything." The fog values were never wrong — we put the sky *inside* them.

### 2c. The colour coupling (the subtle one)
Minecraft Wiki, verbatim mechanism: *volumetric fog uses the colour from the regular (distance) fog, which uses the colour and illumination from atmospherics and lighting.* So the dependency chain for a single foggy pixel is:

```
lighting (sun/moon colour+illuminance)
   → atmospherics (rayleigh/mie tint)
      → distance-fog colour
         → volumetric fog colour
```

Change the sun colour in `lighting/global.json` and you have **moved the volumetric fog colour**, two systems away, with no edit to any fog file. This is the deepest stacking coupling in the engine and the one most likely to cause "I changed lighting and the fog went weird."

---

## 3. The Atmosphere model — where sky colour is actually born

`atmospherics/atmospherics.json` (AbsolutRealism base, real values):

- `rayleigh_strength`: keyframed `0.00→1.5, 0.30→0.4, 0.75→0.95, 1.00→1.5` (day-cycle t). Rayleigh = the blue-sky/short-wavelength scatter. AbsolutRealism drives it **high at night/dawn/dusk (1.4–1.5), low at midday-twilight (0.3–0.4)** — an aggressive, deliberately non-physical curve for mood.
- `sun_mie_strength`: spikes to `0.75` exactly at t=0.25 and t=0.75 (sunrise/sunset), 0 otherwise → the tight warm sun-halo glow only at the golden hours.
- `moon_mie_strength`: peaks `1.0` at t=0.50 (midnight) → moon glow is a full-strength night feature.
- `horizon_blend_stops`: controls how far up the warm horizon band reaches; AbsolutRealism widens it at night/dawn (`start` 0.8→0.25→0.8).

**Microsoft Learn, critical cross-coupling:** *the colours defined for the sun and moon directional lights in `lighting/global.json` are also used in the atmosphere calculation and significantly impact final sky colour, especially through the Rayleigh and Mie terms.* So the atmosphere model is **not self-contained** — it reads lighting. Sky colour = f(atmospherics curves, **lighting sun/moon colour**, time-of-day).

---

## 4. The Lighting model — the root input to everything

`lighting/global.json` (AbsolutRealism base, real values):

- `directional_lights.orbital.sun.illuminance`: keyframed `0.00→105, 0.20→115, 0.25→40, 0.30→0.14 … 0.75→17`. The sun's raw radiometric power over the day; the 0.25→0.14 cliff is civil twilight.
- `directional_lights.orbital.{sun,moon}.color`: tints the sun/moon **and** (per §3) the atmosphere **and** (per §2c) the fog. Highest-leverage colour value in the entire pack.
- `directional_lights.flash`: the End-flash channel — also the **lightning-flash hook** (relevant to the D-051/D-052 storm-perception work).
- `ambient.illuminance`: keyframed `0.08` day → `0.04` night — the floor light with no direct source (shadowed/indoor). Low values = moody deep shadows; this is AbsolutRealism's "realism" lever.
- `sky.intensity: 0.7` — global multiplier on sky-light contribution to surfaces.
- `emissive.desaturation: 0.0` — how much emissive textures lose colour (0 = full saturated glow).

### Lighting biome rule (1.21.90+, easy to get wrong)
Microsoft Learn: as of 1.21.90, `lighting/global.json` **does not override the built-in vanilla per-biome lighting** — to change a biome you must add a separate lighting JSON in `lighting/` and bind it via `client_biome`. AbsolutRealism ships 10 lighting files + client_biome routing precisely for this. **Implication:** the reserved `global.json` is the *fallback*; vanilla per-biome lighting can still win in biomes AbsolutRealism doesn't explicitly route. A "lighting looks vanilla in biome X" bug is almost always a missing client_biome lighting binding, not a wrong global.json.

---

## 5. Biome blending — the layer that surprises everyone

Microsoft Learn / Minecraft Wiki: as the camera moves, the engine **interpolates** atmospherics, lighting, color-grading, and (per §1) averages fog between surrounding biomes. **Exceptions that do NOT blend and must be globally consistent:** *tone mapping, orbital offset, caustics, and waves enabled/disabled.*

Consequences for AbsolutRealism (106 client_biomes):
- Every biome border is a live cross-fade of 4 visual systems simultaneously. A single outlier biome (e.g. one fog with 5× density, one lighting with a wild sun colour) **smears into its neighbours** for dozens of blocks around the border.
- **Tone mapping must be identical in all 10 color-grading files.** AbsolutRealism uses `aces` — verify all 10 are `aces`. If one biome's color-grading uses a different operator, you get a hard non-blending pop at that border (the engine cannot interpolate operators).
- Same for orbital offset / caustics / waves: any per-biome divergence = visible discontinuity, not a smooth transition.

---

## 6. Color grading + tone mapping — the final, global re-grade

`color_grading/color_grading.json` (AbsolutRealism): `tone_mapping.operator: "aces"`, plus `midtones / highlights / shadows` (lift-gamma-gain style) and `temperature`. From the earlier D-056 teardown: midtones sat ≈1.2, highlights ≈1.25, shadows ≈1.2, contrast ≈1.1, ~6500K.

**This stage runs LAST and on the ENTIRE composited frame** — terrain, sky, fog, *and our cubemap*. Two hard consequences:

1. **No double-grading.** Anything we bake into the cubemap texture (ACES, saturation push) is then graded *again* by this stage. The converter must output **near-neutral** and let this stage do the final look (locked in D-056; this dossier confirms the mechanism: color-grading is unconditionally post-composite and global).
2. **Tone-mapping is non-blending (per §5).** ACES everywhere or visible seams. It is also the operator that maps AbsolutRealism's HDR illuminance (sun = 105–115) into displayable range — which is why raw illuminance numbers look enormous; ACES compresses them.

---

## 7. Unorthodox / sophisticated interactions worth knowing

These are the non-obvious, high-leverage couplings — the "sophisticated" angles requested:

1. **The fog-colour back-door to sky tuning.** Because volumetric fog inherits distance-fog colour which inherits atmosphere which inherits lighting (§2c), you can shift the *entire mood* of foggy distance **without touching a fog file** — by nudging `lighting` sun/moon colour. Conversely, a "fog tint" bug may have its root cause in lighting. Always diagnose this chain top-down (lighting → atmosphere → fog), never fog-first.

2. **Y≥320 is a volumetric dead zone.** Volumetric fog stops rendering at/above Y=320 (Minecraft Wiki). High-altitude screenshots (the user's planned sunrise/sunset reference shots) are taken in a *different fog regime* than ground play. Calibrating sky colour from high-altitude shots and applying it to ground play will mismatch unless this is accounted for. **Take reference shots at gameplay altitude, not from the build limit.**

3. **Absorption is secretly monochrome.** Per Microsoft Learn, Vibrant Visuals collapses RGB `absorption` to luminance. AbsolutRealism's per-channel absorption arrays (e.g. water `[0.05,0.08,0.1]`) are partly cosmetic — only the luminance `0.2126R+0.7152G+0.0722B` is used. Tinting via absorption is futile; **tint via `scattering` (which IS per-channel) or via the inherited fog colour.**

4. **`render` vs `fixed` distance-fog idioms don't blend cleanly.** A biome using render-relative fog (0.3→1.0) bordering one using fixed-block fog (10→96) produces a non-linear, render-distance-dependent transition. AbsolutRealism mixes both across its 51 fogs — a likely source of "fog looks inconsistent between areas." Standardising the idiom per region (not per biome) removes a class of border artefacts.

5. **`remove_all_prior_fog` is a silent kill-switch.** One pack setting this true on its `default` biome entry erases every lower pack's fog. In a multi-pack stack with load-order changes, this single boolean explains "fog completely changed when I reordered." Audit all `default` fog entries across the pack set for this flag.

6. **Lighting illuminance is HDR and only sane *after* ACES.** Sun illuminance 105–115 is not "1500% brightness" — it's physical radiance that ACES tone-maps down. Editing illuminance without mentally applying the ACES curve leads to wildly over/under-corrected changes. Always reason about lighting changes *through* the tone-mapping operator.

7. **The cubemap has its own three lighting knobs** (Bedrock Editor docs): `directional_light_contribution`, `sky_light_contribution`, `ambient_light_illuminance` — *separate from* the scattering booleans. These let the cloud overlay be lit by sun/sky/ambient **without** being put inside the volumetric medium. This is the correct surface for "make clouds respond to time-of-day" — not the volumetric flag. (Direct follow-up to the D-088 recommendation: `atmospheric_scattering: true` for sky-integration, `volumetric_scattering: false` to stay out of the fog medium, and tune these three contributions for day/night cloud response.)

---

## 8. Practical model — "if I change X, what moves?"

| Change this | Directly moves | Also moves (coupled) | Non-blending? |
|---|---|---|---|
| `lighting` sun/moon **colour** | sun/moon tint | **atmosphere sky colour, distance-fog colour, volumetric-fog colour** | no |
| `lighting` sun **illuminance** | scene brightness | exposure/bloom feel after ACES | no |
| `lighting` ambient | shadow floor | perceived fog density in shade | no |
| `atmospherics` rayleigh/mie | sky & horizon colour | fog colour (inherits) | no |
| `fog` distance fog_start/end/colour | horizon haze | volumetric fog colour (inherits) | no |
| `fog` volumetric density | god-ray/soup thickness | cubemap if `volumetric_scattering:true` | no |
| `fog` volumetric `henyey_greenstein_g` | **god-ray tightness** | shaft vs glow look | no |
| `color_grading` non-tone | whole frame look incl cubemap | double-grade risk on baked textures | no |
| `color_grading` **tone_mapping** | whole frame mapping | — | **YES — must be global** |
| cubemap `atmospheric_scattering` | cloud sky-integration/tint | — | no |
| cubemap `volumetric_scattering` | **puts sky in fog medium** (regression) | — | no |
| `remove_all_prior_fog` | erases lower-pack fog | entire fog stack below | n/a (structural) |

---

## 9. Recommendations for AbsolutRealism (actionable)

1. **Cubemap scattering:** `volumetric_scattering: false` permanently (it doesn't make god rays; it drowns the sky — §2b/§7). `atmospheric_scattering: true` is the strong candidate for believable time-of-day cloud tint — test it isolated (the D-088 v0.4.2 plan), it does **not** touch the fog medium so it should not re-trigger the fog regression.
2. **Audit all 10 color-grading files: confirm every `tone_mapping.operator` is `aces`.** A single divergent operator causes a hard non-blending seam (§5/§6).
3. **Audit all 51 fog files for `render` vs `fixed` distance idiom**; standardise per region, not per biome (§7.4) to remove border artefacts.
4. **Audit every `default` fog entry across the full canonical pack set for `remove_all_prior_fog: true`** — the silent fog kill-switch (§7.5).
5. **God rays are a separate workstream:** tune `henyey_greenstein_g` + volumetric density profile + sun, *independent of the cloud cubemap* (§2b/§7). Do not couple to the cloud overlay MVP.
6. **Reference screenshots at gameplay altitude, not Y≥320** — volumetric dead zone makes high-altitude colour non-representative (§7.2).
7. **Diagnose all fog/sky colour bugs top-down:** lighting → atmosphere → fog, never fog-first (§7.1). Most "fog tint" issues originate two systems upstream.
8. **Keep the converter output near-neutral** — color-grading re-grades globally and last; baked ACES/saturation double-processes (§6, confirms D-056).

---

### Sources
Microsoft Learn: Lighting Customization, Atmospherics Customization, Volumetric Fog & Light Shafts, Biome Customization, Cubemap Customization, Fog in Resource Packs, Bedrock Editor Vibrant Visuals. Minecraft Wiki: Vibrant Visuals, Fog. bedrock.dev: Fogs (stable/preview). Cross-referenced against AbsolutRealism v1.2.52 RP-02 actual files (51 fogs, 10 atmospherics, 10 lighting, 10 color-grading, 106 client_biome).
