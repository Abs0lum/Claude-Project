#!/usr/bin/env python3
"""gofile_ship.py — upload a .mcpack to the session's gofile delivery folder and run the DELIVERY LAW gate:
   (1) server md5 == local md5  (2) a headless-Chromium browser download is byte-exact.
Credentials are read from the session brief at runtime and NEVER printed.
Usage: gofile_ship.py [--new-folder NAME | --folder ID] FILE [FILE ...]   |   gofile_ship.py --delete-folder ID
       (09-23: every file's verdict is printed and written to the ledger the moment it finishes, so a timed-out
        batch still leaves a record; the browser check waits at most 240 s and retries once.)
       -> prints per-file verdict + download page; appends to _logs/delivery_ledger.md
       (09-29 D-C281: every .mcpack is Molang-linted BEFORE upload; any error refuses the file unless
        --allow-molang-errors is passed, which is logged to the ledger.)
       --new-folder creates a fresh public folder under the guest account (the brief's folder expires) and records its
       id + share code in _intake/gofile-folder-<NAME>.txt (never the token).
"""
import time, hashlib, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint                                   # D-C281 pre-upload Molang gate

BRIEF = Path("/home/claude/_intake/session-brief-2026-09-20-C.txt")
LEDGER = Path("/home/claude/_logs/delivery_ledger.md")

def creds():
    t = BRIEF.read_text(encoding="utf-8")
    folder = re.search(r"folderId ([0-9a-f-]{36})", t).group(1)
    token = re.search(r"guestToken (\S+)", t).group(1)
    server = re.search(r"https://(store-[a-z0-9-]+\.gofile\.io)/contents/uploadfile", t).group(1)
    return folder, token, server

def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()

def api(method, url, token, payload=None):
    cmd = ["curl", "-sS", "-X", method, "-H", f"Authorization: Bearer {token}"]
    if payload is not None: cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(payload)]
    r = subprocess.run(cmd + [url], capture_output=True, text=True, timeout=120)
    try: return json.loads(r.stdout)
    except Exception: return {"status": "curl-failed", "raw": r.stdout[:200]}

def new_folder(token, name):
    acc = api("GET", "https://api.gofile.io/accounts/getid", token)
    account_id = acc["data"]["id"]
    root = api("GET", f"https://api.gofile.io/accounts/{account_id}", token)["data"]["rootFolder"]
    made = api("POST", "https://api.gofile.io/contents/createFolder", token, {"parentFolderId": root, "folderName": name})
    d = made["data"]; fid = d["id"]; code = d.get("code")
    for _ in range(3):                                   # D-C358: the public switch must SUCCEED (his 00:23: a private folder)
        ok = api("PUT", f"https://api.gofile.io/contents/{fid}/update", token, {"attribute": "public", "attributeValue": "true"})
        if ok.get("status") == "ok": break
        time.sleep(3)
    else: raise SystemExit(f"REFUSED: folder {name} could not be made public")
    Path(f"/home/claude/_intake/gofile-folder-{name}.txt").write_text(f"folderId {fid}\ncode {code}\npage https://gofile.io/d/{code}\n", encoding="utf-8")
    return fid, code

