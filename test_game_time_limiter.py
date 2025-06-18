"""
test_game_time_limiter.py

Tests for game_time_limiter.
"""

import importlib
import json
import time
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
import wx

import game_time_limiter as gtl

# 🔧 Fixtures


@pytest.fixture
def tracker():
    _ = wx.App(False)
    return gtl.GameTimeTracker()


@pytest.fixture
def patch_path(monkeypatch):
    """
    Reusable context manager to patch a path constant + file system behavior.
    """

    @contextmanager
    def _patch(name: str, fake_filename: str, content: str):
        fake_path = Path(fake_filename)
        monkeypatch.setattr(gtl, name, fake_path)
        m = mock_open(read_data=content)
        with patch.object(gtl.Path, "exists", return_value=True), patch(
            "pathlib.Path.open", m
        ):
            yield

    return _patch


@pytest.fixture
def wx_app():
    return wx.App(False)


# Initialization and state tests


def test_base_dir(tracker):
    assert "game_time_limiter" in str(tracker.get_base())


def test_log_path(tracker):
    expected = Path.home() / "AppData" / "Roaming" / "GameTimeLog.json"
    assert tracker.log_path == expected


def test_game_times(tracker):
    times = tracker.game_times
    assert times.get("javaw.exe") == 0
    assert "GuildWars2.exe" not in times


def test_tracked_games_type(tracker):
    assert isinstance(tracker.tracked_games, set)


# Config and logic tests


@pytest.mark.parametrize(
    "input_pwd, actual_pwd, expected",
    [
        ("secret", "secret", True),
        ("nope", "secret", False),
        ("", "", True),
        ("123", "321", False),
    ],
)
def test_password_validation(input_pwd, actual_pwd, expected):
    assert gtl.GameTimeTracker.is_password_valid(input_pwd, actual_pwd) == expected


def test_config_path_defaults():
    assert gtl.LOG_PATH == Path.home() / "AppData" / "Roaming" / "GameTimeLog.json"
    assert gtl.APPS_LIST_FILE == Path(__file__).parent / "apps_list.txt"


def test_log_config_load(tmp_path):
    gtl.CONFIG_FILE = tmp_path / "config.json"
    assert gtl.load_config() == {}


# File-loading logic with patched paths


@pytest.mark.parametrize(
    "mock_json, expected_limit, expected_password",
    [
        ('{"limit_minutes": 90, "password": "abc123"}', 90, "abc123"),
        ('{"limit_minutes": 30}', 30, None),
        ('{"password": "letmein"}', None, "letmein"),
        ("{}", None, None),
    ],
)
def test_config_parsing_variants(
    patch_path, mock_json, expected_limit, expected_password
):
    with patch_path("CONFIG_FILE", "config.json", mock_json):
        config = gtl.load_config()

        # Grouped assert block with explanations
        assert (
            config.get("limit_minutes") == expected_limit
        ), "Incorrect limit_minutes from config"
        assert (
            config.get("password") == expected_password
        ), "Incorrect password from config"


@pytest.mark.parametrize(
    "file_content, expected_set",
    [
        ("game1.exe\ngame2.exe", {"game1.exe", "game2.exe"}),
        ("  game3.exe  \n\n", {"game3.exe"}),
        (
            "game4.exe\n#commented.exe",
            {"game4.exe"},
        ),
        ("\n  \n  \t\n", set()),  # Only whitespace and blank lines
    ],
)
def test_app_list_variants(patch_path, tracker, file_content, expected_set):
    with patch_path("APPS_LIST", "apps_list.txt", file_content):
        apps = tracker.load_tracked_games()
        assert apps == expected_set


@pytest.mark.parametrize(
    "log_content, expected",
    [
        (
            '{"date": "2025-06-18", "game_times": {"game1.exe": 45, "game2.exe": 15}}',
            {"game1.exe": 45, "game2.exe": 15},
        ),
        ('{"date": "2025-06-18"}', {}),  # Missing game_times
        ("{}", {}),  # Minimal JSON
        ("", {}),  # Empty file
    ],
)
def test_log_file_loading(patch_path, log_content, expected):
    with patch_path("LOG_PATH", "log.json", log_content):
        result = gtl.load_game_times(gtl.LOG_PATH)
        assert result == expected


# WX logic testing


def test_ask_password_valid(monkeypatch):
    _ = wx.App(False)
    tracker = gtl.GameTimeTracker()

    mock_dialog = MagicMock()
    mock_dialog.ShowModal.return_value = wx.ID_OK
    mock_dialog.GetValue.return_value = gtl.DEFAULT_PASSWORD

    with patch("wx.TextEntryDialog", return_value=mock_dialog), patch.object(
        tracker, "Destroy"
    ) as mock_destroy:
        tracker.ask_password()
        mock_destroy.assert_called_once()


def test_ask_password_invalid(monkeypatch, wx_app):
    tracker = gtl.GameTimeTracker()

    mock_dialog = MagicMock()
    mock_dialog.ShowModal.return_value = wx.ID_OK
    mock_dialog.GetValue.return_value = "wrongpass"

    with patch("wx.TextEntryDialog", return_value=mock_dialog), patch(
        "wx.MessageBox"
    ) as mock_msgbox, patch.object(tracker, "Destroy") as mock_destroy:
        tracker.ask_password()
        mock_msgbox.assert_called_once_with(
            "Incorrect Password!", "Access Denied", wx.OK | wx.ICON_ERROR
        )
        mock_destroy.assert_not_called()


def test_ask_password_cancel(monkeypatch, wx_app):
    tracker = gtl.GameTimeTracker()

    mock_dialog = MagicMock()
    mock_dialog.ShowModal.return_value = wx.ID_CANCEL

    with patch("wx.TextEntryDialog", return_value=mock_dialog), patch.object(
        tracker, "Destroy"
    ) as mock_destroy:
        tracker.ask_password()
        mock_destroy.assert_not_called()


# Saving log file testing


def test_save_game_times(wx_app, tmp_path, capsys):
    tracker = gtl.GameTimeTracker()
    tracker.log_path = tmp_path / "bad_log.json"
    tracker.game_times = {"javaw.exe": 45}

    with patch("pathlib.Path.open", side_effect=PermissionError("No write access")):
        tracker.save_game_times()
        out, err = capsys.readouterr()
        assert "Failed to save game times" in out
