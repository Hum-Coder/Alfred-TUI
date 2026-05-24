from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    RichLog,
    Static,
)
from textual.binding import Binding

from alfred.tui.dummy_data import dummy_challenges, dummy_scoreboard
from alfred.tui.themes import THEMES, css_for_theme


class ChallengesList(Screen):
    BINDINGS = [
        Binding("1", "switch_screen('detail')", "Detail", priority=True),
        Binding("2", "switch_screen('scoreboard')", "Scoreboard", priority=True),
        Binding("3", "switch_screen('settings')", "Settings", priority=True),
        Binding("ctrl+q", "app.quit", "Quit", priority=True),
        Binding("ctrl+t", "cycle_theme", "Theme", priority=True),
        Binding("j", "cursor_down", "", priority=True),
        Binding("k", "cursor_up", "", priority=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        yield Label("  [b]Challenges[/]", id="status-bar")
        yield Horizontal(
            VerticalScroll(
                ListView(id="challenge-list"),
                id="sidebar",
            ),
            Vertical(id="main"),
        )
        yield Footer(id="footer")

    def on_mount(self) -> None:
        self._populate_challenges()

    def _populate_challenges(self) -> None:
        lv = self.query_one("#challenge-list", ListView)
        lv.clear()
        for c in dummy_challenges:
            mark = "✓" if c["solved"] else "○"
            lv.append(ListItem(Label(f"  {mark} {c['name']:<25} {c['value']}pts")))

    def action_switch_screen(self, name: str) -> None:
        self.app.switch_screen(name)

    def action_cycle_theme(self) -> None:
        names = list(THEMES.keys())
        current = getattr(self.app, "_current_theme", "Tokyo Night")
        idx = (names.index(current) + 1) % len(names)
        self.app._current_theme = names[idx]
        self.app.stylesheet = css_for_theme(names[idx])
        self.app.refresh_layout()

    def action_cursor_down(self) -> None:
        lv = self.query_one("#challenge-list", ListView)
        lv.action_cursor_down()

    def action_cursor_up(self) -> None:
        lv = self.query_one("#challenge-list", ListView)
        lv.action_cursor_up()


class DetailScreen(Screen):
    BINDINGS = [
        Binding("1", "switch_screen('list')", "List", priority=True),
        Binding("2", "switch_screen('scoreboard')", "Scoreboard", priority=True),
        Binding("3", "switch_screen('settings')", "Settings", priority=True),
        Binding("ctrl+q", "app.quit", "Quit", priority=True),
        Binding("ctrl+t", "cycle_theme", "Theme", priority=True),
        Binding("ctrl+s", "submit_flag", "Submit", priority=True),
        Binding("ctrl+w", "workspace", "Workspace", priority=True),
        Binding("j", "cursor_down", "", priority=True),
        Binding("k", "cursor_up", "", priority=True),
    ]

    selected_id: int = 1

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        yield Label(id="status-bar")
        yield Horizontal(
            VerticalScroll(
                ListView(id="challenge-list"),
                id="sidebar",
            ),
            VerticalScroll(id="main"),
        )
        yield Footer(id="footer")

    def on_mount(self) -> None:
        self._populate_sidebar()
        self._show_challenge(self.selected_id)

    def _populate_sidebar(self) -> None:
        lv = self.query_one("#challenge-list", ListView)
        lv.clear()
        for c in dummy_challenges:
            mark = "✓" if c["solved"] else "○"
            lv.append(ListItem(Label(f"  {mark} {c['name']:<25} {c['value']}pts")))
        lv.index = self.selected_id - 1

    def _show_challenge(self, cid: int) -> None:
        c = next((ch for ch in dummy_challenges if ch["id"] == cid), dummy_challenges[0])
        self.query_one("#status-bar", Label).update(
            f"  [b]{c['name']}[/]  —  {c['category']}  —  {c['value']}pts"
        )
        main = self.query_one("#main", VerticalScroll)
        main.remove_children()

        desc = c["description"]
        conn = c.get("connection_info", "")
        files = c.get("files", [])
        hints = c.get("hints", 0)

        lines = [
            f"\n  [bold]{c['name']}[/]",
            f"  {'─' * 50}",
            f"",
            f"  {desc}",
        ]
        if conn:
            lines += ["", f"  [dim]Connection:[/] {conn}"]
        if files:
            lines += ["", f"  [dim]Attachments:[/] " + ", ".join(f"📎 {f}" for f in files)]
        if hints:
            lines += ["", f"  [dim]Hints:[/] {hints} available"]
        lines += [
            "",
            f"  [dim]Solves:[/] {c['solves']}  [dim]Solved by me:[/] {'✓' if c['solved'] else '✗'}",
        ]

        main.mount(Static("\n".join(lines)))
        main.mount(Static(""))
        main.mount(Input(placeholder="flag{...}", id="flag-input", classes="flag-input"))
        main.mount(Button("Submit", id="submit-btn", variant="primary"))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        idx = self.query_one("#challenge-list", ListView).index
        if idx is not None:
            self.selected_id = dummy_challenges[idx]["id"]
            self._show_challenge(self.selected_id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit-btn":
            self.action_submit_flag()

    def action_submit_flag(self) -> None:
        inp = self.query_one("#flag-input", Input)
        if inp.value.strip():
            self.notify(f"Submitted: {inp.value}")

    def action_switch_screen(self, name: str) -> None:
        self.app.switch_screen(name)

    def action_cycle_theme(self) -> None:
        self.app.action_cycle_theme()

    def action_cursor_down(self) -> None:
        lv = self.query_one("#challenge-list", ListView)
        lv.action_cursor_down()

    def action_cursor_up(self) -> None:
        lv = self.query_one("#challenge-list", ListView)
        lv.action_cursor_up()


class ScoreboardScreen(Screen):
    BINDINGS = [
        Binding("1", "switch_screen('list')", "List", priority=True),
        Binding("2", "switch_screen('detail')", "Detail", priority=True),
        Binding("3", "switch_screen('settings')", "Settings", priority=True),
        Binding("ctrl+q", "app.quit", "Quit", priority=True),
        Binding("ctrl+t", "cycle_theme", "Theme", priority=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        yield Label("  [b]Scoreboard[/]", id="status-bar")
        yield VerticalScroll(RichLog(id="scoreboard-log", highlight=True), id="main")
        yield Footer(id="footer")

    def on_mount(self) -> None:
        self._render_scoreboard()

    def _render_scoreboard(self) -> None:
        rl = self.query_one("#scoreboard-log", RichLog)
        rl.clear()
        rl.write("")
        rl.write("  [bold]Rank  Team                          Score[/]")
        rl.write("  " + "─" * 48)
        for e in dummy_scoreboard:
            margin = "  "
            marker = ""
            if e["pos"] == 3:
                marker = "  ← you"
            rl.write(f"  #{e['pos']:<3}  {e['name']:<30}  {e['score']}{marker}")
        rl.write("")
        rl.write("  [dim]Press Ctrl+T to switch theme[/]")

    def action_switch_screen(self, name: str) -> None:
        self.app.switch_screen(name)


class SettingsScreen(Screen):
    BINDINGS = [
        Binding("1", "switch_screen('list')", "List", priority=True),
        Binding("2", "switch_screen('detail')", "Detail", priority=True),
        Binding("3", "switch_screen('scoreboard')", "Scoreboard", priority=True),
        Binding("ctrl+q", "app.quit", "Quit", priority=True),
        Binding("ctrl+t", "cycle_theme", "Theme", priority=True),
        Binding("ctrl+s", "save_settings", "Save", priority=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(id="header")
        yield Label("  [b]Settings[/]", id="status-bar")
        yield VerticalScroll(id="main")
        yield Footer(id="footer")

    def on_mount(self) -> None:
        main = self.query_one("#main", VerticalScroll)
        main.mount(Static("\n  [bold]CTFd Instance[/]"))
        main.mount(Input(placeholder="URL", id="setting-url", value="http://localhost:8000"))
        main.mount(Input(placeholder="API Token", id="setting-token", password=True))
        main.mount(Static(""))
        main.mount(Static("  [bold]Theme[/]"))
        tv = ListView(id="theme-list")
        for name in list(THEMES.keys()):
            tv.append(ListItem(Label(name)))
        main.mount(tv)
        main.mount(Static(""))
        main.mount(Button("Save (Ctrl+S)", id="save-btn", variant="primary"))
        main.mount(Button("Back to Challenges", id="back-btn"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            self.action_save_settings()
        elif event.button.id == "back-btn":
            self.app.switch_screen("list")

    def action_save_settings(self) -> None:
        url = self.query_one("#setting-url", Input).value
        token = self.query_one("#setting-token", Input).value
        self.notify(f"Saved: {url}")

    def action_switch_screen(self, name: str) -> None:
        self.app.switch_screen(name)
