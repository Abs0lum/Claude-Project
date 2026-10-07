# TREE APPLIED — program 228 trees (2026-10-06)

Abs0lum's rulings (DECISIONS-2026-10-06, "Trees"):
- the trunk-tip fix applies to all groups;
- the oak elder and pale oak stag limbs are REMOVED (`STAG_OVER_CROWN = False`);
- the fix applies to pale oak too, which becomes lower and flatter;
- the old oak dead leader is REMOVED;
- the jungle_young doubled root is fixed.

**This is a static check only (P1).** The build is shipped and waiting for an in-game check. Nothing was touched in bp02-227, bp02-228, _bds, Drive or the running processes.

## Files changed

| File | Change | md5 after |
|---|---|---|
| tools/tree_gen.py | The plan §6 diff: `TRUNK_TIP_DEPTH`, `crown_base_of` and `sink_tip`, called in oak, spruce and jungle | d30af2cb3e1057b0cab0e2a677f6aebc |
| tools/tree_gen_square.py | The plan §6 diff: `STAG_OVER_CROWN = False`, `TRUNK_TIP_DEPTH`, and `sink_stem` in all 8 square species | 7d871a9349578c1a29f48ba55e14cdec |
| tools/tree_rescale.py | The plan §6 diff (`frame=`) plus F5: a new `is_root()`. A BRANCH WOOD line join that starts at the pw root block now fills with the upper cell's block, so the root is no longer copied up a stretched trunk | 741e8e5fe9ea6e4a5e799c8e4395bb52 |
| The original generators | Backed up to `_garbage/tree_gen_pre228/` (md5 e3d067cf…, d3c89ce5…, 37ef35ba…) | |
| `_docs/trees/rescale_frames_218.json` | A frozen copy of rescale_report.json, holding the build-218 frames (2026-10-03 14:41). md5 7831fe5b2f71dd126de52f6dd39c99f6 | |
| tools/regen_trees_228.py (new) | Regenerates all 544 templates. Birch is written directly; every other group goes build() → rescale(frame = its build-218 frame). It never calls any main(). `--baseline DIR` runs older generators instead | |
| tools/install_trees_228.py (new) | Checks the new templates against bp02-227 and installs only the changed files into the overlay | |
| tools/build_rp01_125.py (new) | Builds RP-01 1.3.125 from 1.3.124 | |
| tools/tree_trunk_sheet_228.py (new) | The after-sheet renderer. The predecessor's scratch renderer had been deleted, so this one follows the plan §9 conventions | |
| `_docs/fell/ft_tpl_index.json` | Rewritten by ft_tpl_gen_lite, as every RP-01 tree build does. The previous version is kept as `ft_tpl_index.pre125.json` | |

## Pipeline check before the change (P8)

I ran the pre-228 generators (the backups) through the same pipeline. They reproduce **all 544 templates byte-identical** to bp02-227 `structures/pw/trees/`. So every difference below comes from the 228 code change.

## Counts

- **281 templates changed:**
  - 269 from the trunk-tip rule. These are exactly the plan §10 "changed" rows.
  - 12 jungle_young root fixes: 00, 02, … 22.
  - The two sets do not overlap. The even jungle_young templates are the cacao forms, which the trunk-tip rule leaves alone.
- **263 templates are byte-identical.** That is the plan's 275 minus the 12 even jungle_young templates. They were NOT copied into the overlay.
- Changed templates by group:

  | Group | Changed |
  |---|---|
  | oak_young | 23 |
  | oak_mature | 24 |
  | oak_old | 24 |
  | oak_elder | 32 |
  | spruce_young | 24 |
  | spruce_mature | 24 |
  | spruce_old | 24 |
  | spruce_elder | 32 |
  | jungle_young | 24 (12 pole forms from the trunk-tip rule + 12 root fixes) |
  | pale_oak_elder | 32 |
  | mangrove | 18 |

- Unchanged groups: birch (72), jungle mature, old and elder, dark oak, acacia, cherry. Also unchanged: 14 of the mangroves and oak_young_12.
- 1,684 logs were removed, and 922 of them became leaves.
- Template height shrinks in 91 templates: mangrove 8, oak old 19, oak elder 32, pale oak 32.
- The per-group logs removed and logs turned to leaves match plan §4 exactly. For example: oak elder 385 / 200, pale oak 740 / 236, oak old 174 / 116.

## Assertions

All of these PASS. They are run by `install_trees_228.py`, and the results are in `TREE-APPLIED-VERIFY.json`.

**Across all 544 templates:**
- There are 544 files.
- The names equal `FT_TPL_NAMES` in bp02-227 `pw_ft_tpl_index.js`, in the same sorted order. The index is unchanged and was not rebuilt.
- The changed set equals the plan's "changed" rows plus the 12 root fixes. Every other template is byte-identical.
- Every template has exactly one pw root, and `pw:tpl + 16·pw:tpl_hi == nn`.

**For each changed template:**
- The root block, its states and its local position are unchanged.
- The x and z size are unchanged, and the y size is never larger.
- Every leaf from before is still a leaf of the same species, with the same states.
  - `pw:variant` changed in 4,836 leaf cells. Every one is within Manhattan distance 4 of a removed log: distance 1: 1,834 · 2: 1,184 · 3: 1,788 · 4: 30.
  - The 30 at distance 4 are the cells the plan predicted.
