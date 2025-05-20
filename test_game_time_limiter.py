"""
test_game_time_limiter.py

Tests for game_time_limiter.
"""

from pathlib import Path

import pytest
import wx

from game_time_limiter import GameTimeTracker


@pytest.fixture
def gtt():
    _ = wx.App(False)
    return GameTimeTracker()


@pytest.fixture
def gtt_custom():
    _ = wx.App(False)
    apps = "test_apps.txt"
    limit = 60
    return GameTimeTracker(apps_list=apps, limit_minutes=limit)


def test_base_dir(gtt):
    base_dir = gtt.get_base()
    assert "game_time_limiter" in str(base_dir)


def test_limit_minutes(gtt_custom):
    assert gtt_custom.limit_minutes == 60


def test_apps_list(gtt_custom):
    assert gtt_custom.apps_list == "test_apps.txt"


def test_tracked_games_file(gtt_custom):
    assert gtt_custom.tracked_games_file == Path.cwd() / "test_apps.txt"


def test_log_path(gtt):
    assert gtt.log_path == Path.home() / "AppData" / "Roaming" / "GameTimeLog.json"


def test_load_game_times(gtt):
    assert gtt.game_times.get("javaw.exe") == 0
    assert gtt.game_times.get("GuildWars2.exe", None) is None


def test_load_tracked_games(gtt):
    assert gtt.tracked_games == {
        "javaw.exe",
        "Minecraft.Windows.exe",
        "MinecraftDungeons.exe",
        "RobloxPlayerBeta.exe",
        "steam.exe",
    }
