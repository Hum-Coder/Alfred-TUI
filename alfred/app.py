from __future__ import annotations

import argparse
import asyncio
import sys

from alfred.state import StateManager
from alfred.api import CTFdClient


def main():
    parser = argparse.ArgumentParser(
        prog="alfred",
        description="Headless CTF workspace engine — TUI + API client for CTFd",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all challenges")

    show = sub.add_parser("show", help="Show challenge details")
    show.add_argument("challenge_id", type=int)

    submit = sub.add_parser("submit", help="Submit a flag")
    submit.add_argument("challenge_id", type=int)
    submit.add_argument("flag", type=str)

    sub.add_parser("scoreboard", help="Show scoreboard")

    config = sub.add_parser("config", help="Set CTFd URL and API token")
    config.add_argument("--url", required=True)
    config.add_argument("--token", required=True)

    args = parser.parse_args()
    asyncio.run(_dispatch(args))


async def _dispatch(args: argparse.Namespace):
    state = StateManager()

    if args.command == "config":
        state.set_config(args.url, args.token)
        print(f"url={args.url}")
        print(f"token={args.token[:8]}...{args.token[-4:]}")
        return

    cfg = state.get_config()
    if not cfg.url or not cfg.token:
        print("Not configured. Run:  alfred config --url <URL> --token <TOKEN>")
        sys.exit(1)

    client = CTFdClient(state)
    try:
        if args.command == "list":
            await _cmd_list(client)
        elif args.command == "show":
            await _cmd_show(client, args.challenge_id)
        elif args.command == "submit":
            await _cmd_submit(client, args.challenge_id, args.flag)
        elif args.command == "scoreboard":
            await _cmd_scoreboard(client)
    finally:
        await client.close()


async def _cmd_list(client: CTFdClient):
    challenges = await client.list_challenges()
    if not challenges:
        print("No challenges found.")
        return
    for c in challenges:
        status = "✓" if c.solved_by_me else " "
        print(f"  [{status}] #{c.id:<4} {c.name:<30} {c.category:<12} {c.value}pts")


async def _cmd_show(client: CTFdClient, challenge_id: int):
    c = await client.get_challenge(challenge_id)
    print(f"ID:          #{c['id']}")
    print(f"Name:        {c['name']}")
    print(f"Category:    {c.get('category', '')}")
    print(f"Points:      {c.get('value', 0)}")
    print(f"Solves:      {c.get('solves', 0)}")
    print(f"Solved by me: {c.get('solved_by_me', False)}")
    print(f"Description:\n{c.get('description', '')}")
    conn = c.get("connection_info") or c.get("connection_info")
    if conn:
        print(f"Connection:  {conn}")
    hints = c.get("hints", [])
    if hints:
        print(f"Hints:       {len(hints)} available")


async def _cmd_submit(client: CTFdClient, challenge_id: int, flag: str):
    status = await client.submit_flag(challenge_id, flag)
    print(f"Submission result: {status}")


async def _cmd_scoreboard(client: CTFdClient):
    entries = await client.get_scoreboard()
    if not entries:
        print("Scoreboard is empty (no solves yet).")
        return
    print(f"{'#':<4} {'Name':<30} {'Score':<8}")
    print("-" * 44)
    for e in entries:
        print(f"{e.pos:<4} {e.name:<30} {e.score:<8}")


if __name__ == "__main__":
    main()
