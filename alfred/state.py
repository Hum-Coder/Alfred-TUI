import json
import os
import threading
from dataclasses import dataclass, field, asdict
from typing import Optional

CONFIG_DIR = os.path.expanduser("~/.config/alfred")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


@dataclass
class Config:
    url: str = ""
    token: str = ""
    username: str = ""


@dataclass
class Challenge:
    id: int
    name: str
    category: str
    value: int
    solved_by_me: bool = False
    description: str = ""
    connection_info: str = ""
    solves: int = 0
    files: list = field(default_factory=list)
    hints: list = field(default_factory=list)


@dataclass
class ScoreboardEntry:
    pos: int
    name: str
    score: int


@dataclass
class AppState:
    config: Config = field(default_factory=Config)
    challenges: list[Challenge] = field(default_factory=list)
    scoreboard: list[ScoreboardEntry] = field(default_factory=list)
    me: Optional[str] = None


class StateManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._state = AppState()
        self._load_config()

    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                data = json.load(f)
            with self._lock:
                self._state.config = Config(**data)

    def save_config(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with self._lock:
            data = asdict(self._state.config)
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def get_config(self) -> Config:
        with self._lock:
            return Config(**asdict(self._state.config))

    def set_config(self, url: str, token: str, username: str = ""):
        with self._lock:
            self._state.config = Config(url=url, token=token, username=username)
        self.save_config()

    def get_challenges(self) -> list[Challenge]:
        with self._lock:
            return list(self._state.challenges)

    def set_challenges(self, challenges: list[Challenge]):
        with self._lock:
            self._state.challenges = challenges

    def get_scoreboard(self) -> list[ScoreboardEntry]:
        with self._lock:
            return list(self._state.scoreboard)

    def set_scoreboard(self, scoreboard: list[ScoreboardEntry]):
        with self._lock:
            self._state.scoreboard = scoreboard

    def set_me(self, name: str):
        with self._lock:
            self._state.me = name
