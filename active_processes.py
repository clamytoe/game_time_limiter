import sys
from pathlib import Path

import psutil

# Detect if running as an EXE
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent  # Get the executable's directory
else:
    BASE_DIR = Path(__file__).parent  # Get script's directory when running normally

# Define tracked games file path
FILE = BASE_DIR / Path("found_processes.txt")


def running_process():
    """
    Print a list of currently running processes.

    This function uses the psutil library to iterate over all currently
    running processes on the system, collects their names, and prints
    them in a sorted order. Empty process names are excluded from the
    output.
    """

    running_games = {p.name() for p in psutil.process_iter()}
    with FILE.open("w") as file:
        print("\n[Processes]")

        for game in sorted(running_games):
            if game != "":
                print(game)
                file.write(game + "\n")


if __name__ == "__main__":
    running_process()
