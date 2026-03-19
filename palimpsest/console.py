"""Rich Console singleton for palimpsest CLI output."""

from rich.console import Console
from rich.theme import Theme

PAL_THEME = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "hint": "dim green",
    "command": "bold magenta",
})

console = Console(theme=PAL_THEME)
err_console = Console(theme=PAL_THEME, stderr=True)