- New leaves appear only where logs used to be.
- No wood was added.
- Wood keeps its block type. The only exception is the doubled root one block above the root, which becomes the jungle_young log.
- `minecraft:mangrove_roots` and every other block are unchanged.
- All wood is 26-connected to the root.
- No trunk log stands above the crown top.
- Logs removed and logs turned to leaves equal the plan §10 columns for every template.
- The 12 root-fix templates differ from 1.3.227 in that one cell only.

## Overlay

- Location: `tools/bp02_overlay_228/structures/pw/trees/`. It holds 281 files (9.0 MB), at the same relative paths as in bp02-227.
- `build_bp02_228.py` copies the overlay when it runs.
- **The existing `_build/bp02-228` was built at 16:54Z, before the overlay existed, so it does NOT contain the overlay.** A new BP-02 1.3.228 build has to run to pick it up.
- BP-02 1.3.228 (with the overlay) and RP-01 1.3.125 must ship together.

## RP-01 1.3.125

- Built in `_build/rp01-125` (188 MB), starting from rp01-124.
- The falling copies were made by running `ft_tpl_gen_lite.py --maxb=8 --clusters=12 --runfrom=3 --close=3` (the 1.3.121 meshing) over a read-only view of the BP. The view held:
  - a copy of the bp02-227 blocks;
  - the bp02-227 trees, linked, with the 281 overlay files swapped in.
  - The view lived in scratch and has been removed.
- Asserted:
  - The file set is unchanged.
  - Exactly the 281 `models/entity/ft_tpl/<name>.geo.json` files changed.
  - These are byte-identical: the other 263 copies, the leaf atlases, the render controllers, and every other file (3,123 in total).
- Manifest:
  - header and module version [1, 3, 125];
  - name "AbsolutRealism Tectonic RP v1.3.125";
  - a new prefix on the description, which is cut at 1,000 characters.
- LITE totals: 544 templates · 70,384 cubes (average 129, largest spruce_elder_17 at 471) · 21.1 MB of geometry.

## After-sheet: `TREE-TRUNK-APPLIED.png` (3182 × 1366)

**Layout:**
- One row per changed group.
- The boxed panel on the left shows a representative template: BEFORE side | AFTER side | BEFORE top | AFTER top.
- To the right is every changed template in its AFTER state, as a side view from the south.

**Colour key:**
- red outline = trunk tip;
- white outline = trunk hidden in leaves;
- orange-red fill = trunk seen in the top 4 layers;
- magenta = the pw root block.

**What I see, viewed as full-resolution crops:**
- **Oak old** (oak_old_17):
  - Before: a white x-ray column runs up through the crown and ends in an orange-red stub, about 2 cells tall, above the crown top.
  - After: the red tip outline sits inside the crown. No orange shows anywhere in the row. The top view is all green.
- **Oak elder** (oak_elder_26):
  - Before: an orange-red column stands about 4–5 cells above the dome.
  - After: no orange. The red tip sits just under the top dome.
  - In several templates (01, 03, 05), the brown stem shows from the side between the lower limb clumps and the top dome. That is below the top 4 layers.
- **Pale oak** (pale_oak_elder_16):
  - Before: a tall orange-red trunk with Y-shaped stag limbs stands far above a low crown.
  - After: a low, flat crown, 7 high.
  - Red outlines and orange fill remain along the crown's top layer. This is the trunk-follow picking up the horizontal limbs, as plan §4 predicted.
- **Mangrove** (mangrove_02):
  - Before: an orange-red log stands 2–3 cells above the crown.
  - After: the tip is inside the crown.
- **Spruce** (spruce_elder_31 and the rest):
  - Before: an orange-red tip cell sits near the spire point.
  - After: the red tip is 3–4 cells under a green leaf spire.
- **Jungle young:**
  - The BEFORE side view of 00 shows a magenta root 2 cells tall. The AFTER side view shows 1 cell.
  - All 12 even templates show one magenta cell.
  - 14R, 16R, 20R and 22R still show an orange tip just under the fan top. These are the cacao forms, which the trunk rule does not change (plan §4, "jungle young 11 (20)").
- **A note on the numbers:** the sheet's "trunk tip" follows limbs one column out, so its before-values differ from the plan's on the elders. For example, oak_elder_26 reads 21 here and 19 in the plan.

