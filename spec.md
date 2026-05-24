Design Guide: Alfred Architecture & Implementation Blueprint

File Target: design-guide.md
Project Type: Headless CTF Workspace Engine & Dual-Protocol Controller (TUI + MCP Server)
Primary Stack: Python 3.10+ (Async IO, Textual, HTTPX) & Native POSIX Bash
1. System Engineering Blueprint

Alfred decouples the platform integration layer from terminal visual handlers and external AI protocol workers. Both the Textual TUI Terminal Application and the Model Context Protocol (MCP) Standard I/O Server interact through a centralized, asynchronous in-memory state repository protected by mutual exclusion resource locks.  

                ┌───────────────────────────────┐
                │     External LLM Client       │
                │  (Cursor, Claude Desktop)     │
                └───────────────┬───────────────┘
                                │ JSON-RPC 2.0 (stdio)
                                ▼
┌───────────────┐     ┌─────────────────────────┐
│  Human User   │     │    Async MCP Server     │
│  (TTY/Stdin)  │     │   (alfred.mcp_core)   │
└───────┬───────┘     └────────────┬────────────┘
        │                          │
        │ Event Hooks              │ Mutex State Locks
        ▼                          ▼
┌───────────────────────────────────────────────┐
│            Centralized State Manager          │
│               (alfred.state)                │
└───────────────────────┬───────────────────────┘
                        │
                        │ Thread-Safe Dispatches
                        ▼
┌───────────────────────────────────────────────┐
│            Asynchronous API Engine            │
│            (HTTPX / Native REST V1)           │
└───────────────────────┬───────────────────────┘
                        │
                        │ Bearer Token / Session Payload
                        ▼
                ┌───────────────────────────────┐
                │      Remote CTFd Target       │
                │     (Production Backend)      │
                └───────────────────────────────┘

2. Directory Structure Blueprint
Bash

~/.local/share/alfred/            # Primary production package installation root
├── venv/                           # Isolated Python virtual runtime sandbox
└── alfred/
    ├── __init__.py
    ├── app.py                      # Core entrypoint orchestration container
    ├── api.py                      # Pure HTTPX CTFd REST v1 payload client
    ├── state.py                    # Thread-safe in-memory database of record
    ├── workspace.py                # Automated directory builder & script generator
    ├── theme.py                    # Real-time visual CSS canvas switching matrix
    └── mcp_server.py               # JSON-RPC 2.0 standard I/O engine

Bash

~/.config/alfred/                 # User-level persistent identity matrices
├── config.json                     # Encrypted/Protected target token profiles
├── mcp_policy.json                 # Security rule definitions for AI models
└── next_dir                        # Volatile state passing path register (IPC link)

3. Module Functional Specifications
3.1 Platform API Client (api.py)

This module handles direct platform interaction by making raw httpx.AsyncClient network calls. It passes headers using the format Authorization: Token <token> and manages standard CTFd REST paths:  

    GET /api/v1/challenges: Collects full challenge listings. It parses challenge profiles to extract names, point values, attachment download listings, and completion indicators (solved_by_me).  

    GET /api/v1/challenges/[id]: Pulls comprehensive metadata maps containing detailed deployment parameters, hints, attachment paths, and network deployment links.

    POST /api/v1/challenges/attempt: Issues structural JSON flag checking payloads: {"challenge_id": id, "submission": "FLAG"}. Returns verification tags (correct, incorrect, already_solved).

    GET /api/v1/scoreboard: Monitors rank indices to compute total points gap calculations relative to adjacent teams.

3.2 Automated Sandbox Manager (workspace.py)

This module streamlines file operations by eliminating manual organization:  

    Path Generation: Constructs standard execution folders: ~/.ctf_workspaces/<ctf_name>/<category>/<challenge_slug>/.  

    Asset Ingestion: Downloads binary files from attachment lists and extracts zip/tar contents cleanly in-line.  

    Exploit Templating: Drops a customized solve.py file into the target directory. The script automatically initializes common connection configurations, importing components like pwntools and pre-filling the target host ip/port parameters.  

3.3 Interprocess Traversal Wrapper (shell_hook.sh)

