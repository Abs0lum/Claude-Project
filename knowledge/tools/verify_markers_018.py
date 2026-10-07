#!/usr/bin/env python3
"""Verification suite + suite-gated packaging for PW-Civitas-Markers v0.1.8 (D-101: zips only from inside the gate)."""
import json, os, sys, subprocess, hashlib, zipfile, itertools, tempfile, shutil, re
ROOT='_build/markers-0.1.8'; B=f'{ROOT}/BP'; R=f'{ROOT}/RP'; PREV_B='_packs/markers/BP'; PREV_R='_packs/markers/RP'
OUT='/mnt/user-data/outputs'; VER=[0,1,8]; VS='v0.1.8'
fails=[]; 
def check(cond, msg):
    print(('PASS ' if cond else 'FAIL ')+msg); 
    if not cond: fails.append(msg)

# V1 every JSON parses
bad=[]
for pk in (B,R):
    for dp,_,fs in os.walk(pk):
        for f in fs:
            if f.endswith('.json'):
                try: json.load(open(os.path.join(dp,f),encoding='utf-8-sig'))
                except Exception as e: bad.append((f,str(e)[:80]))
check(not bad, f'V1 all JSON parses ({bad})')

# V2 block files: states, perms, geometry cross-ref
geo=json.load(open(f'{R}/models/blocks/pw_civitas.geo.json'))['minecraft:geometry']
ids=[g['description']['identifier'] for g in geo]; idset=set(ids)
check(len(ids)==len(idset), f'V2a geometry ids unique ({len(ids)})')
fp=json.load(open(f'{B}/blocks/pw_frame_post.json'))['minecraft:block']; cp=json.load(open(f'{B}/blocks/pw_frame_cornerpost.json'))['minecraft:block']
check(cp['description']['identifier']=='pw:frame_cornerpost', 'V2b cornerpost identifier')
check(fp['description']['states']==cp['description']['states'], 'V2c state sets identical on both posts')
check(len(fp['permutations'])==320 and len(cp['permutations'])==320, 'V2d 320 permutations each')
def refs(blk):
    out=[blk['components']['minecraft:geometry']['identifier']]+[p['components']['minecraft:geometry']['identifier'] for p in blk['permutations']]; return out
rf, rc = refs(fp), refs(cp)
check(all(r in idset for r in rf) and all(r in idset for r in rc), 'V2e every referenced geometry exists')
check(len(set(rc))==320 and all(r.startswith('geometry.pw_frame_cornerpost_') for r in rc) and rc[0]=='geometry.pw_frame_cornerpost_0_s0', 'V2f cornerpost references 320 distinct cornerpost geometries (base = 0_s0, same shape as frame_post)')
check(cp['components']['minecraft:collision_box']=={"origin":[-3,0,-3],"size":[6,16,6]} and cp['components']['minecraft:selection_box']=={"origin":[-3,0,-3],"size":[6,16,6]}, 'V2g cornerpost boxes 6 px, y>=0')
check(json.dumps(fp)==json.dumps(json.load(open(f'{PREV_B}/blocks/pw_frame_post.json'))['minecraft:block']), 'V2h pw_frame_post.json byte-identical to v0.1.7')