## md5 of the overlay files (structures/pw/trees/)
```
a3b72a1f58a95d5aa9c2d7fb8a2afca2  ./structures/pw/trees/jungle_young_00.mcstructure
a725d9f855ff3601d0aaae159d647300  ./structures/pw/trees/jungle_young_01.mcstructure
33032f69d13cac06015a1c126012d731  ./structures/pw/trees/jungle_young_02.mcstructure
cfed9b7a93e11d52268a226d72236048  ./structures/pw/trees/jungle_young_03.mcstructure
322d9b25fd788fdef2995f5049332905  ./structures/pw/trees/jungle_young_04.mcstructure
e41b4248f5354a8cdb28d0a6ae1fa8a2  ./structures/pw/trees/jungle_young_05.mcstructure
94d66d90e7fb48a57bd15f6c91e915e6  ./structures/pw/trees/jungle_young_06.mcstructure
6d200fb539bd7f246c5928cecaced72b  ./structures/pw/trees/jungle_young_07.mcstructure
43230882904799dceb0c66785f7bbea1  ./structures/pw/trees/jungle_young_08.mcstructure
946de39110083ca7e8d7a1e89f44e962  ./structures/pw/trees/jungle_young_09.mcstructure
3ee2127370ad85e53e6581057447b7f2  ./structures/pw/trees/jungle_young_10.mcstructure
d69aaadc8da2b5c95e67357590621107  ./structures/pw/trees/jungle_young_11.mcstructure
13d80e2edf709a0ffad820311cc23f5b  ./structures/pw/trees/jungle_young_12.mcstructure
28cc0c9d140b103af42aed3b4bc5e369  ./structures/pw/trees/jungle_young_13.mcstructure
279282530c4c1709509ce6bd2a374925  ./structures/pw/trees/jungle_young_14.mcstructure
5e4fad11ee1efaa616e901c040b00e1c  ./structures/pw/trees/jungle_young_15.mcstructure
f418bbc33d7716456f10b24c78b334b0  ./structures/pw/trees/jungle_young_16.mcstructure
74f9a6d289490e70418d7a1d53756b53  ./structures/pw/trees/jungle_young_17.mcstructure
fc986a71cf9cf479f324f339f3bd930d  ./structures/pw/trees/jungle_young_18.mcstructure
884afee3f8e7e685e4364c085e6326c7  ./structures/pw/trees/jungle_young_19.mcstructure
a55c173839ee86f63b9d1d1861c51ff9  ./structures/pw/trees/jungle_young_20.mcstructure
82533e8cf075a5f58c9bbda2abef53d1  ./structures/pw/trees/jungle_young_21.mcstructure
2d5b4ff5db8792ddc27df3c68c0268f0  ./structures/pw/trees/jungle_young_22.mcstructure
a077966a493a6a79e684617487c23f7c  ./structures/pw/trees/jungle_young_23.mcstructure
ed8d0bde5231f4d24382ac1d377d2721  ./structures/pw/trees/mangrove_00.mcstructure
ae8ff7ae686af3da694262f9665d0839  ./structures/pw/trees/mangrove_02.mcstructure
b273c2461c6df433d47ac9098384bbe4  ./structures/pw/trees/mangrove_05.mcstructure
2097fdc131adbf4c461fc5417fa30cdc  ./structures/pw/trees/mangrove_06.mcstructure
ae35b2bf3bdca7fd0e2c9fce97450a7f  ./structures/pw/trees/mangrove_08.mcstructure
a8793f6986f4d4b4895e794b15abe4f5  ./structures/pw/trees/mangrove_11.mcstructure
003ec2fd1d6f8807f8dd885bc2eda4e7  ./structures/pw/trees/mangrove_12.mcstructure
2c741a07fe3e1e274892e3263f81ba57  ./structures/pw/trees/mangrove_14.mcstructure
6c0a7b60ed2f9c0bed6154d20518c682  ./structures/pw/trees/mangrove_15.mcstructure
33adaf7719b20fbc89e42f93c954332e  ./structures/pw/trees/mangrove_17.mcstructure
7b48ab6f438e582d055b27dfd9fc4f31  ./structures/pw/trees/mangrove_18.mcstructure
81ff6a7396bb398765ffc485e62015ec  ./structures/pw/trees/mangrove_20.mcstructure
5125c57b76779b72c16eec4e2f3de2e5  ./structures/pw/trees/mangrove_23.mcstructure
7dd1cb655f7a55d9fdf3ba217c9e2672  ./structures/pw/trees/mangrove_24.mcstructure
1ad6cb4b1c3bbb00798eb2aeb02a12ee  ./structures/pw/trees/mangrove_25.mcstructure
ba1cdec51d2a87304acc33cb0ab28b47  ./structures/pw/trees/mangrove_26.mcstructure
6ea9ff14dbac5fa03542856c8960fddf  ./structures/pw/trees/mangrove_29.mcstructure
6abe1261e05069e984a8fc179712cc4d  ./structures/pw/trees/mangrove_30.mcstructure
7b080992b6ce053cbeb77d6769bce138  ./structures/pw/trees/oak_elder_00.mcstructure
3955fb79209f86a5a33636a0b074acfe  ./structures/pw/trees/oak_elder_01.mcstructure
ec1ee9249460b7defea78dd5b9d0036c  ./structures/pw/trees/oak_elder_02.mcstructure
a03025acbb76eaa001362fc364c6e7bf  ./structures/pw/trees/oak_elder_03.mcstructure
115829b6385b64ab8e4197cc51612ff5  ./structures/pw/trees/oak_elder_04.mcstructure
a7b7bf028ee45de876d620b846b1f60c  ./structures/pw/trees/oak_elder_05.mcstructure
72bac0de43a709905bdd4f8e0ba5076b  ./structures/pw/trees/oak_elder_06.mcstructure
0f20436ad08ea4b8aa8a56b8e04d307c  ./structures/pw/trees/oak_elder_07.mcstructure
3816fde26639b7f9412e9362b2b51c4a  ./structures/pw/trees/oak_elder_08.mcstructure
c9aecef258177bc87cd246e6be472c75  ./structures/pw/trees/oak_elder_09.mcstructure
1479a78052ab8e60e875f44d1bafdc61  ./structures/pw/trees/oak_elder_10.mcstructure
6458bda722177b778cbd66f0c76ceaaf  ./structures/pw/trees/oak_elder_11.mcstructure
b3c49e33832c5948c745fd810e8904f0  ./structures/pw/trees/oak_elder_12.mcstructure
42c8231cddda57972930fa90f3342c63  ./structures/pw/trees/oak_elder_13.mcstructure
d7da4e03b28c118be1e230d9c7688f44  ./structures/pw/trees/oak_elder_14.mcstructure
872eabc5aa58ef56edc371b0caeb8af8  ./structures/pw/trees/oak_elder_15.mcstructure
87c4f5308fa291ac1c8138cb0866b57c  ./structures/pw/trees/oak_elder_16.mcstructure
bc8a327003ba7ddde822cf203104e2e0  ./structures/pw/trees/oak_elder_17.mcstructure
b5579511c4e3310275597697cd519de1  ./structures/pw/trees/oak_elder_18.mcstructure
e247f289eb0064cca545c670b3549572  ./structures/pw/trees/oak_elder_19.mcstructure
4e92454868b48d4d436151d7c260ad50  ./structures/pw/trees/oak_elder_20.mcstructure
0370b473c57bad6b3cc81dd4cfd57406  ./structures/pw/trees/oak_elder_21.mcstructure
c77b6f33fab7315671c45eac1d3f385d  ./structures/pw/trees/oak_elder_22.mcstructure
921ecb823b044379038dca69825aba95  ./structures/pw/trees/oak_elder_23.mcstructure
7d4367c6de86bd41661285e2e7146bb8  ./structures/pw/trees/oak_elder_24.mcstructure
bb8a4087699e218f7ffae8fec0ef37a0  ./structures/pw/trees/oak_elder_25.mcstructure
d13fa94fc66a2c931d6abbb1b83a3e10  ./structures/pw/trees/oak_elder_26.mcstructure
6335118d76f194f3bfc5efe459fd46ab  ./structures/pw/trees/oak_elder_27.mcstructure
500a40f21b8d1b7d035e52f66a24dee6  ./structures/pw/trees/oak_elder_28.mcstructure
bda63e0602ff461de86736c961281c5c  ./structures/pw/trees/oak_elder_29.mcstructure
be5715b2199c860155b5687dd883c636  ./structures/pw/trees/oak_elder_30.mcstructure
04ec2c28c41ba2f1aca389f60c1a8545  ./structures/pw/trees/oak_elder_31.mcstructure
bd2c7a6f445a5dcbb6e1714eaf070cd1  ./structures/pw/trees/oak_mature_00.mcstructure
89c4c26ac61d103b9074d76c60038fd5  ./structures/pw/trees/oak_mature_01.mcstructure
4ecae75bab530affdca66a6669c3c85f  ./structures/pw/trees/oak_mature_02.mcstructure
f6e4aaafbb96e42b8d46d5fda029b8d2  ./structures/pw/trees/oak_mature_03.mcstructure
b26c1d56f4465cfd9a0f9094886ebaeb  ./structures/pw/trees/oak_mature_04.mcstructure
606876def24fbc8475f70d39229f4491  ./structures/pw/trees/oak_mature_05.mcstructure
f033c7920e544a5f6d03edc625f704a2  ./structures/pw/trees/oak_mature_06.mcstructure
3664fea13764032ccca264b8e10f307c  ./structures/pw/trees/oak_mature_07.mcstructure
5b06917f737a56d16820aa9ed8143724  ./structures/pw/trees/oak_mature_08.mcstructure
fd3f3f61f381a133ff8d82b96b2366d6  ./structures/pw/trees/oak_mature_09.mcstructure
9b63e5c22b838806b45ff977d71060f1  ./structures/pw/trees/oak_mature_10.mcstructure
731bdfb3cafbf8605962e0dbebc06110  ./structures/pw/trees/oak_mature_11.mcstructure
c8d5fe6250b4f36c11989e8917471a96  ./structures/pw/trees/oak_mature_12.mcstructure
ea0a319f67a82248c9b2cc92a47f2a81  ./structures/pw/trees/oak_mature_13.mcstructure
439df36ac5b34f7f709a82446dde9760  ./structures/pw/trees/oak_mature_14.mcstructure
fb807e812a4621e32753ac1abfc6a0b5  ./structures/pw/trees/oak_mature_15.mcstructure
a4a3c4fad1da1eee6fef92266475648e  ./structures/pw/trees/oak_mature_16.mcstructure
88acb093ce95cfbec8f38f7627334134  ./structures/pw/trees/oak_mature_17.mcstructure
6fa21f91e5cc17d1953d9b68feb75a21  ./structures/pw/trees/oak_mature_18.mcstructure
59ea747ff37ce4d932357af73d5081b4  ./structures/pw/trees/oak_mature_19.mcstructure
ce29a32e42b7cefea300c09588bbcc50  ./structures/pw/trees/oak_mature_20.mcstructure
e8f8a37b50bd37e2e9cc623c70d64d2f  ./structures/pw/trees/oak_mature_21.mcstructure
3e793bc0f02b606cdd2138048b6fb5b6  ./structures/pw/trees/oak_mature_22.mcstructure
519f3823057e491b024fc91cf99fb1ec  ./structures/pw/trees/oak_mature_23.mcstructure
c2fac096dd01bb34740050c53d739f26  ./structures/pw/trees/oak_old_00.mcstructure
6bd40c9ea100c28d7265e4133da0b15d  ./structures/pw/trees/oak_old_01.mcstructure
2740b8685231bc92c092d1b0f67efc58  ./structures/pw/trees/oak_old_02.mcstructure
af3bf9d1e6055bb562276beb746d96a8  ./structures/pw/trees/oak_old_03.mcstructure
10149f6d54b32c533a59589c1bc5c5e0  ./structures/pw/trees/oak_old_04.mcstructure
49b87e15de0427326119d0b7ef69b86b  ./structures/pw/trees/oak_old_05.mcstructure
9b8a65b642781ab46d4139fe6e46a98d  ./structures/pw/trees/oak_old_06.mcstructure
65496f1aa6a433a4b02352ce8740c149  ./structures/pw/trees/oak_old_07.mcstructure
4f9687c8aab2a740a31a9f2cd3fe42c7  ./structures/pw/trees/oak_old_08.mcstructure
e5caebed8593bb022d9688d58fa318a0  ./structures/pw/trees/oak_old_09.mcstructure
dfd262466363d4f06fb401423e866c1e  ./structures/pw/trees/oak_old_10.mcstructure
87188d98063e77a4f7156f4264ded9ed  ./structures/pw/trees/oak_old_11.mcstructure
972339f4754043118aebc63efe53d735  ./structures/pw/trees/oak_old_12.mcstructure
67e29fdd5407e9902362ff457fc2f42d  ./structures/pw/trees/oak_old_13.mcstructure
9ebd6c963b3a59cc9186ad2cf06ba0c6  ./structures/pw/trees/oak_old_14.mcstructure
b80353f25cb2b598d1bb22851f315139  ./structures/pw/trees/oak_old_15.mcstructure
3769674a80f9fda48feba8bf8cf3c26b  ./structures/pw/trees/oak_old_16.mcstructure
f38c64f6e7a1fcc2fa67b800ed178932  ./structures/pw/trees/oak_old_17.mcstructure
6422fc86c4f9deb90bc73d58d5a555e8  ./structures/pw/trees/oak_old_18.mcstructure
4f96a9f90d6fe3c4bc5b5795159786a5  ./structures/pw/trees/oak_old_19.mcstructure
86ecb66b29fec93000ea55c768a5d04b  ./structures/pw/trees/oak_old_20.mcstructure
ab92c4ab216901deface485085cf6048  ./structures/pw/trees/oak_old_21.mcstructure
c206567499bbaf2449b4761f295bcadc  ./structures/pw/trees/oak_old_22.mcstructure
b5c464af72db0e02c32a1768267879a8  ./structures/pw/trees/oak_old_23.mcstructure
ddf146ea1bd96dec31c9f0b03d8da623  ./structures/pw/trees/oak_young_00.mcstructure
6ae57dfdc1bb768bf52693abd7c157e7  ./structures/pw/trees/oak_young_01.mcstructure
cb3fe654b2f9c30c0e3cb70a9c4a5650  ./structures/pw/trees/oak_young_02.mcstructure
c58354763b20f0ca0b67e28c501a5819  ./structures/pw/trees/oak_young_03.mcstructure
25e528a74771fa0a3a082272057f2ada  ./structures/pw/trees/oak_young_04.mcstructure
d02461bcc01143ae38e008a00142a987  ./structures/pw/trees/oak_young_05.mcstructure
07e57a2cb2a03bf2ebfda6423e419e2e  ./structures/pw/trees/oak_young_06.mcstructure
1614cd1367aba3dcbf60e4207e2ffe3f  ./structures/pw/trees/oak_young_07.mcstructure
427ce031f6075dc2904c275dd2bd3fc0  ./structures/pw/trees/oak_young_08.mcstructure
d6488b55854849f57b787bad1d99057a  ./structures/pw/trees/oak_young_09.mcstructure
27857703f22de314061d2b77c2c4b3e6  ./structures/pw/trees/oak_young_10.mcstructure
f548dc323c60bd8a2c1b0185cb226950  ./structures/pw/trees/oak_young_11.mcstructure
6f117bc51439ae7d93f9d1d943474183  ./structures/pw/trees/oak_young_13.mcstructure
26c3d95a3c69e30068b40a9c77bfff88  ./structures/pw/trees/oak_young_14.mcstructure
b676ede67809712100a787469962bbe3  ./structures/pw/trees/oak_young_15.mcstructure
51c88cb44e3653170969ac096166ae3c  ./structures/pw/trees/oak_young_16.mcstructure
569106598dcacdd112f9371f72945538  ./structures/pw/trees/oak_young_17.mcstructure
62798c953942d697248cb6381082360e  ./structures/pw/trees/oak_young_18.mcstructure
3838f45f1b313db5c7c1031ae1180214  ./structures/pw/trees/oak_young_19.mcstructure
254a5d0beae66558f561d600dd99f19f  ./structures/pw/trees/oak_young_20.mcstructure
fe6eaf913b45cd61c5714781312ab3a6  ./structures/pw/trees/oak_young_21.mcstructure
bedf7ee7b988bbca760ef1b00a278c82  ./structures/pw/trees/oak_young_22.mcstructure
a67d8fb7d417a1048999e14d8e968890  ./structures/pw/trees/oak_young_23.mcstructure
4483bdffde5cf9e07a6a749d6a99bcc1  ./structures/pw/trees/pale_oak_elder_00.mcstructure
4861d313311f933f45d30d234275f8f1  ./structures/pw/trees/pale_oak_elder_01.mcstructure
5340bd52048dbb6b19dd7056f70f5fb5  ./structures/pw/trees/pale_oak_elder_02.mcstructure
094a4942bb7391f25c41c07019b8e953  ./structures/pw/trees/pale_oak_elder_03.mcstructure
fde98bafefe720d4ef0109b24d64f861  ./structures/pw/trees/pale_oak_elder_04.mcstructure
6d010b70ff7189849e9226f00e572d7e  ./structures/pw/trees/pale_oak_elder_05.mcstructure
8580c8fa0a059faf93ed098d6e871204  ./structures/pw/trees/pale_oak_elder_06.mcstructure
9a1d78928de49877b7286aba1e1ab9b8  ./structures/pw/trees/pale_oak_elder_07.mcstructure
f88f5965755f23076d99ad5ab6a05abb  ./structures/pw/trees/pale_oak_elder_08.mcstructure
16b03d2c8377d2a27dd2d7fc1e2b26c9  ./structures/pw/trees/pale_oak_elder_09.mcstructure
971c5ec3c96f408ed75688393baa2b01  ./structures/pw/trees/pale_oak_elder_10.mcstructure
c49855c2dcd672175e9e74b4f6d28129  ./structures/pw/trees/pale_oak_elder_11.mcstructure
d71d4cd8c7eca376ee86497ccf9cbc64  ./structures/pw/trees/pale_oak_elder_12.mcstructure
933bf00d58f33b3625ed07d39d377fef  ./structures/pw/trees/pale_oak_elder_13.mcstructure
09feb823235e66d7d7fb1697d3b01c3e  ./structures/pw/trees/pale_oak_elder_14.mcstructure
508c2f6045be2954e170b91896fef779  ./structures/pw/trees/pale_oak_elder_15.mcstructure
14ad34b1d2f402f231c802cad8e78392  ./structures/pw/trees/pale_oak_elder_16.mcstructure
c75edecba5cbbf77ab94e6105122989c  ./structures/pw/trees/pale_oak_elder_17.mcstructure
8877a1eafe533332f5bb68b599410a79  ./structures/pw/trees/pale_oak_elder_18.mcstructure
d18d7affeaae1a4dad981b2c517687b7  ./structures/pw/trees/pale_oak_elder_19.mcstructure
55140a88ea0de66ca6ad1908cce54f3e  ./structures/pw/trees/pale_oak_elder_20.mcstructure
1a96b8e2003af5f336e3dc29815c0f54  ./structures/pw/trees/pale_oak_elder_21.mcstructure
1b1c91c1ecf2fe0c9b92cf3d1c84a974  ./structures/pw/trees/pale_oak_elder_22.mcstructure
d7ded787aa3cff1de1bd9a72e6e7f2ce  ./structures/pw/trees/pale_oak_elder_23.mcstructure
d5aba432e3aa9630f2223b962d4b4e10  ./structures/pw/trees/pale_oak_elder_24.mcstructure
343bbe67fc346d8d6cc736e78670af61  ./structures/pw/trees/pale_oak_elder_25.mcstructure
1e9149e726ed5497237f34ca62142a77  ./structures/pw/trees/pale_oak_elder_26.mcstructure
5534089593310487a85c1f7a8b8a9c72  ./structures/pw/trees/pale_oak_elder_27.mcstructure
290d24b6c53013ef39e9d156abeaaaa5  ./structures/pw/trees/pale_oak_elder_28.mcstructure
099099a069f47bdbbd8e0c2dc29ad425  ./structures/pw/trees/pale_oak_elder_29.mcstructure
2e6b46d69946e2450f0006f9283b7f1b  ./structures/pw/trees/pale_oak_elder_30.mcstructure
defa79c09d52ec9902a6097d6e11ad5f  ./structures/pw/trees/pale_oak_elder_31.mcstructure
5242d6d8ba32c597e51dc1238f4fa6dd  ./structures/pw/trees/spruce_elder_00.mcstructure
8160595ee88fd62b48d8209b4aa733b2  ./structures/pw/trees/spruce_elder_01.mcstructure
1c68a60c557ab4dfd4d3adda20b4b158  ./structures/pw/trees/spruce_elder_02.mcstructure
aa2e727f08717f0f37fb0cc809592b06  ./structures/pw/trees/spruce_elder_03.mcstructure
787d5b24e3cd61b3b6a19f29d2abc922  ./structures/pw/trees/spruce_elder_04.mcstructure
8e03d18ed65c7258866dfe736bf53097  ./structures/pw/trees/spruce_elder_05.mcstructure
c7ab8459f77f9a1eb9ee87a2b3aeabba  ./structures/pw/trees/spruce_elder_06.mcstructure
cf839f5853037102e83373c546faf78b  ./structures/pw/trees/spruce_elder_07.mcstructure
c1577455bdb9a1f78123820bf30b6ca8  ./structures/pw/trees/spruce_elder_08.mcstructure
fec0e73e7c7c4ac9785b8cf5415a47ce  ./structures/pw/trees/spruce_elder_09.mcstructure
511ff11280e81ed551eb41386454515f  ./structures/pw/trees/spruce_elder_10.mcstructure
9be8f1db44d4e17c5d5b8f926419bd06  ./structures/pw/trees/spruce_elder_11.mcstructure
d07feb51f42739be8eabd7fd17500b61  ./structures/pw/trees/spruce_elder_12.mcstructure
a2a72d4719d8a0224a55ee11764b1e61  ./structures/pw/trees/spruce_elder_13.mcstructure
7e7450ba6ee4b275b00519a3b2b12cb5  ./structures/pw/trees/spruce_elder_14.mcstructure
b72fd9d8abd33246b7e998f95413480a  ./structures/pw/trees/spruce_elder_15.mcstructure
87c262a229f28bc65462c2e3d2d9d2ca  ./structures/pw/trees/spruce_elder_16.mcstructure
386e3cec50c63893f0d1b1207671d8d1  ./structures/pw/trees/spruce_elder_17.mcstructure
090dd76b7115db8567310ae3f9b6a9ab  ./structures/pw/trees/spruce_elder_18.mcstructure
66cf5b6709cba2e26cf9271c206cf7bc  ./structures/pw/trees/spruce_elder_19.mcstructure
96a277d11ea2c3821a7b4185b77be4f6  ./structures/pw/trees/spruce_elder_20.mcstructure
0a9576fea500a229694c7fbabac02b22  ./structures/pw/trees/spruce_elder_21.mcstructure
0d56cd0da07827a5c2127668449f8649  ./structures/pw/trees/spruce_elder_22.mcstructure
dd43b3a1bd3cca46358e9f028284ff38  ./structures/pw/trees/spruce_elder_23.mcstructure
17ae4afee1edfc6a5d1772ed8afa7882  ./structures/pw/trees/spruce_elder_24.mcstructure
f0a280efc55863be6e8bca0f97ba3239  ./structures/pw/trees/spruce_elder_25.mcstructure
c043c5f5db2511c73a7ae7e72eb11672  ./structures/pw/trees/spruce_elder_26.mcstructure
f92413bb2c88467ffc78dcee9fc52a0d  ./structures/pw/trees/spruce_elder_27.mcstructure
dda859e12acafa37e451b323ffc2a3b9  ./structures/pw/trees/spruce_elder_28.mcstructure
54a72a697683301a710dabacc5ac7f38  ./structures/pw/trees/spruce_elder_29.mcstructure
8a28b9f6bbc5df5f38c6196322065777  ./structures/pw/trees/spruce_elder_30.mcstructure
90a3f09d05490790ecbd8b66d3079230  ./structures/pw/trees/spruce_elder_31.mcstructure
997eb92a7c1817b7bcc46d64d47988ec  ./structures/pw/trees/spruce_mature_00.mcstructure
315f5262cbc550c9741532e615d8da37  ./structures/pw/trees/spruce_mature_01.mcstructure
f7ba1bc1738e04471968163ea99fbe18  ./structures/pw/trees/spruce_mature_02.mcstructure
c1bd534371634f44811867ed3912af6d  ./structures/pw/trees/spruce_mature_03.mcstructure
0de830e015076f9bbd3993dcef98a356  ./structures/pw/trees/spruce_mature_04.mcstructure
2bd7f55ed7892cac6590a3408975cd80  ./structures/pw/trees/spruce_mature_05.mcstructure
2a914fa027886cdff96c3db597235bb9  ./structures/pw/trees/spruce_mature_06.mcstructure
f544aed8bbb54c54424ea98bcb32b6e1  ./structures/pw/trees/spruce_mature_07.mcstructure
307a18255dd8d6a9d50b60641c0b9b75  ./structures/pw/trees/spruce_mature_08.mcstructure
d14648f062431e2758c7623097906884  ./structures/pw/trees/spruce_mature_09.mcstructure
b435d53f3f6eb1eebf6b2b7e88edd38f  ./structures/pw/trees/spruce_mature_10.mcstructure
5c0c171aa450ca39eff81403edfbd78c  ./structures/pw/trees/spruce_mature_11.mcstructure
7b2ed0d424308d964a35fd9a1a0b1085  ./structures/pw/trees/spruce_mature_12.mcstructure
c9d654b15d31d3888803bcabb28114a5  ./structures/pw/trees/spruce_mature_13.mcstructure
f83b1b62ae26a50f10ea8010c1cfb1ed  ./structures/pw/trees/spruce_mature_14.mcstructure
09e86e29f0604ebc9fbfc8456f899008  ./structures/pw/trees/spruce_mature_15.mcstructure
75ab07518400851e0f4b5c33c61739ee  ./structures/pw/trees/spruce_mature_16.mcstructure
d86c219eac8010a1b49505e5d6b61f64  ./structures/pw/trees/spruce_mature_17.mcstructure
f407c96a132ad713ad22453e08cbc67a  ./structures/pw/trees/spruce_mature_18.mcstructure
d7a717bb090027945b562da07d612e9e  ./structures/pw/trees/spruce_mature_19.mcstructure
581b005ede1ca81892d14d2f1acb555e  ./structures/pw/trees/spruce_mature_20.mcstructure
18734238656ea051a77a4a4c41a9c038  ./structures/pw/trees/spruce_mature_21.mcstructure
28d2be1d538d469b38e7a4deb7c4a534  ./structures/pw/trees/spruce_mature_22.mcstructure
ee0b13c5f3624128db0a7ce61d7e7218  ./structures/pw/trees/spruce_mature_23.mcstructure
3ecac8590869a65e85a2565909883a6e  ./structures/pw/trees/spruce_old_00.mcstructure
f165ff791f630db15231923d01f78c3d  ./structures/pw/trees/spruce_old_01.mcstructure
d6336f1190074f8fdb9ab046ce1cae34  ./structures/pw/trees/spruce_old_02.mcstructure
e1f02ecd9ddf864bddbcf72aa66b617d  ./structures/pw/trees/spruce_old_03.mcstructure
512b6a7748f10e21435d25d1b755e7e1  ./structures/pw/trees/spruce_old_04.mcstructure
252c00c67f907fb4b46db0bd4cc63d65  ./structures/pw/trees/spruce_old_05.mcstructure
10ab115d90352e9000753b5b24565dc0  ./structures/pw/trees/spruce_old_06.mcstructure
5c15a584abaa3b1633d58241b0894fe1  ./structures/pw/trees/spruce_old_07.mcstructure
c732b7d33f3162a0bf3f17525105727f  ./structures/pw/trees/spruce_old_08.mcstructure
11da2174b73c1cc8502bf40c1f463d98  ./structures/pw/trees/spruce_old_09.mcstructure
c561dc279689fff7e50ca95e2d7d8461  ./structures/pw/trees/spruce_old_10.mcstructure
8b7dab1b9737e7b3a2aaf56df42e1981  ./structures/pw/trees/spruce_old_11.mcstructure
0a865eb4d12e3c75c3df0f390c527eee  ./structures/pw/trees/spruce_old_12.mcstructure
b5e0cf974a78d56b82e2a5e4cbb907bb  ./structures/pw/trees/spruce_old_13.mcstructure
b80280b0883a7bb10cb623c1cc045136  ./structures/pw/trees/spruce_old_14.mcstructure
677b15e62f54476b0685bf04f338b92a  ./structures/pw/trees/spruce_old_15.mcstructure
652e896c7f9e756012c9d3c05e3371b3  ./structures/pw/trees/spruce_old_16.mcstructure
e6f547cfc327e627f3ae224b905ee0e4  ./structures/pw/trees/spruce_old_17.mcstructure
c77ef02cfd8e13c5403fede75eb8db0c  ./structures/pw/trees/spruce_old_18.mcstructure
321107d8ed63245ed0204df2e8b7e318  ./structures/pw/trees/spruce_old_19.mcstructure
9e67486ad590b3473390abe7aac90e2b  ./structures/pw/trees/spruce_old_20.mcstructure
31155dd890db6af90a65a56856b73826  ./structures/pw/trees/spruce_old_21.mcstructure
63b3691ce0851625dbd0aa42673fb518  ./structures/pw/trees/spruce_old_22.mcstructure
5a29a7c56a596c7bf92ffa9c19f8ed06  ./structures/pw/trees/spruce_old_23.mcstructure
526b9650b53cc1b5f73ff4cf70e9a3bf  ./structures/pw/trees/spruce_young_00.mcstructure
0fe8d37cca43a7eb210a9ebf01212b97  ./structures/pw/trees/spruce_young_01.mcstructure
a43551798562a9c77f29a82c323550e4  ./structures/pw/trees/spruce_young_02.mcstructure
8f98160a3bf89c54173828a570a315df  ./structures/pw/trees/spruce_young_03.mcstructure
50790dd10206a1531e79283af674872e  ./structures/pw/trees/spruce_young_04.mcstructure
c336e3ea7b3d338f8a0e759d0ccc359d  ./structures/pw/trees/spruce_young_05.mcstructure
d942e39405a8463550c1ae321e864dca  ./structures/pw/trees/spruce_young_06.mcstructure
0536139a14cf916b8b333222a2f2e8b4  ./structures/pw/trees/spruce_young_07.mcstructure
38ebbae889c057f1471e113bac8aa254  ./structures/pw/trees/spruce_young_08.mcstructure
f736af133ec2c507a51ba321484e4acb  ./structures/pw/trees/spruce_young_09.mcstructure
5d572ca63d70bdc55d69280c71352d29  ./structures/pw/trees/spruce_young_10.mcstructure
1ef74afe14070cdc07ca2810e2aef3b4  ./structures/pw/trees/spruce_young_11.mcstructure
e1ab472f778955d60c0f203ced675c09  ./structures/pw/trees/spruce_young_12.mcstructure
aefa66a3b3caa34ad4ce62a5a7fb8e63  ./structures/pw/trees/spruce_young_13.mcstructure
82f91393f6943628bf0f7f3ee433f83f  ./structures/pw/trees/spruce_young_14.mcstructure
1f4ce805be6e124761b2ded656aaa5f9  ./structures/pw/trees/spruce_young_15.mcstructure
2e0a498c38fc0ba0d3843ac3aff18b0b  ./structures/pw/trees/spruce_young_16.mcstructure
17fa44f20fae1f7224911213a25d8075  ./structures/pw/trees/spruce_young_17.mcstructure
66d1561ab3c1d8f076b9cf784d8612a6  ./structures/pw/trees/spruce_young_18.mcstructure
a5ecb37091810cf47977dd3f66134283  ./structures/pw/trees/spruce_young_19.mcstructure
942b5bd359765255476435deb3ab9a4e  ./structures/pw/trees/spruce_young_20.mcstructure
053fe0b32ebaf5f5c6b4e4f45ccf126f  ./structures/pw/trees/spruce_young_21.mcstructure
c97db42502afcba2a1c026dd9f121d9d  ./structures/pw/trees/spruce_young_22.mcstructure
dd4637fa06f8e8bf865aa31a58e8ffc4  ./structures/pw/trees/spruce_young_23.mcstructure
```
