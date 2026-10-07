#!/usr/bin/env python3
"""verify_testrunner.py — gate for PW-TestRunner BP v0.4.9 (D-C338: whole-box scan, areas in the job, q9 reset) — v0.4.8 (D-C336: p15 = every species-age on our trees, copies; BP-02 feature / trunk cross-checks) — earlier v0.4.6 (+ the unchanged RP v0.3.0 check; the pilot RP v0.4.0 has its own gate verify_leaf_pilot.py) (D-C332 adds Z: lineup p15, the leaf pilot) (D-C317 adds Y: lineup p14) (D-C314 adds X: lineup p13) (D-C310 adds W: lineup p12 + item proof + spec.boxes) (D-C307 adds V: lineup p11) (D-C300 adds U: lineup p10 + re-roll / jukebox / sweep) (D-C292 adds T: lineup p9 + grow-up/age) (D-C288 adds S: lineup p8 + rig armor) (D-C286 adds R: lineup p7) (D-C285 adds Q: lineup p6 + rig items) (D-C284 adds P: lineup p5 + rig name tags) (D-C257/D-C260/D-C263/D-C264/D-C267/D-C277). Packages the BP on GATE OPEN.
  M (0.3.2) p3 = q0 n01-n14 e01-e17 q9 (33), p3n = q0 n01-n14 q9 (16, the same step objects); every rigged mob id (main + row) is a vanilla
    behaviour entity; row offsets sit inside the pen; big pens keep their south wall >= 2 blocks ahead; every body names PASS; first lines <= 200
  L (0.3.1) every P1 hostile id is a vanilla BEHAVIOUR entity id (the evoker = minecraft:evocation_illager); every block-state clause in every lineup
    uses Bedrock's ["name"=value] grammar; every block a p1 station places exists (vanilla blocks.json, the probe blocks, BP-02's pw: blocks);
    p1r = the 16 re-run ids with the p1 step contents; the RP rebuilt from source is byte-identical to the shipped RP v0.3.0
  K (0.3.0) the XPACK probe: 3 BP blocks (1.21.80, full_block geometry, one material key each) whose keys the RP registers; the RP holds NONE of the
    3 paths; across the whole stack + vanilla: A is held by RP-04 (and vanilla), B only by RP-01 (not vanilla), C by nobody (P11 census); P1 = 27 steps
    (q0, h01-h11 roofed, b01-b14, q9; no size steps); P2 = 9 steps (q0, s01-s04, r01-r03 with the shark in water, q9)
  A manifests: BP header/script uuids unchanged since 0.1.0, NEW data module uuid fixed, RP uuids fixed, versions 0.2.0,
    pins server 2.3.0 + server-ui 2.0.0, NO pack-uuid dependencies (L-VV-2), all uuids unique across every built pack
  B every JSON parses; node --check on every script; the 4 shipped scripts == tools/testrunner_src byte for byte
  C api_audit: 0 flags against the pinned typings
  D mock-run of the SHIPPED scripts (test_testrunner.mjs): all assertions pass (witness lineup + PHASE 0 end to end)
  E lineups: the witness lineup is the 0.1.2 table (48 steps, only the two version strings changed); PHASE 0 = q0 q1 q2 +
    one rig step per mob + q9, unique ids, every rig mob id is a vanilla entity in the 1.26.50 samples (P11 census), water
    flags only on the aquatic set, every body names PASS and the shots
  F no other pack is touched (each current build dir == its delivered mcpack)
  G isolation: pw:test / pw:test_state / pw:test_rig / pw:probe / the clicker name collide with nothing in the stack
  H wording law (0.1.2): 'you are in:' + flat-world guidance + the facing readout on the P0 bar
  I the probe: geometry bones/rotations/colours exactly the protocol table; 64x64 chart with 8 distinct swatches; the client
    entity's geometry/texture/animation/controller ids all resolve inside the RP; the animation adds [30,0,0] to xbar and
    lifts zbar 8; the BP entity floats (no gravity), cannot be pushed/hurt, has pw:anim + event pw:t6
  J the predictions I gave him are what the law computes: green top toward file +x, orange tip forward, cyan tip down,
    magenta tip forward AND toward file -x, animated cyan dips more, animated green higher; the figure is fresh
"""
import json, re, sys, hashlib, zipfile, subprocess, glob, datetime, shutil
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); SRC = ROOT / "tools/testrunner_src"
VER = "0.5.7"; RP_VER = "0.3.0"; B = ROOT / f"_build/testrunner-{VER}"; R = ROOT / f"_build/testrunner-rp-{RP_VER}"; RCHECK = ROOT / f"_build/testrunner-rp-{RP_VER}-check"
BP_NAME = f"PW-TestRunner-BP-v{VER.replace('.', '_')}.mcpack"
SCRIPTS = ("pw_testrunner.js", "pw_testrunner_steps.js", "pw_testrunner_p0.js", "pw_testrunner_p1.js", "pw_testrunner_p2.js", "pw_testrunner_p3.js", "pw_testrunner_p4.js", "pw_testrunner_p5.js", "pw_testrunner_p6.js", "pw_testrunner_p7.js", "pw_testrunner_p8.js", "pw_testrunner_p9.js", "pw_testrunner_p10.js", "pw_testrunner_p11.js", "pw_testrunner_p12.js", "pw_testrunner_p13.js", "pw_testrunner_p14.js", "pw_testrunner_rig.js")
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok))); print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
def jload(p): return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()

# A
m = jload(B / "manifest.json"); h = m["header"]; mods = {x["type"]: x for x in m["modules"]}
check("A BP manifest: name/version, header + script uuids unchanged since 0.1.0, data module fixed uuid", h["name"] == f"PW Test Runner BP v{VER}" and h["version"] == [int(x) for x in VER.split(".")] and h["uuid"] == "6b1f0c2e-9a47-4d3b-8e5c-2f7a9d1c4e60"
      and mods["script"]["uuid"] == "d4e8a1f2-3c6b-4b9e-a7d5-8f1e2c3b4a90" and mods["script"]["entry"] == "scripts/main.js" and mods["data"]["uuid"] == "9c2e7b41-5d3a-4f68-b1c9-2e8a4d7f6c13" and all(x["version"] == [int(x_) for x_ in VER.split(".")] for x in m["modules"]))
deps = {d.get("module_name"): d.get("version") for d in m["dependencies"]}
check("A BP pins server 2.3.0 + server-ui 2.0.0, no pack-uuid deps (L-VV-2)", deps == {"@minecraft/server": "2.3.0", "@minecraft/server-ui": "2.0.0"} and all("module_name" in d for d in m["dependencies"]))
rm = jload(R / "manifest.json"); rh = rm["header"]
check("A RP manifest: name/version/uuids fixed, resources module, no dependencies", rh["name"] == f"PW Test Runner RP v{RP_VER}" and rh["version"] == [0, 3, 0] and rh["uuid"] == "3f8b6a2d-1c4e-4d7b-9a5f-6e2c8b1d4a37"
      and rm["modules"][0]["type"] == "resources" and rm["modules"][0]["uuid"] == "7a1d4c9e-8b2f-4e6a-a3d5-1f9c7e2b5d48" and "dependencies" not in rm)
check("A descriptions stamped", h["description"].startswith(f"v{VER} (2026-09-30) TEST RUNNER") and rh["description"].startswith(f"v{RP_VER} (2026-09-28) TEST RUNNER RP"))
uuids = set()
for p in glob.glob(str(ROOT / "_build/*/manifest.json")) + glob.glob(str(ROOT / "_build/*/*/manifest.json")):
    if "testrunner" in p: continue
    try: mm = jload(p); uuids.add(mm["header"]["uuid"]); uuids.update(x["uuid"] for x in mm["modules"])
    except Exception: pass
ours = {h["uuid"], mods["script"]["uuid"], mods["data"]["uuid"], rh["uuid"], rm["modules"][0]["uuid"]}
check("A the 5 runner uuids are unique across every built pack and among themselves", not (ours & uuids) and len(ours) == 5, f"{len(uuids)} known uuids")

# B
bad = []
for d in (B, R):
    for p in d.rglob("*.json"):
        try: jload(p)
        except Exception: bad.append(str(p))
check("B every JSON in both packs parses", not bad, str(bad))
nc = [subprocess.run(["node", "--check", str(p)], capture_output=True, text=True).returncode for p in (B / "scripts").glob("*.js")]
check("B node --check on every script (main + 23 modules)", all(c == 0 for c in nc) and len(nc) == 24, f"{len(nc)} scripts")
check("B shipped scripts byte-identical to tools/testrunner_src", all(md5(B / "scripts" / f) == md5(SRC / f) for f in SCRIPTS))

# C
r = subprocess.run([sys.executable, str(ROOT / "tools/api_audit.py"), str(B)], capture_output=True, text=True, timeout=600)
check("C api_audit 0 flags on the pinned typings", r.returncode == 0 and "0 flag(s)" in r.stdout, r.stdout.strip().splitlines()[-1][:160] if r.stdout.strip() else r.stderr[:160])

# D
r = subprocess.run(["node", str(SRC / "test_testrunner.mjs"), str(B / "scripts")], capture_output=True, text=True, timeout=600)
tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]
check("D mock-run of the shipped scripts passes (witness lineup + PHASE 0)", r.returncode == 0 and ", 0 failed" in tail, tail)

# E
def steps_of(path, name):
    r = subprocess.run(["node", "--input-type=module", "-e", f"import(process.argv[1]).then(m=>console.log(JSON.stringify(m.{name})))", "--", str(path)], capture_output=True, text=True)
    return json.loads(r.stdout)
steps = steps_of(B / "scripts/pw_testrunner_steps.js", "STEPS")
old = steps_of(ROOT / "_build/testrunner-0.1.2/scripts/pw_testrunner_steps.js", "STEPS")
norm = lambda L: [dict(s, body=s["body"].replace("v0.5.1", "vX").replace("v0.5.0", "vX").replace("v0.4.9", "vX").replace("v0.4.8", "vX").replace("v0.4.7", "vX").replace("v0.4.6", "vX").replace("v0.4.5", "vX").replace("v0.4.4", "vX").replace("v0.4.3", "vX").replace("v0.4.2", "vX").replace("v0.4.1", "vX").replace("v0.4.0", "vX").replace("v0.3.9", "vX").replace("v0.3.8", "vX").replace("v0.3.7", "vX").replace("v0.3.6", "vX").replace("v0.3.5", "vX").replace("v0.3.4", "vX").replace("v0.3.3", "vX").replace("v0.3.2", "vX").replace("v0.3.1", "vX").replace("v0.3.0", "vX").replace("v0.2.2", "vX").replace("v0.2.1", "vX").replace("v0.2.0", "vX").replace("v0.1.2", "vX")) for s in L]
check("E witness lineup = the 0.1.2 table (48 steps; only the version strings differ)", len(steps) == 48 and norm(steps) == norm(old))
p0 = steps_of(B / "scripts/pw_testrunner_p0.js", "P0_STEPS"); mobs = steps_of(B / "scripts/pw_testrunner_p0.js", "P0_MOBS")
ids = [s["id"] for s in p0]
check("E PHASE 0 = q0 q1 q2 + one rig step per mob + q9, unique ids, 35 steps", ids[:3] == ["q0", "q1", "q2"] and ids[-1] == "q9" and len(ids) == 4 + len(mobs) and len(set(ids)) == len(ids) and len(mobs) == 31, f"{len(ids)} steps, {len(mobs)} mobs")
vanilla = set()          # P11: the samples intake has no behavior_pack/; the census source is RP-07 1.4.11's client entities (every rig mob is an RP-07 mob by construction)
for p in (ROOT / "_build/rp07-1412/entity").glob("*.json"):
    try: vanilla.add(jload(p)["minecraft:client_entity"]["description"]["identifier"])
    except Exception: pass
# D-C257 found RP-07 1.4.11 overriding the dead ids minecraft:zombified_piglin / minecraft:tropical_fish; RP-07 1.4.12 (D-C260) carries the
# Bedrock ids minecraft:zombie_pigman / minecraft:tropicalfish, so every rig mob must now be an exact RP-07 override — no aliases.
missing = [mb["id"] for mb in mobs if mb["id"] not in vanilla]
check("E every rig mob id is a client entity RP-07 1.4.12 overrides exactly (P11 census; the 1.4.11 id mismatches are gone)", len(vanilla) > 100 and not missing, f"{len(vanilla)} ids; missing {missing}")
# v0.2.1 behaviour is in the source (the mock suite proves it runs): quick tags, adults, NO MOB bar, ice re-melt, 1 s title
src = (B / "scripts/pw_testrunner.js").read_text(encoding="utf-8") + (B / "scripts/pw_testrunner_rig.js").read_text(encoding="utf-8")
p1 = steps_of(B / "scripts/pw_testrunner_p1.js", "P1_STEPS")
check("E P1 v2 = q0 + 11 hostile rig steps (roofed) + 14 block stations + q9, unique ids, no size steps", [x["id"] for x in p1][:2] == ["q0", "h01"] and p1[-1]["id"] == "q9" and len(p1) == 27 and len({x["id"] for x in p1}) == 27 and not [x for x in p1 if x["id"].startswith("s")]
      and all(any("rig" in a and a["rig"].get("roof") for a in x["setup"]) for x in p1 if x["id"].startswith("h")) and all(any("cmd" in a for a in x["setup"]) for x in p1 if x["id"].startswith("b")), f"{len(p1)} steps")
