"""Auto-setup a fresh CTFd instance with challenges and an API token."""
import sys
import re
import requests

BASE = "http://localhost:8000"
s = requests.Session()


def get_nonce(text):
    m = re.search(r'name="nonce"[^>]*value="([^"]+)"', text)
    return m.group(1) if m else ""


def ok(r):
    if not r.ok:
        return False
    return r.json().get("success", False)


# ── 1. Setup wizard ──
print("[1/4] Checking CTFd...")
setup_ses = requests.Session()
r = setup_ses.get(f"{BASE}/setup", allow_redirects=False)
if r.status_code == 302:
    print("  Already configured.")
    # Copy cookies to main session
    for c in setup_ses.cookies:
        s.cookies.set(c.name, c.value)
else:
    print("  Running setup wizard...")
    nonce = get_nonce(r.text)
    r = setup_ses.post(f"{BASE}/setup", data={
        "ctf_name": "NexusCTF Demo",
        "ctf_description": "Local testing instance",
        "user_mode": "users",
        "name": "admin",
        "email": "admin@alfred.ctf",
        "password": "admin",
        "challenge_visibility": "public",
        "account_visibility": "public",
        "score_visibility": "public",
        "registration_visibility": "public",
        "verify_emails": "false",
        "team_size": "",
        "ctf_theme": "core",
        "nonce": nonce,
    }, allow_redirects=False)
    if r.status_code != 302:
        print(f"  Setup failed: {r.status_code} {r.text[:200]}")
        sys.exit(1)
    for c in setup_ses.cookies:
        s.cookies.set(c.name, c.value)
    print("  Setup complete!")

# ── 2. Login as admin & get CSRF nonce ──
print("[2/4] Logging in as admin...")
r = s.get(f"{BASE}/login")
nonce = get_nonce(r.text)
r = s.post(f"{BASE}/login", data={"name": "admin", "password": "admin", "nonce": nonce}, allow_redirects=False)
if r.status_code != 302:
    print(f"  Login failed: {r.status_code}")
    sys.exit(1)
# Follow redirect
loc = r.headers.get("location", "/")
s.get(f"{BASE}{loc}" if loc.startswith("/") else loc)
print("  Logged in.")

# Set CSRF header for all subsequent API calls
s.headers.update({"CSRF-Token": nonce})

# ── 3. Create API token ──
print("[3/4] Creating API token...")
r = s.post(f"{BASE}/api/v1/tokens", json={"expiration": None, "description": "alfred dev"})
if ok(r):
    token = r.json()["data"]["value"]
    print(f"  Token: {token}")
else:
    print(f"  Token creation failed: {r.status_code} {r.text[:200]}")
    sys.exit(1)

# ── 4. Create sample challenges and flags ──
print("[4/4] Creating sample challenges...")
challenges = [
    ("Admin Panel", "Web",
     "The admin panel has a known session vulnerability. Recover the secret key to forge a cookie.",
     "admin-panel.ctf.local:443",
     500, "flag{s3ss10n_h4ck3d}"),
    ("RSA Oracle", "Crypto",
     "A remote oracle leaks partial plaintext. Recover the full message.\n\nHint: Check the padding scheme.",
     "",
     400, "flag{rs4_0r4cl3_br0k3n}"),
    ("Buffer Overflow", "Pwn",
     "A simple stack buffer overflow. Overwrite the return address to call win().",
     "pwn.ctf.local:1337",
     350, "flag{buff3r_0v3rfl0w}"),
]
for name, cat, desc, conn, val, flag in challenges:
    r = s.post(f"{BASE}/api/v1/challenges", json={
        "name": name, "category": cat, "description": desc,
        "connection_info": conn,
        "value": val, "state": "visible", "type": "standard",
    })
    if ok(r):
        cid = r.json()["data"]["id"]
        s.post(f"{BASE}/api/v1/flags", json={
            "challenge_id": cid, "content": flag, "type": "static", "data": "",
        })
        print(f"  #{cid}: {name} ({val}pts) — {flag}")
    else:
        print(f"  Skipped {name}")

# ── Verify token works ──
print("\nVerifying player token...")
r = requests.get(f"{BASE}/api/v1/challenges", headers={"Authorization": f"Token {token}"})
if ok(r):
    count = len(r.json()["data"])
    print(f"  Token works! {count} challenges visible.")

print(f"\n── Alfred setup complete ──")
FLAG1 = "flag{s3ss10n_h4ck3d}"
print(f"\npython -m alfred config --url {BASE} --token {token}")
print(f"python -m alfred list")
print(f"python -m alfred show 1")
print(f"python -m alfred submit 1 '{FLAG1}'")
