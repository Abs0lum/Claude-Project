# AbsolutRealism — repo CLAUDE.md

The full law for every Claude session in this repo is imported here:

@knowledge/CLAUDE-AR.md

## This venue (Claude Code on the GitHub repo / laptop)
- This session cannot see the claude.ai Project. Its knowledge is mirrored here: `knowledge/` (canonical docs, the newest
  handoff in `knowledge/current/`, logs, memory, tools) and `prompts/`. Read `knowledge/00-INDEX.md` for the map.
- Start every action turn with the start-of-session check (CLAUDE-AR §6): `git log --oneline -15`, `git status`, the tails
  of `knowledge/logs/phase_log.md`, `decision_journal.md`, `intake_ledger.md`, and the newest handoff.
- Effort: ultracode on (`/effort ultracode`); `.claude/settings.json` carries `"ultracode": true` and `"effortLevel": "xhigh"`.
- Knowledge sync: a new mirror zip arrives in `_inbox/` (or is given as a Drive link). Run the sync procedure in
  `prompts/claude-code-github-paste.md` §B: verify every md5 in `MANIFEST.json`, replace `knowledge/`, `prompts/`,
  `claude-settings/`, keep this file's venue section, commit "knowledge sync <date> <headline>", delete the zip.
- Never commit secrets (`_intake/secrets/`, tokens, `.env`), `.mcpack` files or worlds. The repo stays private.
