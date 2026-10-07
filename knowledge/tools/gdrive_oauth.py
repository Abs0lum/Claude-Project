#!/usr/bin/env python3
"""gdrive_oauth.py — D-C288: one-time sign-in for the 'AR Uploader' Google Cloud app, so this workspace can put files
byte-exact into Abs0lum's Google Drive (his 18:14-18:17 CT 09-29: every unique version in Drive, split to fit its rules).

Security design (his standing law: security first):
- Scope is ONLY https://www.googleapis.com/auth/drive.file: the app sees and changes only the files it creates itself,
  never the rest of his Drive. He can revoke at myaccount.google.com -> Security -> third-party connections.
- PKCE (RFC 7636, S256) + a random `state`: the one-time code he pastes back is useless without the verifier that
  never leaves this workspace, and a mismatched state is refused.
- Client file, pending PKCE data and the token live in _intake/secrets (dir 700, files 600). Nothing secret is ever
  printed: `finish` and `whoami` report only facts (scope, email, whether a refresh token exists).
- The app is in 'Testing' publishing status (publishing needs a home page + privacy policy URL), so Google expires the
  refresh token after 7 days; `whoami` says when a new sign-in is needed.

Usage:
  gdrive_oauth.py selftest              PKCE vector check (RFC 7636 appendix B)
  gdrive_oauth.py start                 prints the sign-in link (stores verifier + state)
  gdrive_oauth.py finish '<url|code>'   exchanges the code from the localhost address bar, stores the token
  gdrive_oauth.py whoami                refreshes and prints the Drive account email (proves the token works)
API: access_token() -> str (fresh access token, in memory only)"""
import base64, hashlib, json, os, secrets, sys, time, urllib.parse, urllib.request
from pathlib import Path

SECRETS = Path("/home/claude/_intake/secrets")
CLIENT = SECRETS / "gdrive_oauth_client.json"
PENDING = SECRETS / "gdrive_oauth_pending.json"
TOKEN = SECRETS / "gdrive_oauth_token.json"
SCOPE = "https://www.googleapis.com/auth/drive.file"
REDIRECT = "http://localhost"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
LOGIN_HINT = "jessed.perry@gmail.com"


def _write_private(path, obj):
    """Write JSON so that only this user can read it (umask-proof: create with 0600)."""
    SECRETS.mkdir(mode=0o700, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f)
    os.chmod(path, 0o600)


def _client():
    return json.load(open(CLIENT))["installed"]


def pkce_challenge(verifier):
    """S256 code challenge = base64url(sha256(verifier)) without padding (RFC 7636 §4.2)."""
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).decode("ascii").rstrip("=")


def _post(url, fields):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:                      # Google returns JSON errors; they carry no secret
        body = e.read().decode("utf-8", "replace")
        try: err = json.loads(body)
        except Exception: err = {"error": body[:200]}
        raise SystemExit(f"token endpoint refused: HTTP {e.code} {err.get('error')} {err.get('error_description', '')}")


def _pending_list():
    """Outstanding sign-in links (verifier + state), newest last; entries over 30 minutes old are dropped."""
    if not PENDING.exists():
        return []
    raw = json.load(open(PENDING))
    items = raw.get("pending", [raw] if "verifier" in raw else [])
    return [p for p in items if time.time() - p.get("created", 0) < 1800]


def start():
    c = _client()
    verifier = secrets.token_urlsafe(64)[:96]
    state = secrets.token_urlsafe(24)
    # D-C1006-OA: keep up to 3 outstanding links (each <= 30 min old) so a newer link never voids an older one
    _write_private(PENDING, {"pending": (_pending_list() + [{"verifier": verifier, "state": state, "created": time.time()}])[-3:]})
    q = {"client_id": c["client_id"], "redirect_uri": REDIRECT, "response_type": "code", "scope": SCOPE,
         "access_type": "offline", "prompt": "consent", "code_challenge": pkce_challenge(verifier),
         "code_challenge_method": "S256", "state": state, "login_hint": LOGIN_HINT}
    return AUTH_URL + "?" + urllib.parse.urlencode(q)


def finish(pasted):
    pend_all = _pending_list()
    if not pend_all:
        raise SystemExit("no sign-in link is outstanding (or it is over 30 minutes old); run start again")
    pend = pend_all[-1]
    pasted = pasted.strip()
    if pasted.startswith("http"):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(pasted).query)
        if "error" in qs:
            raise SystemExit(f"Google returned an error instead of a code: {qs['error'][0]}")
        code = qs.get("code", [""])[0]; state = qs.get("state", [""])[0]
        match = [p for p in pend_all if secrets.compare_digest(p["state"], state)]
        if match:
            pend = match[0]
        else:
            raise SystemExit("state mismatch - this address is not from the sign-in link I made; nothing stored")
    else:
        code = pasted
    if not code:
        raise SystemExit("no code found in what was pasted")
    c = _client()
    tok = _post(c["token_uri"], {"code": code, "client_id": c["client_id"], "client_secret": c["client_secret"],
                                 "redirect_uri": REDIRECT, "grant_type": "authorization_code", "code_verifier": pend["verifier"]})
    if "refresh_token" not in tok:
        raise SystemExit("Google gave no refresh token (sign-in must use the link with prompt=consent); nothing stored")
    _write_private(TOKEN, {"refresh_token": tok["refresh_token"], "scope": tok.get("scope"), "obtained": time.time()})
    os.remove(PENDING)                                         # single use
    return {"scope": tok.get("scope"), "refresh_token_stored": True, "access_expires_in_s": tok.get("expires_in")}


def access_token():
    """Fresh access token from the stored refresh token (kept in memory only)."""
    t = json.load(open(TOKEN)); c = _client()
    r = _post(c["token_uri"], {"client_id": c["client_id"], "client_secret": c["client_secret"],
                               "refresh_token": t["refresh_token"], "grant_type": "refresh_token"})
    return r["access_token"]


def whoami():
    req = urllib.request.Request("https://www.googleapis.com/drive/v3/about?fields=user(emailAddress,displayName)",
                                 headers={"Authorization": "Bearer " + access_token()})
    with urllib.request.urlopen(req, timeout=60) as r:
        u = json.load(r)["user"]
    age_days = (time.time() - json.load(open(TOKEN))["obtained"]) / 86400
    return {"email": u.get("emailAddress"), "name": u.get("displayName"), "signed_in_days_ago": round(age_days, 2),
            "new_sign_in_needed_after_days": 7}


def _selftest():
    # RFC 7636 Appendix B test vector
    assert pkce_challenge("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk") == "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
    print("gdrive_oauth self-test OK (RFC 7636 S256 vector)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    if cmd == "selftest": _selftest()
    elif cmd == "start": _selftest(); print(start())
    elif cmd == "finish": print(json.dumps(finish(sys.argv[2])))
    elif cmd == "whoami": print(json.dumps(whoami()))
    else: raise SystemExit(__doc__)
