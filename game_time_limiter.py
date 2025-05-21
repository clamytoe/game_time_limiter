import json
import sys
import time
from pathlib import Path

import psutil
import wx


def get_base() -> Path:
    """Determine the correct base directory, whether running as a script or an EXE."""
    if getattr(sys, "frozen", False):
        return Path.home() / "AppData" / "Roaming"
        # return Path(sys.executable).parent  # EXE location
    else:
        return Path(__file__).parent  # Script location


BASE_DIR = get_base()
CONFIG_FILE = BASE_DIR / "gtl_config.json"


def load_config():
    if CONFIG_FILE.exists():
        with CONFIG_FILE.open("r") as file:
            return json.load(file)
    return {}


config = load_config()

# Default values
DEFAULT_LIMIT_MINUTES = 120
DEFAULT_APPS_LIST = BASE_DIR / "apps_list.txt"
DEFAULT_LOG_PATH = BASE_DIR / "GameTimeLog.json"
DEFAULT_TITLE = "Game Time Tracker"
DEFAULT_PASSWORD = "password"

# Assign values from config file
LIMIT_MINUTES = config.get("limit_minutes", DEFAULT_LIMIT_MINUTES)
APPS_LIST = Path(config.get("apps_list", DEFAULT_APPS_LIST))
LOG_PATH = Path(config.get("log_path", DEFAULT_LOG_PATH))
TITLE = config.get("title", DEFAULT_TITLE)
PASSWORD = config.get("password", DEFAULT_PASSWORD)

# For testing python script
print(f"{PASSWORD=}")


class GameTimeTracker(wx.Frame):
    def __init__(
        self,
        title: str,
        limit_minutes: int,
        apps_list: Path,
        log_path: Path,
        password: str,
    ) -> None:
        """
        Initialize the GameTimeTracker window and set up UI elements.

        The GameTimeTracker window displays a progress bar showing the percentage
        of time used and a button to toggle the visibility of a list of games being
        tracked. The window is initially created with a smaller size and the game
        list is hidden.

        Parameters:
        title (str): The title of the window.
        limit_minutes (int): The total amount of time to allow for games to be played.
        apps_list (Path): The path to a text file containing a list of games to track.
        log_path (Path): The path to a JSON file to store game playtimes.
        password (str): The password to use for encrypting/decrypting the log file.

        Returns:
        None
        """
        self.title = title
        self.limit_minutes = limit_minutes
        self.apps_list = apps_list
        self.tracked_games = self.load_tracked_games()
        self.log_path = log_path
        self.game_times = self.load_game_times()
        self.password = password

        super().__init__(None, title=self.title, size=wx.Size(350, 300))
        self.Bind(wx.EVT_CLOSE, self.on_close_attempt)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Progress Bar
        self.progress_bar = wx.Gauge(
            panel, range=self.limit_minutes, size=wx.Size(320, 25)
        )
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
        self.SetTitle(f"{self.title} - {percentage_used:.1f}%")

        # Update game list display
        self.game_listbox.Clear()
        for game in self.tracked_games:
            self.game_listbox.Append(
                f"{game.rstrip('.exe')} - {self.game_times[game]} min"
            )

        # Show 10-minute warning
        if used_minutes >= (self.limit_minutes - 10) and not self.warning_shown:
            wx.MessageBox(
                "Warning: You have 10 minutes left!",
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
        if self.apps_list.exists():
            with self.apps_list.open("r") as file:
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
                log_date = data.get("date")

                # If log date is outdated, reset all playtimes
                if log_date != time.strftime("%Y-%m-%d"):
                    return {game: 0 for game in self.tracked_games}

                return data.get("game_times", {})

        # If log file doesn't exist, initialize game times
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

    def ask_password(self):
        """
        Prompts the user to enter an admin password to exit the application.

        When the user attempts to close the application, this function is called.
        It displays a password dialog with a password entry field and OK/Cancel
        buttons. If the user enters the correct password, the application is
        closed. If the user enters an incorrect password or cancels, an error
        message is displayed and the application remains open.

        The password is currently hardcoded as "mys3cur3p@$$w0rd!".
        """
        dlg = wx.TextEntryDialog(
            self,
            "Enter Admin Password:",
            "Restricted Access",
            style=wx.TE_PASSWORD | wx.OK | wx.CANCEL,
        )

        if dlg.ShowModal() == wx.ID_OK:  # Ensures user can press OK
            entered_password = dlg.GetValue()
            dlg.Destroy()

            # Validate the password
            if entered_password == self.password:
                self.Destroy()  # Close the app
            else:
                wx.MessageBox(
                    "Incorrect Password!", "Access Denied", wx.OK | wx.ICON_ERROR
                )

        else:
            dlg.Destroy()  # Close dialog if user cancels

    def on_close_attempt(self, event):
        """
        Handle the close event for the application window.

        This function is triggered when the user attempts to close the application
        window. It invokes the ask_password method to prompt the user for an admin
        password, ensuring that unauthorized users cannot terminate the application
        without the correct credentials.

        Parameters:
        event: The wxPython event object triggered by the close attempt.
        """
        self.ask_password()


if __name__ == "__main__":
    app = wx.App(False)
    GameTimeTracker(
        title=TITLE,
        log_path=LOG_PATH,
        apps_list=APPS_LIST,
        limit_minutes=LIMIT_MINUTES,
        password=PASSWORD,
    )
    app.MainLoop()
