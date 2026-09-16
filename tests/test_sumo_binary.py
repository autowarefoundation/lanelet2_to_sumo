from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ll2sumo.sumo_binary import (
    resolve_sumo_home,
    resolve_tool,
    resolve_tools_script,
)

# A name that cannot be found on PATH or in any SUMO installation, so the
# fallback behaviour stays deterministic wherever the tests run.
MISSING_TOOL = "ll2sumo-missing-tool"


def _fake_sumo_home(root: Path) -> Path:
    home = root / "sumo"
    (home / "bin").mkdir(parents=True)
    (home / "tools").mkdir(parents=True)
    (home / "bin" / MISSING_TOOL).write_text("")
    (home / "tools" / "randomTrips.py").write_text("")
    return home


class ResolveToolTest(unittest.TestCase):
    def test_explicit_path_wins_over_path_lookup(self) -> None:
        with patch("ll2sumo.sumo_binary.which", return_value="/usr/bin/netconvert") as which:
            resolved = resolve_tool("netconvert", "/opt/sumo/bin/netconvert")

        self.assertEqual(resolved, "/opt/sumo/bin/netconvert")
        which.assert_not_called()

    def test_uses_path_lookup_when_no_explicit_binary(self) -> None:
        with patch("ll2sumo.sumo_binary.which", return_value="/usr/bin/netconvert"):
            self.assertEqual(resolve_tool("netconvert"), "/usr/bin/netconvert")

    def test_falls_back_to_sumo_home_bin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = _fake_sumo_home(Path(tmp))

            with patch.dict(os.environ, {"SUMO_HOME": str(home)}):
                resolved = resolve_tool(MISSING_TOOL)

        self.assertEqual(resolved, str(home / "bin" / MISSING_TOOL))

    def test_falls_back_to_bare_tool_name_when_nothing_is_installed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"SUMO_HOME": tmp}):
                self.assertEqual(resolve_tool(MISSING_TOOL), MISSING_TOOL)


class ResolveSumoHomeTest(unittest.TestCase):
    def test_prefers_exported_sumo_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = _fake_sumo_home(Path(tmp))

            with patch.dict(os.environ, {"SUMO_HOME": str(home)}):
                self.assertEqual(resolve_sumo_home(), home)

    def test_ignores_sumo_home_that_does_not_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = str(Path(tmp) / "absent")

            with patch.dict(os.environ, {"SUMO_HOME": missing}):
                self.assertNotEqual(resolve_sumo_home(), Path(missing))

    def test_finds_random_trips_under_tools(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = _fake_sumo_home(Path(tmp))

            with patch.dict(os.environ, {"SUMO_HOME": str(home)}):
                self.assertEqual(
                    resolve_tools_script("randomTrips.py"),
                    home / "tools" / "randomTrips.py",
                )


if __name__ == "__main__":
    unittest.main()
