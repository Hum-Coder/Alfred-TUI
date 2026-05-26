from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from alfred.api import CTFdClient
from alfred.state import StateManager, Challenge, ScoreboardEntry


@dataclass
class Notification:
    kind: str
    message: str


class Poller:
    def __init__(
        self,
        client: CTFdClient,
        state: StateManager,
        on_notify: Callable[[Notification], None],
        interval: int = 30,
    ):
        self.client = client
        self.state = state
        self.on_notify = on_notify
        self.interval = interval
        self._prev_challenges: dict[int, int] = {}
        self._prev_scoreboard: list[ScoreboardEntry] = []
        self._prev_solved_by_me: dict[int, bool] = {}

    async def poll(self) -> None:
        challenges: list[Challenge] = []
        try:
            challenges = await self.client.list_challenges()
        except Exception:
            return

        for c in challenges:
            prev_solves = self._prev_challenges.get(c.id, 0)
            prev_solved = self._prev_solved_by_me.get(c.id, False)

            if prev_solves == 0 and c.solves > 0:
                self.on_notify(Notification(
                    kind="first_blood",
                    message=f"First blood: {c.name} ({c.category}, {c.value}pts)",
                ))
            elif prev_solves > 0 and c.solves > prev_solves:
                self.on_notify(Notification(
                    kind="teammate_solve",
                    message=f"New solve on {c.name} — {c.solves} total",
                ))

            if not prev_solved and c.solved_by_me:
                self.on_notify(Notification(
                    kind="my_solve",
                    message=f"You solved {c.name}! ({c.value}pts)",
                ))

            self._prev_challenges[c.id] = c.solves
            self._prev_solved_by_me[c.id] = c.solved_by_me

        try:
            entries = await self.client.get_scoreboard()
        except Exception:
            return

        if not entries or not self._prev_scoreboard:
            self._prev_scoreboard = entries
            return

        me = self.state.get_config().username
        if not me:
            self._prev_scoreboard = entries
            return

        my_pos = None
        for i, e in enumerate(entries):
            if e.name == me:
                my_pos = i
                break

        if my_pos is None:
            self._prev_scoreboard = entries
            return

        PROXIMITY_THRESHOLD = 50

        if my_pos > 0:
            above = entries[my_pos - 1]
            gap_above = above.score - entries[my_pos].score
            prev_above = self._prev_scoreboard[my_pos - 1] if my_pos - 1 < len(self._prev_scoreboard) else None
            if gap_above <= PROXIMITY_THRESHOLD:
                if not prev_above or (above.score - entries[my_pos].score) != gap_above:
                    self.on_notify(Notification(
                        kind="proximity",
                        message=f"Only {gap_above} pts behind #{above.pos} {above.name}!",
                    ))

        if my_pos < len(entries) - 1:
            below = entries[my_pos + 1]
            gap_below = entries[my_pos].score - below.score
            prev_below = self._prev_scoreboard[my_pos + 1] if my_pos + 1 < len(self._prev_scoreboard) else None
            if gap_below <= PROXIMITY_THRESHOLD:
                if not prev_below or (entries[my_pos].score - below.score) != gap_below:
                    self.on_notify(Notification(
                        kind="proximity",
                        message=f"#{below.pos} {below.name} is {gap_below} pts behind — watch out!",
                    ))

        self._prev_scoreboard = entries
