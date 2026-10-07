# Study brief — civ mods for CIVITAS (2026-10-06)

## What CIVITAS is (our system; Minecraft BEDROCK, Script API @minecraft/server 2.3.0, QuickJS, BDS 1.26.52)
A behaviour pack (BP-02) whose scripts grow villager towns from village I to metropolis III on real terrain:
- Town planning: kit streets (13-wide corridors with sewers), ramps, junction windows, contour lanes on hillsides, a land
  survey, a business core with homes pushed outward, conversions of old houses into businesses, districts, a palace with a
  reserved block, walls/border stones, parks. Buildings are placed from .mcstructure templates in stages over days.
- People: a census (people with homes, jobs, families, friends, trust/opinions, rumours, moods, migration, skills/ranks).
- Bodies: villager entities (minecraft:villager_v2 with our component groups) walk via an invisible "lead" entity (a carrot)
  along a route graph built from the streets (A* in script); schedules by time of day (work / market / dusk / home).
- Jobs: builders (labour on construction sites), quarrymen, woodcutters (fell trees, plant coppices), farmers, fishermen,
  shopkeepers at counters, a market clerk on the square, watchmen on patrol, a surveyor who moves border stones.
- Economy: a ledger per town (goods, wages, coin), a market that buys/sells for gold coins, counters stocked daily.
- Performance limits: script watchdog (a tick of script > ~3 s kills a server; PS5 limit 10 s); dynamic properties
  hold the saved state (keep it small); runJob generators for long work. Bedrock add-ons CANNOT reshape terrain.
- Code (read if useful): /home/claude/tools/bp02_src_227/pw_civ_*.js (clock, people, walk, work, shop, watch, economy,
  streets, lanes). Program doc: /home/claude/_docs/GROWTH-PROGRAM-2026-10-05.md.
- Personal use only: any licence is fine to STUDY and borrow ideas from; we write our own Bedrock code. Note licences.

## Your job
For EACH item in your group: open it (jar/zip/tar.gz/mcaddon/mcpack), read what matters (source code, decompiled classes,
JSON data, entity/behaviour files, scripts, configs, lang files, structures), and find the MECHANISMS — how it actually
works (with the numbers: radii, timers, chances, formulas, data schemas) — not the marketing description.
Then judge what CIVITAS can use and HOW we would implement it on Bedrock (Script API / entity JSON / structures), and the
effort (S/M/L) and value (1-5).

## Tools and rules
- Files: /home/claude/_intake/civmods/{modrinth,curseforge,source,manual}/ (LEDGER.json in the first three; manual = his uploads).
- Decompiler: java -jar /home/claude/tools/java/cfr-local.jar <file.class or jar> --outputdir <dir> (decompile only the
  classes you need: unzip the jar, pick packages by name; whole big jars take long). javap -p also works.
- Extract ONLY into /tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/study/<your group>/ and
  remove your extracts when done. DISK IS TIGHT (~1.5 GB free for everyone): never extract a whole 80 MB jar's assets;
  list first (unzip -l), extract the parts you need.
- Do NOT touch /home/claude/_build, /home/claude/_bds, /home/claude/tools/bp02_src_*, running processes, or Drive.
- Do not invent: every mechanism you report must come from a file you opened (name the file/class). Say "not found" when so.

## Output
Write /home/claude/_docs/research/civmods/<GROUP>.md with, per item:
  ### <Name> (<platform>, <licence>, files examined: …)
  - What it does (2-3 lines)
  - Mechanisms found (bullets with numbers, schemas, class/file names)
  - Usable for CIVITAS: idea -> how on Bedrock -> effort S/M/L -> value 1-5
Then a section "Top ideas from this group" (ranked) and "Files examined" (every file you opened, one per line).
Return to the caller: the top ideas (ranked, 1 line each) and the full "Files examined" list (filenames only).
