test:
    pytest -v

coverage:
    pytest --cov=game_time_limiter --cov-report=term-missing

lint:
    flake8 game_time_limiter.py test_game_time_limiter.py

format:
    black game_time_limiter.py test_game_time_limiter.py

compile:
    pyinstaller --onefile --windowed --icon=OGS.ico game_time_limiter.py

helpers:
    pyinstaller --onefile --windowed --icon=OGS.ico active_processes.py
    pyinstaller --onefile --windowed --icon=OGS.ico find_games.py

all: compile helpers
