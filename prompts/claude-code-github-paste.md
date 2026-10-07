# PASTE FOR THE CLAUDE CODE (GITHUB) CHAT

Abs0lum: copy section **A** into the GitHub Claude Code chat once, the first time. After that, every time a new knowledge
zip lands, paste section **B**. Before either paste, put the zip in the repo (see "How the zip gets into the repo").

## How the zip gets into the repo (you do this part)
1. On the laptop (or phone), open Google Drive → `ClaudeUploads` → `knowledge` → download the newest `AR-Knowledge-<date>.zip`.
2. Open your repository on github.com → **Add file** → **Upload files**.
3. Drag the zip in. In the path box at the top, type `_inbox/` before the file name so it lands in a folder named `_inbox`.
4. Commit message: `knowledge zip <date>` → **Commit changes** (directly to the default branch is fine).
   (The browser upload takes files up to 25 MB; the zip is built to stay under that.)
5. Paste section A (first time) or B (every later time) into the Claude Code chat.

---

## A. FIRST-TIME SETUP (paste once)

```text
You are working in Abs0lum's private AbsolutRealism repository (a personal-use Minecraft Bedrock pack suite). You cannot
see our claude.ai Project, so the whole knowledge base is delivered to you as a zip in `_inbox/AR-Knowledge-<date>.zip`.
Use the highest reasoning effort available: run `/effort ultracode` now (if it is not available, use the highest level
you have and tell me which). Then do this, in order, and stop at the end:

1. Read the zip's file list. Unzip it into a temporary folder OUTSIDE the repo. Check every row of
   `knowledge/MANIFEST.json` against the unzipped files (bytes + md5). If any row fails, stop and tell me which.
2. Copy into the repo root, replacing any older copies: `knowledge/`, `prompts/`, `claude-settings/`.
3. Repo-root CLAUDE.md:
   - If the repo has no CLAUDE.md, copy `claude-settings/CLAUDE.md.repo-root` to `CLAUDE.md`.
   - If it already has one, KEEP everything in it and add the line `@knowledge/CLAUDE-AR.md` near the top plus the
     "This venue" section from `claude-settings/CLAUDE.md.repo-root`. Show me the diff before committing.
4. `.claude/settings.json`: merge in the keys from `claude-settings/settings.json` ("effortLevel": "xhigh",
   "ultracode": true, "alwaysThinkingEnabled": true, "promptCacheTtl": "1h", and the permissions deny list). Keep any
   keys that already exist unless they conflict; show me the result.
5. `.gitignore`: make sure these are ignored: `_inbox/*.zip`, `_intake/secrets/`, `*.mcpack`, `*.mcaddon`, `*.mcworld`,
   `.env`, `node_modules/`, `__pycache__/`.
6. Delete the zip from `_inbox/` and commit everything as one commit:
   `knowledge sync <date> — first mirror (law CLAUDE-AR v3.0, prompts v2.6)`.
7. Read, in this order: `knowledge/CLAUDE-AR.md` (the law — it overrides your defaults), `knowledge/00-INDEX.md`, the
   canonical docs in `knowledge/canonical/` (OPERATING-MANUAL-v4 first), and the newest HANDOFF in `knowledge/current/`.
8. Reply with: the commit hash; the MANIFEST check result (N/N md5 OK); the CLAUDE-AR integrity marker line you found at
   its end; a 5-line summary of the current state from the newest handoff; and anything that looked wrong. Then wait for
   my instructions. Do not start pack work on your own.

Standing rules for this repo: personal use only — the repo stays private and nothing is published; never commit secrets,
.mcpack files or worlds; the witness rule in CLAUDE-AR §4 applies to everything I report from my PS5.
```

---

## B. EVERY LATER SYNC (paste each time a new zip is uploaded)

```text
Knowledge sync. A new zip is in `_inbox/` (use the newest AR-Knowledge-*.zip). At ultracode effort:
1. Unzip outside the repo; check every MANIFEST row (bytes + md5); stop on any failure.
2. Replace `knowledge/`, `prompts/`, `claude-settings/` with the zip's versions (deleted files go too — the zip is the
   whole mirror). Keep the repo CLAUDE.md; if `claude-settings/CLAUDE.md.repo-root` changed, show me the difference
   and merge the "This venue" section. Merge any new keys from `claude-settings/settings.json` into `.claude/settings.json`.
3. Delete the zip; commit as `knowledge sync <stamp> — <headline from knowledge/00-INDEX.md>`.
4. Re-read `knowledge/CLAUDE-AR.md` (check its integrity marker) and the newest handoff in `knowledge/current/`.
5. Reply: commit hash, N/N md5 OK, what changed (files added / changed / removed, counted), and the newest handoff's open
   list in 5 lines. Then wait.
```

---

## C. Better long-term option (removes the manual upload)
When you start a NEW cloud session in the Claude app for AbsolutRealism work, attach this GitHub repository to that
session (the repository picker when the session is created). Then that session can commit the knowledge mirror itself on
every ship, and step "How the zip gets into the repo" disappears. The current session was started without the repo, so it
cannot push (GitHub answers "access to this repository is not enabled for this session").
