import json,re,sys
recs=[]
for line in open(sys.argv[1],errors="ignore"):
    m=re.search(r'\[CIVTEST\] (\{.*\})\s*$',line)
    if m:
        try: recs.append(json.loads(m.group(1)))
        except: pass
for e in [r for r in recs if r.get("step")=="evo"]:
    w=e.get("walk") or {}
    print(e["cmd"], "|", e["expect"][:14], "| tier", e.get("tier"), "plots", e["plots"], "fin", e["finished"], "ok", e["verifiedOk"], "bad", len(e["bad"]), "census", (e.get("census") or {}).get("n"), (e.get("census") or {}).get("mood"), "kids", (e.get("census") or {}).get("children"), "left", e.get("leftover"), "streets", len(e.get("streets") or []), "walk", w.get("arrived"), w.get("stuck"), w.get("legs"), "border", (e.get("border") or {}).get("r"), "slotWhy", e.get("slotWhy"), "works", (e.get("works") or {}).get("missing"), (e.get("works") or {}).get("sanitation"), "bodies", e.get("bodies"))
