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
$text-muted: {c["text_dim"]};
$text-disabled: {c["text_dim"]};
$text-dim: {c["text_dim"]};
$text-primary: {c["primary"]};
$text-secondary: {c["secondary"]};
$text-success: {c["success"]};
$text-warning: {c["warning"]};
$text-error: {c["error"]};
$text-accent: {c["accent"]};
$primary: {c["primary"]};
$primary-muted: {c["primary"]}40;
$primary-darken-1: {c["primary"]};
$primary-darken-2: {c["primary"]};
$primary-lighten-1: {c["primary"]};
$secondary: {c["secondary"]};
$secondary-muted: {c["secondary"]}40;
$accent: {c["accent"]};
$accent-muted: {c["accent"]}40;
$error: {c["error"]};
$error-muted: {c["error"]}40;
$error-darken-1: {c["error"]};
$error-darken-2: {c["error"]};
$error-darken-3: {c["error"]};
$error-lighten-2: {c["error"]};
$success: {c["success"]};
$success-muted: {c["success"]}40;
$success-darken-1: {c["success"]};
$success-darken-2: {c["success"]};
$success-darken-3: {c["success"]};
$success-lighten-1: {c["success"]};
$success-lighten-2: {c["success"]};
$warning: {c["warning"]};
$warning-muted: {c["warning"]}40;
$warning-darken-1: {c["warning"]};
$warning-darken-2: {c["warning"]};
$warning-darken-3: {c["warning"]};
$warning-lighten-2: {c["warning"]};
$warning-text: {c["text"]};
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
$footer-description-background: {c["surface"]};
$footer-description-foreground: {c["text"]};
$footer-key-background: {c["primary"]}30;
$footer-key-foreground: {c["primary"]};
$footer-item-background: {c["background"]};
$scrollbar: {c["primary"]};
$scrollbar-active: {c["primary"]};
$scrollbar-background: {c["surface"]};
$scrollbar-background-active: {c["background"]};
$scrollbar-background-hover: {c["background"]};
$scrollbar-hover: {c["primary"]};
$scrollbar-corner-color: {c["background"]};
$input-cursor-background: {c["text"]};
$input-cursor-foreground: {c["background"]};
$input-selection-background: {c["primary"]}50;
$input-selection-foreground: {c["text"]};
$block-cursor-background: {c["primary"]};
$block-cursor-foreground: {c["surface"]};
$block-cursor-blurred-background: {c["text_dim"]};
$block-cursor-blurred-foreground: {c["surface"]};
$block-hover-background: {c["primary"]}20;
$button-color-foreground: {c["surface"]};
$button-foreground: {c["surface"]};
$button-focus-text-style: bold;
$link-color: {c["primary"]};
$link-color-hover: {c["secondary"]};
$link-background: transparent;
$link-background-hover: transparent;
$link-style-hover: underline;
$markdown-h1-color: {c["primary"]};
$markdown-h1-background: transparent;
$markdown-h1-text-style: bold;
$markdown-h2-color: {c["secondary"]};
$markdown-h2-background: transparent;
$markdown-h2-text-style: bold;
$markdown-h3-color: {c["text"]};
$markdown-h3-background: transparent;
$markdown-h3-text-style: bold;
$markdown-h4-color: {c["text"]};
$markdown-h4-background: transparent;
$markdown-h4-text-style: bold;
$markdown-h5-color: {c["text"]};
$markdown-h5-background: transparent;
$markdown-h5-text-style: bold;
$markdown-h6-color: {c["text"]};
$markdown-h6-background: transparent;
$markdown-h6-text-style: bold;
$screen-selection-background: {c["primary"]}30;
$screen-selection-foreground: {c["text"]};
$name: {c["text"]};
$ansi-background: {c["background"]};
$ansi-foreground: {c["text"]};

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

.flag-input {{
    background: $surface;
    color: $text;
    border: solid $primary;
}}

Button {{
    background: $primary;
    color: $surface;
}}

Button:hover {{
    background: $secondary;
}}

#celebration {{
    dock: top;
    height: 3;
    text-align: center;
    padding: 1;
}}

.celebration-hidden {{
    display: none;
}}

.celebration-correct {{
    display: block;
    background: $success;
    color: $surface;
    text-style: bold;
}}

.celebration-incorrect {{
    display: block;
    background: $error;
    color: $surface;
    text-style: bold;
}}

.celebration-already {{
    display: block;
    background: $warning;
    color: $surface;
    text-style: bold;
}}

.category-header {{
    color: $primary;
    background: $surface;
    text-style: bold;
    padding: 0 1;
}}

#theme-list {{
    background: $surface;
}}
"""
