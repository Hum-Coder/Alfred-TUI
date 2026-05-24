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
Screen {{
    background: {c["background"]};
    color: {c["text"]};
}}

#header {{
    background: {c["surface"]};
    color: {c["text"]};
    height: 1;
    dock: top;
}}

#sidebar {{
    background: {c["surface"]};
    width: 30;
    dock: left;
    overflow-y: auto;
}}

#main {{
    background: {c["background"]};
}}

#footer {{
    background: {c["surface"]};
    color: {c["text_dim"]};
    height: 2;
    dock: bottom;
}}

#status-bar {{
    background: {c["surface"]};
    height: 1;
    dock: top;
}}

.challenge-card {{
    padding: 1;
    margin: 0 1;
}}

.challenge-card:hover {{
    background: {c["primary"]}20;
}}

.challenge-card.selected {{
    background: {c["primary"]}30;
    border-left: solid {c["primary"]};
}}

.challenge-name {{
    color: {c["text"]};
}}

.challenge-value {{
    color: {c["primary"]};
}}

.challenge-solved {{
    color: {c["success"]};
}}

.challenge-unsolved {{
    color: {c["accent"]};
}}

.detail-label {{
    color: {c["text_dim"]};
}}

.detail-value {{
    color: {c["text"]};
}}

.flag-input {{
    background: {c["surface"]};
    color: {c["text"]};
    border: solid {c["primary"]};
}}

.scoreboard-row {{
    padding: 0 2;
}}

.scoreboard-row.highlight {{
    background: {c["primary"]}30;
}}

Button {{
    background: {c["primary"]};
    color: {c["surface"]};
}}

Button:hover {{
    background: {c["secondary"]};
}}

#theme-list {{
    background: {c["surface"]};
}}

#settings-panel {{
    background: {c["surface"]};
}}
"""
