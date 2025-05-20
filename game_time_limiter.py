import json
import sys
import time
from pathlib import Path

import psutil
import wx


class GameTimeTracker(wx.Frame):
    def __init__(
        self, apps_list: str = "apps_list.txt", limit_minutes: int = 120
    ) -> None:
        """
        Initialize the GameTimeTracker application window.

        Parameters:
        apps_list (str): The filename of the text file containing the list of tracked
                        games. Defaults to "apps_list.txt".
        limit_minutes (int): The maximum allowed game time in minutes. Defaults to 120.

        Initializes various GUI components including a progress bar, toggle button,
        and game list box. Sets up a timer to update the game time tracking GUI
        every minute. Loads tracked games and their playtimes. Configures the
        window layout and displays a warning message when the time limit is near.
        """

        super().__init__(None, title="Game Time Tracker", size=wx.Size(350, 300))

        self.base_dir = self.get_base()
        self.limit_minutes = limit_minutes
        self.apps_list = apps_list
        self.tracked_games_file = self.base_dir / self.apps_list
        self.tracked_games = self.load_tracked_games()
        self.log_path = Path.home() / "AppData" / "Roaming" / "GameTimeLog.json"
        self.game_times = self.load_game_times()

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Progress Bar
        self.progress_bar = wx.Gauge(panel, range=limit_minutes, size=wx.Size(320, 25))
        vbox.Add(self.progress_bar, flag=wx.ALL | wx.EXPAND, border=10)

        # Toggle Button
        self.toggle_btn = wx.Button(panel, label="Hide List")
        self.toggle_btn.Bind(wx.EVT_BUTTON, self.toggle_list)
        vbox.Add(self.toggle_btn, flag=wx.ALL | wx.EXPAND, border=10)

        # Game List Box
        self.game_listbox = wx.ListBox(panel)
        vbox.Add(self.game_listbox, flag=wx.ALL | wx.EXPAND, border=10)

        panel.SetSizer(vbox)

        self.warning_shown = False
        self.alert_shown = False

        self.update_gui()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_gui, self.timer)
        self.timer.Start(60000)  # Update every 60 seconds

        self.game_listbox.Hide()  # Initially hide the game list
        self.SetSize(350, 130)  # Start with the smaller window
        self.toggle_btn.SetLabel("Show List")

        self.Show()

    def get_base(self) -> Path:
        """
        Determine the base directory of the application.

        If running as an executable, it is the directory of the executable.
        If running normally, it is the directory of the script.

        Returns:
            Path: The base directory of the application.
        """
        if getattr(sys, "frozen", False):
            # Get the executable's directory
            base_dir = Path(sys.executable).parent
        else:
            # Get script's directory when running normally
            base_dir = Path(__file__).parent

        return base_dir

    def toggle_list(self, event) -> None:
        """
        Toggle the visibility of the game list box in the application window.

        When the list is shown, the window expands to accommodate it and the button
        label changes to "Hide List". When the list is hidden, the window shrinks
        and the button label changes to "Show List".

        Parameters:
        event: The wxPython event object triggered by the button click.
        """

        if self.game_listbox.IsShown():
            self.game_listbox.Hide()  # Hide only the list, NOT the button
            self.SetSize(350, 130)  # Shrink window but keep button visible
            self.toggle_btn.SetLabel("Show List")
        else:
            self.game_listbox.Show()
            self.SetSize(350, 300)  # Expand window when list is visible
            self.toggle_btn.SetLabel("Hide List")
        self.Layout()

    def update_gui(self, event=None) -> None:
        """
        Update the graphical user interface of the Game Time Tracker.

        This function performs several tasks:
        - Identifies currently running games and increments their playtime.
        - Updates the progress bar to reflect total used minutes.
        - Sets the window title to show the percentage of time used.
        - Refreshes the game list display with current playtimes.
        - Displays a warning message when there are 5 minutes left.
        - Terminates tracked games and shows an alert when the time limit is reached.

        Parameters:
        event: Optional wxPython event object triggered by a timer or user interaction.
        """

        running_games = {p.name() for p in psutil.process_iter()}

        # Increment playtime only once per active game
        for game in self.tracked_games:
            if game in running_games:
                self.game_times[game] += 1

        # Update progress bar
        used_minutes = sum(self.game_times.values())
        self.progress_bar.SetValue(min(used_minutes, self.limit_minutes))

        # Update percentage in window title
        percentage_used = (used_minutes / self.limit_minutes) * 100
        self.SetTitle(f"Game Time Tracker - {percentage_used:.1f}%")

        # Update game list display
        self.game_listbox.Clear()
        for game in self.tracked_games:
            self.game_listbox.Append(
                f"{game.rstrip('.exe')} - {self.game_times[game]} min"
            )

        # Show 5-minute warning
        if used_minutes >= (self.limit_minutes - 5) and not self.warning_shown:
            wx.MessageBox(
                "Warning: You have 5 minutes left!",
                "Time Running Out",
                wx.OK | wx.ICON_WARNING,
            )
            self.warning_shown = True

        # Stop games when time runs out
        if used_minutes >= self.limit_minutes and not self.alert_shown:
            for p in psutil.process_iter():
                if p.name() in self.tracked_games:
                    p.terminate()
            wx.MessageBox(
                "Your game time is up for today!",
                "Limit Reached",
                wx.OK | wx.ICON_ERROR,
            )
            self.alert_shown = True

        self.save_game_times()

    def load_tracked_games(self) -> set:
        """
        Load tracked games from file.

        Reads the contents of the tracked games file into a set.
        If the file is missing, an empty set is returned.
        """
        if self.tracked_games_file.exists():
            with self.tracked_games_file.open("r") as file:
                return {line.strip() for line in file}

        return set()

    def load_game_times(self) -> dict:
        """
        Load playtime from file.

        Reads the contents of the log file into a dictionary with game names as
        keys and playtime in minutes as values. If the file is missing or the
        date is not today, an empty dictionary is returned.
        """
        if self.log_path.exists():
            with self.log_path.open("r") as file:
                data = json.load(file)
                if data["date"] == time.strftime("%Y-%m-%d"):
                    return data["game_times"]
        return {game: 0 for game in self.tracked_games}

    def save_game_times(self):
        """
        Save the current playtime data to a log file.

        This function writes the current date and playtime data for each tracked
        game to a JSON log file. The log file is stored at the specified log path.
        """

        data = {"date": time.strftime("%Y-%m-%d"), "game_times": self.game_times}
        with self.log_path.open("w") as file:
            json.dump(data, file)


if __name__ == "__main__":
    app = wx.App(False)
    GameTimeTracker()
    app.MainLoop()
