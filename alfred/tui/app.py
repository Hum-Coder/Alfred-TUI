from __future__ import annotations

from textual.app import App
from textual.binding import Binding

from alfred.tui.screens import ChallengesList, DetailScreen, ScoreboardScreen, SettingsScreen
from alfred.tui.themes import THEMES, css_for_theme


CSS_LOCATION = "alfred-theme"


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

    def on_mount(self) -> None:
        self.push_screen("list")

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


def run():
    app = AlfredTUI()
    app.run()


if __name__ == "__main__":
    run()
