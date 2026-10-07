#!/usr/bin/env python3
"""texture_tier_231.py — deterministic texture variant cut + RP-13 fill retirement (ruling D-C1007-R231 / R231c).

Inputs (read-only): base RP build dirs (_build/rp01-125, rp04-159, rp05-59, rp10-151, rp13-101),
  _staging/textures231/keepers/keepers_231.json, _staging/textures231/keepers/repoint_map_231.json.
Output: ONLY changed files under _staging/textures231/<pack>/ mirroring pack paths, plus
  <pack>/_DELETE.txt (pack-relative files the overlay must remove) and _staging/textures231/texture_tier_231_report.json.

Steps per pack terrain_texture.json:
  1. single / lattice / bark-tier keys: repoint old->new from repoint_map (only when current path == old).
  2. array / variation keys: drop every path in the keepers 'drop' set.
  3. RP-13 (flag REMOVE_FILLS, default on — D-C1007-R231c): delete every pw_fill* key and its image files.
  4. dropped images: colour + texture_set.json + every layer it names (normal/heightmap/MER) -> _DELETE.txt.
TIER: one config value per class; None = keep TODAY's resolution (no resize). Pending Abs0lum.
Never writes to _build. Re-running produces byte-identical output (sorted iteration, fixed JSON dump settings).
"""
import json, shutil, sys
from pathlib import Path

ROOT = Path('/home/claude')
BUILD = ROOT / '_build'
STAGE = ROOT / '_staging/textures231'
KEEPERS = STAGE / 'keepers/keepers_231.json'
REPOINT = STAGE / 'keepers/repoint_map_231.json'
PACKS = {'rp01': 'rp01-125', 'rp04': 'rp04-159', 'rp05': 'rp05-59', 'rp10': 'rp10-151', 'rp13': 'rp13-101'}
REMOVE_FILLS = True          # D-C1007-R231c — RP-13's pw_fill* retired with ramps v9
FILL_PREFIX = 'pw_fill'
# Tier resolutions — ONE value per class. None = today's resolution, no resize (questions with Abs0lum).
TIER = {'leaves': None, 'sand': None, 'dirt': None, 'logs_bark': None, 'ores': None,
        'layer_scale': None}   # layer_scale None = normal/MER stay == colour size
IMG_EXT = ('.png', '.tga', '.jpg', '.jpeg')


def load_inputs():
    keepers = json.loads(KEEPERS.read_text())
    rmap = json.loads(REPOINT.read_text())
    drop = sorted({p for fam in keepers.values() for p in fam['drop']})
    repoint = {}
    for fam in rmap['lattices'].values():
        repoint.update({k: tuple(v[:2]) for k, v in fam['changes'].items()})
    for tier in rmap['bark_tiers'].values():
        repoint.update({k: tuple(v[:2]) for k, v in tier['changes'].items()})
    repoint.update({k: tuple(v[:2]) for k, v in rmap['singles'].items()})
    return keepers, rmap, set(drop), repoint


def is_array(tex):
    return isinstance(tex, list) or (isinstance(tex, dict) and 'variations' in tex)


def rewrite_textures(tex, drop, old_new):
    """Return (new_tex, n_dropped, n_repointed). Arrays lose dropped paths; singles repoint old->new."""
    if isinstance(tex, str):
        if old_new and tex == old_new[0]:
            return old_new[1], 0, 1
        return tex, 0, 0
    if isinstance(tex, dict) and 'variations' in tex:   # random variations: strip dropped paths
        def path_of(e):
            return e if isinstance(e, str) else e.get('path')
        kept = [e for e in tex['variations'] if path_of(e) not in drop]
        if not kept:
            raise SystemExit(f'variations would be empty: {tex}')
        return {**tex, 'variations': kept}, len(tex['variations']) - len(kept), 0
    if isinstance(tex, dict):
        if old_new and tex.get('path') == old_new[0]:
            return {**tex, 'path': old_new[1]}, 0, 1
        return tex, 0, 0
    if isinstance(tex, list):   # data-value-indexed list: NEVER remove elements (index shift); recurse per element
        out, d, r = [], 0, 0
        for e in tex:
            if isinstance(e, dict) and 'variations' in e:
                ne, nd, nr = rewrite_textures(e, drop, None)
            else:
                pe = e if isinstance(e, str) else e.get('path')
                if pe in drop:
                    raise SystemExit(f'dropped path in indexed list element: {pe}')
                ne, nd, nr = e, 0, 0
            out.append(ne); d += nd; r += nr
        return out, d, r
    return tex, 0, 0


