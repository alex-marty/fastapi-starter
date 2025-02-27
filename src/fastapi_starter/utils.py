import subprocess
from pathlib import Path
from typing import Literal, overload


@overload
def git_root_path(
    cwd: Path | str | None = None, *, allow_none: Literal[False] = False
) -> Path: ...


@overload
def git_root_path(
    cwd: Path | str | None = None, *, allow_none: Literal[True]
) -> Path | None: ...


def git_root_path(
    cwd: Path | str | None = None, *, allow_none: bool = False
) -> Path | None:
    """Get the root path of the current git repository, if any."""
    if cwd is None:
        cwd = Path.cwd()
    cmd = ["git", "rev-parse", "--show-toplevel"]
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, check=False)  # noqa: S603
    if result.returncode != 0:
        if allow_none:
            return None
        else:
            msg = (
                f"Failed to get git root path from '{cwd}', are you in a git repository?"
            )
            raise RuntimeError(msg)
    return Path(result.stdout.decode("utf-8").strip())


def git_revision_hash(cwd: Path | str | None = None, *, short: bool = False) -> str:
    """Get the current git revision hash."""
    if cwd is None:
        cwd = Path.cwd()

    if short:
        cmd = ["git", "rev-parse", "--short", "HEAD"]
    else:
        cmd = ["git", "rev-parse", "HEAD"]

    result = subprocess.run(cmd, cwd=cwd, capture_output=True, check=False)  # noqa: S603
    if result.returncode != 0:
        msg = f"Failed to get git revision hash from '{cwd}'"
        raise RuntimeError(msg)
    return result.stdout.decode("utf-8").strip()


def git_working_directory_is_clean(cwd: Path | str | None = None) -> bool:
    """Check if the current git working directory is clean. Checks for untracked files."""
    if cwd is None:
        cwd = Path.cwd()
    cmd = ["git", "status", "--porcelain"]
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, check=False)  # noqa: S603
    if result.returncode != 0:
        msg = f"Failed to check git status for '{cwd}'"
        raise RuntimeError(msg)
    # If the output is empty, the working directory is clean
    return result.stdout == b""
