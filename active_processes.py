import psutil


def running_process():
    """
    Print a list of currently running processes.

    This function uses the psutil library to iterate over all currently
    running processes on the system, collects their names, and prints
    them in a sorted order. Empty process names are excluded from the
    output.
    """

    running_games = {p.name() for p in psutil.process_iter()}
    print("\n[Processes]")
    for game in sorted(running_games):
        if game != "":
            print(game)


if __name__ == "__main__":
    running_process()