def paths_in(tex):
    if isinstance(tex, str):
        return [tex]
    if isinstance(tex, dict):
        return paths_in(tex['variations']) if 'variations' in tex else [tex.get('path')]
    if isinstance(tex, list):
        return [p for e in tex for p in paths_in(e)]
    return []


def image_files(pack_dir, rel_path):
    """Pack-relative files that make up one texture: colour + .texture_set.json + layers it names."""
    out = []
    base = pack_dir / rel_path
    for ext in IMG_EXT + ('.texture_set.json',):
        f = base.with_name(base.name + ext)
        if f.is_file():
            out.append(f)
    ts = base.with_name(base.name + '.texture_set.json')
    if ts.is_file():
        try:
            layers = json.loads(ts.read_text()).get('minecraft:texture_set', {})
        except json.JSONDecodeError:
            layers = {}
        for key in ('normal', 'heightmap', 'metalness_emissive_roughness', 'metalness_emissive_roughness_subsurface'):
            name = layers.get(key)
            if isinstance(name, str):
                for ext in IMG_EXT:
                    f = base.parent / (name + ext)
                    if f.is_file():
                        out.append(f)
    return sorted({f.relative_to(pack_dir).as_posix() for f in out})


def main():
    if any(v is not None for v in TIER.values()):
        sys.exit('TIER resize requested but resize step is not built yet (rulings pending) — leave TIER values None.')
    keepers, rmap, drop, repoint = load_inputs()
    report = {'config': {'REMOVE_FILLS': REMOVE_FILLS, 'TIER': TIER, 'packs': PACKS},
              'drop_images': len(drop), 'packs': {}}
    for out_name in PACKS:
        out = STAGE / out_name
        if out.exists():
            shutil.rmtree(out)
    still_referenced = set()
    staged_tt = {}
    for name, d in PACKS.items():
        pdir = BUILD / d
        tt_path = pdir / 'textures/terrain_texture.json'
        tt = json.loads(tt_path.read_text())
        td = tt['texture_data']
        stats = {'keys_before': len(td), 'array_keys_touched': 0, 'array_paths_dropped': 0,
                 'single_keys_repointed': 0, 'fill_keys_removed': 0, 'delete_files': 0}
        fill_paths = set()
        new_td = {}
        for key in td:   # preserve original key order
            entry = td[key]
            if REMOVE_FILLS and name == 'rp13' and key.startswith(FILL_PREFIX):
                fill_paths.update(paths_in(entry.get('textures')))
                stats['fill_keys_removed'] += 1
                continue
            tex = entry.get('textures')
            new_tex, nd, nr = rewrite_textures(tex, drop, repoint.get(key))
            if nd:
                stats['array_keys_touched'] += 1
                stats['array_paths_dropped'] += nd
            stats['single_keys_repointed'] += nr
            new_td[key] = {**entry, 'textures': new_tex} if new_tex is not tex else entry
            still_referenced.update(paths_in(new_tex))
        changed = new_td != td
        stats['keys_after'] = len(new_td)
        if changed:
            tt['texture_data'] = new_td
            dest = STAGE / name / 'textures/terrain_texture.json'
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(tt, indent=2, ensure_ascii=False) + '\n')
            staged_tt[name] = dest
        deletes = []
        for p in sorted(drop | fill_paths):
            deletes += image_files(pdir, p)
        deletes = sorted(set(deletes))
        stats['delete_files'] = len(deletes)
        stats['delete_bytes'] = sum((pdir / f).stat().st_size for f in deletes)
        stats['fill_images'] = len(fill_paths)
        if deletes:
            dl = STAGE / name / '_DELETE.txt'
            dl.parent.mkdir(parents=True, exist_ok=True)
            dl.write_text('\n'.join(deletes) + '\n')
        stats['staged_terrain_texture'] = changed
        report['packs'][name] = stats
    leftover = sorted(drop & still_referenced)
    report['dropped_paths_still_referenced'] = leftover
    report['array_keys_touched_total'] = sum(s['array_keys_touched'] for s in report['packs'].values())
    report['array_keys_expected'] = rmap['array_keys_touched']
    report['single_keys_repointed_total'] = sum(s['single_keys_repointed'] for s in report['packs'].values())
    report['single_keys_expected'] = rmap['summary']['single_keys_changed_total']
    (STAGE / 'texture_tier_231_report.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'config'}, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
