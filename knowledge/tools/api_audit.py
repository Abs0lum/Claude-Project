#!/usr/bin/env python3
"""api_audit.py — L-API-STABLE gate: every script in a behaviour pack may only touch engine members that exist in the
@minecraft/server (and server-ui) version its manifest PINS.  D-C228: Block.isSolid is beta-only; on the stable 2.0.0 pin
it silently reads undefined.

For each pack: the manifest's module pins -> the typings of exactly that version (npm pack, cached) + a SUPERSET (the
current beta + latest stable).  A member name used after a dot in the pack's scripts is FLAGGED when it exists in the
superset typings but nowhere in the pinned typings (so JS built-ins like .push never flag).  Imports from the module that
the pinned version does not export are flagged too.  Output: a report per pack; exit 1 when anything is flagged.

usage: api_audit.py <pack.mcpack | pack dir> [...] [--json out.json]"""
import json, re, sys, subprocess, zipfile, tarfile, io
from pathlib import Path

CACHE = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/typings")
SUPERSET = {"@minecraft/server": ["2.12.0-beta.1.26.60-preview.28", "2.10.0"], "@minecraft/server-ui": ["beta", "latest"]}

def typings(module, version):
    """index.d.ts text of module@version (npm pack, cached)."""
    safe = module.replace("/", "_").replace("@", "") + "-" + version.replace("/", "_")
    d = CACHE / safe; f = d / "index.d.ts"
    if f.exists(): return f.read_text(encoding="utf-8")
    d.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["npm", "pack", f"{module}@{version}", "--silent"], cwd=d, capture_output=True, text=True, timeout=180)
    tgz = sorted(d.glob("*.tgz"))
    if not tgz: raise RuntimeError(f"npm pack failed for {module}@{version}: {r.stderr[:200]}")
    with tarfile.open(tgz[-1]) as t:
        member = next(m for m in t.getmembers() if m.name.endswith("index.d.ts"))
        f.write_text(t.extractfile(member).read().decode("utf-8"), encoding="utf-8")
    return f.read_text(encoding="utf-8")

# JavaScript built-in method/property names: a newer engine class may declare one (e.g. a .set/.push method), but in
# our scripts they are Array/Map/Set/Object/String calls — never flag them.
JS_BUILTINS = set("""push pop shift unshift slice splice map filter find findIndex findLast findLastIndex some every reduce reduceRight
forEach includes indexOf lastIndexOf join sort reverse concat flat flatMap fill keys values entries set get has delete clear add size length
toString toFixed valueOf hasOwnProperty call apply bind then catch finally trim split replace replaceAll startsWith endsWith padStart padEnd
toLowerCase toUpperCase charAt charCodeAt codePointAt substring substr match matchAll test exec at from of assign freeze parse stringify
floor ceil round abs min max sqrt random pow sin cos tan atan2 hypot sign trunc log exp now""".split())
MEMBER_RE = re.compile(r"^\s+(?:readonly\s+|static\s+|get\s+|set\s+)*([A-Za-z_]\w*)\??\s*[(:<]", re.M)
EXPORT_RE = re.compile(r"^export\s+(?:declare\s+)?(?:abstract\s+)?(?:class|interface|enum|const|function|type|let|var)\s+([A-Za-z_]\w*)", re.M)
ENUM_MEMBER_RE = re.compile(r"^\s+([A-Za-z_]\w*)\s*=\s*['\"\d]", re.M)
def index(text):
    members = set(MEMBER_RE.findall(text)) | set(ENUM_MEMBER_RE.findall(text))
    exports = set(EXPORT_RE.findall(text))
    return members, exports

def strip_comments_and_strings(js):
    js = re.sub(r"/\*.*?\*/", " ", js, flags=re.S)
    js = re.sub(r"//[^\n]*", " ", js)
    js = re.sub(r"`(?:\\.|[^`\\])*`", "``", js, flags=re.S)
    js = re.sub(r"'(?:\\.|[^'\\\n])*'", "''", js)
    js = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', js)
    return js

def pack_files(path):
    p = Path(path)
    if p.is_dir():
        return {str(f.relative_to(p)).replace("\\", "/"): f.read_bytes() for f in p.rglob("*") if f.is_file()}
    with zipfile.ZipFile(p) as z:
        return {n: z.read(n) for n in z.namelist() if not n.endswith("/")}

