from __future__ import annotations

from collections import defaultdict

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

from alfred.tui.themes import THEMES


def _group_by_category(challenges):
    groups = defaultdict(list)
    for c in challenges:
        groups[c.category].append(c)
    return dict(groups)


def _challenge_at_index(challenges, target_idx):
    """Return the challenge at a ListView index, accounting for category headers."""
    idx = 0
    for cat, items in _group_by_category(challenges).items():
        idx += 1
        for c in items:
            if idx == target_idx:
                return c
            idx += 1
    return None


def _populate_listview(lv: ListView, challenges: list, selected_id: int | None = None):
    lv.clear()
    groups = _group_by_category(challenges)
    idx = 0
    target_idx = 0
    for cat, items in groups.items():
        lv.append(ListItem(Label(f"  [bold]{cat}[/]", classes="category-header"), classes="category-header"))
        idx += 1
        for c in items:
            mark = "✓" if c.solved_by_me else "○"
            lv.append(ListItem(Label(f"  {mark} {c.name:<25} {c.value}pts")))
            if selected_id is not None and c.id == selected_id:
                target_idx = idx
            idx += 1
    if selected_id is not None:
        lv.index = target_idx


class ChallengesList(Screen):
    BINDINGS = [
        Binding("1", "switch_screen('detail')", "Detail", priority=True),
        Binding("2", "switch_screen('scoreboard')", "Scoreboard", priority=True),
        Binding("3", "switch_screen('settings')", "Settings", priority=True),
        Binding("ctrl+q", "app.quit", "Quit", priority=True),
        Binding("ctrl+t", "cycle_theme", "Theme", priority=True),
        Binding("j", "cursor_down", "", priority=True),
        Binding("k", "cursor_up", "", priority=True),
        Binding("up", "cursor_up", "", priority=True),
        Binding("down", "cursor_down", "", priority=True),
        Binding("enter", "select_challenge", "", priority=True),
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

    async def on_mount(self) -> None:
        client = self.app.client
        if client:
            try:
                await client.list_challenges()
            except Exception as e:
                self.notify(f"Failed to fetch challenges: {e}", severity="error")
        _populate_listview(self.query_one("#challenge-list", ListView), self.app.state.get_challenges())

    def action_select_challenge(self) -> None:
        lv = self.query_one("#challenge-list", ListView)
        if lv.index is not None:
            c = _challenge_at_index(self.app.state.get_challenges(), lv.index)
            if c:
                self.app._selected_challenge_id = c.id
                self.app.switch_screen("detail")

    def action_switch_screen(self, name: str) -> None:
        if name == "detail":
            challenges = self.app.state.get_challenges()
            if challenges and not hasattr(self.app, "_selected_challenge_id"):
                self.app._selected_challenge_id = challenges[0].id
        self.app.switch_screen(name)

    def action_cycle_theme(self) -> None:
        self.app.action_cycle_theme()

    def action_cursor_down(self) -> None:
        self.query_one("#challenge-list", ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one("#challenge-list", ListView).action_cursor_up()


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
        Binding("up", "cursor_up", "", priority=True),
        Binding("down", "cursor_down", "", priority=True),
    ]

    _challenge_data: dict | None = None

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
        yield Label(id="celebration", classes="celebration-hidden")
        yield Footer(id="footer")

    async def on_mount(self) -> None:
        challenges = self.app.state.get_challenges()
        selected_id = getattr(self.app, "_selected_challenge_id", None)
        if selected_id is None and challenges:
            selected_id = challenges[0].id
            self.app._selected_challenge_id = selected_id
        _populate_listview(
            self.query_one("#challenge-list", ListView),
            challenges,
            selected_id,
        )
        # _load_and_show is triggered by the Selected event from setting lv.index

    async def _load_and_show(self, challenge_id: int | None) -> None:
        if challenge_id is None:
            self.query_one("#status-bar", Label).update("  [dim]Select a challenge[/]")
            return
        client = self.app.client
        if client:
            try:
                self._challenge_data = await client.get_challenge(challenge_id)
            except Exception as e:
                self.notify(f"Failed to load challenge: {e}", severity="error")
                self._challenge_data = None
        else:
            self._challenge_data = None
        self._show_challenge(challenge_id)

    def _challenge_from_list(self, challenge_id: int):
        for c in self.app.state.get_challenges():
            if c.id == challenge_id:
                return c
        return None

    def _show_challenge(self, challenge_id: int) -> None:
        c = self._challenge_data
        list_c = self._challenge_from_list(challenge_id)

        self.query_one("#celebration", Label).update("")
        self.query_one("#celebration", Label).classes = "celebration-hidden"

        if not c:
            self.query_one("#status-bar", Label).update("  [dim]Challenge not found[/]")
            main = self.query_one("#main", VerticalScroll)
            main.remove_children()
            main.mount(Static("\n  [dim]Select a challenge from the sidebar or run alfred config first[/]"))
            return

        name = c.get("name", "?")
        category = c.get("category", "")
        value = c.get("value", 0)
        solved = c.get("solved_by_me", False)
        solved_str = "✓ Solved" if solved else "○ Unsolved"
        self.query_one("#status-bar", Label).update(
            f"  [b]{name}[/]  —  {category}  —  {value}pts  —  {solved_str}"
        )

        main = self.query_one("#main", VerticalScroll)
        main.remove_children()

        desc = c.get("description", "")
        conn = c.get("connection_info", "")
        files_list = c.get("files", [])
        hints_list = c.get("hints", [])
        solves = c.get("solves", 0)

        lines = [
            f"\n  [bold]{name}[/]",
            f"  {'─' * 50}",
            "",
            f"  {desc}",
        ]
        if conn:
            lines += ["", f"  [dim]Connection:[/] {conn}"]
        if files_list:
            file_names = [f.get("name", "?") if isinstance(f, dict) else str(f) for f in files_list]
            lines += ["", f"  [dim]Attachments:[/] " + ", ".join(f"📎 {f}" for f in file_names)]
        hint_count = len(hints_list) if isinstance(hints_list, list) else (hints_list or 0)
        if hint_count:
            lines += ["", f"  [dim]Hints:[/] {hint_count} available"]
        lines += ["", f"  [dim]Solves:[/] {solves}"]

        main.mount(Static("\n".join(lines)))
        main.mount(Static(""))
        main.mount(Input(placeholder="flag{...}", id="flag-input", classes="flag-input"))
        main.mount(Button("Submit (Ctrl+S)", id="submit-btn", variant="primary"))
        main.mount(Static(""))

        if list_c:
            slug = list_c.name.lower().replace(" ", "_")
            ws_path = f"~/.ctf_workspaces/localhost_8000/{list_c.category.lower()}/{slug}"
            main.mount(Static(f"  [dim]Workspace:[/] {ws_path}"))
            main.mount(Button("Create Workspace (Ctrl+W)", id="workspace-btn", variant="default"))

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        idx = self.query_one("#challenge-list", ListView).index
        if idx is not None:
            c = _challenge_at_index(self.app.state.get_challenges(), idx)
            if c:
                self.app._selected_challenge_id = c.id
                await self._load_and_show(c.id)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit-btn":
            await self.action_submit_flag()
        elif event.button.id == "workspace-btn":
            await self.action_workspace()

    async def action_submit_flag(self) -> None:
        inp = self.query_one("#flag-input", Input)
        val = inp.value.strip()
        if not val:
            self.notify("Enter a flag first!", severity="warning")
            return

        challenge_id = getattr(self.app, "_selected_challenge_id", None)
        if challenge_id is None:
            self.notify("No challenge selected", severity="error")
            return

        client = self.app.client
        if not client:
            self.notify("API not configured — go to Settings", severity="error")
            return

        try:
            status = await client.submit_flag(challenge_id, val)
        except Exception as e:
            self.notify(f"Submit failed: {e}", severity="error")
            return

        cel = self.query_one("#celebration", Label)
        inp.value = ""

        if status == "correct":
            cel.classes = "celebration-correct"
            cel.update("  🎉 CORRECT!  ")
            self.notify("🎉 Correct flag!", severity="information", timeout=3)
            # refresh list to update solved status
            if client:
                try:
                    await client.list_challenges()
                except Exception:
                    pass
        elif status == "already_solved":
            cel.classes = "celebration-already"
            cel.update("  ⚠ Already solved  ")
            self.notify("⚠ Already solved", severity="warning", timeout=3)
        else:
            cel.classes = "celebration-incorrect"
            cel.update("  ✗ INCORRECT  ")
            self.notify("✗ Incorrect flag", severity="error", timeout=3)

    async def action_workspace(self) -> None:
        from alfred.workspace import create_workspace
        challenge_id = getattr(self.app, "_selected_challenge_id", None)
        if challenge_id is None:
            self.notify("No challenge selected", severity="error")
            return
        client = self.app.client
        if not client:
            self.notify("API not configured", severity="error")
            return
        try:
            ws_dir = await create_workspace(client, self.app.state, challenge_id)
            self.notify(f"Workspace: {ws_dir}", timeout=3)
        except Exception as e:
            self.notify(f"Workspace failed: {e}", severity="error")

    def action_switch_screen(self, name: str) -> None:
        self.app.switch_screen(name)

    def action_cycle_theme(self) -> None:
        self.app.action_cycle_theme()

    def action_cursor_down(self) -> None:
        self.query_one("#challenge-list", ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one("#challenge-list", ListView).action_cursor_up()


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

    async def on_mount(self) -> None:
        client = self.app.client
        if client:
            try:
                await client.get_scoreboard()
            except Exception as e:
                self.notify(f"Failed to fetch scoreboard: {e}", severity="error")
        self._render_scoreboard()

    def _render_scoreboard(self) -> None:
        rl = self.query_one("#scoreboard-log", RichLog)
        rl.clear()
        entries = self.app.state.get_scoreboard()
        if not entries:
            rl.write("")
            rl.write("  [dim]No scoreboard data yet.[/]")
            return

        rl.write("")
        rl.write("  [bold]Rank  Team                          Score   Gap[/]")
        rl.write("  " + "─" * 56)
        for i, e in enumerate(entries):
            prev_score = entries[i - 1].score if i > 0 else e.score
            gap = prev_score - e.score
            gap_str = f"-{gap}" if gap > 0 and i > 0 else ""
            gap_display = f"  {gap_str}" if gap_str else ""
            rl.write(f"  #{e.pos:<3}  {e.name:<30}  {e.score:<5}{gap_display:<8}")

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
        with VerticalScroll(id="main"):
            yield Static("\n  [bold]CTFd Instance[/]")
            cfg = self.app.state.get_config()
            yield Input(placeholder="URL", id="setting-url", value=cfg.url)
            yield Input(placeholder="API Token", id="setting-token", password=True, value=cfg.token)
            yield Input(placeholder="Username (for proximity alerts)", id="setting-username", value=cfg.username)
            yield Static("")
            yield Static("  [bold]Theme[/]")
            with ListView(id="theme-list"):
                for name in list(THEMES.keys()):
                    yield ListItem(Label(name))
            yield Static("")
            yield Button("Save (Ctrl+S)", id="save-btn", variant="primary")
            yield Button("Back to Challenges", id="back-btn")
        yield Footer(id="footer")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-btn":
            await self.action_save_settings()
        elif event.button.id == "back-btn":
            self.app.switch_screen("list")

    async def action_save_settings(self) -> None:
        url = self.query_one("#setting-url", Input).value
        token = self.query_one("#setting-token", Input).value
        username = self.query_one("#setting-username", Input).value
        self.app.state.set_config(url, token, username)
        self.notify(f"Saved — restart TUI to pick up new config")

    def action_switch_screen(self, name: str) -> None:
        self.app.switch_screen(name)
