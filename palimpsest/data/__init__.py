"""Helpers for accessing palimpsest package data."""

from importlib.resources import files


def get_package_files():
    """Return a Traversable pointing to the palimpsest package root."""
    return files("palimpsest")


def read_template(name: str) -> str:
    """Read a template file by name."""
    return get_package_files().joinpath("templates", name).read_text()


def read_doc(name: str) -> str:
    """Read a methodology doc by name."""
    return get_package_files().joinpath("docs", name).read_text()