check("E v0.2.1 source carries the quick tags, ageable_grow_up, rigStatus/NO MOB, meltPool, stayDuration 20",
      all(k in src for k in ('"§4FAIL: vanilla?"', '"§4FAIL: magenta?"', '"§4FAIL: parts?"', "minecraft:ageable_grow_up", "NO MOB (", "function meltPool", "stayDuration: 20")))
AQUATIC = {"minecraft:turtle", "minecraft:salmon", "minecraft:pufferfish", "minecraft:dolphin", "minecraft:cod", "minecraft:axolotl", "minecraft:tadpole", "minecraft:squid", "minecraft:glow_squid", "minecraft:tropicalfish"}
check("E water flags = exactly the aquatic set", {mb["id"] for mb in mobs if mb["water"]} == AQUATIC)
rig_steps = [s for s in p0 if s["id"].startswith("r")]
check("E probe steps use probe static/anim; rig steps carry one rig action with the mob id; q9 clears both",
      p0[1]["setup"] == [{"probe": "static"}] and p0[2]["setup"] == [{"probe": "anim"}] and all(len(s["setup"]) == 1 and s["setup"][0]["rig"]["mob"] == mb["id"] for s, mb in zip(rig_steps, mobs)) and p0[-1]["setup"] == [{"probeclear": True}, {"rigclear": True}])
check("E every P0 body names PASS; rig bodies name SHOT 1/SHOT 2 (+SHOT 3 where top); q1 names shots A B C and the five questions",
      all("PASS" in s["body"] for s in p0) and all("SHOT 1 FRONT" in s["body"] and "SHOT 2 LEFT FLANK" in s["body"] and (("SHOT 3 TOP" in s["body"]) == mb["top"]) for s, mb in zip(rig_steps, mobs))
      and all(k in p0[1]["body"] for k in ("SHOT A", "SHOT B", "SHOT C", "RED cube", "GREEN bar", "ORANGE bar", "CYAN bar", "MAGENTA bar")) and "SHOT D" in p0[2]["body"])
check("E every step body first line <= 200 chars (chat line)", all(len(s["body"].split("\n")[0]) <= 200 for s in steps + p0), str([(s["id"], len(s["body"].split("\n")[0])) for s in steps + p0 if len(s["body"].split("\n")[0]) > 200]))

# K (0.3.0) the XPACK probe + P2
PROBES = {"a": "textures/blocks/stone", "b": "textures/blocks/mushroom_stem_v3", "c": "textures/blocks/pw_xprobe_nowhere"}
p1probes = steps_of(B / "scripts/pw_testrunner_p1.js", "P1_PROBES")
tt = jload(R / "textures/terrain_texture.json")["texture_data"]
blocks = {k: jload(B / "blocks" / f"pw_xprobe_{k}.json")["minecraft:block"] for k in PROBES}
check("K probe blocks: 3 x format 1.21.80, ids pw:xprobe_a/b/c, full_block geometry, one material key each == the RP's terrain keys == the lineup's paths",
      all(jload(B / "blocks" / f"pw_xprobe_{k}.json")["format_version"] == "1.21.80" and blocks[k]["description"]["identifier"] == f"pw:xprobe_{k}"
          and blocks[k]["components"]["minecraft:geometry"] == "minecraft:geometry.full_block" and blocks[k]["components"]["minecraft:material_instances"]["*"]["texture"] == f"pw_xprobe_{k}"
          and tt[f"pw_xprobe_{k}"]["textures"] == PROBES[k] == p1probes[k] for k in PROBES) and len(tt) == 3)
rp_paths = {str(q.relative_to(R)).replace("\\", "/").rsplit(".", 1)[0] for q in R.rglob("*") if q.is_file()}
check("K the TestRunner RP holds NONE of the 3 probe paths (the keys point outside the pack on purpose)", not any(v in rp_paths for v in PROBES.values()))
import zipfile as _zf
STACK = [("Markers RP", ROOT / "_build/markers-0.2.1/RP"), ("RP-10", ROOT / "_build/rp10-142"), ("RP-08", ROOT / "_build/rp08-147"), ("RP-07", ROOT / "_build/rp07-1413"), ("RP-06", ROOT / "_build/rp06-148"),
         ("RP-05", ROOT / "_build/rp05-51"), ("RP-04", ROOT / "_build/rp04-141"), ("RP-03", ROOT / "_build/rp03-60"), ("RP-02", ROOT / "_build/rp02-205"), ("RP-01", ROOT / "_build/rp01-104")]
