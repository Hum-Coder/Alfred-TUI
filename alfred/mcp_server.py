from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from alfred.api import CTFdClient
from alfred.state import StateManager

POLICY_PATH = Path.home() / ".config" / "alfred" / "mcp_policy.json"

DEFAULT_POLICY = {
    "allow_flag_submission": "require_human",
    "sandbox_directory_jail": True,
}


def load_policy() -> dict:
    if POLICY_PATH.exists():
        return json.loads(POLICY_PATH.read_text())
    return dict(DEFAULT_POLICY)


def save_policy(policy: dict) -> None:
    POLICY_PATH.parent.mkdir(parents=True, exist_ok=True)
    POLICY_PATH.write_text(json.dumps(policy, indent=2))


TOOL_DEFINITIONS = [
    {
        "name": "alfred_list_challenges",
        "description": "Fetch available CTF categories, target names, point allocations, and state parameters.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "alfred_get_workspace_path",
        "description": "Returns the exact disk directory holding challenge binaries and exploit scripts.",
        "inputSchema": {
            "type": "object",
            "properties": {"challenge_id": {"type": "integer"}},
            "required": ["challenge_id"],
        },
    },
    {
        "name": "alfred_submit_flag",
        "description": "Submits a discovered flag string directly to the platform for validation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "challenge_id": {"type": "integer"},
                "flag_string": {"type": "string"},
            },
            "required": ["challenge_id", "flag_string"],
        },
    },
]


CRLF = "\r\n"


def respond(req: dict, result: Any = None, error: Any = None) -> str:
    resp = {"jsonrpc": "2.0", "id": req.get("id")}
    if error:
        resp["error"] = {"code": error[0], "message": error[1]}
    else:
        resp["result"] = result
    return json.dumps(resp)


def frame(msg: str) -> str:
    return f"Content-Length: {len(msg)}{CRLF}{CRLF}{msg}"


async def handle_request(req: dict, client: CTFdClient, state: StateManager) -> str:
    method = req.get("method", "")
    req_id = req.get("id")

    if method == "initialize":
        return respond(req, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "alfred", "version": "0.1.0"},
        })

    if method == "notifications/initialized":
        return ""

    if method == "tools/list":
        return respond(req, {"tools": TOOL_DEFINITIONS})

    if method == "tools/call":
        return await handle_tool_call(req, client, state)

    return respond(req, error=(-32601, f"Method not found: {method}"))


async def handle_tool_call(req: dict, client: CTFdClient, state: StateManager) -> str:
    params = req.get("params", {})
    name = params.get("name", "")
    args = params.get("arguments", {})

    if name == "alfred_list_challenges":
        try:
            challenges = await client.list_challenges()
            data = [
                {
                    "id": c.id,
                    "name": c.name,
                    "category": c.category,
                    "value": c.value,
                    "solved": c.solved_by_me,
                    "solves": c.solves,
                }
                for c in challenges
            ]
            return respond(req, {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]})
        except Exception as e:
            return respond(req, error=(-32603, str(e)))

    if name == "alfred_get_workspace_path":
        challenge_id = args.get("challenge_id")
        if not challenge_id:
            return respond(req, error=(-32602, "Missing challenge_id"))
        try:
            from alfred.workspace import ctf_name_from_url, _slugify
            data = await client.get_challenge(challenge_id)
            ctf = _slugify(ctf_name_from_url(state.get_config().url))
            cat = _slugify(data.get("category", "uncategorized"))
            slug = _slugify(data["name"])
            ws_dir = Path.home() / ".ctf_workspaces" / ctf / cat / slug

            policy = load_policy()
            if policy.get("sandbox_directory_jail", True):
                jail_base = Path.home() / ".ctf_workspaces"
                try:
                    ws_dir.resolve().relative_to(jail_base.resolve())
                except ValueError:
                    return respond(req, error=(-32000, "Access denied: outside sandbox directory jail"))

            return respond(req, {"content": [{"type": "text", "text": str(ws_dir)}]})
        except Exception as e:
            return respond(req, error=(-32603, str(e)))

    if name == "alfred_submit_flag":
        challenge_id = args.get("challenge_id")
        flag_string = args.get("flag_string")
        if not challenge_id or not flag_string:
            return respond(req, error=(-32602, "Missing challenge_id or flag_string"))

        policy = load_policy()
        allow = policy.get("allow_flag_submission", "require_human")

        if allow == "require_human":
            return respond(req, {
                "content": [{"type": "text", "text": "Flag submission requires human approval. Use the TUI to submit."}],
                "isError": True,
            })
        if allow is False:
            return respond(req, {
                "content": [{"type": "text", "text": "Flag submission is disabled by policy."}],
                "isError": True,
            })

        try:
            status = await client.submit_flag(challenge_id, flag_string)
            return respond(req, {"content": [{"type": "text", "text": f"Submission result: {status}"}]})
        except Exception as e:
            return respond(req, error=(-32603, str(e)))

    return respond(req, error=(-32601, f"Tool not found: {name}"))


async def main():
    state = StateManager()
    cfg = state.get_config()
    if not cfg.url or not cfg.token:
        err = json.dumps({
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": "Alfred not configured. Run: alfred config --url <URL> --token <TOKEN>"},
            "id": None,
        })
        sys.stdout.write(frame(err))
        sys.stdout.flush()
        return

    client = CTFdClient(state)
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

    async def read_line():
        return await reader.readline()

    while True:
        line = await read_line()
        if not line:
            break
        header = line.decode().strip()

        if not header.startswith("Content-Length:"):
            if header == "":
                continue
            else:
                continue

        length = int(header.split(":")[1].strip())

        # Read the empty line separator
        sep = await read_line()

        # Read the JSON body
        raw = await reader.readexactly(length)
        body = raw.decode()

        try:
            req = json.loads(body)
            resp = await handle_request(req, client, state)
            if resp:
                sys.stdout.write(frame(resp))
                sys.stdout.flush()
        except (ValueError, json.JSONDecodeError) as e:
            err = json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": str(e)}, "id": None})
            sys.stdout.write(frame(err))
            sys.stdout.flush()

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
