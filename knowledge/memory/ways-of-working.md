---
name: ways-of-working
description: Workflow, communication patterns, STOP/recovery protocols, and tooling for working with Abs0lum on this pack suite
sources: [backfill]
aliases: [protocols, workflow, bridge, tooling]
---
## Workflow

- [stated] Session flow: amnesia check at session start → plan-first gate → build → suite-gated packaging → from-zip re-measurement → witness verification
- [stated] No behavior is assumed correct until confirmed in-game
- [stated] Pack-home law (2026-09-21): "the pack home IS the mcaddon" — every change goes into its current relevant existing pack (blocks/scripts → BP-02, geometry/textures → RP-04, particles/fog → RP-02, etc.); new packs are made only when necessary, never when convenient
- [stated] Test-runner exception (2026-09-27): in-game test commands live in a SEPARATE job-only pack (PW-TestRunner BP), never in the current packs — "we'll use this pack to edit new test commands into for future need"; it is attached at the bottom of the behavior-pack list so it loads last and can use every asset of the other packs; test props are placed only when he presses the button
- [stated] PS5 test routine (2026-09-30 correction): he starts everything on his PHONE (imports packs, copies the world, sets packs + toggles, launches/hosts the game) and JOINS that game with his PlayStation; the PS5 cannot download/import packs itself, it only receives them by joining a single-player or Realm game — install steps go to the phone, the PS5 just joins (and runs Vibrant Visuals). Don't restate corrected instructions back to him
- [stated] Testing: Android primary, PS5 as natural control group; the laptop now also runs Minecraft Bedrock (worlds under `%APPDATA%\Minecraft Bedrock\Users\<id>\games\com.mojang\minecraftWorlds\`) and hosts the PROVING GROUND authoring world (flat, Tunnelers' Dream preset, datum y=173)
- [stated] Pack-update routine on the laptop while a world has nothing built in it: delete the old world, delete the old packs from storage, clear caches, then recreate the world with the same name and the new packs; once a world holds builds, update packs via world settings (remove → re-activate) instead of deleting the world
- [stated] In-world building sessions: always restate the relevant protocol step before answering any "what's next" or "did I do this right" question
- [stated] Abs0lum issues rulings and corrects course when Claude moves too fast or makes incorrect assumptions; he expects step-by-step pacing in procedural sessions, and corrections are accepted immediately without defending the prior model
- [stated] Molang gate (2026-09-29, "ABSOLUTELY!"): going with a standing Molang-parse check on every pack build, extended to particle files and behavior-pack Molang (block conditions etc.)

## Communication patterns

- [stated] Abs0lum's hyphens and double hyphens are pauses/thought-beats — moments of remembering or realizing — never cut-off thoughts; read as beats, not omissions
- [stated] He communicates through symptom descriptions and mental imagery; these have consistently proven diagnostically accurate and should be taken seriously
- [stated] AutoCAD fluency and architecture coursework inform his spatial reasoning; he works from precise internal imagery described verbally
- [stated] Unit vocabulary (2026-09-21): a "cube" is 1/16 of a block edge (a block is 16×16×16 cubes) and geometry elements are called "boxes"; moving a texture one pixel is NOT one cube (at the suite's 128 px textures 1 cube = 8 px) — the two were used interchangeably before and caused wrong-unit deliveries on the roof ridge/cap gables; he prefers plane-level, skill-saw-cut language for texture/geometry edits ("top plane flush with the block corner, bottom cut to 135°")
- [stated] Abs0lum is autistic and disregards ideas that aren't tracked — the Thread-Keeper Duty is standing law: track all active threads explicitly

## STOP / recovery protocols (all active)

- [stated] ECHO-FIRST LAW: before evaluating any pasted document, log, or attachment — state its size (bytes/lines) and quote its first line verbatim; if Claude cannot do this, full STOP
- [stated] TOOL-RECOVERY CHAIN: when any paste/upload/image is missing or unreadable, attempt recovery via tools first — (1) list `/mnt/user-data/uploads` via bash/view, (2) for images, view file at full resolution from disk, (3) for text/pastes, read via bash; report paths attempted and results; fire STOP + multiple-choice prompt only if tool recovery also fails
- [stated] Upload STOP rule: if an attachment exists per Abs0lum but is missing/failed/unreadable, STOP and prompt via multiple choice — (a) retry upload, or (b) proceed without it; explicitly state whether Claude has enough information to solve correctly WITHOUT the upload; never proceed silently
- [stated] SNAPSHOT-ON-RECEIPT: immediately copy critical uploads to the working directory with recorded sha256 (uploads can vanish from mount mid-conversation)
- [stated] Failsafe + recoverable-delete law (2026-10-03): the sandbox's garbage folder is Claude's recoverable delete (never a true delete — "there are reports of you deleting entire databases"); when the sandbox needs clearing, its contents go into space on his Google Drive that Claude can reach instantly to recover lost data; and there must be a folder Claude can DUMP information, files and set-asides into but can never DELETE from — a failsafe holding all current details and files for the aftermath of a failure on either side. He himself uploads everything correct and current to Drive occasionally so he never loses progress and gives Claude the same space; his Drive has 5 TB free — "don't argue it", he will make space when needed. Stopping points (stop, verify the work, disconnect from the sandbox, start again) are for safety; he doesn't require an actual stop
- [stated] SELF-VIEW SINGLE-FAIL RULE: if Claude's view of its own generated image fails once, do not retry-loop — switch to numeric verification and present the file to Abs0lum's eyes as the verdict channel
- [stated] CLARIFY-FIRST LAW: never proceed on an assumed answer to a question not yet asked; never proceed past content referenced but unverifiable; stop and ask explicitly at any decision point, ambiguity, or unverifiable reference
- [stated] SCOPE-ECHO practice: before executing any broad or ambiguous request, state the scope being assumed AND what is being excluded, so Abs0lum can widen or correct the frame before work begins
- [stated] Witness reporting protocol: when Abs0lum reports test/witness results without screenshots for some items, always ask per-item (multiple choice ok) — was it a success, not encountered, or forgotten? He forgets to capture successes; never assume absence of evidence means failure
- [stated] Auto-transform proactive surfacing: whenever designing or reviewing any block system, proactively recommend opportunities for the auto-transform mechanic — blocks that change into different versions when placed adjacent to identical blocks or to special combinations of unique blocks (double doors, connected panels, arches, merged furniture)

## Tools & resources

- [stated] AbsolutRealism Bridge MCP tools: `bridge_status`, `get_live_tail`, `list_sessions`, `get_session_tail`, `search_events`, `run_game_command`
- [stated] Bridge state authoritative source: `C:\AbsolutRealism-Bridge\bridge_state.json`; Phase 3 session logs at `C:\AbsolutRealism-Bridge\phase3\logs\session_YYYYMMDD_HHMMSS.jsonl` (all timestamps UTC); launch path `C:\AbsolutRealism-Bridge\phase3\bridge_phase3.py`
- [stated] `bridge-files` MCP tool: `read_text_file` (head/tail params), `write_file`, `move_file`, `search_files` (glob), `list_allowed_directories`
- [stated] `conversation_search` and `search_files` MCP tools available
- [stated] Amulet: structure extraction pipeline — Realms download → `.mcworld` → Syncthing → laptop → Amulet box-select → `.mcstructure` → baked into BP-02
- [stated] `depscan.py`: dependency manifest injection/tracking (DEP-MANIFEST LAW)
- [stated] `slabforge_offline.py`: offline slab pre-pass pipeline
- [stated] `ft_av_sync.py`: falling-tree A/V sync diagnostic tool
- [stated] UV-Contract Linter: suite-wide structural audit tool (size-contract, claim-map theft, white-sampling, orphan-art census, polarity taxonomy)
- [stated] Blockbench: visual geometry editing bridge — Claude emits `.bbmodel` files with embedded textures; Abs0lum inspects/nudges, saves and uploads; Claude reads the diff and cuts the pack
- [stated] Syncthing: asset sync pipeline, phone↔laptop; Inbox/Pipeline folder structure established
- [stated] Google Drive: "Abs0lutMedievalism" folder for study assets; the shared Drive folder is the exchange point (Sep 2026) — witness screenshots go to its screenshots folder, uploaded worlds to a worlds folder, saved structures to a structures folder, source textures (ambientCG sets) to packs/Assets, and packs/Mine holds pack files — check Drive for deliveries rather than expecting chat attachments
- [stated] Drive archive rule (2026-09-22 22:34): "OLD COPIES AND OLD PACKS stay in the shared drive as resources" — he keeps every previous version there as reference for as long as space allows and deliberately doesn't delete them, so the Drive (packs/Mine included) never shows what is installed; he no longer uses the older/retired packs stored there
- [stated] Pack handling (2026-09-22): he removes the previous version from the game as he loads a new one (so version numbers must always be bumped) and always attaches the latest versions of all packs to his world; the current versions live in his Abs0lutMedievalism folder, where he adds/deletes as new versions arrive; Drive uploads happen only when a pack tested successfully AND he remembered — skipped versions there are his forgetting or too small a change to upload, so Claude must check for gaps rather than trust the Drive as current
- [stated] Two-lists rule (2026-09-23): he now uploads every pack he downloads to the Drive packs folder and Claude verifies them; HIS list updates as he tests, Claude's list updates from what he uploads to the packs folder AND what he says in conversation is accepted; when unsure what's current (esp. long-running content with no recent upload), Claude may request a refresher and he uploads the latest complete mcaddon for review and correction
- [stated] Pipeline lanes in git: `inbox/Pipeline/` (pack processing) and `docs/` (documentation output)
- [stated] Confirmed alive WebSocket events: PlayerTravelled, PlayerTransform, ItemAcquired, BlockBroken, ItemInteracted, BlockPlaced, ItemCrafted, PlayerMessage, EntitySpawned, MobKilled, EndOfDay, PlayerDied
- [stated] Pack delivery cap (Sep 2026): he can't receive files over 30 MB through a Claude chat — a chat sent RP-04 as .partN pieces plus a Python joiner, which he doesn't know how to run and doesn't want; he wants each pack delivered as a single .mcpack. Chosen route for a large pack: an expiring gofile.io download link (laptop-link route also acceptable to him only as an alternative). Handoff documents are delivered in the chat itself (attached/pasted), never via the download link
- [stated] Pack delivery route (2026-10-04, supersedes gofile as the default): new and updated packs are uploaded directly into his Google Drive, in a folder named "ClaudeUploads", instead of the gofile page
- [stated] `ldbscan.py` + `nbt.py` (project knowledge `claude/tools/`, Drive `/Claude/Tools/`): Claude can read `structuretemplate_*` straight out of any world he uploads to Drive (extracted world folder or .mcworld) via the LevelDB write-ahead log — no structure export from him needed
- [stated] Conversation archive (2026-09-29): when a conversation needs room, store contiguous pieces of it in Google Drive and always reference those older conversation logs going forward
- [stated] Knowledge storage (2026-09-29): Google Drive (Google One, 5 TB, plenty of room) is to be used as backup AND primary store for project knowledge, checked as often as needed — a dedicated "AbsolutRealism Knowledge" folder; keep at least one copy of every unique version of every file/folder/document (from the Drive and from project knowledge), duplicates are unnecessary, don't delete reference material; project knowledge itself to be rebuilt as core docs + all tools; large files may be split into smaller parts to fit Drive's rules
