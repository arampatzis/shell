"""Tests for GitHubSSHSetup: setup_git_repo and get_email_for_key."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from installers.custom.github import GitHubSSHSetup, _ssh_to_https_url


SSH_URL = "git@github.com:test/repo.git"
HTTPS_URL = "https://github.com/test/repo.git"


def make_inputs(*responses):
    """Return a lambda that yields responses in order for successive input() calls."""
    it = iter(responses)
    return lambda _: next(it)


@pytest.fixture
def setup(tmp_path):
    return GitHubSSHSetup(gh_binary=tmp_path / "gh")


class TestSshToHttpsUrl:
    def test_converts_github_ssh_url(self):
        assert _ssh_to_https_url("git@github.com:user/repo.git") == "https://github.com/user/repo.git"

    def test_converts_other_host(self):
        assert _ssh_to_https_url("git@gitlab.com:org/proj.git") == "https://gitlab.com/org/proj.git"

    def test_returns_input_unchanged_if_not_ssh(self):
        url = "https://github.com/user/repo.git"
        assert _ssh_to_https_url(url) == url


class TestSetupGitRepo:
    def test_already_git_repo_skips(self, setup, tmp_path):
        (tmp_path / ".git").mkdir()
        assert setup.setup_git_repo(tmp_path, SSH_URL) is True

    def test_user_declines_with_n(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "n")
        assert setup.setup_git_repo(tmp_path, SSH_URL) is True
        assert not (tmp_path / ".git").exists()

    def test_user_declines_with_no(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "no")
        assert setup.setup_git_repo(tmp_path, SSH_URL) is True
        assert not (tmp_path / ".git").exists()

    def test_ssh_choice_uses_ssh_url(self, setup, tmp_path, monkeypatch):
        # "y" → proceed, "1" → SSH
        monkeypatch.setattr("builtins.input", make_inputs("y", "1"))
        success = MagicMock(success=True)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = success
            result = setup.setup_git_repo(tmp_path, SSH_URL)

        assert result is True
        executed_cmds = [c.args[0] for c in MockExecutor.return_value.execute_cmd.call_args_list]
        assert ["git", "remote", "add", "origin", SSH_URL] in executed_cmds

    def test_https_choice_uses_https_url(self, setup, tmp_path, monkeypatch):
        # "y" → proceed, "2" → HTTPS
        monkeypatch.setattr("builtins.input", make_inputs("y", "2"))
        success = MagicMock(success=True)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = success
            result = setup.setup_git_repo(tmp_path, SSH_URL)

        assert result is True
        executed_cmds = [c.args[0] for c in MockExecutor.return_value.execute_cmd.call_args_list]
        assert ["git", "remote", "add", "origin", HTTPS_URL] in executed_cmds

    def test_default_choice_uses_ssh_url(self, setup, tmp_path, monkeypatch):
        # "y" → proceed, "" → default (SSH)
        monkeypatch.setattr("builtins.input", make_inputs("y", ""))
        success = MagicMock(success=True)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = success
            setup.setup_git_repo(tmp_path, SSH_URL)

        executed_cmds = [c.args[0] for c in MockExecutor.return_value.execute_cmd.call_args_list]
        assert ["git", "remote", "add", "origin", SSH_URL] in executed_cmds

    def test_confirms_runs_all_git_commands(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", make_inputs("y", "1"))
        success = MagicMock(success=True)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = success
            result = setup.setup_git_repo(tmp_path, SSH_URL)

        assert result is True
        executed_cmds = [c.args[0] for c in MockExecutor.return_value.execute_cmd.call_args_list]
        assert ["git", "init"] in executed_cmds
        assert ["git", "fetch", "origin"] in executed_cmds
        assert ["git", "reset", "origin/master"] in executed_cmds

    def test_git_command_failure_returns_false(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", make_inputs("y", "1"))
        failure = MagicMock(success=False)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = failure
            result = setup.setup_git_repo(tmp_path, SSH_URL)

        assert result is False

    def test_git_commands_run_in_project_dir(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", make_inputs("y", "1"))
        success = MagicMock(success=True)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = success
            setup.setup_git_repo(tmp_path, SSH_URL)

        for call in MockExecutor.return_value.execute_cmd.call_args_list:
            assert call.kwargs["cwd"] == tmp_path

    def test_keyboard_interrupt_returns_true(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", make_inputs("y", "1"))

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.side_effect = KeyboardInterrupt
            result = setup.setup_git_repo(tmp_path, SSH_URL)

        assert result is True

    def test_stops_after_first_git_failure(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", make_inputs("y", "1"))
        failure = MagicMock(success=False)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = failure
            setup.setup_git_repo(tmp_path, SSH_URL)

        assert MockExecutor.return_value.execute_cmd.call_count == 1


class TestGetEmailForKey:
    def test_empty_input_returns_empty(self, setup, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "")
        assert setup.get_email_for_key() == ""

    def test_valid_email_returns_email(self, setup, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "user@example.com")
        assert setup.get_email_for_key() == "user@example.com"

    def test_invalid_then_valid_loops(self, setup, monkeypatch):
        responses = iter(["notanemail", "also_bad", "good@example.com"])
        monkeypatch.setattr("builtins.input", lambda _: next(responses))
        assert setup.get_email_for_key() == "good@example.com"
