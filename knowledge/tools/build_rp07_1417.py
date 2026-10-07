#!/usr/bin/env python3
"""build_rp07_1417.py — his 09-28 21:43 GO ("continue making fixes"), Phase B (D-C274). RP-07 Neutral Mobs RP v1.4.17 from v1.4.16.
Converter B for: squid + glow squid (all 8 tentacles on the ring: the vanilla tentacle part's pivot AND rotation, D-C274),
zombified piglin (the texture mosaic: the old geometry's UVs; the Patrix JEM's own UVs + the FreshLX hunched pose),
rabbit (nose/mouth back on the lower front of the face; ears follow the head; feet follow the thighs), camel (ears follow
the wobbling head — `head2` now carries the head so the ears move with it), chicken (two legs, wing plates, legs hinge at the
hip), llama (the old geometry had the 5 fur shells COPLANAR — sizeAdd dropped, 16 px instead of 18 — so the
rear face Z-fought: his "south face clipping"). `look_at_target` -> animation.pw_convb.look on camel, rabbit, chicken, llama.
manifest 1.4.17, uuid kept. verify: verify_rp07_1417.py."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R

ROOT = Path("/home/claude")
CFG = {
    "src": ROOT / "_build/rp07-1416", "dst": ROOT / "_build/rp07-1417", "version": "1.4.17",
    "name": "AbsolutRealism Neutral Mobs RP v1.4.17",
    "desc": ("v1.4.17 (2026-09-28) CONVERTER B ROUND 3 (D-C274): squid + glow squid tentacles in a ring, zombified piglin without the "
             "patchwork limbs, rabbit nose/mouth on the face, camel ears that stay on the head, chicken with two legs and wing plates, "
             "llama fur layers no longer flickering on the rump. Everything else byte-identical to v1.4.16."),
    "jobs": [("squid", "squid", "default", "squid", "default"), ("glow squid", "glow_squid", "default", "glow_squid", "default"),
             ("zombified piglin", "zombie_pigman", "default", "zombified_piglin", "default"), ("rabbit", "rabbit", "default", "rabbit", "default"),
             ("camel", "camel", "default", "camel", "default"), ("chicken", "chicken", "default", "chicken", "default"),
             ("llama", "llama", "default", "llama", "default")],
    # trader llama HELD BACK (D-C274): its blanket/tassels are painted on the INNER fur shell only; with the shells correctly
    # separated (0.1-0.4 px) the dense outer fur covers the blanket — needs a decor layer of its own (proposal to him)
    "look": {s: "animation.common.look_at_target" for s in ("camel", "rabbit", "chicken", "llama")},
    "unbound_ok": {"squid": {"head"}, "glow squid": {"head"}, "zombified piglin": {"leftForearm", "rightForearm", "leftShin", "rightShin"}},
    # squid reference = the old squid's box centre (y 7): its height in the water was never reported
    "placement": {"squid": ("centre", 7.0, 0.0), "glow squid": ("centre", 7.0, 0.0), "zombified piglin": ("ground",), "rabbit": ("ground",),
                  "camel": ("ground",), "chicken": ("ground",), "llama": ("ground",)},
    "report": ROOT / "_docs/convb/build_1417_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
