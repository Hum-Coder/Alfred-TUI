from __future__ import annotations

import asyncio

from textual.app import App
from textual.binding import Binding

from alfred.api import CTFdClient
from alfred.state import StateManager
from alfred.tui.screens import ChallengesList, DetailScreen, ScoreboardScreen, SettingsScreen
from alfred.tui.themes import THEMES, css_for_theme


CSS_LOCATION = "alfred-theme"
POLL_INTERVAL = 30


class AlfredTUI(App):
    CSS = css_for_theme("Tokyo Night")
    SCREENS = {
        "list": ChallengesList,
        "detail": DetailScreen,
        "scoreboard": ScoreboardScreen,
        "settings": SettingsScreen,
    }
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+t", "cycle_theme", "Theme"),
    ]

    _current_theme: str = "Tokyo Night"

    def __init__(self, state: StateManager, client: CTFdClient):
        super().__init__()
        self.state = state
        self.client = client
        self._poller = None
        self._poll_task = None

    def on_mount(self) -> None:
        self.push_screen("list")
        if self.client:
            self._start_poller()

    def on_unmount(self) -> None:
        if self._poll_task:
            self._poll_task.cancel()

    def _start_poller(self) -> None:
        async def _discover_me():
            try:
                me = await self.client.get_me()
                cfg = self.state.get_config()
                if me and not cfg.username:
                    self.state.set_config(cfg.url, cfg.token, username=me)
            except Exception:
                pass

        async def _poll_loop():
            from alfred.poller import Poller

            await _discover_me()
            poller = Poller(self.client, self.state, self._on_notify, POLL_INTERVAL)
            self._poller = poller
            while True:
                await poller.poll()
                await self.sleep(POLL_INTERVAL)

        self._poll_task = asyncio.create_task(_poll_loop())

    def _on_notify(self, notification) -> None:
        self.notify(notification.message, timeout=5)

    def action_cycle_theme(self) -> None:
        names = list(THEMES.keys())
        idx = (names.index(self._current_theme) + 1) % len(names)
        self._current_theme = names[idx]
        self.stylesheet.source[CSS_LOCATION] = (
            css_for_theme(names[idx]),
            False,
            0,
            "",
        )
        self.stylesheet.parse()
        self.refresh()
        self.notify(f"Theme: {self._current_theme}", timeout=2)


def run(state: StateManager | None = None, client: CTFdClient | None = None):
    app = AlfredTUI(state, client)
    app.run()
