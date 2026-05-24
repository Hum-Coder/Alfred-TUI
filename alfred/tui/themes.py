THEMES = {
    "Tokyo Night": {
        "primary": "#7aa2f7",
        "secondary": "#bb9af7",
        "accent": "#f7768e",
        "surface": "#1a1b26",
        "background": "#24283b",
        "text": "#c0caf5",
        "text_dim": "#565f89",
        "success": "#9ece6a",
        "warning": "#e0af68",
        "error": "#f7768e",
    },
    "Gruvbox": {
        "primary": "#83a598",
        "secondary": "#d3869b",
        "accent": "#fb4934",
        "surface": "#282828",
        "background": "#1d2021",
        "text": "#ebdbb2",
        "text_dim": "#928374",
        "success": "#b8bb26",
        "warning": "#fabd2f",
        "error": "#fb4934",
    },
    "Catppuccin Mocha": {
        "primary": "#89b4fa",
        "secondary": "#cba6f7",
        "accent": "#f38ba8",
        "surface": "#1e1e2e",
        "background": "#11111b",
        "text": "#cdd6f4",
        "text_dim": "#6c7086",
        "success": "#a6e3a1",
        "warning": "#f9e2af",
        "error": "#f38ba8",
    },
    "Nord": {
        "primary": "#88c0d0",
        "secondary": "#b48ead",
        "accent": "#bf616a",
        "surface": "#2e3440",
        "background": "#3b4252",
        "text": "#e5e9f0",
        "text_dim": "#616e88",
        "success": "#a3be8c",
        "warning": "#ebcb8b",
        "error": "#bf616a",
    },
    "Solarized Dark": {
        "primary": "#268bd2",
        "secondary": "#6c71c4",
        "accent": "#dc322f",
        "surface": "#002b36",
        "background": "#073642",
        "text": "#93a1a1",
        "text_dim": "#657b83",
        "success": "#859900",
        "warning": "#b58900",
        "error": "#dc322f",
    },
}


def css_for_theme(name: str) -> str:
    c = THEMES.get(name)
    if not c:
        c = THEMES["Tokyo Night"]
    return f"""
$background: {c["background"]};
$surface: {c["surface"]};
$text: {c["text"]};
$text-dim: {c["text_dim"]};
$primary: {c["primary"]};
$secondary: {c["secondary"]};
$accent: {c["accent"]};
$error: {c["error"]};
$success: {c["success"]};
$warning: {c["warning"]};
$foreground: {c["text"]};
$foreground-muted: {c["text_dim"]};
$foreground-darken-1: {c["text"]};
$panel: {c["surface"]};
$panel-lighten-1: {c["surface"]};
$panel-darken-1: {c["background"]};
$border: {c["primary"]};
$border-blurred: {c["text_dim"]};
$boost: {c["surface"]};
$footer-background: {c["surface"]};
$footer-foreground: {c["text_dim"]};
$scrollbar: {c["primary"]};
$scrollbar-background: {c["surface"]};

Screen {{
    background: $background;
    color: $text;
}}

#header {{
    background: $surface;
    color: $text;
    height: 1;
    dock: top;
}}

#sidebar {{
    background: $surface;
    width: 30;
    dock: left;
    overflow-y: auto;
}}

#main {{
    background: $background;
}}

#footer {{
    background: $surface;
    color: $text-dim;
    height: 2;
    dock: bottom;
}}

#status-bar {{
    background: $surface;
    height: 1;
    dock: top;
}}

.challenge-card:hover {{
    background: $primary 20%;
}}

.challenge-card.selected {{
    background: $primary 30%;
    border-left: solid $primary;
}}

.challenge-name {{
    color: $text;
}}

.challenge-value {{
    color: $primary;
}}

.challenge-solved {{
    color: $success;
}}

.challenge-unsolved {{
    color: $accent;
}}

.detail-label {{
    color: $text-dim;
}}

.detail-value {{
    color: $text;
}}

.flag-input {{
    background: $surface;
    color: $text;
    border: solid $primary;
}}

.scoreboard-row {{
    padding: 0 2;
}}

.scoreboard-row.highlight {{
    background: $primary 30%;
}}

Button {{
    background: $primary;
    color: $surface;
}}

Button:hover {{
    background: $secondary;
}}

#theme-list {{
    background: $surface;
}}

#settings-panel {{
    background: $surface;
}}
"""
