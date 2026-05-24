# shell_hook.sh — Source this in your .bashrc or .zshrc to enable
# `alfred workspace --solve` to cd into the workspace directory.
#
# Add to your shell:
#   echo "source ~/.local/share/alfred/scripts/shell_hook.sh" >> ~/.bashrc

alfred() {
    local next_dir_file="$HOME/.config/alfred/next_dir"
    command alfred "$@"
    local rc=$?
    if [ $rc -eq 110 ]; then
        if [ -f "$next_dir_file" ]; then
            local target
            target=$(cat "$next_dir_file" 2>/dev/null)
            if [ -n "$target" ] && [ -d "$target" ]; then
                command rm -f "$next_dir_file"
                cd "$target" || return 1
            fi
        fi
    fi
    return $rc
}
