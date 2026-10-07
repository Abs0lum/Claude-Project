# SANDBOX SAFETY PROTOCOL — stopping points, the recoverable delete, the failsafe (law since 2026-10-03 02:16–02:28 CT)

His rulings (Abs0lum, 10-03): *stop, verify the work, disconnect from the sandbox, start again* at points of my own choosing · *the garbage folder is the recoverable delete* · *clear the sandbox into my Drive when necessary, with instant recovery* · *a folder you can DUMP into but never DELETE from — a failsafe holding every current, correct detail and file for the aftermath of a failure on either side* · *I upload everything correct and current to Drive occasionally; I'm giving you the same space* · *my free space is 5 TB — don't argue it* · *maintain the three-minute update interval*.

## 1. The three layers
| Layer | Where | What it does | Proof |
|---|---|---|---|
| **Recoverable delete** | `tools/pw_safe.py`, loaded into every python process by `~/.local/lib/python3.11/site-packages/usercustomize.py`; `/root/.local/bin/rm` + `mv` shims first on PATH | `shutil.rmtree`, `os.remove/unlink`, `Path.unlink` and the shell `rm` inside `/home/claude` become MOVES into `_garbage/<utc stamp>/<path>`, logged in `_logs/pw_safe_ledger.md`. Real deletes only outside the workspace, in dot-dirs, inside `_garbage` itself, or with `PW_ALLOW_DELETE=1`. Calls with `dir_fd` (rmtree's internals) are never guarded; `rmdir` keeps its semantics (an empty dir has nothing to recover) | `python3 tools/pw_safe.py --selftest` 10/10 |
| **The failsafe (append-only)** | `/home/claude/_failsafe/` + Drive `AR-Failsafe` | `tools/failsafe.py snapshot NOTE` streams a md5-verified tar of the RECORD (logs, journal, ledgers, docs, handoffs, every tool, root docs, every build manifest + PW-DEPENDENCIES, the gofile folder records — never secrets; bulk images / >4 MiB dumps listed but left out) to Drive with a README that says how to restore from Drive alone; `builds NAME…` uploads each frozen build dir ONCE; `restore` / `restore-build` pull members back md5-checked. Locally every delete, unlink, rmtree, rmdir, rename or move-out under `_failsafe/` raises (`PW_ALLOW_DELETE` included); the shims refuse. The tool has no update or delete call | self-test covers the refusals; snapshot #1 `failsafe-20261003-072919.tar` 67.7 MiB verified; round trip (archive → restore → md5) proven |
| **Clearing the sandbox** | `tools/garbage_tar_to_drive.py` → Drive `AR-Garbage-Archives`; `tools/garbage_restore.py` | each `_garbage/<dir>` streamed as one tar, md5 + size + manifest verified on Drive BEFORE the local copy goes; selective streamed restore. The quarantine folder is never archived | 86 folders / 7.4 GB archived 10-03 02:20–02:48; the sandbox went from 1.4 GB free to 6.8 GB |

## 2. Stopping points (SP)
At the end of every work package, before any risky operation, and at least once an hour:
1. **STOP** — nothing new starts.
2. **VERIFY** — the gates for what was produced: node tests, the load gate, md5 of delivered bytes vs the ledger, frozen build dirs untouched, the body/elevation gates of the server probes.
3. **DISCONNECT** — no server running (kill by PID, never `pkill -f`), background jobs finished or logged, phase log + decision journal written, `tools/failsafe.py snapshot "<why>"`.
4. **RESTART** — the amnesia check from disk (§3 of the custom instructions), then the next package from the queue.
A stopping point is written into `_logs/phase_log.md` as `SP: …` and into the status board.

## 3. The incident that proved the layers (10-03 02:20 CT)
Minutes after the guard went live, the Drive archiver removed a verified folder and Python's `rmtree` internals passed the guard a bare entry name (`_bds`) relative to an open directory handle. The first guard build resolved it against the working directory and moved the real `_bds` (the test server, its logs, the pristine world) into `_garbage`. A plain delete would have failed harmlessly; the guard had turned a failing call into a successful one on the wrong target. Recovered with one `mv`; fixed (dir_fd calls pass through; rmdir unchanged; remove/unlink move FILES only); the exact scenario is a regression test. **Lesson: a safety wrapper must keep the original call's failure modes.**

## 4. What a fresh session does after a failure
1. Drive → `AR-Failsafe` → the newest `failsafe-<stamp>-README.md` says what the snapshot holds and how to restore.
2. Untar `failsafe-<stamp>.tar` into a fresh `/home/claude` (or `tools/failsafe.py restore <stamp> …` from a sandbox with the OAuth files).
3. Frozen builds: `AR-Failsafe/builds/<name>.tar`; delivered packs: the gofile folder in `_intake/gofile-folder-*.txt` with md5s in `_logs/delivery_ledger.md`.
4. Read `_docs/recheck/STATUS-BOARD.md` and the newest `_docs/handoff/HANDOFF-*.md`, then the decision journal's last entries.
