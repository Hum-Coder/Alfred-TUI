from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

WORKSPACE_BASE = Path.home() / ".ctf_workspaces"
NEXT_DIR_PATH = Path.home() / ".config" / "alfred" / "next_dir"


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9_-]", "_", text.lower().strip()).strip("_")


def parse_connection(challenge: dict) -> tuple[str, int] | None:
    raw = challenge.get("connection_info") or ""
    if not raw:
        m = re.search(
            r"(?:Connection|Host|nc)[:\s]+([\w.-]+)[:\s]*(\d+)",
            challenge.get("description", ""),
        )
        if m:
            return m.group(1), int(m.group(2))
        return None
    m = re.match(r"([\w.-]+)[:\s]*(\d+)", raw)
    if m:
        return m.group(1), int(m.group(2))
    return None


def ctf_name_from_url(url: str) -> str:
    name = url.replace("http://", "").replace("https://", "").split(".")[0]
    return name or "ctf"


async def create_workspace(client, state, challenge_id: int) -> Path:
    data = await client.get_challenge(challenge_id)
    ctf = _slugify(ctf_name_from_url(state.get_config().url))
    cat = _slugify(data.get("category", "uncategorized"))
    slug = _slugify(data["name"])
    ws_dir = WORKSPACE_BASE / ctf / cat / slug
    ws_dir.mkdir(parents=True, exist_ok=True)

    files = data.get("files", [])
    if files:
        print(f"  Downloading {len(files)} attachment(s)...")
        await client.download_files(files, ws_dir)
        for f in ws_dir.iterdir():
            if f.suffix in (".zip", ".tar", ".tar.gz", ".tgz"):
                print(f"  Extracting {f.name}...")
                shutil.unpack_archive(str(f), str(ws_dir))
                f.unlink()

    _generate_solve_py(data, ws_dir)
    return ws_dir


def _generate_solve_py(challenge: dict, dest: Path):
    conn = parse_connection(challenge)
    host, port = conn if conn else ("", 0)
    name = challenge["name"]
    cat = challenge.get("category", "")
    cid = challenge["id"]

    lines = [
        "from pwn import *",
        "",
        'context.log_level = "debug"',
        "",
        f"# {name} — {cat}",
    ]

    if host and port:
        lines += [
            "",
            f"def connect():",
            f'    return remote("{host}", {port})',
        ]

    lines += [
        "",
        "def exploit():",
        "    # TODO: implement exploit",
        "    pass",
        "",
        "",
        'if __name__ == "__main__":',
        "    exploit()",
    ]

    (dest / "solve.py").write_text("\n".join(lines) + "\n")
    print(f"  Generated solve.py")


def connect_nc(challenge: dict):
    conn = parse_connection(challenge)
    if not conn:
        print("No connection info for this challenge.")
        sys.exit(1)
    host, port = conn
    print(f"Connecting to {host}:{port}...")
    try:
        subprocess.run(["nc", host, str(port)], check=True)
    except FileNotFoundError:
        subprocess.run(["ncat", host, str(port)], check=True)


def write_next_dir(path: Path):
    NEXT_DIR_PATH.parent.mkdir(parents=True, exist_ok=True)
    NEXT_DIR_PATH.write_text(str(path.resolve()))


def exit_open(path: Path):
    write_next_dir(path)
    print(f"Workspace: {path}")
    sys.exit(110)
