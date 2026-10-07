#!/usr/bin/env python3
"""Verify texture_tier_231 staging: every terrain key in each staged terrain_texture.json resolves to an existing
image (staged pack -> base pack minus _DELETE -> rest of stack -> vanilla). Also: base-state missing count for comparison."""
import json, sys
from pathlib import Path
B = Path('/home/claude/_build'); ST = Path('/home/claude/_staging/textures231')
PACKS = {'rp01': 'rp01-125', 'rp04': 'rp04-159', 'rp05': 'rp05-59', 'rp10': 'rp10-151', 'rp13': 'rp13-101'}
STACK = ['markers-0.2.3-rp', 'rp13-101', 'rp12-101', 'rp11-140', 'rp10-151', 'rp08-1414', 'rp07-1445', 'rp06-1429',
         'rp05-59', 'rp04-159', 'rp03-67', 'rp02-207', 'rp01-125']
VAN = Path('/home/claude/_intake/bedrock-samples/resource_pack')
EXT = ('.png', '.tga', '.jpg', '.jpeg')
deleted = {}
for n, d in PACKS.items():
    f = ST / n / '_DELETE.txt'
    deleted[d] = set(f.read_text().split()) if f.exists() else set()
def exists(rel, staged):
    roots = [(B / d, deleted.get(d, set()) if staged else set()) for d in STACK if (B / d).is_dir()] + [(VAN, set())]
    for root, dl in roots:
        for e in EXT:
            r = rel + e
            if r not in dl and (root / r).is_file():
                return True
    return False
def paths(t):
    if isinstance(t, str): return [t]
    if isinstance(t, dict): return paths(t['variations']) if 'variations' in t else [t.get('path')]
    if isinstance(t, list): return [p for e in t for p in paths(e)]
    return []
res = {}; touched = set()
for n, d in PACKS.items():
    sf = ST / n / 'textures/terrain_texture.json'
    for label, f, staged in (('base', B / d / 'textures/terrain_texture.json', False), ('staged', sf, True)):
        td = json.loads(f.read_text())['texture_data']
        miss = sorted({(k, p) for k, v in td.items() for p in paths(v.get('textures')) if not exists(p, staged)})
        res[f'{n}.{label}'] = {'keys': len(td), 'missing': len(miss), 'sample': miss[:10]}
    b = json.loads((B / d / 'textures/terrain_texture.json').read_text())['texture_data']
    s = json.loads(sf.read_text())['texture_data']
    touched |= {k for k in s if k in b and s[k] != b[k] and not (isinstance(s[k]['textures'], str) or 'path' in s[k]['textures'] if isinstance(s[k]['textures'], dict) else False)}
res['unique_array_key_names_touched'] = len(touched)
print(json.dumps(res, indent=1))
