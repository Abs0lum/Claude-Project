import json,re,sys
recs=[]
for line in open(sys.argv[1],errors="ignore"):
    m=re.search(r'\[CIVTEST\] (\{.*\})\s*$',line)
    if m:
        try: recs.append(json.loads(m.group(1)))
        except: pass
pts=[]
for r in recs:
    if r.get("step")=="evo" and r.get("prof"): pts.append((r["cmd"]+" "+str(r["tier"]), r["prof"]))
    if r.get("step")=="worksamples":
        for s in r["samples"]:
            if s.get("prof"): pts.append(("work t"+str(s["t"]), s["prof"]))
prev=None
for name,p in pts:
    if prev:
        dt=p["tick"]-prev["tick"]; dms=p["ms"]-prev["ms"]
        keys=[k for k in p if k not in ("tick","ms")]
        per={k: round((p.get(k,0)-prev.get(k,0))/max(1,dt),2) for k in keys}
        tot=round(sum(per.values()),1)
        print(f"{name:22s} ticks {dt:5d} TPS {round(dt/(dms/1000),1) if dms else None:5} scripts {tot:5} ms/t", per)
    prev=p
