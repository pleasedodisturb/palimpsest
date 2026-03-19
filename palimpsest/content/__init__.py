"""Access bundled palimpsest content (docs, templates, agents, playbooks, showcase, case-study)."""

from importlib.resources import files
from pathlib import Path

CONTENT_CATEGORIES = [
    "docs",
    "templates",
    "agents",
    "playbooks",
    "showcase",
    "case-study",
]


def get_content_path(category: str, filename: str) -> Path:
    """Get path to a bundled content file.

    Args:
        category: One of docs, templates, agents, playbooks, showcase, case-study.
        filename: File name within the category directory.

    Returns:
        Path to the content file.

    Raises:
        FileNotFoundError: If the category or file does not exist.
    """
    if category not in CONTENT_CATEGORIES:
        raise FileNotFoundError(
            f"Unknown content category '{category}'. "
            f"Available: {', '.join(CONTENT_CATEGORIES)}"
        )
    resource = files("palimpsest.content").joinpath(category, filename)
    path = Path(str(resource))
    if not path.exists():
        raise FileNotFoundError(f"Content file not found: {category}/{filename}")
    return path


def list_content(category: str) -> list[str]:
    """List files in a content category.

    Args:
        category: One of docs, templates, agents, playbooks, showcase, case-study.

    Returns:
        Sorted list of file names in the category.
    """
    if category not in CONTENT_CATEGORIES:
        raise FileNotFoundError(
            f"Unknown content category '{category}'. "
            f"Available: {', '.join(CONTENT_CATEGORIES)}"
        )
    resource_dir = files("palimpsest.content").joinpath(category)
    return sorted(
        item.name
        for item in resource_dir.iterdir()
        if not item.name.startswith("__")
    )
