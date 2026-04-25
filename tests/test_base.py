"""Tests for Installer base class: _check_installed and _check_dependencies."""

import pytest
from dataclasses import dataclass
from pathlib import Path
from installers.base import Installer


@dataclass(kw_only=True)
class ConcreteInstaller(Installer):
    def _install(self) -> bool:
        return True


@pytest.fixture
def installer(tmp_path):
    return ConcreteInstaller(
        name="test-tool",
        installation_path=str(tmp_path / "bin"),
    )


class TestCheckInstalled:
    def test_check_cmd_found_skips(self, installer):
        installer.check_cmd = "python3"
        assert installer._check_installed("test-tool") is True

    def test_check_cmd_not_found_proceeds(self, installer):
        installer.check_cmd = "definitely_not_a_real_binary_xyz123"
        assert installer._check_installed("test-tool") is False

    def test_check_path_exists_skips(self, installer, tmp_path):
        existing = tmp_path / "existing_tool"
        existing.touch()
        installer.check_path = str(existing)
        assert installer._check_installed("test-tool") is True

    def test_check_path_missing_proceeds(self, installer, tmp_path):
        installer.check_path = str(tmp_path / "nonexistent")
        assert installer._check_installed("test-tool") is False

    def test_force_bypasses_check_cmd(self, installer):
        installer.check_cmd = "python3"
        installer.force = True
        assert installer._check_installed("test-tool") is False

    def test_force_bypasses_check_path(self, installer, tmp_path):
        existing = tmp_path / "existing_tool"
        existing.touch()
        installer.check_path = str(existing)
        installer.force = True
        assert installer._check_installed("test-tool") is False

    def test_no_checks_returns_not_installed(self, installer):
        installer.check_cmd = ""
        installer.check_path = ""
        assert installer._check_installed("test-tool") is False


class TestCheckDependencies:
    def test_all_deps_present(self, installer):
        assert installer._check_dependencies(["python3", "sh"]) is True

    def test_missing_dep_returns_false(self, installer):
        assert installer._check_dependencies(["definitely_not_real_xyz123"]) is False

    def test_none_deps_returns_true(self, installer):
        assert installer._check_dependencies(None) is True

    def test_empty_deps_returns_true(self, installer):
        assert installer._check_dependencies([]) is True
