import sys
from pathlib import Path

# Detect if running as an EXE
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent  # Get the executable's directory
else:
    BASE_DIR = Path(__file__).parent  # Get script's directory when running normally

# Define tracked games file path
FILE = BASE_DIR / Path("found_games.txt")
IGNORED_EXES = [
    "uninst.exe",
    "launcher.exe",
]


def find_game_executables(platform_dir: Path) -> set[str]:
    """
    Find all game executables in a given platform directory.
    Goes one level deeper only for subdirectories whose names
    start with their parent directory's name.

    Parameters:
    platform_dir (Path): The directory to search for games.

    Returns:
    set[str]: A set of executable names found in the directory.
    """
    game_executables = set()

    for game_folder in platform_dir.iterdir():
        if game_folder.is_dir():
            # First level: scan for .exe files directly inside game_folder
            for file in game_folder.glob("*.exe"):
                if file.name not in IGNORED_EXES:
                    game_executables.add(file.name)
            # Second level: only scan subdirectories whose names start with
            # game_folder's name
            for sub_folder in game_folder.iterdir():
                if sub_folder.is_dir() and sub_folder.name.startswith(
                    game_folder.name.replace("Launcher", "")
                ):
                    for file in sub_folder.glob("*.exe"):
                        if file.name not in IGNORED_EXES:
                            game_executables.add(file.name)
    return game_executables


def show_games(platform: str, games: set[str]):
    """
    Print a list of games found on a given platform.

    Parameters:
    platform (str): The name of the platform (e.g. "Steam", "EpicGames")
    games (set[str]): A set of game executable names found on the platform
    """

    with FILE.open("a") as file:
        print(f"\n[{platform}]")
        file.write(f"\n[{platform}]\n")
        for game in games:
            print(game)
            file.write(game + "\n")


def epic():
    """
    Scans the default EpicGames installation directory for games and prints a
    list of found executables.

    Note: You can update the default installation directory by modifying the
    `epic_dir` variable.
    """
    epic_dir = Path("D:/Epic/Games")  # custom directory
    if not epic_dir.is_dir():
        epic_dir = Path("C:/Program Files (x86)/Epic Games/Launcher/Engine/Programs")

    epic_games = find_game_executables(epic_dir)
    # Print detected games
    show_games("EpicGames", epic_games)


def steam():
    """
    Scans the default Steam installation directory for games and prints a
    list of found executables.

    Note: You can update the default installation directory by modifying the
    `steam_dir` variable.
    """
    steam_dir = Path("D:/SteamLibrary/steamapps/common")  # custom directory
    if not steam_dir.is_dir():
        steam_dir = Path("C:/Program Files (x86)/Steam/steamapps/common")

    steam_games = find_game_executables(steam_dir)
    # Print detected games
    show_games("Steam", steam_games)


def main():
    """
    Main entry point of the script.

    Calls both the `steam` and `epic` functions to scan their respective
    directories for games and print a list of found executables.
    """
    steam()
    epic()


if __name__ == "__main__":
    main()