def audit(path, pin_override=None):
    """pin_override = {"@minecraft/server": "2.3.0"} audits the scripts AS IF re-pinned (migration check); also flags
    members the scripts use that exist in the manifest's CURRENT pin but NOT in the override (removed / renamed)."""
    files = pack_files(path)
    man_name = next((n for n in files if n.split("/")[-1] == "manifest.json" and n.count("/") <= 1), None)
    if not man_name: return {"pack": str(path), "error": "no manifest"}
    man = json.loads(files[man_name].decode("utf-8-sig"))
    pins = {d["module_name"]: d["version"] for d in man.get("dependencies", []) if d.get("module_name")}
    current = dict(pins)
    if pin_override: pins = {**pins, **pin_override}
    root = man_name.rsplit("/", 1)[0] + "/" if "/" in man_name else ""
    scripts = {n: files[n].decode("utf-8", "replace") for n in files if n.endswith(".js") and n.startswith(root)}
    out = {"pack": Path(path).name, "version": man["header"].get("version"), "pins": pins, "scripts": len(scripts), "flags": []}
    if not scripts or "@minecraft/server" not in pins: return out
    pinned = {}
    for mod, ver in pins.items():
        if mod not in SUPERSET: continue
        pinned[mod] = index(typings(mod, ver))
    sup_members, sup_exports = set(), set()
    for mod in pinned:
        for v in SUPERSET[mod]:
            m, e = index(typings(mod, v)); sup_members |= m; sup_exports |= e
    pin_members = set().union(*[m for m, _ in pinned.values()]); pin_exports = set().union(*[e for _, e in pinned.values()])
    beta_only = (sup_members - pin_members) - JS_BUILTINS
    removed = set()
    if pin_override:
        for mod, ver in current.items():
            if mod in pinned and ver != pins.get(mod):
                removed |= (index(typings(mod, ver))[0] - pinned[mod][0]) - JS_BUILTINS
    out["removed_used"] = []
    for name, src in scripts.items():
        code = strip_comments_and_strings(src)
        lines = src.splitlines()
        for mod in pinned:
            for m in re.finditer(r"import\s*\{([^}]*)\}\s*from\s*['\"]" + re.escape(mod) + r"['\"]", src):
                for imp in [x.strip().split(" as ")[0] for x in m.group(1).split(",") if x.strip()]:
                    if imp not in pinned[mod][1] and imp in sup_exports:
                        out["flags"].append({"file": name, "kind": "import", "name": imp, "module": mod})
        used = {}
        for m in re.finditer(r"\.\s*([A-Za-z_]\w*)", code):
            used.setdefault(m.group(1), m.start())
        for member in sorted(set(used) & removed):
            ln = next((i + 1 for i, l in enumerate(lines) if re.search(r"\.\s*" + re.escape(member) + r"\b", l) and not l.strip().startswith("//")), None)
            out["removed_used"].append({"file": name, "name": member, "line": ln, "text": (lines[ln - 1].strip()[:140] if ln else "")})
        for member in sorted(set(used) & beta_only):
            ln = next((i + 1 for i, l in enumerate(lines) if re.search(r"\.\s*" + re.escape(member) + r"\b", l) and not l.strip().startswith("//")), None)
            out["flags"].append({"file": name, "kind": "member", "name": member, "line": ln, "text": (lines[ln - 1].strip()[:140] if ln else "")})
    return out

if __name__ == "__main__":
    override = None
    if "--pin" in sys.argv:
        override = {"@minecraft/server": sys.argv[sys.argv.index("--pin") + 1]}
    args = [a for a in sys.argv[1:] if not a.startswith("--") and (not override or a != override["@minecraft/server"])]
    jout = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    if jout in args: args.remove(jout)
    reports = [audit(a, override) for a in args]
    bad = 0
    for r in reports:
        if "error" in r: print(f"?? {r['pack']}: {r['error']}"); continue
        flags = r["flags"]; bad += len(flags)
        print(f"{'FLAG' if flags else 'ok  '} {r['pack']} v{'.'.join(map(str, r['version'] or []))} · pins {r['pins'] or '-'} · {r['scripts']} script(s) · {len(flags)} flag(s)")
        for f in flags:
            if f["kind"] == "import": print(f"       import {{{f['name']}}} from {f['module']} — not exported by the pinned version")
            else: print(f"       {f['file']}:{f['line']}  .{f['name']}  — not in the pinned typings  |  {f['text']}")
        for f in r.get("removed_used", []):
            print(f"       REMOVED in the new pin: {f['file']}:{f['line']}  .{f['name']}  |  {f['text']}")
        bad += len(r.get("removed_used", []))
    if jout: Path(jout).write_text(json.dumps(reports, indent=1), encoding="utf-8")
    sys.exit(1 if bad else 0)
