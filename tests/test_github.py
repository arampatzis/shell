"""Tests for GitHubSSHSetup: setup_git_repo and get_email_for_key."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from installers.custom.github import GitHubSSHSetup


REPO_URL = "git@github.com:test/repo.git"


@pytest.fixture
def setup(tmp_path):
    return GitHubSSHSetup(gh_binary=tmp_path / "gh")


class TestSetupGitRepo:
    def test_already_git_repo_skips(self, setup, tmp_path):
        (tmp_path / ".git").mkdir()
        assert setup.setup_git_repo(tmp_path, REPO_URL) is True

    def test_user_declines_with_n(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "n")
        assert setup.setup_git_repo(tmp_path, REPO_URL) is True
        assert not (tmp_path / ".git").exists()

    def test_user_declines_with_no(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "no")
        assert setup.setup_git_repo(tmp_path, REPO_URL) is True
        assert not (tmp_path / ".git").exists()

    def test_user_confirms_runs_all_git_commands(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "y")
        success = MagicMock(success=True)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = success
            result = setup.setup_git_repo(tmp_path, REPO_URL)

        assert result is True
        executed_cmds = [
            c.args[0] for c in MockExecutor.return_value.execute_cmd.call_args_list
        ]
        assert ["git", "init"] in executed_cmds
        assert ["git", "remote", "add", "origin", REPO_URL] in executed_cmds
        assert ["git", "fetch", "origin"] in executed_cmds
        assert ["git", "branch", "master", "origin/master"] in executed_cmds

    def test_empty_answer_proceeds(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "")
        success = MagicMock(success=True)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = success
            result = setup.setup_git_repo(tmp_path, REPO_URL)

        assert result is True

    def test_git_command_failure_returns_false(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "y")
        failure = MagicMock(success=False)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = failure
            result = setup.setup_git_repo(tmp_path, REPO_URL)

        assert result is False

    def test_git_commands_run_in_project_dir(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "y")
        success = MagicMock(success=True)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = success
            setup.setup_git_repo(tmp_path, REPO_URL)

        for call in MockExecutor.return_value.execute_cmd.call_args_list:
            assert call.kwargs["cwd"] == tmp_path

    def test_stops_after_first_git_failure(self, setup, tmp_path, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "y")
        failure = MagicMock(success=False)

        with patch("installers.custom.github.Executor") as MockExecutor:
            MockExecutor.return_value.execute_cmd.return_value = failure
            setup.setup_git_repo(tmp_path, REPO_URL)

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
