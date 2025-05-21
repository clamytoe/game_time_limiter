"""
test_game_time_limiter.py

Tests for game_time_limiter.
"""

import pytest
import wx

from game_time_limiter import (
    APPS_LIST,
    LIMIT_MINUTES,
    LOG_PATH,
    PASSWORD,
    TITLE,
    GameTimeTracker,
)


@pytest.fixture(scope="module")
def gtt():
    """
    A fixture that creates a GameTimeTracker with the default values.

    Scope is at the module level, so this will be created once per module.
    """
    _ = wx.App(False)
    return GameTimeTracker(TITLE, LIMIT_MINUTES, APPS_LIST, LOG_PATH, PASSWORD)


@pytest.fixture(scope="function")
def gtt_custom(tmp_path):
    """
    A fixture that creates a GameTimeTracker with custom values for testing.

    This fixture uses a temporary path to create test files for the apps list
    and log. It provides a GameTimeTracker instance with a title of "Test Tracker",
    a playtime limit of 60 minutes, and paths to the temporary apps list and log files.

    Parameters:
    tmp_path: Pytest fixture that provides a temporary directory unique to the test
    invocation.

    Returns:
    GameTimeTracker: An instance of GameTimeTracker configured with test-specific
    values.
    """
    _ = wx.App(False)
    title = "Test Tracker"
    limit = 60
    apps = tmp_path / "test_apps.txt"
    log = tmp_path / "test_log.json"
    password = "admin"
    return GameTimeTracker(title, limit, apps, log, password)


def test_title(gtt_custom):
    assert gtt_custom.title == "Test Tracker"


def test_limit_minutes(gtt_custom):
    assert gtt_custom.limit_minutes == 60


def test_apps_list(gtt_custom):
    assert gtt_custom.apps_list.name == "test_apps.txt"


def test_log_path(gtt_custom):
    assert gtt_custom.log_path.name == "test_log.json"


def test_load_game_times(gtt):
    assert gtt.game_times.get("javaw.exe") == 0
    assert gtt.game_times.get("GuildWars2.exe", None) is None


def test_load_tracked_games(gtt):
    assert gtt.tracked_games == {
        "javaw.exe",
        "Minecraft.Windows.exe",
        "MinecraftDungeons.exe",
        "RobloxPlayerBeta.exe",
    }
