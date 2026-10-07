# COMMON BRIEF FOR ALL ROUND-231 WORKERS (2026-10-07 ~03:00 CT)

Project: AbsolutRealism — Abs0lum's personal-use Minecraft Bedrock pack suite (PS5 + Android). Workspace /home/claude.
The full law is /home/claude/_knowledge/src/knowledge/CLAUDE-AR.md (read §4 witness rule, §5 failure modes, §7 engine
laws, §9 execution law before you start — about 5 minutes).

## Rules that bind every worker
1. **Witness rule:** Abs0lum's in-game reports are ground truth for symptoms. Never assume he made an operational error
   (stale world, wrong pack). Investigate the cause. His words "maybe a glitch / load a new world" are a hypothesis to test,
   not a conclusion.
2. **Mechanism before fix:** state the mechanism with file paths, line numbers and numbers before changing anything.
   If you can't, say "investigation incomplete" and what is missing.
3. **TDD for logic:** CIVITAS suites live in tools/bp02_src_228/tests/ (run all: `cd tools/bp02_src_228 && for t in tests/*.mjs; do node $t || echo FAIL $t; done`).
   All suites must pass at the end; `node --check` every edited .js.
4. **Shared hot file:** tools/bp02_src_228/pw_civ_clock.js (615 KB) is edited by two workers (CIV-PEOPLE, CIV-LAND).
   Edit it ONLY with small exact-string edits (the Edit tool), re-Read the exact region right before each edit, never
   rewrite the whole file, never reformat. If an edit fails because the file changed, re-read and retry.
5. **File ownership:** edit only the files your task lists as yours. Need a change elsewhere? Write it as a proposal in
   your report (exact diff), don't apply it.
6. **No builds, no packaging, no BDS server runs, no Drive uploads, no Project writes** — the lead assembles, gates and
   ships everything. Do NOT copy _build/ directories (disk has ~2 GB free; keep your scratch < 200 MB, delete it at the
   end). Stage new/changed pack files under /home/claude/_staging/<your-name>/ mirroring the pack path, plus a
   README.md there saying exactly which pack + path each file replaces or adds.
7. **Backups:** before editing any existing tool or source file, copy it to /home/claude/_garbage/<your-name>-pre/.
8. **Geometry law (P13):** block geometry identifiers lowercase; geometry format_version "1.16.0"; run
   `python3 tools/geo_ref_check.py --help` for the cross-pack checker if you add geometry.
9. **Visual work:** render before/after images (PIL / existing render tools in tools/) and VIEW them yourself before you
   claim anything looks right. State the camera facing for any orientation claim.
10. **Status file (required):** create /home/claude/_logs/agent_status/<YOUR-NAME>.md now and append one line every
    time you finish a step: `[HH:MM CT] <what finished / what's next>` (CT = UTC-5; get time with
    `TZ=America/Chicago date +%H:%M`). Your LAST line must be `DONE: <one-line result>` or `BLOCKED: <why>`.
    A monitor reads these every 5 minutes and reports to Abs0lum, so keep them truthful and plain.
11. **Final report** (your reply to the lead): what you changed (files + md5), how you verified it, what is staged where,
    open questions for Abs0lum (as plain questions), and anything you could NOT do. Also append one line to
    /home/claude/_logs/phase_log.md: `[HH:MM CT 10-07] <YOUR-NAME> DONE: ...`.

## Evidence locations
- His 00:23 CT report screenshots (46): /home/claude/_intake/screens-1007/ — labelled contact sheets
  CONTACT-SHEET-1..3.png show every image with its filename; open the ones you need at full resolution.
- His 02:54 CT report screenshots (11): /home/claude/_intake/screens-1007b/ (inn "We're closed" in daylight at
  -146 65 125; civs clustered at the well at -168 68 125; dirt wedges sitting on top of the street ramps at
  -190..-205 64 122 that he cannot break in creative; ramp shadow bands at -146 65 125).
- His current state + full open list: /home/claude/_docs/program228/HANDOFF-2026-10-07-STATE.md.
- Decision journal (rulings): /home/claude/_logs/decision_journal.md (search D-C1006-*, D-C1007-*).
- Current shipped builds (read-only reference): _build/bp02-230 (BP-02 1.3.230 slim), _build/rp13-101 (RP-13 1.0.1),
  RP-04 1.3.159 and RP-01 1.3.125 build dirs under _build/ (ls _build).
