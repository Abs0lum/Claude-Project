"""arm_gap2.py — sequential-tick version (the JEM smooths dance / hold weights per tick). For each arm and tick: the arm
cube's TOP-CENTRE (the shoulder end, world) -> its distance to the body cube (oriented box; 0 = touching / inside).
Shipped (arms = Bedrock roots) vs Java tree (arms nested under body)."""
import sys, copy, json
sys.path.insert(0, "/home/claude/tools")
from pathlib import Path
import numpy as np
import convb_round as R
import molang_eval as ME
import posed_preview as PP
from equine_compare import bone_affines

def obb_dist(p, corners):
    B = np.array(corners); o = B[0]; ex, ey, ez = B[4] - o, B[2] - o, B[1] - o
    M = np.stack([ex, ey, ez], 1); q = np.linalg.solve(M, p - o)       # box-local 0..1 coords
    qc = np.clip(q, 0, 1); return float(np.linalg.norm(M @ (q - qc)))

def cube_corners(A, t, c):
    o, s = np.array(c["origin"], float), np.array(c["size"], float)
    return [A @ np.array([x, y, z]) + t for x in (o[0], o[0] + s[0]) for y in (o[1], o[1] + s[1]) for z in (o[2], o[2] + s[2])]

def sim(dst, stem, gid, env_state, nest, ticks=160, warm=60, arms=("right_arm", "left_arm"), body="body"):
    ent = R.jl(dst / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
    env = {"q.delta_time": 0.05, "q.is_on_ground": 0.0, "q.is_alive": 1.0, "q.modified_move_speed": 0.0,
           "q.target_x_rotation": 0.0, "q.target_y_rotation": 0.0, "q.hurt_time": 0.0, "q.death_ticks": 0.0,
           "q.modified_distance_moved": 0.0, "q.position(1)": 173.0, "q.is_riding": 0.0, "q.is_dancing": 0.0,
           "q.is_charging": 0.0, "q.is_item_equipped(0)": 0.0, "q.is_item_equipped(1)": 0.0, "q.life_time": 0.0, **env_state}
    for s in ent["scripts"].get("initialize", []): ME.run(s, env)
    lib = {}
    for f in (dst / "animations").glob("*.json"): lib.update(R.jl(f).get("animations", {}))
    _, g = R.geo_file(dst, gid)
    a = lib[ent["animations"]["pw_jem"]]
    worst = {k: (0.0, 0) for k in arms}; shoulder = {k: 0.0 for k in arms}
    for n in range(ticks):
        env["q.life_time"] = n * 0.05
        if "q.modified_move_speed" in env_state: env["q.modified_distance_moved"] = n * 0.05 * 4.0 * env_state["q.modified_move_speed"]
        for s in ent["scripts"].get("pre_animation", []):
            if "'" in s: continue
            ME.run(s, env)
        if n < warm: continue
        bones = copy.deepcopy(g["bones"])
        if nest:
            for b in bones:
                if b["name"] in arms: b["parent"] = body
        posed = PP.posed_bones(bones, a["bones"], dict(env)); aff = bone_affines(posed); by = {b["name"]: b for b in posed}
        Ab, tb = aff[body]; bc = by[body]["cubes"][0]; bbox = cube_corners(Ab, tb, bc)
        for arm in arms:
            A, t = aff[arm]; c = by[arm]["cubes"][0]; o, s = np.array(c["origin"], float), np.array(c["size"], float)
            top = A @ np.array([o[0] + s[0] / 2, o[1] + s[1], o[2] + s[2] / 2]) + t
            d = obb_dist(top, bbox)
            if d > worst[arm][0]: worst[arm] = (d, n)
            shoulder[arm] = max(shoulder[arm], d)
    return worst

if __name__ == "__main__":
    dst, stem, gid = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    STATES = json.loads(sys.argv[4])
    for st, env in STATES.items():
        row = []
        for nest in (False, True):
            w = sim(dst, stem, gid, env, nest)
            row.append(f"{'JAVA TREE' if nest else 'SHIPPED  '} R {w['right_arm'][0]:.2f} px (t{w['right_arm'][1]}) L {w['left_arm'][0]:.2f} px (t{w['left_arm'][1]})")
        print(f"{st:12s} | " + " | ".join(row))