# V3 cornerpost geometry sanity
cg={g['description']['identifier']:g for g in geo if g['description']['identifier'].startswith('geometry.pw_frame_cornerpost_')}
ok=True; msgs=[]
for gid,g in cg.items():
    m=re.match(r'geometry\.pw_frame_cornerpost_(\w+?)_s(\d)(t?)(g?)$', gid); dirs,snow,t,gr=m.group(1),int(m.group(2)),bool(m.group(3)),bool(m.group(4)); dirs='' if dirs=='0' else dirs
    cubes=g['bones'][0]['cubes']; wood=[c for c in cubes if c['uv']['up'].get('material_instance')!='snow']; snowc=[c for c in cubes if c['uv']['up'].get('material_instance')=='snow']
    for c in cubes:
        o,s=c['origin'],c['size']
        if not (o[0]>=-8 and o[2]>=-8 and o[0]+s[0]<=8 and o[2]+s[2]<=8 and o[1]>=0 and o[1]+s[1]<=24): ok=False; msgs.append(f'{gid} out of cell {o}{s}')
    check_spurs = 1+len(dirs)
    if len(wood)!=check_spurs: ok=False; msgs.append(f'{gid} wood cubes {len(wood)} != {check_spurs}')
    for c in wood[1:]:
        o,s=c['origin'],c['size']
        if o[1]!=12 or s[1]!=4: ok=False; msgs.append(f'{gid} spur not at y12..16')
        reach = (o[2]==-8) or (o[2]+s[2]==8) or (o[0]==-8) or (o[0]+s[0]==8)
        if not reach: ok=False; msgs.append(f'{gid} spur does not reach the boundary')
    exp_snow = 0 if snow==0 else len(dirs)+(1 if t else 0)+(4 if gr else 0)
    if len(snowc)!=exp_snow: ok=False; msgs.append(f'{gid} snow cubes {len(snowc)} != {exp_snow}')
    for c in snowc:
        if c['size'][1]!=2*snow: ok=False; msgs.append(f'{gid} snow height {c["size"][1]} != {2*snow}')
check(ok and len(cg)==320, f'V3 cornerpost geometry sanity (320; {msgs[:3]})')

# V4 texture keys resolve
tt=json.load(open(f'{R}/textures/terrain_texture.json'))['texture_data']
keys=set()
for blk in (fp,cp):
    for mi in [blk['components']['minecraft:material_instances']]+[p['components']['minecraft:material_instances'] for p in blk['permutations']]:
        for v in mi.values(): keys.add(v['texture'])
check(all(k in tt for k in keys), f'V4 material textures resolve in terrain_texture ({sorted(keys)})')
check(tt['pw_frame_wood_dark']['textures']=='textures/blocks/stripped_dark_oak_log', 'V4b pw_frame_wood_dark -> stripped_dark_oak_log (vanilla name, resolves stack-wide)')

# V5 version-spot law + manifest diff gate + string dep
for pk,prev in ((B,PREV_B),(R,PREV_R)):
    m=json.load(open(f'{pk}/manifest.json')); p=json.load(open(f'{prev}/manifest.json'))
    check(m['header']['version']==VER and all(x['version']==VER for x in m['modules']) and VS in m['header']['name'] and m['header']['description'].startswith(VS), f'V5a {os.path.basename(pk)} version-spot: header/modules/name/description agree on {VS}')
    led=open(f'{pk}/PW-DEPENDENCIES.md').read(); check(re.search(r'^'+re.escape(VS)+r' ·', led, re.M) is not None, f'V5b {os.path.basename(pk)} PW-DEPENDENCIES stamp {VS}')
    changed={k for k in set(m)|set(p) if m.get(k)!=p.get(k)}
    hdr={k for k in m['header'] if m['header'].get(k)!=p['header'].get(k)}
    check(changed<= {'header','modules'} and hdr<= {'name','version','description'} and [ (x['type'],x['uuid']) for x in m['modules']]==[(x['type'],x['uuid']) for x in p['modules']] and m.get('dependencies')==p.get('dependencies'), f'V5c {os.path.basename(pk)} manifest diff gate (only name/version/description + module versions)')
mb=json.load(open(f'{B}/manifest.json')); check(any(d.get('module_name')=='@minecraft/server' and d.get('version')=='2.0.0' for d in mb['dependencies']), 'V5d @minecraft/server "2.0.0" string dep preserved (Lesson #53)')