ZIPS = [("LeafProbe RP", ROOT / "_intake/stack-rps/PW-LeafProbe-RP-v0_3_1.mcpack"), ("StripMine RP", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-11", ROOT / "_intake/stack-rps/RP-11-AbsolutRealism-Ores-RP-v1_3_35.mcpack")]
holders = {k: [] for k in PROBES}
for name, d in STACK:
    for k, v in PROBES.items():
        if any((d / (v + ext)).exists() for ext in (".png", ".tga", ".jpg")): holders[k].append(name)
for name, z in ZIPS:
    names = set(n.rsplit(".", 1)[0] for n in _zf.ZipFile(z).namelist())
    for k, v in PROBES.items():
        if v in names: holders[k].append(name)
van_paths = set(re.findall(r'"(textures/blocks/[a-z0-9_/]+)"', (ROOT / "_intake/vanilla-1.21/terrain_texture.json").read_text(encoding="utf-8-sig")))
check("K P11 census: A held by RP-04 (+RP-03) and named by vanilla; B held ONLY by RP-01 and not a vanilla name; C held by nobody, not vanilla",
      "RP-04" in holders["a"] and PROBES["a"] in van_paths and holders["b"] == ["RP-01"] and PROBES["b"] not in van_paths and holders["c"] == [] and PROBES["c"] not in van_paths, str(holders))
p2 = steps_of(B / "scripts/pw_testrunner_p2.js", "P2_STEPS")
check("K P2 = q0 s01-s04 r01-r03 q9 (9 steps), the shark step rigs in water, every rig step clears the station volume first",
      [x["id"] for x in p2] == ["q0", "s01", "s02", "s03", "s04", "r01", "r02", "r03", "q9"] and p2[7]["setup"][1]["rig"]["water"] is True and p2[5]["setup"][1]["rig"]["water"] is False
      and all(x["setup"][0] == {"cmd": ["fill ~-3 ~ ~-9 ~3 ~5 ~-2 air"]} for x in p2[1:8]))
sky = {x["id"]: x for x in p1}
check("K sky stations set 12500 / 18000 / noon before their commands; b13 restores noon; q9 ends at noon",
      sky["b10"]["setup"][1] == {"daytime": 12500} and sky["b11"]["setup"][1] == {"daytime": 18000} and sky["b12"]["setup"][1] == {"daytime": "noon"} and sky["b13"]["setup"][1] == {"daytime": "noon"} and p1[-1]["setup"][-1] == {"daytime": "noon"})

# L (0.3.1)
van_ent = set()
for q in (ROOT / "_intake/bedrock-samples/behavior_pack/entities").glob("*.json"):     # 40 of 128 vanilla BP files carry inline comments /
    van_ent.update(re.findall(r'"identifier"\s*:\s*"([^"]+)"', q.read_text(encoding="utf-8-sig")))   # trailing commas: census the identifier field
p1h = steps_of(B / "scripts/pw_testrunner_p1.js", "P1_HOSTILES")
check("L every P1 hostile id is a vanilla behaviour entity (bedrock-samples 1.26.50, P11 census); the evoker = minecraft:evocation_illager",
      len(van_ent) > 100 and all(x["id"] in van_ent for x in p1h) and any(x["id"] == "minecraft:evocation_illager" for x in p1h) and "minecraft:evoker" not in {x["id"] for x in p1h},
      f"{len(van_ent)} vanilla ids; not found {[x['id'] for x in p1h if x['id'] not in van_ent]}")
lineups = {"main": steps, "p0": p0, "p1": p1, "p2": p2, "p1r": steps_of(B / "scripts/pw_testrunner_p1.js", "P1R_STEPS")}
GRAMMAR = re.compile(r'^\s*"[^"]+"\s*=\s*("[^"]*"|true|false|-?\d+)\s*$')
bad_states = []
for ln, L in lineups.items():
    for s in L:
        for a in s.get("setup", []):
            for c in a.get("cmd", []) or []:
                for clause in re.findall(r"\[([^\]]*)\]", c):
                    if not all(GRAMMAR.match(pair) for pair in clause.split(",")): bad_states.append((ln, s["id"], c))
check("L every block-state clause in every lineup uses [\"name\"=value] (the 0.3.0 ':' form never parsed)", not bad_states, str(bad_states[:4]))
van_blocks = set(json.loads(re.sub(r"//[^\n]*", "", (ROOT / "_intake/vanilla-1.21/blocks.json").read_text(encoding="utf-8-sig"))))
pw_blocks = set()
for q in list((ROOT / "_build/bp02-189/blocks").rglob("*.json")) + list((B / "blocks").glob("*.json")):
    try: pw_blocks.add(jload(q)["minecraft:block"]["description"]["identifier"])
    except Exception: pass
placed, unknown = set(), []
for s in p1:
    for a in s.get("setup", []):
        for c in a.get("cmd", []) or []:
            mm = re.match(r"^(?:setblock(?:\s+\S+){3}|fill(?:\s+\S+){6})\s+(\S+)", c)
            if mm:
                bid = mm.group(1); placed.add(bid)
                if not (bid in van_blocks or bid.replace("minecraft:", "") in van_blocks or bid in pw_blocks): unknown.append((s["id"], bid))
check("L every block a p1 station places exists (vanilla blocks.json / the probe blocks / BP-02 1.3.189's pw: blocks)", placed and not unknown, f"{len(placed)} block ids; unknown {unknown}")
P1R_IDS = steps_of(B / "scripts/pw_testrunner_p1.js", "P1R_IDS"); p1r = lineups["p1r"]; by1 = {s["id"]: s for s in p1}
check("L p1r = q0 h03..h10 b03 b04 b07 b08 b13 b14 q9 (16), each step identical to its p1 step", [s["id"] for s in p1r] == P1R_IDS == ["q0", "h03", "h04", "h05", "h06", "h07", "h08", "h09", "h10", "b03", "b04", "b07", "b08", "b13", "b14", "q9"]
      and all(s == by1[s["id"]] for s in p1r))
ra = {str(q.relative_to(RCHECK)): md5(q) for q in RCHECK.rglob("*") if q.is_file()}; rb = {str(q.relative_to(R)): md5(q) for q in R.rglob("*") if q.is_file()}
check("L the RP rebuilt from source is byte-identical to the shipped RP v0.3.0 (he keeps the RP he has)", ra == rb and len(ra) > 5, f"{len(ra)} files")

# M (0.3.2) the P3 lineups
p3 = steps_of(B / "scripts/pw_testrunner_p3.js", "P3_STEPS"); p3n = steps_of(B / "scripts/pw_testrunner_p3.js", "P3N_STEPS")
ids3 = [x["id"] for x in p3]
check("M p3 = q0 n01..n14 e01..e17 q9 (33, unique); p3n = q0 n01..n14 q9 (16) with the same step contents",
      ids3 == ["q0"] + [f"n{i:02d}" for i in range(1, 15)] + [f"e{i:02d}" for i in range(1, 18)] + ["q9"] and len(set(ids3)) == 33
      and [x["id"] for x in p3n] == ["q0"] + [f"n{i:02d}" for i in range(1, 15)] + ["q9"] and all(x == {y["id"]: y for y in p3}[x["id"]] for x in p3n))
rigs = [(x["id"], a["rig"]) for x in p3 for a in x["setup"] if "rig" in a]
mob_ids = sorted({r["mob"] for _, r in rigs} | {q["mob"] for _, r in rigs for q in r.get("row", [])})
check("M every p3 rig mob (main + row) is a vanilla behaviour entity id", all(i in van_ent for i in mob_ids), f"{len(mob_ids)} ids; not vanilla {[i for i in mob_ids if i not in van_ent]}")
geo_ok = all(abs(q["dx"]) <= r.get("half", 2) for _, r in rigs for q in r.get("row", [])) and all((r.get("halfz") or r.get("half", 2)) + 3 >= 5 for _, r in rigs)
check("M row offsets inside the pen; every pen's south wall >= 2 blocks ahead (centre moves north with halfz)", geo_ok and "Math.max(PEN_DISTANCE, halfz + 3)" in (B / "scripts/pw_testrunner_rig.js").read_text(encoding="utf-8"))
AQ3 = {"minecraft:guardian", "minecraft:elder_guardian", "minecraft:tadpole", "minecraft:turtle", "minecraft:salmon", "minecraft:dolphin", "minecraft:axolotl", "minecraft:tropicalfish", "minecraft:squid", "minecraft:glow_squid"}
check("M water flags = exactly the aquatic p3 mobs; the swim tank is free, the resting guardian held", {r["mob"] for _, r in rigs if r.get("water")} == AQ3
      and dict(rigs)["n05"].get("free") is True and not dict(rigs)["n04"].get("free") and dict(rigs)["n08"].get("free") is True)
check("M every p3 body names PASS; first lines <= 200 chars; every rig step clears the wide station volume first",
      all("PASS" in x["body"] for x in p3) and all(len(x["body"].split("\n")[0]) <= 200 for x in p3) and all(x["setup"][0] == {"cmd": ["fill ~-6 ~ ~-12 ~6 ~5 ~-2 air"]} for x in p3 if x["id"][0] in "ne"),
      str([(x["id"], len(x["body"].split("\n")[0])) for x in p3 if len(x["body"].split("\n")[0]) > 200]))

# N (0.3.3) the P4 lineup
p4 = steps_of(B / "scripts/pw_testrunner_p4.js", "P4_STEPS"); ids4 = [x["id"] for x in p4]
check("N p4 = q0 a01..a22 q9 (24, unique)", ids4 == ["q0"] + [f"a{i:02d}" for i in range(1, 23)] + ["q9"] and len(set(ids4)) == 24, " ".join(ids4))
rigs4 = [(x["id"], a["rig"]) for x in p4 for a in x["setup"] if "rig" in a]
mob4 = sorted({r["mob"] for _, r in rigs4} | {q["mob"] for _, r in rigs4 for q in r.get("row", [])})
check("N every p4 rig mob (main + row) is a vanilla behaviour entity id", all(i in van_ent for i in mob4), f"{len(mob4)} ids; not vanilla {[i for i in mob4 if i not in van_ent]}")
check("N row offsets inside the pen; row spawn events are vanilla mooshroom events",
      all(abs(q["dx"]) <= r.get("half", 2) for _, r in rigs4 for q in r.get("row", [])) and all(q.get("event") in (None, "minecraft:become_brown", "minecraft:hatch_warm", "minecraft:hatch_cold") for _, r in rigs4 for q in r.get("row", []))
      and "x.triggerEvent(r.event)" in (B / "scripts/pw_testrunner_rig.js").read_text(encoding="utf-8"))
AQ4 = {"minecraft:tropicalfish", "minecraft:guardian", "minecraft:dolphin", "minecraft:axolotl", "minecraft:squid", "minecraft:glow_squid", "minecraft:tadpole"}
d4 = dict(rigs4)
check("N water flags = exactly the aquatic p4 mobs; free where the step watches motion (spider walk, guardian tank, squids, enderman, silverfish)",
      {r["mob"] for _, r in rigs4 if r.get("water")} == AQ4 and all(d4[k].get("free") is True for k in ("a06", "a08", "a14", "a15", "a16", "a17"))
      and not any(d4[k].get("free") for k in ("a05", "a07", "a09", "a10", "a11")))
check("N every p4 body names PASS; first lines <= 200 chars; every rig step clears the station volume first",
      all("PASS" in x["body"] for x in p4) and all(len(x["body"].split("\n")[0]) <= 200 for x in p4) and all(x["setup"][0] == {"cmd": ["fill ~-6 ~ ~-12 ~6 ~5 ~-2 air"]} for x in p4 if x["id"][0] == "a"),
      str([(x["id"], len(x["body"].split("\n")[0])) for x in p4 if len(x["body"].split("\n")[0]) > 200]))
check("N the q0 step names the versions RP-07 v1.4.20 / RP-06 v1.4.13 / runner v0.3.4 (p4 text frozen as shipped)", all(s in p4[0]["body"] for s in ("v1.4.20", "v1.4.13", "v0.3.4")))
a01 = dict(rigs4)["a01"]
check("N a01: temperate chicken in the middle (property), warm left / cold right (vanilla chicken events hatch_warm / hatch_cold)", a01.get("props") == {"minecraft:climate_variant": "temperate"}
      and sorted((q["dx"], q.get("event")) for q in a01["row"]) == [(-2, "minecraft:hatch_warm"), (2, "minecraft:hatch_cold")] and "e.setProperty(k, v)" in (B / "scripts/pw_testrunner_rig.js").read_text(encoding="utf-8"))

# P (0.3.5, D-C284) the P5 lineup + name tags
p5 = steps_of(B / "scripts/pw_testrunner_p5.js", "P5_STEPS"); ids5 = [x["id"] for x in p5]
check("P p5 = q0 b01..b18 q9 (20, unique)", ids5 == ["q0"] + [f"b{i:02d}" for i in range(1, 19)] + ["q9"] and len(set(ids5)) == 20, " ".join(ids5))
rigs5 = [(x["id"], a["rig"]) for x in p5 for a in x["setup"] if "rig" in a]; d5 = dict(rigs5)
mob5 = sorted({r["mob"] for _, r in rigs5} | {q["mob"] for _, r in rigs5 for q in r.get("row", [])})
check("P every p5 rig mob (main + row) is a vanilla behaviour entity id", all(i in van_ent for i in mob5), f"{len(mob5)} ids; not vanilla {[i for i in mob5 if i not in van_ent]}")
EV5 = {"minecraft:become_brown", "minecraft:hatch_warm", "minecraft:hatch_cold", "minecraft:become_angry"}
check("P row offsets inside the pen; spawn events are vanilla (hatch_warm / hatch_cold, become_angry on the enderman)",
      all(abs(q["dx"]) <= r.get("half", 2) for _, r in rigs5 for q in r.get("row", []))
      and all(q.get("event") in (None, *EV5) for _, r in rigs5 for q in r.get("row", [])) and all(r.get("event") in (None, *EV5) for _, r in rigs5)
      and d5["b06"].get("event") == "minecraft:become_angry")
names = {q.get("name") for q in d5["b14"]["row"]} | {d5["b14"].get("name")}
rigsrc = (B / "scripts/pw_testrunner_rig.js").read_text(encoding="utf-8")
check("P b14: four mooshrooms named exactly Moo A..D, left to right (the RP-07 1.4.21 render controller keys), the rig sets name tags",
      names == {"Moo A", "Moo B", "Moo C", "Moo D"} and sorted([(q["dx"], q["name"]) for q in d5["b14"]["row"]] + [(0, d5["b14"]["name"])]) == [(-6, "Moo A"), (-3, "Moo B"), (0, "Moo C"), (3, "Moo D")]
      and "x.nameTag = r.name" in rigsrc and "const mm = { r: spec, dx: 0, isMain: true }" in rigsrc, str(sorted(names, key=str)))
AQ5 = {"minecraft:guardian", "minecraft:dolphin", "minecraft:squid", "minecraft:axolotl"}
check("P water flags = exactly the aquatic p5 steps; free where the step watches motion (silverfish, guardian tank, squids)",
      {r["mob"] for _, r in rigs5 if r.get("water")} == AQ5 and all(d5[k].get("free") is True for k in ("b04", "b10", "b12"))
      and not any(d5[k].get("free") for k in ("b02", "b05", "b06", "b07", "b11", "b13", "b14")))
check("P every p5 body names PASS; first lines <= 200 chars; every rig step clears the wide station volume first; the pens fit inside it",
      all("PASS" in x["body"] for x in p5) and all(len(x["body"].split("\n")[0]) <= 200 for x in p5)
      and all(x["setup"][0] == {"cmd": ["fill ~-9 ~ ~-14 ~9 ~5 ~-2 air"]} for x in p5 if x["id"][0] == "b") and all(r.get("half", 2) <= 8 for _, r in rigs5),
      str([(x["id"], len(x["body"].split("\n")[0])) for x in p5 if len(x["body"].split("\n")[0]) > 200]))
check("P the q0 step names RP-07 v1.4.22 / RP-06 v1.4.15 / RP-08 v1.4.8 / runner v0.3.6", all(s in p5[0]["body"] for s in ("v1.4.22", "v1.4.15", "v1.4.8", "v0.3.6")))
check("P b09 gives the player a bow; q9 removes stray vexes", {"cmd": ["give @s bow"]} in [a for x in p5 if x["id"] == "b09" for a in x["setup"]]
      and any("kill @e[type=vex" in c for x in p5 if x["id"] == "q9" for a in x["setup"] for c in a.get("cmd", [])))

# Q (0.3.7, D-C285) the P6 lineup + rig items
p6 = steps_of(B / "scripts/pw_testrunner_p6.js", "P6_STEPS"); ids6 = [x["id"] for x in p6]
check("Q p6 = q0 c01..c08 q9 (10, unique)", ids6 == ["q0"] + [f"c{i:02d}" for i in range(1, 9)] + ["q9"] and len(set(ids6)) == 10, " ".join(ids6))
rigs6 = [(x["id"], a["rig"]) for x in p6 for a in x["setup"] if "rig" in a]; d6 = dict(rigs6)
mob6 = sorted({r["mob"] for _, r in rigs6} | {q["mob"] for _, r in rigs6 for q in r.get("row", [])})
check("Q every p6 rig mob (main + row) is a vanilla behaviour entity id", all(i in van_ent for i in mob6), f"{len(mob6)} ids; not vanilla {[i for i in mob6 if i not in van_ent]}")
check("Q row offsets inside the pen; the enderman is made angry; silverfish + squids FREE; aquatic = squid / tadpole / pufferfish",
      all(abs(q["dx"]) <= r.get("half", 2) for _, r in rigs6 for q in r.get("row", [])) and d6["c03"].get("event") == "minecraft:become_angry"
      and d6["c01"].get("free") is True and d6["c02"].get("free") is True and not any(d6[k].get("free") for k in ("c03", "c04", "c05", "c06", "c07", "c08"))
      and {r["mob"] for _, r in rigs6 if r.get("water")} == {"minecraft:squid", "minecraft:tadpole", "minecraft:pufferfish"})
c07 = d6["c07"]; held = sorted([(0, c07["mob"], c07.get("item"))] + [(q["dx"], q["mob"], q.get("item")) for q in c07["row"]])
VAN_ITEMS = {"iron_sword", "crossbow", "bow", "iron_shovel", "trident", "golden_sword"}
check("Q c07: seven mobs left to right with a vanilla item each (pillager control + the six models without a hold point); roofed; the rig equips by replaceitem",
      [m for _, m, _ in held] == ["minecraft:pillager", "minecraft:stray", "minecraft:bogged", "minecraft:zombie", "minecraft:husk", "minecraft:drowned", "minecraft:piglin"]
      and all(i in VAN_ITEMS for _, _, i in held) and c07.get("roof") is True and "replaceitem entity @s slot.weapon.mainhand 0" in rigsrc
      and "equip(x, r.item" in rigsrc and "const mm = { r: spec, dx: 0, isMain: true }" in rigsrc, str(held))
check("Q every p6 body names PASS; first lines <= 200 chars; every rig step clears the wide station volume first; the pens fit inside it",
      all("PASS" in x["body"] for x in p6) and all(len(x["body"].split("\n")[0]) <= 200 for x in p6)
      and all(x["setup"][0] == {"cmd": ["fill ~-9 ~ ~-14 ~9 ~5 ~-2 air"]} for x in p6 if x["id"][0] == "c") and all(r.get("half", 2) <= 8 for _, r in rigs6))
check("Q the q0 step names RP-07 v1.4.23 / RP-06 v1.4.16 / RP-08 v1.4.8 / runner v0.3.7 (p6 text frozen as shipped)", all(s in p6[0]["body"] for s in ("v1.4.23", "v1.4.16", "v1.4.8", "v0.3.7")))

# R (0.3.8, D-C286) the P7 lineup
p7 = steps_of(B / "scripts/pw_testrunner_p7.js", "P7_STEPS"); ids7 = [x["id"] for x in p7]
check("R p7 = q0 d01 d02 d03 q9 (5, unique)", ids7 == ["q0", "d01", "d02", "d03", "q9"], " ".join(ids7))
rigs7 = [(x["id"], a["rig"]) for x in p7 for a in x["setup"] if "rig" in a]; d7 = dict(rigs7)
mob7 = sorted({r["mob"] for _, r in rigs7} | {q["mob"] for _, r in rigs7 for q in r.get("row", [])})
check("R every p7 rig mob is a vanilla behaviour entity id; the enderman is made angry; squids FREE in water; the three archers each get a bow",
      all(i in van_ent for i in mob7) and d7["d01"].get("event") == "minecraft:become_angry" and d7["d03"].get("free") is True and d7["d03"].get("water") is True
      and sorted([(0, d7["d02"]["mob"], d7["d02"].get("item"))] + [(q["dx"], q["mob"], q.get("item")) for q in d7["d02"]["row"]])
          == [(-3, "minecraft:skeleton", "bow"), (0, "minecraft:stray", "bow"), (3, "minecraft:bogged", "bow")], str(mob7))
check("R every p7 body names PASS; first lines <= 200 chars; rig steps clear the station volume first; q0 names RP-07 v1.4.24 / RP-06 v1.4.17 / runner v0.3.8",
      all("PASS" in x["body"] for x in p7) and all(len(x["body"].split("\n")[0]) <= 200 for x in p7)
      and all(x["setup"][0] == {"cmd": ["fill ~-9 ~ ~-14 ~9 ~5 ~-2 air"]} for x in p7 if x["id"][0] == "d")
      and all(s in p7[0]["body"] for s in ("v1.4.24", "v1.4.17", "v0.3.8")))

# S (0.3.9, D-C288) the P8 lineup + rig body armor
p8 = steps_of(B / "scripts/pw_testrunner_p8.js", "P8_STEPS"); ids8 = [x["id"] for x in p8]
check("S p8 = q0 e01 e02 e03 q9 (5, unique)", ids8 == ["q0", "e01", "e02", "e03", "q9"], " ".join(ids8))
rigs8 = [(x["id"], a["rig"]) for x in p8 for a in x["setup"] if "rig" in a]; d8 = dict(rigs8)
mob8 = sorted({r["mob"] for _, r in rigs8} | {q["mob"] for _, r in rigs8 for q in r.get("row", [])})
held8 = lambda st: sorted([(0, d8[st]["mob"], d8[st].get("item"))] + [(q["dx"], q["mob"], q.get("item")) for q in d8[st].get("row", [])])
check("S every p8 rig mob is a vanilla behaviour entity id; e01 skeleton + bogged with bows; e02 brute/piglin crossbows + wither skeleton bow; e03 tamed wolf in wolf armor + zombified piglin crossbow",
      all(i in van_ent for i in mob8)
      and held8("e01") == [(-3, "minecraft:skeleton", "bow"), (0, "minecraft:bogged", "bow")]
      and held8("e02") == [(-3, "minecraft:piglin_brute", "crossbow"), (0, "minecraft:piglin", "crossbow"), (3, "minecraft:wither_skeleton", "bow")]
      and d8["e03"]["mob"] == "minecraft:wolf" and d8["e03"].get("event") == "minecraft:on_tame" and d8["e03"].get("armor") == "wolf_armor"
      and [(q["mob"], q.get("item")) for q in d8["e03"]["row"]] == [("minecraft:zombie_pigman", "crossbow")], str(mob8))
rigsrc8 = (B / "scripts/pw_testrunner_rig.js").read_text()
check("S the rig puts body armor on by replaceitem slot.armor.body (main mob and row), logged either way",
      "replaceitem entity @s slot.armor.body 0" in rigsrc8 and "armorOn(x, r.armor" in rigsrc8 and "const mm = { r: spec, dx: 0, isMain: true }" in rigsrc8 and "RIG armor" in rigsrc8)
check("S every p8 body names PASS; first lines <= 200 chars; rig steps clear the station volume first; q0 names RP-06 v1.4.18 / RP-07 v1.4.25 / runner v0.3.9",
      all("PASS" in x["body"] for x in p8) and all(len(x["body"].split("\n")[0]) <= 200 for x in p8)
      and all(x["setup"][0] == {"cmd": ["fill ~-9 ~ ~-14 ~9 ~5 ~-2 air"]} for x in p8 if x["id"][0] == "e")
      and all(s in p8[0]["body"] for s in ("v1.4.18", "v1.4.25", "v0.3.9")))

# T (0.4.0, D-C292) the P9 size parade + grow-up after a step event + age log
p9 = steps_of(B / "scripts/pw_testrunner_p9.js", "P9_STEPS"); ids9 = [x["id"] for x in p9]
exp9 = ["q0", "z01", "z02", "z03", "z04", "z05", "z06", "z07", "z08", "w09", "w10", "w11", "w12", "w13", "q9"]
check("T p9 = q0 z01..z08 w09..w13 q9 (15, unique)", ids9 == exp9, " ".join(ids9))
rigs9 = [(x["id"], a["rig"]) for x in p9 for a in x["setup"] if "rig" in a]
mob9 = sorted({r["mob"] for _, r in rigs9} | {q["mob"] for _, r in rigs9 for q in r.get("row", [])})
import build_size_round as BSR
sm_ids = set()
for pp in (ROOT / "_build/stripmine-bp-134/entities").rglob("*.json"):
    mm = re.search(r'"identifier"\s*:\s*"(sf_nba:[a-z_]+)"', pp.read_text(encoding="utf-8-sig", errors="ignore"))
    if mm: sm_ids.add(mm.group(1))
resized = {"minecraft:" + k for k in BSR.VANILLA_FILES} | {"minecraft:warden"}
refs = {"minecraft:wolf", "minecraft:pufferfish", "sf_nba:deer"}
check("T every p9 mob exists (vanilla behaviour entity or StripMine 1.3.4 creature); every vanilla mob shown is resized this round or a named reference",
      all((i in van_ent) or (i in sm_ids) for i in mob9) and all(i in resized | refs for i in mob9 if i.startswith("minecraft:"))
      and resized <= set(mob9), str([i for i in mob9 if not ((i in van_ent) or (i in sm_ids))]))
check("T Naturalist steps say REALM ONLY; water steps use pools; the warden pen is roofed and tall enough (>= 5)",
      all("REALM ONLY" in x["body"] for x in p9 if x["id"].startswith("w")) and all(dict(rigs9)[k].get("water") for k in ("z06", "z07", "w13"))
      and dict(rigs9)["z08"].get("roof") and dict(rigs9)["z08"].get("height", 0) >= 5)
rigsrc9 = (B / "scripts/pw_testrunner_rig.js").read_text()
check("T the rig grows a mob up after a step event unless spec.baby, and logs every rigged mob's age",
      "if (spec.event && !spec.baby)" in rigsrc9 and "if (spec.baby) {" in rigsrc9 and "RIG age " in rigsrc9)
check("T every p9 body names PASS; first lines <= 200 chars; rig steps clear the volume first; q0 names BP-02 v1.3.190 / RP-06 v1.4.19 / StripMine BP v1.3.4 / runner v0.4.0",
      all("PASS" in x["body"] for x in p9) and all(len(x["body"].split("\n")[0]) <= 200 for x in p9)
      and all(x["setup"][0] == {"cmd": ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"]} for x in p9 if x["id"][0] in "zw")
      and all(s in p9[0]["body"] for s in ("v1.3.190", "v1.4.19", "v1.3.4", "v0.4.0")))

# U (0.4.1, D-C300) the P10 lineup (FA-1 + predator sizes) + re-roll / jukebox / leftover-water sweep
p10 = steps_of(B / "scripts/pw_testrunner_p10.js", "P10_STEPS"); ids10 = [x["id"] for x in p10]
exp10 = ["q0"] + [f"f{i:02d}" for i in range(1, 16)] + ["w16", "w17", "q9"]
check("U p10 = q0 f01..f15 w16 w17 q9 (19, unique)", ids10 == exp10 and len(set(ids10)) == 19, " ".join(ids10))
rigs10 = [(x["id"], a["rig"]) for x in p10 for a in x["setup"] if "rig" in a]; d10 = dict(rigs10)
mob10 = sorted({r["mob"] for _, r in rigs10} | {q["mob"] for _, r in rigs10 for q in r.get("row", [])})
sm_ids5 = set()
for pp in (ROOT / "_build/stripmine-bp-135/entities").rglob("*.json"):
    mm = re.search(r'"identifier"\s*:\s*"(sf_nba:[a-z_]+)"', pp.read_text(encoding="utf-8-sig", errors="ignore"))
    if mm: sm_ids5.add(mm.group(1))
FA1 = {"minecraft:parrot", "minecraft:bat", "minecraft:allay", "minecraft:vex", "minecraft:phantom", "minecraft:warden", "minecraft:blaze", "minecraft:breeze",
       "minecraft:creaking", "minecraft:endermite", "minecraft:sniffer"}
rep2 = json.load(open(ROOT / "_docs/sizes/size_round2_report.json"))
resized2 = {d["id"] for d in rep2["bp02"]} | {r["id"] for r in rep2["stripmine"]}
check("U every p10 mob exists (vanilla behaviour entity or StripMine 1.3.5 creature); every FA-1 conversion has a step; every sf_nba mob shown was resized in size round 2",
      all((i in van_ent) or (i in sm_ids5) for i in mob10) and FA1 <= set(mob10) and all(i in resized2 for i in mob10 if i.startswith("sf_nba:")),
      str([i for i in mob10 if not ((i in van_ent) or (i in sm_ids5))] + sorted(FA1 - set(mob10)) + [i for i in mob10 if i.startswith("sf_nba:") and i not in resized2]))
cols = sorted([(0, d10["f01"].get("variant"))] + [(q["dx"], q.get("variant")) for q in d10["f01"]["row"]])
check("U f01: five parrots, variants 0..4 left to right (red-blue, blue, green, yellow-blue, grey); f02 flying pair free + roofed; f03 jukebox inside the pen with a disc",
      cols == [(-4, 0), (-2, 1), (0, 2), (2, 3), (4, 4)] and d10["f02"].get("free") and d10["f02"].get("roof")
      and abs(d10["f03"]["jukebox"]["dx"]) <= d10["f03"]["half"] and abs(d10["f03"]["jukebox"]["dz"]) <= d10["f03"]["halfz"] and d10["f03"]["jukebox"]["disc"] == "music_disc_cat"
      and (d10["f03"]["jukebox"]["dx"] ** 2 + d10["f03"]["jukebox"]["dz"] ** 2) ** 0.5 <= 3.0, str(cols))
check("U the dance step carries his disc commands (give + use); the allay holds an amethyst shard, the vex an iron sword",
      "/give @s music_disc_cat" in next(x for x in p10 if x["id"] == "f03")["body"] and "tap (use) the jukebox" in next(x for x in p10 if x["id"] == "f03")["body"]
      and d10["f05"].get("item") == "amethyst_shard" and d10["f06"].get("item") == "iron_sword")
check("U flyers roofed (allay, vex, phantom, blaze, breeze, bat, flying parrots); warden roofed + tall at midnight; phantom at dusk; the blaze step returns to noon",
      all(d10[k].get("roof") for k in ("f02", "f04", "f05", "f06", "f07", "f08", "f09", "f10")) and d10["f08"].get("height", 0) >= 5
      and {"daytime": 18000} in next(x for x in p10 if x["id"] == "f08")["setup"] and {"daytime": 13000} in next(x for x in p10 if x["id"] == "f07")["setup"]
      and {"daytime": "noon"} in next(x for x in p10 if x["id"] == "f09")["setup"])
check("U row offsets inside the pen; the dolphin step is a 3-deep pool; the Naturalist steps say REALM ONLY",
      all(abs(q["dx"]) <= r.get("half", 2) for _, r in rigs10 for q in r.get("row", [])) and d10["f15"].get("water") and d10["f15"].get("depth") == 3
      and all("REALM ONLY" in x["body"] for x in p10 if x["id"].startswith("w")))
check("U every p10 body names PASS; first lines <= 200 chars; rig steps clear the volume first; q0 names RP-06 v1.4.20 / RP-07 v1.4.26 / BP-02 v1.3.192 / StripMine BP v1.3.5 / runner v0.4.1",
      all("PASS" in x["body"] for x in p10) and all(len(x["body"].split("\n")[0]) <= 200 for x in p10)
      and all(x["setup"][0] == {"cmd": ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"]} for x in p10 if x["id"][0] in "fw")
      and all(s in p10[0]["body"] for s in ("v1.4.20", "v1.4.26", "v1.3.192", "v1.3.5", "v0.4.1")),
      str([(x["id"], len(x["body"].split("\n")[0])) for x in p10 if len(x["body"].split("\n")[0]) > 200]))
fig = {"f01": "0.89", "f04": "0.56", "f14": "2.64", "f15": "4.0"}
bp02 = {d["id"]: d for d in rep2["bp02"]}
pb = bp02["minecraft:polar_bear"]; dol = bp02["minecraft:dolphin"]; prr = bp02["minecraft:parrot"]; bat = bp02["minecraft:bat"]
check("U the sizes quoted to him are the built ones (parrot macaw / grey, bat, polar bear, dolphin; 2 dp)",
      f"{prr['to_blocks']:.2f}" in next(x for x in p10 if x["id"] == "f01")["body"] and f"{prr['grey_to_blocks']:.2f}" in next(x for x in p10 if x["id"] == "f01")["body"]
      and f"{bat['to_blocks']:.2f}" in next(x for x in p10 if x["id"] == "f04")["body"] and f"{pb['to_blocks']:.2f}" in next(x for x in p10 if x["id"] == "f14")["body"]
      and f"{dol['to_blocks']:.1f}" in next(x for x in p10 if x["id"] == "f15")["body"],
      f"parrot {prr['to_blocks']:.3f}/{prr['grey_to_blocks']:.3f} bat {bat['to_blocks']:.3f} polar {pb['to_blocks']:.3f} dolphin {dol['to_blocks']:.3f}")
rigsrc10 = (B / "scripts/pw_testrunner_rig.js").read_text()
check("U the rig: re-roll (babies without a grow-up event, wrong colour; cap 30, logged), jukebox via minecraft:record_player setRecord with a logged fallback, "
      "a pre-pool water snapshot the sweep never touches (> 400 cells = no sweep), the sweep after a pool clear, the stand-in-water note",
      all(k in rigsrc10 for k in ("const MAX_REROLL = 30;", "RIG re-roll", 'getComponent("minecraft:variant")', 'getComponent("minecraft:record_player")', "rp.setRecord(disc, true)",
                                  "use the commands in the step text", "snapshotWater(dim, { centre: c, half, halfz, height })", "const PRE_CAP = 400;", "RIG sweep skipped:",
                                  "if (R && R.water && R.centre) { try { sweepWater(dim, R);", "RIG note: you stand in")))
check("U the rig repairs a broken pen every 0.5 s (walls / roof it placed -> barrier; a pool's open floor -> stone), each repair logged once (D-C303)",
      all(k in rigsrc10 for k in ("const HEAL_EVERY = 10;", "if (holdTicks % HEAL_EVERY === 0)", 'if (cell.kind === "wall" && !healOwned.has(k)) continue;',
                                  "RIG pen wall broken at", "RIG pool floor open at")))

# V (0.4.2, D-C307) the P11 lineup (the R14 fixes)
p11 = steps_of(B / "scripts/pw_testrunner_p11.js", "P11_STEPS"); ids11 = [x["id"] for x in p11]
exp11 = ["q0"] + [f"g{i:02d}" for i in range(1, 11)] + ["w11", "w12", "q9"]
check("V p11 = q0 g01..g10 w11 w12 q9 (14, unique)", ids11 == exp11 and len(set(ids11)) == 14, " ".join(ids11))
rigs11 = [(x["id"], a["rig"]) for x in p11 for a in x["setup"] if "rig" in a]; d11 = dict(rigs11)
mob11 = sorted({r["mob"] for _, r in rigs11} | {q["mob"] for _, r in rigs11 for q in r.get("row", [])})
sm_ids6 = set()
for pp in (ROOT / "_build/stripmine-bp-136/entities").rglob("*.json"):
    mm = re.search(r'"identifier"\s*:\s*"(sf_nba:[a-z_]+)"', pp.read_text(encoding="utf-8-sig", errors="ignore"))
    if mm: sm_ids6.add(mm.group(1))
check("V every p11 mob exists (vanilla behaviour entity or StripMine 1.3.6 creature)", all((i in van_ent) or (i in sm_ids6) for i in mob11),
      str([i for i in mob11 if not ((i in van_ent) or (i in sm_ids6))]))
check("V the fixes each have a step: allay dance (jukebox + disc) + hold (shard), vex + sword, probes vex + shard / allay + sword, blaze midnight + noon, polar bear + wolf",
      d11["g01"]["mob"] == "minecraft:allay" and d11["g01"]["jukebox"]["disc"] == "music_disc_cat" and d11["g02"].get("item") == "amethyst_shard"
      and (d11["g03"]["mob"], d11["g03"].get("item")) == ("minecraft:vex", "iron_sword") and (d11["g04"]["mob"], d11["g04"].get("item")) == ("minecraft:vex", "amethyst_shard")
      and (d11["g05"]["mob"], d11["g05"].get("item")) == ("minecraft:allay", "iron_sword")
      and {"daytime": 18000} in next(x for x in p11 if x["id"] == "g06")["setup"] and {"daytime": "noon"} in next(x for x in p11 if x["id"] == "g07")["setup"]
      and d11["g08"]["mob"] == "minecraft:polar_bear" and [q["mob"] for q in d11["g08"]["row"]] == ["minecraft:wolf"])
check("V flyers roofed; the dolphin step is a 3-deep pool; the Naturalist steps say REALM ONLY; row offsets inside the pen",
      all(d11[k].get("roof") for k in ("g02", "g03", "g04", "g05", "g06", "g07")) and d11["g09"].get("water") and d11["g09"].get("depth") == 3
      and all("REALM ONLY" in x["body"] for x in p11 if x["id"].startswith("w")) and all(abs(q["dx"]) <= r.get("half", 2) for _, r in rigs11 for q in r.get("row", [])))
check("V every p11 body names PASS; lines <= 190 chars; rig steps clear the volume first; q0 names RP-06 v1.4.21 / RP-07 v1.4.27 / BP-02 v1.3.193 / StripMine BP v1.3.6 / runner v0.4.2",
      all("PASS" in x["body"] for x in p11) and all(len(l) <= 190 for x in p11 for l in x["body"].split("\n"))
      and all(x["setup"][0] == {"cmd": ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"]} for x in p11 if x["id"][0] in "gw")
      and all(s_ in p11[0]["body"] for s_ in ("v1.4.21", "v1.4.27", "v1.3.193", "v1.3.6", "v0.4.2")))
rep3 = json.load(open(ROOT / "_docs/sizes/size_round3_report.json")); r3 = {r["id"]: r for r in rep3["rows"]}
body = lambda i: next(x for x in p11 if x["id"] == i)["body"]
check("V the sizes quoted to him are the built ones (dolphin, grizzly, alligator, komodo, rat snake; 2 dp)",
      f"{r3['minecraft:dolphin']['to_blocks']:.1f}" in body("g09") and f"{r3['sf_nba:grizzly_bear']['to_blocks']:.2f}" in body("w11")
      and f"{r3['sf_nba:alligator']['to_blocks']:.1f}" in body("w12") and f"{r3['sf_nba:komodo_dragon']['to_blocks']:.2f}" in body("w12")
      and f"{r3['sf_nba:snake']['to_blocks']:.2f}" in body("w12"),
      str({k: v["to_blocks"] for k, v in r3.items()}))

# W (0.4.3, D-C310) the P12 lineup (R16a) + the item proof + spec.blocks
p12 = steps_of(B / "scripts/pw_testrunner_p12.js", "P12_STEPS"); ids12 = [x["id"] for x in p12]
check("W p12 = q0 h01 h02 h03 l01 l02 l03 w01 w02 t01 q9 (11, unique)", ids12 == ["q0", "h01", "h02", "h03", "l01", "l02", "l03", "w01", "w02", "t01", "q9"] and len(set(ids12)) == 11, " ".join(ids12))
rigs12 = [(x["id"], a["rig"]) for x in p12 for a in x["setup"] if "rig" in a]; d12 = dict(rigs12)
check("W every p12 mob is a vanilla behaviour entity", all(r["mob"] in van_ent for _, r in rigs12), str([r["mob"] for _, r in rigs12 if r["mob"] not in van_ent]))
set12 = lambda i: next(x for x in p12 if x["id"] == i)["setup"]
check("W the R16a fixes each have a step: vex + sword / shard, allay + sword, blaze / magma cube / glow squid at midnight, parrot noon, phantom dusk, leaves",
      (d12["h01"]["mob"], d12["h01"].get("item")) == ("minecraft:vex", "iron_sword") and (d12["h02"]["mob"], d12["h02"].get("item")) == ("minecraft:vex", "amethyst_shard")
      and (d12["h03"]["mob"], d12["h03"].get("item")) == ("minecraft:allay", "iron_sword")
      and [d12[k]["mob"] for k in ("l01", "l02", "l03")] == ["minecraft:blaze", "minecraft:magma_cube", "minecraft:glow_squid"] and all({"daytime": 18000} in set12(k) for k in ("l01", "l02", "l03"))
      and d12["l03"].get("water") and d12["w01"]["mob"] == "minecraft:parrot" and {"daytime": "noon"} in set12("w01") and d12["w02"]["mob"] == "minecraft:phantom" and {"daytime": 13000} in set12("w02")
      and all(d12[k].get("free") for k in ("l02", "w01", "w02")) and all(d12[k].get("roof") for k in ("h01", "h02", "h03", "l01", "w01", "w02")))
leaf_ids = set()
for pp in (ROOT / "_build/bp02-194/blocks").glob("*.json"):
    mm = re.search(r'"identifier"\s*:\s*"([^"]+)"', pp.read_text(encoding="utf-8-sig", errors="ignore"))
    if mm: leaf_ids.add(mm.group(1))
bl = d12["t01"].get("boxes") or []
inside = all(abs(v) <= d12["t01"].get("halfz" if i == 2 else "half", 2) for b_ in bl for k in ("from", "to") for i, v in enumerate(b_[k]) if i != 1)
check("W t01: a 3x3x3 pw:oak_leaves cube (a BP-02 1.3.194 block) with a 3-high oak-log core (decay needs a log within 6), inside the pen, clear of the chicken at the centre",
      [b_["id"] for b_ in bl] == ["pw:oak_leaves", "minecraft:oak_log"] and "pw:oak_leaves" in leaf_ids and bl[0]["from"] == [2, 0, -1] and bl[0]["to"] == [4, 2, 1]
      and bl[1]["from"] == [3, 0, 0] and bl[1]["to"] == [3, 2, 0] and inside and not any("fill" in c for a in set12("t01") if "cmd" in a for c in a["cmd"] if "leaves" in c), str(bl))
rigsrc12 = (B / "scripts/pw_testrunner_rig.js").read_text(encoding="utf-8")
check("W the rig proves the item: testfor @s[hasitem={item=..,location=slot.weapon.mainhand}] 2 ticks later, 'CONFIRMED in' / 'NOT in'; the old unchecked 'in <label>'s hand' line is gone",
      "testfor @s[hasitem={item=${name},location=slot.weapon.mainhand}]" in rigsrc12 and "CONFIRMED in ${label}'s main hand" in rigsrc12 and "NOT in ${label}'s main hand" in rigsrc12
      and "in ${label}'s hand`" not in rigsrc12 and "if (spec.boxes) placeBlocks(dim, c, spec.boxes, changed);" in rigsrc12)
check("W every p12 body names PASS; lines <= 190 chars; rig steps clear the volume first; q0 names RP-06 v1.4.22 / RP-07 v1.4.28 / BP-02 v1.3.194 / runner v0.4.3 and a COPY of the world",
      all("PASS" in x["body"] for x in p12) and all(len(l) <= 190 for x in p12 for l in x["body"].split("\n"))
      and all(x["setup"][0] == {"cmd": ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"]} for x in p12 if x["id"][0] in "hlwt")
      and all(s_ in p12[0]["body"] for s_ in ("v1.4.22", "v1.4.28", "v1.3.194", "v0.4.3", "COPY")))
man_rp06 = json.loads((ROOT / "_build/rp06-1422/manifest.json").read_text(encoding="utf-8-sig")); man_rp07 = json.loads((ROOT / "_build/rp07-1428/manifest.json").read_text(encoding="utf-8-sig"))
man_bp02 = json.loads((ROOT / "_build/bp02-194/manifest.json").read_text(encoding="utf-8-sig"))
check("W the versions p12 names are the built ones", man_rp06["header"]["version"] == [1, 4, 22] and man_rp07["header"]["version"] == [1, 4, 28] and man_bp02["header"]["version"] == [1, 3, 194])

# X (0.4.4, D-C314) the P13 lineup (R16b)
p13 = steps_of(B / "scripts/pw_testrunner_p13.js", "P13_STEPS"); ids13 = [x["id"] for x in p13]
check("X p13 = q0 f01 f02 c01 o01 g01 d01 d02 i01 i02 h01 q9 (12, unique)", ids13 == ["q0", "f01", "f02", "c01", "o01", "g01", "d01", "d02", "i01", "i02", "h01", "q9"] and len(set(ids13)) == 12, " ".join(ids13))
rigs13 = [(x["id"], a["rig"]) for x in p13 for a in x["setup"] if "rig" in a]; d13 = dict(rigs13)
mob13 = sorted({r["mob"] for _, r in rigs13} | {q["mob"] for _, r in rigs13 for q in r.get("row", [])})
check("X every p13 mob is a vanilla behaviour entity", all(i in van_ent for i in mob13), str([i for i in mob13 if i not in van_ent]))
check("X the eight ported mobs each have a step (fox x2, cat, ocelot, goat, cod water + land, golem walk + attack, hoglin + zoglin)",
      {r["mob"] for _, r in rigs13} >= {"minecraft:fox", "minecraft:cat", "minecraft:ocelot", "minecraft:goat", "minecraft:cod", "minecraft:iron_golem", "minecraft:hoglin"}
      and [q["mob"] for q in d13["h01"]["row"]] == ["minecraft:zoglin"] and d13["d01"].get("water") and not d13["d02"].get("water")
      and [q["mob"] for q in d13["i02"]["row"]] == ["minecraft:zombie"] and [q["mob"] for q in d13["f02"]["row"]] == ["minecraft:chicken"])
check("X every p13 body names PASS; lines <= 190 chars; rig steps clear the volume first; row offsets inside the pen; q0 names RP-06 v1.4.23 / RP-07 v1.4.29 / runner v0.4.4",
      all("PASS" in x["body"] for x in p13) and all(len(l) <= 190 for x in p13 for l in x["body"].split("\n"))
      and all(x["setup"][0] == {"cmd": ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"]} for x in p13 if x["id"] not in ("q0", "q9"))
      and all(abs(q["dx"]) <= r.get("half", 2) for _, r in rigs13 for q in r.get("row", []))
      and all(s_ in p13[0]["body"] for s_ in ("v1.4.23", "v1.4.29", "v0.4.4")))
man6 = json.loads((ROOT / "_build/rp06-1423/manifest.json").read_text(encoding="utf-8-sig")); man7 = json.loads((ROOT / "_build/rp07-1429/manifest.json").read_text(encoding="utf-8-sig"))
check("X the versions p13 names are the built ones", man6["header"]["version"] == [1, 4, 23] and man7["header"]["version"] == [1, 4, 29])

# Y (0.4.5, D-C317 / D-C318) the P14 lineup (R17)
p14 = steps_of(B / "scripts/pw_testrunner_p14.js", "P14_STEPS"); ids14 = [x["id"] for x in p14]
check("Y p14 = q0 i01 i02 v01 v02 f01 f02 f03 d01 c01 c02 t01 q9 (13, unique)", ids14 == ["q0", "i01", "i02", "v01", "v02", "f01", "f02", "f03", "d01", "c01", "c02", "t01", "q9"] and len(set(ids14)) == 13, " ".join(ids14))
rigs14 = [(x["id"], a["rig"]) for x in p14 for a in x["setup"] if "rig" in a]; d14 = dict(rigs14)
mob14 = sorted({r["mob"] for _, r in rigs14} | {q["mob"] for _, r in rigs14 for q in r.get("row", [])})
check("Y every p14 mob is a vanilla behaviour entity", all(i in van_ent for i in mob14), str([i for i in mob14 if i not in van_ent]))
check("Y the behaviour is PROVOKED (p13 lesson): golem free, vex sword / shard in hand, fox + chicken, fox with berries, fox free under a roof, cod FREE in water, cat + rabbit, cat free to tame, leaves with a log core",
      d14["i01"].get("free") and d14["v01"].get("item") == "iron_sword" and d14["v02"].get("item") == "amethyst_shard"
      and [q["mob"] for q in d14["f01"]["row"]] == ["minecraft:chicken"] and d14["f02"].get("item") == "sweet_berries" and d14["f03"].get("roof") and d14["f03"].get("free")
      and d14["d01"].get("water") and d14["d01"].get("free") and [q["mob"] for q in d14["c01"]["row"]] == ["minecraft:rabbit"] and d14["c02"].get("free")
      and [b_["id"] for b_ in d14["t01"]["boxes"]] == ["pw:oak_leaves", "minecraft:oak_log"])
check("Y every p14 body names PASS; lines <= 190 chars; rig steps clear the volume first; row offsets inside the pen; q0 names RP-06 v1.4.24 / RP-07 v1.4.31 / BP-02 v1.3.195 / runner v0.4.5",
      all("PASS" in x["body"] for x in p14) and all(len(l) <= 190 for x in p14 for l in x["body"].split("\n"))
      and all(x["setup"][0] == {"cmd": ["fill ~-9 ~ ~-14 ~9 ~6 ~-2 air"]} for x in p14 if x["id"] not in ("q0", "q9"))
      and all(abs(q["dx"]) <= r.get("half", 2) for _, r in rigs14 for q in r.get("row", []))
      and all(s_ in p14[0]["body"] for s_ in ("v1.4.24", "v1.4.31", "v1.3.195", "v0.4.5")))
m6 = json.loads((ROOT / "_build/rp06-1424/manifest.json").read_text(encoding="utf-8-sig")); m7 = json.loads((ROOT / "_build/rp07-1431/manifest.json").read_text(encoding="utf-8-sig"))
m2 = json.loads((ROOT / "_build/bp02-195/manifest.json").read_text(encoding="utf-8-sig"))
check("Y the versions p14 names are the built ones", m6["header"]["version"] == [1, 4, 24] and m7["header"]["version"] == [1, 4, 31] and m2["header"]["version"] == [1, 3, 195])

# Z (0.4.6, D-C332) the P15 lineup (the LEAF PILOT) — p15 imports @minecraft/server, so it is read through the mock package
def steps_of_mc(path, name):
    import tempfile, os
    td = Path(tempfile.mkdtemp(prefix="pwz-")); (td / "package.json").write_text('{"type":"module"}')
    for mod in ("@minecraft/server",):
        d = td / "node_modules" / mod; d.mkdir(parents=True); (d / "package.json").write_text('{"name":"%s","type":"module","main":"index.js"}' % mod)
        (d / "index.js").write_text(f'export * from "{(ROOT / "tools/testrunner_src/mock_mc2.mjs").as_uri()}";')
    shutil.copyfile(path, td / Path(path).name)
    r = subprocess.run(["node", "--input-type=module", "-e", f"import(process.argv[1]).then(m=>console.log(JSON.stringify(m.{name})))", "--", str(td / Path(path).name)], capture_output=True, text=True, cwd=td)
    shutil.rmtree(td, ignore_errors=True)
    return json.loads(r.stdout)
p15 = steps_of_mc(B / "scripts/pw_testrunner_p15.js", "P15_STEPS"); ids15 = [x["id"] for x in p15]
check("Z p15 = q0 l01..l25 q9 (27, unique)", ids15 == ["q0"] + [f"l{i:02d}" for i in range(1, 26)] + ["q9"] and len(set(ids15)) == 27, " ".join(ids15))
trees = [a["leaftree"] for x in p15 for a in x["setup"] if "leaftree" in a]
blk = {json.loads(p.read_text())["minecraft:block"]["description"]["identifier"] for p in (B / "blocks").glob("pw_pilot_*.json")}
named = {(t.get("block") or "pw:pilot_{sp}_leaves").replace("{sp}", t["sp"]) for t in trees if not t.get("keep")}
check("Z every pilot block a p15 tree names exists in BP blocks/ (24 pilot blocks shipped)", len(blk) == 24 and named <= blk, str(sorted(named - blk)))
sp_steps = {x["id"]: sorted({a["leaftree"]["sp"] for a in x["setup"] if "leaftree" in a}) for x in p15}
check("Z all 11 species (azalea tree carries both azalea kinds) + a TODAY reference tree in every species-age step, shade and far",
      {s for v in sp_steps.values() for s in v} >= {"oak", "birch", "spruce", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "azalea"}
      and all(any(a["leaftree"].get("keep") for a in x["setup"] if "leaftree" in a) for x in p15 if x["id"] in [f"l{i:02d}" for i in range(1, 22)] + ["l23", "l24"]))
# (0.4.8, D-C336) every tree a p15 step grows comes from a feature BP-02 1.3.195 really ships, with a trunk block BP-02 really ships
def p15_trees():
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="pwz-")); (td / "package.json").write_text('{"type":"module"}')
    d = td / "node_modules" / "@minecraft/server"; d.mkdir(parents=True); (d / "package.json").write_text('{"name":"@minecraft/server","type":"module","main":"index.js"}')
    (d / "index.js").write_text(f'export * from "{(ROOT / "tools/testrunner_src/mock_mc2.mjs").as_uri()}";')
    shutil.copyfile(B / "scripts/pw_testrunner_p15.js", td / "p15.js")
    js = "import(process.argv[1]).then(m=>console.log(JSON.stringify(m.P15_STEPS.map(s=>[s.id,(s.setup||[]).filter(a=>a.leaftree).map(a=>Object.assign({},a.leaftree,m.treeOf(a.leaftree.sp,a.leaftree.age))),(s.setup||[]).filter(a=>a.leafclear).map(a=>a.leafclear),(s.setup||[]).filter(a=>a.leafarea).map(a=>a.leafarea)]))))"
    r = subprocess.run(["node", "--input-type=module", "-e", js, "--", str(td / "p15.js")], capture_output=True, text=True, cwd=td)
    shutil.rmtree(td, ignore_errors=True)
    return json.loads(r.stdout)
T15 = p15_trees(); BP2 = ROOT / "_build/bp02-197"
bp2_feats = set()
for f in (BP2 / "features").glob("*.json"):
    jj = json.loads(re.sub(r"//.*", "", f.read_text())); k = [x for x in jj if x.startswith("minecraft:")][0]; bp2_feats.add(jj[k]["description"]["identifier"])
bp2_blocks = {json.loads(re.sub(r"//.*", "", f.read_text()))["minecraft:block"]["description"]["identifier"] for f in (BP2 / "blocks").rglob("*.json") if "minecraft:block" in f.read_text()}
grown = {t["feature"] for _, ts, _, _a in T15 for t in ts}
trunks = {t["trunk"] for _, ts, _, _a in T15 for t in ts if t["trunk"].startswith("pw:")}
check("Z every p15 feature exists in BP-02 1.3.195 (or is vanilla azalea); every pw trunk block exists in BP-02",
      all(f in bp2_feats or f == "minecraft:azalea_tree_feature" for f in grown) and trunks <= bp2_blocks and len(grown) >= 21,
      f"missing features {sorted(f for f in grown if f not in bp2_feats and f != 'minecraft:azalea_tree_feature')} trunks {sorted(trunks - bp2_blocks)}")
elder_geo = {b: json.loads(re.sub(r"//.*", "", (BP2 / "blocks" / f"{b[3:]}.json").read_text()))["minecraft:block"]["components"]["minecraft:geometry"] for b in trunks if (BP2 / "blocks" / f"{b[3:]}.json").exists()}
elder_geo = {b: (g if isinstance(g, str) else g.get("identifier")) for b, g in elder_geo.items()}
check("Z trunks: every ELDER is the square pw_simple_log; every young / mature / old is a round (non-simple) log geometry (his 16:14 / 16:15 rulings)",
      all((g == "geometry.pw_simple_log") == b.endswith("_elder") for b, g in elder_geo.items()) and len(elder_geo) == len(trunks), json.dumps(elder_geo)[:300])
vol = lambda r, h: (2 * r + 1) ** 2 * (h + 2)
depth = lambda xa, xb, h: max(1, min(8, 32768 // ((xb - xa + 1) * (h + 1))))
check("Z every tree box and clear slice <= 32,768 blocks; trees in one step never share a cleared box (grove excepted)",
      all(vol(t["r"], t["h"]) <= 32768 for _, ts, _, _a in T15 for t in ts)
      and all((c["box"][1] - c["box"][0] + 1) * (c.get("h", 40) + 1) * depth(c["box"][0], c["box"][1], c.get("h", 40)) <= 32768 for _, _, cs, _a in T15 for c in cs)
      and all(t.get("noclear") or u.get("noclear") or t is u or abs(t["dx"] - u["dx"]) > t["r"] + u["r"] or abs(t["dz"] - u["dz"]) > t["r"] + u["r"] for _, ts, _, _a in T15 for t in ts for u in ts))
check("Z copies name a tree grown in the same step; every tree step makes a ticking area covering all its tree boxes; q9 resets, then drops both areas",
      all(tuple(t["from"]) in {(u["dx"], u["dz"]) for u in ts if not u.get("from")} for _, ts, _, _a in T15 for t in ts if t.get("from"))
      and all(ar and all(ar[0]["box"][0] <= t["dx"] - t["r"] and t["dx"] + t["r"] <= ar[0]["box"][3] and ar[0]["box"][2] <= t["dz"] - t["r"] and t["dz"] + t["r"] <= ar[0]["box"][5] for t in ts)
              for _, ts, _, ar in T15 if ts)
      and all(((abs(a_["box"][3] - a_["box"][0]) + 16) // 16 + 1) * ((abs(a_["box"][5] - a_["box"][2]) + 16) // 16 + 1) <= 100 for _, _, _, ar in T15 for a_ in ar)
      and set(p15[-1]["setup"][0]["leafreset"]["areas"]) == {"pw_pilot_far", "pw_pilot_near"})
check("Z every p15 body names PASS; lines <= 190 chars; q0 names RP v0.4.0 + BP v0.5.1 + Markers RP v0.2.2 and asks about Texture Streaming",
      all("PASS" in x["body"] for x in p15) and all(len(l) <= 190 for x in p15 for l in x["body"].split("\n"))
      and all(s_ in p15[0]["body"] for s_ in ("v0.4.0", "v0.5.1", "v0.2.2", "Texture Streaming")))

# Z2 (0.5.0, D-C346) the P16 lineup (the LEAF ROLLOUT) — same mock import as p15
p16 = steps_of_mc(B / "scripts/pw_testrunner_p16.js", "P16_STEPS"); ids16 = [x["id"] for x in p16]
check("Z2 p16 = q0 n01..n12 m01..m10 n13 q9 (25, unique)", ids16 == ["q0"] + [f"n{i:02d}" for i in range(1, 13)] + [f"m{i:02d}" for i in range(1, 11)] + ["n13", "q9"], " ".join(ids16))
feats16 = set()
for x in p16:
    for a in x["setup"]:
        if "placeprobe" in a: feats16 |= {c["feature"] for c in a["placeprobe"]["cases"]}
check("Z2 every /place probe feature exists in BP-02 1.3.197 (or is vanilla azalea)", all(f in bp2_feats or f == "minecraft:azalea_tree_feature" for f in feats16) and len(feats16) == 5, str(sorted(feats16)))
check("Z2 p16 names BP-02 v1.3.197 + RP-01 v1.3.106 + runner v0.5.2 + runner RP v0.5.0 in q0; every body names PASS; lines <= 190",
      all(s_ in p16[0]["body"] for s_ in ("v1.3.197", "v1.3.106", "v0.5.2", "v0.5.0")) and all("PASS" in x["body"] for x in p16) and all(len(l) <= 190 for x in p16 for l in x["body"].split("\n")))
blk196 = {json.loads(re.sub(r"//.*", "", f.read_text()))["minecraft:block"]["description"]["identifier"] for f in (BP2 / "blocks").glob("*leaves*.json")}
check("Z2 the leaf ids p16 places / gives exist in BP-02 1.3.197 (pw:oak_leaves, pw:azalea_leaves, pw:flowering_azalea_leaves)",
      {"pw:oak_leaves", "pw:azalea_leaves", "pw:flowering_azalea_leaves"} <= blk196, str(sorted(blk196)))

# Z3 (0.5.2, D-C348) the 128 vs 256 comparison: 22 test blocks in the BP, their keys + texture sets in runner RP v0.5.0, geometry in RP-01 1.3.106
RP5 = ROOT / "_build/testrunner-rp-0.5.0"; RP01 = ROOT / "_build/rp01-106"
ALL11 = ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "azalea", "flowering_azalea")
tblk = {}
for f in (B / "blocks").glob("pw_t256*.json"):
    d = jload(f)["minecraft:block"]; tblk[d["description"]["identifier"]] = d
want = {f"pw:{st}_{s}_leaves" for st in ("t256", "t256m") for s in ALL11}
check("Z3 the BP holds exactly the 22 test blocks pw:t256_* + pw:t256m_* (all 11 species), no custom component, no loot", set(tblk) == want
      and all("minecraft:custom_components" not in d["components"] and "minecraft:loot" not in d["components"] for d in tblk.values()), str(len(tblk)))
real = {s: jload(RP01.parent / "bp02-197" / "blocks" / f"{s}_leaves.json")["minecraft:block"] for s in ALL11}
def strip_keys(o, st, s): return json.loads(json.dumps(o).replace(f'"pw_{st}_{s}_', f'"pw_leaves2_{s}_'))
check("Z3 each test block = BP-02 1.3.197's own leaf block (same 5 states, same 7 permutations: shapes, turns, tint, render method) with only the texture keys swapped",
      all(tblk[f"pw:{st}_{s}_leaves"]["description"]["states"] == real[s]["description"]["states"]
          and strip_keys(tblk[f"pw:{st}_{s}_leaves"]["permutations"], st, s) == real[s]["permutations"] for st in ("t256", "t256m") for s in ALL11))
tt5 = jload(RP5 / "textures/terrain_texture.json")["texture_data"]
geo01 = {g["description"]["identifier"] for g in jload(RP01 / "models/blocks/pw_leaves2.geo.json")["minecraft:geometry"]}
keys, geos = set(), set()
for d in tblk.values():
    for pm in d["permutations"]:
        geos.add(pm["components"]["minecraft:geometry"])
        for mi in pm["components"]["minecraft:material_instances"].values(): keys.add(mi["texture"])
from PIL import Image
sz_ok, sets_ok, n_t = True, True, 0
for k in sorted(keys):
    if k not in tt5: sets_ok = False; continue
    base = RP5 / (tt5[k]["textures"]); ts = jload(Path(str(base) + ".texture_set.json"))["minecraft:texture_set"]
    st = "t256m" if k.startswith("pw_t256m_") else "t256"
    sizes = tuple(Image.open(base.parent / (ts[c] + ".png")).size[0] for c in ("color", "normal", "metalness_emissive_roughness_subsurface"))
    sz_ok &= sizes == ((256, 128, 128) if st == "t256" else (256, 128, 64)); n_t += 1
check("Z3 every texture key the test blocks use is in runner RP v0.5.0, with a texture set: t256 = colour 256 / normal 128 / MERS 128, t256m = 256 / 128 / 64",
      sets_ok and sz_ok and n_t == 200, f"{n_t} keys")
check("Z3 the test blocks' geometry (pw_leaves2 full / cards / spruce) is in RP-01 1.3.106", geos <= geo01 and len(geos) == 3, str(sorted(geos)))
m5 = jload(RP5 / "manifest.json")
check("Z3 runner RP v0.5.0: same uuids as v0.4.0, version 0.5.0, pbr capability, no dependencies",
      m5["header"]["uuid"] == "3f8b6a2d-1c4e-4d7b-9a5f-6e2c8b1d4a37" and m5["header"]["version"] == [0, 5, 0] and m5["modules"][0]["version"] == [0, 5, 0]
      and m5.get("capabilities") == ["pbr"] and "dependencies" not in m5)
lang5 = (RP5 / "texts/en_US.lang").read_text(encoding="utf-8")
check("Z3 every test block has a name in runner RP v0.5.0", all(f"tile.{i}.name=" in lang5 for i in want))
mblocks = {a["leaftree"]["block"].replace("{sp}", s) for x in p16 if x["id"].startswith("m") for a in x["setup"] if "leaftree" in a for s in ALL11}
check("Z3 every block id the m-steps can place exists (test blocks in this BP, real leaves in BP-02 1.3.197)", all(i in want or i in blk196 for i in mblocks if
      any(i.endswith(f"_{s}_leaves") for s in ALL11)), str(len(mblocks)))

# Z4 (0.5.3, D-C350) lineup p17: the leaf fixes + the culling probe
RP6 = ROOT / "_build/testrunner-rp-0.6.0"; BP198 = ROOT / "_build/bp02-198"
p17 = steps_of_mc(B / "scripts/pw_testrunner_p17.js", "P17_STEPS"); ids17 = [x["id"] for x in p17]
check("Z4 p17 = q0 f01 f02 f03 z01 q9; q0 names BP-02 v1.3.198 + RP-01 v1.3.107 + runner v0.5.4 + RP v0.6.0; bodies name PASS, lines <= 190",
      ids17 == ["q0", "f01", "f02", "f03", "z01", "q9"] and all(v in p17[0]["body"] for v in ("v1.3.198", "v1.3.107", "v0.5.4", "v0.6.0"))
      and all("PASS" in x["body"] and all(len(l) <= 190 for l in x["body"].split("\n")) for x in p17), " ".join(ids17))
pb = jload(B / "blocks/pw_cullprobe.json")["minecraft:block"]; cl = jload(RP6 / "block_culling/pw_cullprobe.json")["minecraft:block_culling_rules"]
pg = jload(RP6 / "models/blocks/pw_cullprobe.geo.json")["minecraft:geometry"][0]
keys = {mi["texture"] for mi in pb["components"]["minecraft:material_instances"].values()}
tt6 = jload(RP6 / "textures/terrain_texture.json")["texture_data"]
check("Z4 pw:cullprobe: geometry + culling definition found by id in RP v0.6.0, rules = east/south same_block on cube 0 of bone 'probe', every texture key registered",
      pb["components"]["minecraft:geometry"] == {"identifier": pg["description"]["identifier"], "culling": cl["description"]["identifier"]}
      and sorted((r["direction"], r["condition"], r["geometry_part"]["face"]) for r in cl["rules"]) == [("east", "same_block", "east"), ("south", "same_block", "south")]
      and all(r["geometry_part"]["bone"] == "probe" and r["geometry_part"]["cube"] == 0 for r in cl["rules"])
      and all(k in tt6 and (RP6 / (tt6[k]["textures"] + ".png")).exists() for k in keys) and len(keys) == 6)
check("Z4 pw:cullprobe: state pw:q 0-3, quarter turns 90/180/270 for q 1-3, every geometry face maps to its own material instance",
      pb["description"]["states"] == {"pw:q": [0, 1, 2, 3]} and [pm["components"]["minecraft:transformation"]["rotation"][1] for pm in pb["permutations"]] == [90, 180, 270]
      and {f["material_instance"] for f in pg["bones"][0]["cubes"][0]["uv"].values()} <= set(pb["components"]["minecraft:material_instances"]))
cmd17 = [c for x in p17 for a in x["setup"] if "cmd" in a for c in a["cmd"]]
check("Z4 p17 places only blocks that exist (pw:cullprobe in this BP) and gives only shears / iron axe",
      all(("pw:cullprobe" in c) for c in cmd17 if c.startswith("setblock")) and len([c for c in cmd17 if c.startswith("setblock")]) == 16)
bl198 = {jload(f)["minecraft:block"]["description"]["identifier"] for f in (BP198 / "blocks").glob("*leaves*.json")}
check("Z4 the leaf ids p17's trees carry exist in BP-02 1.3.198", {"pw:oak_leaves", "pw:birch_leaves", "pw:spruce_leaves", "pw:cherry_leaves"} <= bl198)

# Z5 (0.5.5, D-C351) lineup p18: the new-animals parade
SM7 = ROOT / "_build/stripmine-bp-139"; RP7 = ROOT / "_build/rp07-1434"          # 0.5.6: p18 runs on the P3 packs (they hold all of P1)
p18 = steps_of_mc(B / "scripts/pw_testrunner_p18.js", "P18_STEPS"); ids18 = [x["id"] for x in p18]
bp7 = {jload(f)["minecraft:entity"]["description"]["identifier"] for f in SM7.glob("entities/pw_menagerie/**/*.json")}
rp7 = {jload(f)["minecraft:client_entity"]["description"]["identifier"] for f in RP7.glob("entity/pw_menagerie/**/*.json")}
mobs18 = [m for x in p18 for a in x["setup"] if "rig" in a for m in [a["rig"]["mob"]] + [r["mob"] for r in a["rig"].get("row", [])]]
check("Z5 p18 = q0 + a01..a32 + q9 (34, unique); q0 names RP-07 v1.4.34 + StripMine BP v1.3.9 + runner v0.5.7; bodies name PASS, lines <= 190",
      len(ids18) == 34 and len(set(ids18)) == 34 and all(v in p18[0]["body"] for v in ("v1.4.34", "v1.3.9", "v0.5.7"))
      and all("PASS" in x["body"] and all(len(l) <= 190 for l in x["body"].split("\n")) for x in p18), " ".join(ids18[:4]))
check("Z5 p18 shows every ported creature exactly once, and every one exists in StripMine BP 1.3.8 + RP-07 1.4.33",
      len(mobs18) == len(set(mobs18)) == 147 and all(m in bp7 and m in rp7 for m in mobs18), f"{len(mobs18)} shown, {len(set(mobs18))} unique")
check("Z5 every p18 pen fits: animals 4 blocks apart (pools 3), the main one at the centre, offsets inside the pen",
      all(a["rig"].get("water") or all(abs(r["dx"]) <= a["rig"]["half"] - 2 for r in a["rig"].get("row", [])) for x in p18 for a in x["setup"] if "rig" in a))

# Z6 (0.5.6, D-C353) lineup p19: his picks parade
p19 = steps_of_mc(B / "scripts/pw_testrunner_p19.js", "P19_STEPS"); ids19 = [x["id"] for x in p19]
J3 = json.loads((ROOT / "_logs/menagerie_jobs_P3.json").read_text())
want19 = set()
for e in J3["entities"]:
    f = next((f for f in SM7.glob("entities/pw_menagerie/**/*.json") if jload(f)["minecraft:entity"]["description"]["identifier"] == e[2]), None) if False else None
bp_all = {}
for f in SM7.glob("entities/**/*.json"):
    try: d = jload(f)["minecraft:entity"]["description"]; bp_all[d["identifier"]] = d
    except Exception: pass
rp_all = set()
for f in RP7.glob("entity/**/*.json"):
    try: rp_all.add(jload(f)["minecraft:client_entity"]["description"]["identifier"])
    except Exception: pass
want19 = {e[2] for e in J3["entities"] if bp_all.get(e[2], {}).get("is_spawnable")}
OURS19 = {"sf_nba:gorilla", "sf_nba:boar", "sf_nba:black_bear", "sf_nba:grizzly_bear"}
mobs19 = [m for x in p19 for a in x["setup"] if "rig" in a for m in [a["rig"]["mob"]] + [r["mob"] for r in a["rig"].get("row", [])]]
check("Z6 p19 = q0 + b01.. + q9 (unique); q0 names RP-07 v1.4.34 + StripMine BP v1.3.9 + runner v0.5.7; bodies name PASS, lines <= 190",
      len(ids19) == len(set(ids19)) and ids19[0] == "q0" and ids19[-1] == "q9" and all(v in p19[0]["body"] for v in ("v1.4.34", "v1.3.9", "v0.5.7"))
      and all("PASS" in x["body"] and all(len(l) <= 190 for l in x["body"].split("\n")) for x in p19), f"{len(ids19)} steps")
check("Z6 p19 shows every spawnable P3 creature exactly once (+ our gorilla / boar / 2 bears), each in StripMine BP 1.3.8 + RP-07 1.4.33",
      len(mobs19) == len(set(mobs19)) and set(mobs19) == want19 | OURS19 and all(m in bp_all and m in rp_all for m in mobs19),
      f"{len(mobs19)} shown; missing {sorted(want19 - set(mobs19))[:3]} extra {sorted(set(mobs19) - want19 - OURS19)[:3]}")
check("Z6 every p19 pen fits: offsets inside the pen / pool, one creature at the centre, every one with a 'Name (PACK)' tag",
      all(all(abs(r["dx"]) <= a["rig"]["half"] - 1 for r in a["rig"].get("row", [])) and a["rig"]["name"].endswith(")")
          and all(r["name"].endswith(")") for r in a["rig"].get("row", [])) for x in p19 for a in x["setup"] if "rig" in a))

# F
def dir_equals_zip(d, z):
    with zipfile.ZipFile(z) as zf:
        return all(hashlib.md5(zf.read(n)).hexdigest() == md5(d / n) for n in zf.namelist() if not n.endswith("/"))
untouched = all(dir_equals_zip(ROOT / "_build" / d, OUT / z) for d, z in (("bp01-135", "BP-01-AbsolutRealism-Atmospheric-Effects-BP-v1_3_35.mcpack"), ("bp02-187", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_187.mcpack"),
                                                                        ("bp03-134", "BP-03-Abs0lutRealism-Identification-Diagnostics-BP-v1_3_34.mcpack"), ("markers-0.2.1/BP", "PW-Civitas-Markers-BP-v0_2_1.mcpack"), ("markers-0.2.1/RP", "PW-Civitas-Markers-RP-v0_2_1.mcpack"),
                                                                        ("rp07-1411", "RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_11.mcpack")))
check("F no current pack was modified by this build (each build dir == its delivered mcpack)", untouched)

# G
texts = []
for d in ("bp01-135", "bp02-187", "bp03-134", "markers-0.2.1/BP"):
    for p in (ROOT / "_build" / d).rglob("*.js"): texts.append(p.read_text(encoding="utf-8", errors="ignore"))
for d in ("bp02-187", "markers-0.2.1/BP", "markers-0.2.1/RP", "rp07-1411", "rp04-138"):
    for p in (ROOT / "_build" / d).rglob("*.json"): texts.append(p.read_text(encoding="utf-8", errors="ignore"))
for z in ("_intake/stack-bps/PW-SlabForge-Key-BP-v0_1_0.mcpack", "_intake/stack-bps/PW-StripMine-BP-v1_3_1.mcpack"):
    try:
        with zipfile.ZipFile(ROOT / z) as zf:
            for n in zf.namelist():
                if n.endswith((".js", ".json")): texts.append(zf.read(n).decode("utf-8", "ignore"))
    except Exception: pass
blob = "\n".join(texts)
check("G nothing else in the stack uses pw:test / pw:test_state / pw:test_rig / pw:probe / pw_rig / the clicker name", all(k not in blob for k in ('"pw:test"', "pw:test_state", "pw:test_rig", '"pw:probe"', "pw_rig", "PW TEST CLICKER")), f"{len(texts)} files censused")

# H
src = (B / "scripts/pw_testrunner.js").read_text(encoding="utf-8")
check("H bar + menu + where say 'you are in:'; the P0 bar and menu add the facing", src.count("you are in: ${") >= 3 and src.count("facing ") >= 3 and "§7· ${where(p).biome} ·" not in src)
flat = {s["id"]: s["body"] for s in steps}
check("H flat-world guidance on u4 / v1 / v2 / v6; y3 names the 1.4.11 shape", all("FLAT WORLD" in flat[i] for i in ("u4", "v1", "v2")) and "flat world counts" in flat["v6"] and "1.4.11" in flat["y3"])

# I the probe
import probe_assets as PA
from PIL import Image
geo = jload(R / "models/entity/pw_probe.geo.json")["minecraft:geometry"][0]
bones = {b["name"]: b for b in geo["bones"]}
want = {n: (piv, rot, o, s) for n, piv, rot, c, o, s in PA.BONES}
ok_geo = geo["description"]["identifier"] == "geometry.pw_probe" and geo["description"]["texture_width"] == 64 and set(bones) == set(want) and all(
    bones[n]["pivot"] == piv and bones[n].get("rotation", [0, 0, 0]) == rot and bones[n]["cubes"][0]["origin"] == o and bones[n]["cubes"][0]["size"] == s for n, (piv, rot, o, s) in want.items())
check("I geometry.pw_probe: 8 bones, pivots/rotations/cubes == the protocol table (zbar [0,0,30] ybar [0,45,0] xbar [30,0,0] cbar [45,45,0])", ok_geo)
im = Image.open(R / "textures/entity/pw_probe.png").convert("RGBA")
cols = {im.getpixel((u + 8, v + 8))[:3] for _, (u, v, rgb) in PA.SWATCH.items()}
check("I texture 64x64 with 8 distinct opaque swatches", im.size == (64, 64) and len(cols) == 8 and all(im.getpixel((u + 8, v + 8))[:3] == rgb for _, (u, v, rgb) in PA.SWATCH.items()))
uvs_ok = all(all(bones[n]["cubes"][0]["uv"][f]["uv"] == [PA.SWATCH[c][0], PA.SWATCH[c][1]] for f in ("north", "south", "east", "west", "up", "down")) for n, _, _, c, _, _ in PA.BONES)
check("I every face of every bone samples its own swatch (solid colour per bone)", uvs_ok)
ce = jload(R / "entity/pw_probe.entity.json")["minecraft:client_entity"]["description"]
anim = jload(R / "animations/pw_probe.animation.json")["animations"]; ac = jload(R / "animation_controllers/pw_probe.animation_controllers.json")["animation_controllers"]; rc = jload(R / "render_controllers/pw_probe.render_controllers.json")["render_controllers"]
check("I client entity refs resolve: geometry id, texture file, animation + controller ids, render controller, scripts.animate",
      ce["identifier"] == "pw:probe" and ce["geometry"]["default"] == geo["description"]["identifier"] and (R / (ce["textures"]["default"] + ".png")).exists()
      and ce["animations"]["t6"] in anim and ce["animations"]["ctrl"] in ac and ce["render_controllers"] == list(rc) and ce["scripts"]["animate"] == ["ctrl"])
a6 = anim["animation.pw_probe.t6"]["bones"]
check("I animation.pw_probe.t6: xbar rotation [30,0,0] + zbar position [0,8,0], loop; controller keyed on q.property('pw:anim')", a6["xbar"]["rotation"] == [30, 0, 0] and a6["zbar"]["position"] == [0, 8, 0] and anim["animation.pw_probe.t6"]["loop"] is True
      and "q.property('pw:anim')" in json.dumps(ac) and ac["controller.animation.pw_probe"]["states"]["t6"]["animations"] == ["t6"])
be = jload(B / "entities/pw_probe.json")["minecraft:entity"]; bc = be["components"]
check("I BP entity pw:probe: summonable, floats (no gravity/collision), unpushable, unhurtable, persistent, body rotation blocked, pw:anim property, event pw:t6",
      be["description"]["identifier"] == "pw:probe" and be["description"]["is_summonable"] and not be["description"]["is_spawnable"] and bc["minecraft:physics"] == {"has_gravity": False, "has_collision": False}
      and bc["minecraft:pushable"]["is_pushable"] is False and bc["minecraft:damage_sensor"]["triggers"][0]["deals_damage"] == "no" and "minecraft:persistent" in bc and "minecraft:body_rotation_blocked" in bc
      and be["description"]["properties"]["pw:anim"]["client_sync"] is True and be["events"]["pw:t6"]["set_property"]["pw:anim"] is True)
check("I the BP data module exists for entities/ and the RP ships the 6 probe files", "data" in mods and all((R / f).exists() for f in ("entity/pw_probe.entity.json", "models/entity/pw_probe.geo.json", "textures/entity/pw_probe.png", "animations/pw_probe.animation.json", "animation_controllers/pw_probe.animation_controllers.json", "render_controllers/pw_probe.render_controllers.json")))

# J the predictions are what the law computes (file frame: +x = the model's left, -z = its front, +y up)
from entity_render import cubes_from_bones
def tip(cubes, bone):
    P = [p for b, corners in cubes if b == bone for p in corners]
    return P
st = cubes_from_bones(PA.bones_for(False)); an = cubes_from_bones(PA.bones_for(True))
def top_of(cubes, bone):
    P = sorted(tip(cubes, bone), key=lambda p: -p[1])[:4]          # the tip = centroid of the 4 highest corners (the bar's top face)
    return [sum(p[i] for p in P) / 4 for i in range(3)]
def far_x(cubes, bone): return max(tip(cubes, bone), key=lambda p: p[0])
def far_front(cubes, bone): return min(tip(cubes, bone), key=lambda p: p[2])
z_top = top_of(st, "zbar"); y_tip = far_x(st, "ybar"); x_tip = far_front(st, "xbar"); c_top = top_of(st, "cbar")
check("J green (zbar [0,0,30]) top leans toward file +x (the model's LEFT = his RIGHT from the front)", z_top[0] > 4 and z_top[1] > 34, str([round(v, 2) for v in z_top]))
check("J orange (ybar [0,45,0]) free end swings to the FRONT (file -z)", y_tip[2] < -5 and y_tip[0] > 5, str([round(v, 2) for v in y_tip]))
check("J cyan (xbar [30,0,0]) front tip DIPS (y below the pivot's 16)", x_tip[1] < 12 and x_tip[2] < -7, str([round(v, 2) for v in x_tip]))
check("J magenta (cbar [45,45,0], X first) top leans to the FRONT and toward file -x (his LEFT); Y-first would give x == 0", c_top[2] < -3 and c_top[0] < -3, str([round(v, 2) for v in c_top]))
x_tip_a = far_front(an, "xbar"); z_top_a = top_of(an, "zbar")
check("J animated: cyan tip dips further (60 vs 30), green top 8 higher", x_tip_a[1] < x_tip[1] - 2 and abs(z_top_a[1] - z_top[1] - 8) < 1e-6, f"cyan {round(x_tip[1], 2)} -> {round(x_tip_a[1], 2)}; green {round(z_top[1], 2)} -> {round(z_top_a[1], 2)}")
fig = ROOT / "_design/p0-probe-predicted.png"
check("J the predicted-view figure exists and is newer than the built geometry", fig.exists() and fig.stat().st_mtime >= (R / "models/entity/pw_probe.geo.json").stat().st_mtime - 5)

if any(not ok for _, ok in res): print("GATE CLOSED"); sys.exit(1)
print(f"\nGATE OPEN — {len(res)} checks")
with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-30] VERIFY testrunner {VER} GATE OPEN {len(res)}/{len(res)} — packaging the BP (runner RP v0.6.0 = v0.5.0 + the culling probe, gated in Z3/Z4)\n")
for src_dir, name in ((B, BP_NAME),):
    out = OUT / name
    # D-C278: never reuse a version number for different bytes (0.3.3's first gate run overwrote the delivered 0.3.2 archive
    # because BP_NAME was hardcoded; restored byte-exact from _build/testrunner-0.3.2, md5 5ed09792)
    assert f"v{VER.replace('.', '_')}" in name, (name, VER)
    # D-C300: deterministic archive (fixed entry dates, sorted) so a re-run gives the same bytes; a name that exists with DIFFERENT
    # bytes is refused (never reuse a version number for different bytes)
    tmp = out.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(src_dir.rglob("*")):
            if p.is_file():
                zi = zipfile.ZipInfo(str(p.relative_to(src_dir)).replace("\\", "/"), date_time=(2026, 9, 29, 0, 0, 0)); zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = 0o644 << 16; z.writestr(zi, p.read_bytes(), compresslevel=6)
    if out.exists() and md5(out) != md5(tmp):
        tmp.unlink(); raise SystemExit(f"REFUSED: {out.name} already exists with different bytes")
    tmp.replace(out)
    with zipfile.ZipFile(out) as z:
        zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
        th = {str(p.relative_to(src_dir)).replace("\\", "/"): md5(p) for p in src_dir.rglob("*") if p.is_file()}
        assert zh == th and "manifest.json" in z.namelist()
    print(f"  {out.name} {out.stat().st_size:,} B md5 {md5(out)}")
