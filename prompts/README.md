# PROMPTS — every prompt in use for AbsolutRealism (2026-10-07)

| File | Where it goes | What changed |
|---|---|---|
| `project-custom-instructions-v2.6.md` | claude.ai → Project "Abs0lutRealism" → Instructions (replace v2.5 entirely) | + §0 effort law; knowledge mirror + SYNC-EVERYWHERE law; P12–P15 from the 10-06 regressions; amnesia check for repo venues; P6 = deliver files (not the old present_files tool); venue map adds Claude Code on GitHub; §11 his working rules; stale "07-06-07 handoff" note removed. Integrity marker v2.6. |
| `project-description-v3.md` | claude.ai → Project → Description (replace) | the old description still said "v1.2.36" and "v2 doc set" — now the current packs, CIVITAS, read order, mirror. |
| `user-preferences-v2.md` | claude.ai account settings → the personal preferences field (replace) | + EFFORT paragraph (highest effort, mechanism before fix, fallacy check, ultracode in Claude Code); + standing rules (personal use, security, versions, complete packs, 3-minute updates, sync everywhere). The `CLAUDE_CODE_EFFORT_LEVEL=max` line is dropped: it is an environment variable for Claude Code, not a chat preference — the settings file does that job now. |
| `cowork-global-instructions-v2.md` | Cowork → global instructions (replace) | finds the law in the folder or the Drive mirror; effort; persistent-folder logs; sync law. |
| `claude-code-github-paste.md` | the GitHub Claude Code chat (A once, B each sync) | new — the workaround for "Claude Code can't see the Project". |
| `../claude-settings/settings.json` | repo `.claude/settings.json` (merged by the paste) | `effortLevel: xhigh`, `ultracode: true`, thinking always on, 1 h prompt cache, secrets unreadable. |
| `../claude-settings/CLAUDE.md.repo-root` | repo `CLAUDE.md` (merged by the paste) | imports `knowledge/CLAUDE-AR.md`; venue notes. |
| `../knowledge/CLAUDE-AR.md` | read by every file-based venue | the full-length law v3.0 (no character limit). |
| `agent-templates/*.md` | reference for future subagent briefs | the 25 subagent briefs from 2026-10-06/07 (CIVITAS batches, palace, castles, Academy II, skyways, furniture, acacia, skirt tint, households & dynasty, plateau). |

## Notes on effort settings (checked against the Claude Code settings reference, 2026-10-07)
- `effortLevel` accepts `low`, `medium`, `high`, `xhigh`. `ultracode: true` (or `/effort ultracode`, or `--effort ultracode`)
  is the top mode; it needs a model that supports `xhigh`. `/effort ultracode off` needs Claude Code 2.1.284 or newer.
- The environment variable `CLAUDE_CODE_EFFORT_LEVEL` overrides the settings file when set.
- claude.ai chats have no effort switch in the instructions; the EFFORT paragraph sets the behaviour instead.