This component uses a dual-process handshake to bypass the operating system safety rule that blocks child scripts from changing a parent terminal's active directory path:  

    The interactive Python application writes the designated destination folder into ~/.config/alfred/next_dir and drops out of frame with custom status flag 110.  

    A lightweight shell monitor hooked inside the user's terminal runtime intercepts code 110, extracts the target folder path, and updates the parent shell's location by firing a clean native cd sequence.  

4. Model Context Protocol (MCP) Integration

The server configures standard input/output channels (stdio) to expose security operations directly to AI models using a structured JSON-RPC 2.0 framework.  
4.1 Exposed JSON-RPC Tool Schema

Models discover the application capabilities by executing standard tool enumeration workflows:
JSON

{
  "tools": [
    {
      "name": "alfred_list_challenges",
      "description": "Fetch available CTF categories, target names, point allocations, and state parameters.",
      "inputSchema": { "type": "object", "properties": {} }
    },
    {
      "name": "alfred_get_workspace_path",
      "description": "Returns the exact disk directory holding challenge binaries and exploit scripts.",
      "inputSchema": {
        "type": "object",
        "properties": { "challenge_id": { "type": "integer" } },
        "required": ["challenge_id"]
      }
    },
    {
      "name": "alfred_submit_flag",
      "description": "Submits a discovered flag string directly to the platform for validation.",
      "inputSchema": {
        "type": "object",
        "properties": {
          "challenge_id": { "type": "integer" },
          "flag_string": { "type": "string" }
        },
        "required": ["challenge_id", "flag_string"]
      }
    }
  ]
}

4.2 Security Containment & Policy Engine

To prevent autonomous agents from triggering platform rate limits or accessing unauthorized directories, the policy layer enforces specific runtime validation rules via mcp_policy.json:  

    allow_flag_submission: Manages automated submissions via a multi-state flag (true, false, require_human).  

    sandbox_directory_jail: Restricts the model's file operations exclusively to target workspace trees to prevent accidental directory traversal.  

When an AI agent requests a restricted task while the safety rules require human review, the backend pauses the execution thread. The TUI pops up a visual review card detailing the action. The model's execution context is held at a thread barrier until the human operator confirms or denies the request by pressing a hotkey.  
5. UI Themes & Notification Mechanics
5.1 Dynamic Styling Canvas Engine

Visual skin assets swap in real time by binding specific class palettes dynamically, such as Tokyo Night and Gruvbox.

    Terminal Native Sync: Completely disables hardcoded hexadecimal color configurations. All display assets pull directly from the host terminal's built-in ANSI colors (color0 to color15), preserving custom opacity filters, blur levels, and backdrop configurations.  

5.2 Async Overlay Notification Matrix

The user interface tracks server data updates to handle event flags asynchronously without causing frame-rate drops:  

    🩸 First Blood Alert: Fires when point monitoring logs catch an asset's global solve metric transition from 0 to 1, indicating a team member claimed first blood.  

    Teammate Solve Alerts: Triggers a sliding banner block when background synchronization flags show another squad member successfully cleared a challenge.  

    Proximity Alerts: Calculates the exact score differences relative to adjacent competitors, warning the player if an active opponent moves within striking distance of their rank position.  

6. Execution Lifecycle Guide

[System Boot]
      │
      ▼
Installer Pipeline (Install.sh)
      │
      ├── Provisions isolation path (~/.local/share/alfred/)
      ├── Scaffolds standalone Python virtual runtime (venv)
      ├── Registers parent shell environment hooks into .bashrc/.zshrc
      └── Appends JSON-RPC command array into Claude/Cursor workspace configs
      │
      ▼
[User Invokes `alfred`]
      │
      ├── TUI initializes interface canvas & boots state server asynchronously
      ├── Background network workers start polling platform REST endpoints
      │
      ├───[Action: Human hits Ctrl+W] ───> Generates sandbox folders & code templates
      ├───[Action: Human hits Ctrl+G] ───> Passes path to IPC token, exits via Code 110
      │                                    (Host wrapper intercepts and handles `cd`)
      │
      └───[Action: AI triggers tool]  ───> MCP server intercept captures payload
                                           (Validates parameters against safety policy)