def upload(path, folder, token, server):
    cmd = ["curl", "-sS", "-H", f"Authorization: Bearer {token}", "-F", f"file=@{path}", "-F", f"folderId={folder}",
           f"https://{server}/contents/uploadfile"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    try: return json.loads(r.stdout)
    except Exception: return {"status": "curl-failed", "raw": r.stdout[:300] + r.stderr[:300]}

def browser_download(direct_link, token, expect_bytes, expect_md5):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = "/opt/pw-browsers/chromium" if os.path.isdir("/opt/pw-browsers/chromium") else None
        kwargs = {"headless": True}
        if exe and os.path.exists(os.path.join(exe, "chrome")): kwargs["executable_path"] = os.path.join(exe, "chrome")
        try: browser = p.chromium.launch(**kwargs)
        except Exception: browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(accept_downloads=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36")
        ctx.add_cookies([{"name": "accountToken", "value": token, "domain": ".gofile.io", "path": "/"}])
        page = ctx.new_page()
        wait_ms = int(min(240, 60 + expect_bytes / 1e6) * 1000)      # scaled by size: 60 s + 1 s per MB, capped at 240 s
        with page.expect_download(timeout=wait_ms) as dl:
            try: page.goto(direct_link, timeout=wait_ms, wait_until="commit")
            except Exception: pass   # goto raises "Download is starting" — that is the success path
        d = dl.value
        tmp = Path(tempfile.mkdtemp()) / "dl.bin"
        d.save_as(str(tmp))
        got = tmp.read_bytes()
        ok = len(got) == expect_bytes and hashlib.md5(got).hexdigest() == expect_md5
        browser.close()
        try: tmp.unlink()
        except Exception: pass
        return ok, len(got)

def main():
    folder, token, server = creds()
    args = sys.argv[1:]
    if args and args[0] == "--new-folder":
        folder, code = new_folder(token, args[1]); args = args[2:]
        print(f"new public folder: https://gofile.io/d/{code}", flush=True)
    elif args and args[0] == "--folder":
        folder = args[1]; args = args[2:]
    elif args and args[0] == "--delete-folder":
        r = api("DELETE", "https://api.gofile.io/contents", token, {"contentsId": args[1]})
        print(f"delete folder {args[1]}: {r.get('status')}", flush=True)
        with LEDGER.open("a", encoding="utf-8") as fh: fh.write(f"- {time.strftime('%Y-%m-%d %H:%M')} FOLDER {args[1]} DELETED ({r.get('status')})\n")
        return
    allow_molang = "--allow-molang-errors" in args          # explicit, logged override only
    args = [a for a in args if a != "--allow-molang-errors"]
    lines = []
    def record(line):
        LEDGER.parent.mkdir(exist_ok=True)
        with LEDGER.open("a", encoding="utf-8") as fh: fh.write(line + "\n")
    for f in args:
        f = Path(f); local = md5(f); size = f.stat().st_size
        if f.suffix.lower() in (".mcpack", ".zip", ".mcaddon"):
            # D-C281 standing ship gate: no pack leaves with a Molang string Bedrock cannot parse
            n_ml, e_ml = molang_lint.lint_pack(f)
            if e_ml and not allow_molang:
                print(f"REFUSED {f.name}: {len(e_ml)} Molang errors in {n_ml} strings (molang_lint) — not uploaded", flush=True)
                for rel, path, expr, err in e_ml[:10]: print(f"     {rel} | {path} | {err}", flush=True)
                record(f"- {time.strftime('%Y-%m-%d %H:%M')} {f.name} REFUSED: {len(e_ml)} Molang errors (molang_lint)"); continue
            print(f"MOLANG {f.name}: {n_ml} strings, {len(e_ml)} errors{' (OVERRIDE --allow-molang-errors)' if e_ml else ''}", flush=True)
            if e_ml: record(f"- {time.strftime('%Y-%m-%d %H:%M')} {f.name} MOLANG OVERRIDE: {len(e_ml)} errors shipped by explicit flag")
        t0 = time.time()
        res = upload(f, folder, token, server)
        if res.get("status") != "ok":
            print(f"FAIL {f.name}: upload {res.get('status')} {str(res)[:200]}", flush=True); record(f"- {f.name} UPLOAD FAILED {res.get('status')}"); continue
        d = res["data"]
        smd5 = d.get("md5"); fid = d.get("id") or d.get("fileId"); page = d.get("downloadPage"); name = d.get("name") or d.get("fileName")
        m_ok = (smd5 == local)
        srv = d.get("servers", [server])[0] if isinstance(d.get("servers"), list) else server
        if "." not in srv: srv = srv + ".gofile.io"
        direct = f"https://{srv}/download/web/{fid}/{name}"
        b_ok, got = False, "not run"
        for attempt in (1, 2):
            try: b_ok, got = browser_download(direct, token, size, local)
            except Exception as e: b_ok, got = False, f"error {str(e)[:120]}"
            if b_ok: break
        verdict = "PASS" if (m_ok and b_ok) else "FAIL"
        print(f"{verdict} {f.name}: {size:,} B md5 {local} · server md5 {'==' if m_ok else '!='} local · browser download {'byte-exact' if b_ok else f'MISMATCH ({got})'} · {time.time()-t0:.0f}s", flush=True)
        print(f"     page {page}  fileId {fid}", flush=True)
        record(f"- {time.strftime('%Y-%m-%d %H:%M')} {f.name} {size:,} B md5 {local} · server md5 {'OK' if m_ok else 'MISMATCH'} · browser {'byte-exact' if b_ok else 'MISMATCH'} · fileId {fid} · {page}")

if __name__ == "__main__":
    main()
