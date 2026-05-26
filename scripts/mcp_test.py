"""Quick test: send a JSON-RPC request to the MCP server and print response."""
import json
import subprocess
import sys

MCP_ARGS = [sys.executable, "-m", "alfred.mcp_server"]


def send(req: dict) -> dict:
    payload = json.dumps(req)
    framed = f"Content-Length: {len(payload)}\r\n\r\n{payload}"
    proc = subprocess.run(
        MCP_ARGS,
        input=framed,
        capture_output=True,
        text=True,
        timeout=10,
    )
    out = proc.stdout.strip()
    resp_start = out.index("{") if "{" in out else 0
    return json.loads(out[resp_start:])


if __name__ == "__main__":
    # 1. Initialize
    print("=== Initialize ===")
    r = send({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    print(json.dumps(r, indent=2)[:300])

    # 2. List tools
    print("\n=== List Tools ===")
    r = send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    print(json.dumps(r, indent=2)[:500])

    # 3. List challenges
    print("\n=== List Challenges ===")
    r = send({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "alfred_list_challenges", "arguments": {}}})
    print(json.dumps(r, indent=2)[:500])

    # 4. Get workspace
    print("\n=== Get Workspace Path ===")
    r = send({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "alfred_get_workspace_path", "arguments": {"challenge_id": 1}}})
    print(json.dumps(r, indent=2)[:300])

    # 5. Submit flag
    print("\n=== Submit Flag (should require human) ===")
    r = send({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "alfred_submit_flag", "arguments": {"challenge_id": 1, "flag_string": "test"}}})
    print(json.dumps(r, indent=2)[:300])
