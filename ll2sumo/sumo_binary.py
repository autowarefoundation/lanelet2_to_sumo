"""Locate SUMO command line tools and data without a Docker image.

The converter shells out to `netconvert`, and the documented validation steps
also use `randomTrips.py` from the SUMO tools directory. Both are available
from the `eclipse-sumo` wheel, so a plain `pip install` is enough to run the
converter; Docker is only one of several ways to provide them.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from shutil import which


def _executable_name(tool: str) -> str:
    return f"{tool}.exe" if sys.platform == "win32" else tool


def sumo_home_candidates() -> list[Path]:
    """Return SUMO_HOME candidates, most explicit first.

    An exported SUMO_HOME wins over the installed wheel so that a host SUMO
    installation stays selectable even when `eclipse-sumo` is also present.
    """

    candidates: list[Path] = []
    env_home = os.environ.get("SUMO_HOME")
    if env_home:
        candidates.append(Path(env_home))
    try:
        import sumo  # noqa: PLC0415  # optional dependency, provided by the eclipse-sumo wheel
    except ImportError:
        pass
    else:
        # Importing the wheel also exports SUMO_HOME and PROJ_LIB / PROJ_DATA,
        # which the bundled binaries need at runtime.
        candidates.append(Path(sumo.SUMO_HOME))
    return candidates


def resolve_sumo_home() -> Path | None:
    """Return the first SUMO_HOME candidate that exists on disk."""

    for candidate in sumo_home_candidates():
        if candidate.is_dir():
            return candidate
    return None


def resolve_tool(tool: str, explicit: str | None = None) -> str:
    """Return the path to a SUMO tool such as `netconvert`.

    Resolution order: an explicit path, then PATH, then the SUMO_HOME
    candidates. The bare tool name is returned as a last resort so that the
    failure surfaces as a normal "command not found" error.
    """

    if explicit:
        return explicit
    on_path = which(tool)
    if on_path:
        return on_path
    executable = _executable_name(tool)
    for home in sumo_home_candidates():
        candidate = home / "bin" / executable
        if candidate.is_file():
            return str(candidate)
    return tool


def resolve_tools_script(name: str) -> Path | None:
    """Return the path to a script under the SUMO tools directory."""

    for home in sumo_home_candidates():
        candidate = home / "tools" / name
        if candidate.is_file():
            return candidate
    return None


def main() -> None:
    """Print the resolved SUMO environment, for troubleshooting a local setup."""

    home = resolve_sumo_home()
    random_trips = resolve_tools_script("randomTrips.py")
    print(
        json.dumps(
            {
                "sumo_home": str(home) if home is not None else None,
                "netconvert": resolve_tool("netconvert"),
                "sumo": resolve_tool("sumo"),
                "random_trips": str(random_trips) if random_trips is not None else None,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