7. Implementation Roadmap

The build order prioritizes the TUI experience first, deferring MCP to the final phase.

Phase 1 — Skeleton & API (Week 1)
  Goal: Headless CLI that can talk to a CTFd instance.
  [ ] Scaffold package structure (alfred/, __init__.py, app.py entrypoint)
  [ ] Implement api.py — httpx.AsyncClient wrapper for all CTFd REST endpoints
  [ ] Implement state.py — thread-safe in-memory store (challenges, scoreboard, config)
  [ ] Implement config.json read/write in ~/.config/alfred/ (token, URL)
  [ ] Basic CLI mode in app.py: `alfred list`, `alfred submit <id> <flag>`
  [ ] Verify: `alfred list` prints challenges from a real CTFd instance

Phase 2 — TUI Shell (Week 2)
  Goal: Browse challenges, submit flags, view scoreboard — all from a Textual TUI.
  [ ] Wire up Textual App + basic screen layout (header, sidebar, main panel)
  [ ] Build ChallengeListScreen — scrollable list of challenges with status/points
  [ ] Build ChallengeDetailScreen — description, hints, attachments, submit form
  [ ] Build ScoreboardScreen — rank table with proximity calculation
  [ ] Ctrl+S flag submit hotkey, Ctrl+Q quit, Tab navigation between screens
  [ ] Verify: full read-only TUI workflow against a live CTFd instance

Phase 3 — Workspace & Shell Hook (Week 3)
  Goal: Generate challenge directories, download assets, drop exploit templates, cd into them.
  [ ] Implement workspace.py path generation (~/.ctf_workspaces/<ctf>/<category>/<slug>/)
  [ ] Download + extract attachments (zip/tar) into workspace directory
  [ ] Build solve.py template generator (pwntools skeleton, host/port from challenge meta)
  [ ] Implement Ctrl+W hotkey in TUI — creates workspace, opens it
  [ ] Implement shell_hook.sh — next_dir IPC + exit code 110 handler
  [ ] Write install.sh that hooks shell_hook.sh into .bashrc/.zshrc
  [ ] Verify: Ctrl+W creates a workspace, `alfred` exits 110, parent shell cd's

Phase 4 — TUI Polish & Notifications (Week 4)
  Goal: Eye candy, live polling, theme swapping, alert overlays.
  [ ] Implement theme.py — Textual CSS theme classes (Tokyo Night, Gruvbox, default)
  [ ] Bind theme cycling hotkey (e.g., Ctrl+T)
  [ ] Background async polling for scoreboard / challenge updates
  [ ] Overlay notification — first blood alert (solve count 0→1)
  [ ] Overlay notification — teammate solve alert
  [ ] Overlay notification — proximity alert (score gap < threshold)
  [ ] Verify: TUI feels responsive, themes switch, alerts fire on real data

Phase 5 — Installer & Packaging (Week 5)
  Goal: Single-command install, clean uninstall, production-ready layout.
  [ ] Finalize install.sh — venv creation, pip install deps, hook injection, MCP config stubs
  [ ] Add `alfred uninstall` or separate uninstall.sh
  [ ] Pin dependencies (textual, httpx, pwntools) in requirements.txt
  [ ] Handle edge cases: missing ~/.config/alfred/, token rotation, connection errors
  [ ] Write --help, man-page-style usage in app.py
  [ ] Verify: fresh install on clean machine → everything works end to end

Phase 6 — MCP Server (Week 6, HARDEST — deferred last)
  Goal: AI agents can list challenges, inspect workspaces, and submit flags with safety gates.
  [ ] Implement mcp_server.py — stdio JSON-RPC 2.0 listener using SDK primitives
  [ ] Register tools: alfred_list_challenges, alfred_get_workspace_path, alfred_submit_flag
  [ ] Implement mcp_policy.json — allow_flag_submission, sandbox_directory_jail
  [ ] Build "require_human" flow: MCP thread blocks → TUI pops human review card → hotkey approve/deny
  [ ] Write MCP config snippets for Cursor and Claude Desktop (auto-appended by install.sh)
  [ ] Verify: Claude Desktop connects, tools enumerate, policy gates work correctly