# V6 script parses + resolver model agrees with the diagram
r=subprocess.run(['node','--check',f'{B}/scripts/main.js'],capture_output=True,text=True); check(r.returncode==0, f'V6a node --check main.js ({r.stderr.strip()[:120]})')
js=open(f'{B}/scripts/main.js').read()
check('CORNER_MODE = "tied"' in js and 'pw:frame_cornerpost' in js and 'civ:frame' in js and js.count('_postRefresh(')>=6, 'V6b resolver v2 present (CORNER_MODE tied, both types, civ:frame reflow)')
def bay_on(a,b,key,y, mode='tied'):
    if a is None or b is None: return False
    if mode=='tied' and ('C' in (a,b)): return True
    return (key+y)%2==0
row=['C']+['P']*7+['C']   # 9 posts along z=0..8 at x=0
props=True
for y in range(4):
    for i,t in enumerate(row):
        n = bay_on(t, row[i-1] if i>0 else None, i-1, y); s = bay_on(t, row[i+1] if i<8 else None, i, y)
        if t=='P' and 2<=i<=6 and (n and s): props=False
        if t=='P' and 2<=i<=6 and not (n or s): props=False
for b in range(1,7):
    for y in range(3):
        if bay_on('P','P',b,y)==bay_on('P','P',b,y+1): props=False
check(props, 'V6c parity model: inner plain posts never opposite spurs, one spur per level, bays alternate (matches framing-stagger-v1)')

# V7 structural diff vs v0.1.7
def tree(pk): return {os.path.relpath(os.path.join(dp,f),pk):hashlib.md5(open(os.path.join(dp,f),'rb').read()).hexdigest() for dp,_,fs in os.walk(pk) for f in fs}
tb,pb=tree(B),tree(PREV_B); tr,pr=tree(R),tree(PREV_R)
db={k for k in set(tb)|set(pb) if tb.get(k)!=pb.get(k)}; dr={k for k in set(tr)|set(pr) if tr.get(k)!=pr.get(k)}
check(db=={'blocks/pw_frame_cornerpost.json','scripts/main.js','manifest.json','PW-DEPENDENCIES.md'}, f'V7a BP diff = cornerpost + main.js + manifest + ledger ({sorted(db)})')
check(dr=={'models/blocks/pw_civitas.geo.json','textures/terrain_texture.json','manifest.json','PW-DEPENDENCIES.md'}, f'V7b RP diff = geo + terrain_texture + manifest + ledger ({sorted(dr)})')

if fails:
    print(f'\nGATE FAILED ({len(fails)}): '+' | '.join(fails)); sys.exit(1)

# ---- suite-gated packaging (structurally unreachable on failure)
os.makedirs(OUT, exist_ok=True)
outs=[]
for pk,name in ((B,'PW-Civitas-Markers-BP-v0_1_8.mcpack'),(R,'PW-Civitas-Markers-RP-v0_1_8.mcpack')):
    path=os.path.join(OUT,name)
    if os.path.exists(path): os.remove(path)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for dp,_,fs in os.walk(pk):
            for f in sorted(fs):
                full=os.path.join(dp,f); z.write(full, os.path.relpath(full,pk))
    # from-zip identity
    with tempfile.TemporaryDirectory() as td:
        zipfile.ZipFile(path).extractall(td); t2=tree(td); src=tree(pk)
        check(t2==src, f'V8 from-zip identity {name} ({len(t2)} files)')
        check(all(not n.endswith('/') for n in zipfile.ZipFile(path).namelist()), f'V8b no directory entries in {name}')
    md5=hashlib.md5(open(path,'rb').read()).hexdigest(); outs.append((name,os.path.getsize(path),md5))
for n,s,m in outs: print(f'SHIP {n} {s:,} B md5 {m}')
open('_logs/phase_log.md','a').write('[%s] SHIP — Markers v0.1.8 built + suite PASSED: ' % __import__('time').strftime('%H:%M CT') + '; '.join(f'{n} {s:,}B md5 {m}' for n,s,m in outs) + '\n')
print('ALL PASS' if not fails else 'FAILS')
