from __future__ import annotations

from pathlib import Path

import httpx
from typing import Any

from alfred.state import StateManager, Challenge, ScoreboardEntry


class CTFdClient:
    def __init__(self, state: StateManager):
        self.state = state
        self._http: httpx.AsyncClient | None = None

    async def _ensure_http(self) -> httpx.AsyncClient:
        if self._http and not self._http.is_closed:
            await self._http.aclose()
        cfg = self.state.get_config()
        self._http = httpx.AsyncClient(
            base_url=cfg.url,
            headers={"Authorization": f"Token {cfg.token}"},
            timeout=60,
        )
        return self._http

    async def close(self):
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    async def _get(self, path: str) -> dict[str, Any]:
        c = await self._ensure_http()
        r = await c.get(path)
        r.raise_for_status()
        body = r.json()
        if not body.get("success"):
            raise RuntimeError(f"API error: {body.get('message', r.text)}")
        return body["data"]

    async def _post(self, path: str, json: dict[str, Any]) -> dict[str, Any]:
        c = await self._ensure_http()
        r = await c.post(path, json=json)
        r.raise_for_status()
        body = r.json()
        if not body.get("success"):
            raise RuntimeError(f"API error: {body.get('message', r.text)}")
        return body["data"]

    async def download_files(self, files: list[dict], dest: Path):
        c = await self._ensure_http()
        for f in files:
            route = f.get("route", "")
            if not route:
                continue
            url = route if route.startswith("http") else route
            r = await c.get(url)
            r.raise_for_status()
            name = route.rsplit("/", 1)[-1]
            path = dest / name
            with open(path, "wb") as fh:
                fh.write(r.content)
            print(f"    Downloaded {name}")

    async def list_challenges(self) -> list[Challenge]:
        data = await self._get("/api/v1/challenges")
        challenges = [
            Challenge(
                id=c["id"],
                name=c["name"],
                category=c.get("category", ""),
                value=c.get("value", 0),
                solved_by_me=c.get("solved_by_me", False),
                solves=c.get("solves", 0),
            )
            for c in data
        ]
        self.state.set_challenges(challenges)
        return challenges

    async def get_challenge(self, challenge_id: int) -> dict[str, Any]:
        return await self._get(f"/api/v1/challenges/{challenge_id}")

    async def submit_flag(self, challenge_id: int, flag: str) -> str:
        data = await self._post(
            "/api/v1/challenges/attempt",
            {
                "challenge_id": challenge_id,
                "submission": flag,
            },
        )
        return data.get("status", "unknown")

    async def get_me(self) -> str | None:
        try:
            data = await self._get("/api/v1/users/me")
            return data.get("name")
        except Exception:
            return None

    async def get_scoreboard(self) -> list[ScoreboardEntry]:
        data = await self._get("/api/v1/scoreboard")
        entries = [
            ScoreboardEntry(pos=i + 1, name=e.get("name", ""), score=e.get("score", 0))
            for i, e in enumerate(data)
        ]
        self.state.set_scoreboard(entries)
        return entries
