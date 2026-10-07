#!/usr/bin/env python3
"""gofile_public_check.py — D-C358 (his 00:23 screenshot: 'This content is not publicly accessible'): open a delivery page as a
STRANGER (fresh browser, no account cookie) and report whether the file list shows. The delivery browser check used the account
cookie, so it passed on a private folder. Usage: gofile_public_check.py CODE [CODE ...]"""
import os, sys
from playwright.sync_api import sync_playwright


def check(codes):
    out = {}
    with sync_playwright() as p:
        exe = "/opt/pw-browsers/chromium/chrome"
        b = p.chromium.launch(headless=True, **({"executable_path": exe} if os.path.exists(exe) else {}))
        for c in codes:
            ctx = b.new_context(user_agent="Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Mobile Safari/537.36")
            pg = ctx.new_page()
            try:
                pg.goto(f"https://gofile.io/d/{c}", timeout=60000, wait_until="networkidle")
            except Exception: pass
            pg.wait_for_timeout(4000)
            txt = pg.inner_text("body")
            out[c] = ("PRIVATE" if "not publicly accessible" in txt else "PUBLIC" if ".mcpack" in txt else "UNKNOWN: " + txt[:120].replace("\n", " "))
            ctx.close()
        b.close()
    return out


if __name__ == "__main__":
    for c, s in check(sys.argv[1:]).items(): print(c, s)
