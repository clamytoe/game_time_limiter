# Parental Controls: Game Time Limiter (*game_time_limiter*)

> *Application for setting a time limit for kids Windows games and applications.*

![Python version][python-version]
![Latest version][latest-version]
[![GitHub issues][issues-image]][issues-url]
![Coverage](https://img.shields.io/badge/Coverage-84%25-brightgreen)
[![GitHub forks][fork-image]][fork-url]
[![GitHub Stars][stars-image]][stars-url]
[![License][license-image]][license-url]

NOTE: This project was generated with [Cookiecutter](https://github.com/audreyr/cookiecutter) along with [@clamytoe's](https://github.com/clamytoe) [toepack](https://github.com/clamytoe/toepack) project template.

## Initial setup

```zsh
cd Projects
git clone https://github.com/clamytoe/game_time_limiter.git
cd game_time_limiter
```

### Anaconda setup

If you are an Anaconda user, this command will get you up to speed with the base installation.

```zsh
conda env create
conda activate game_time_limiter
```

### Regular Python setup

If you are just using normal Python, this will get you ready, but I highly recommend that you do this in a virtual environment.
There are many ways to do this, the simplest using *venv*.

```zsh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Create Windows executable

```cmd
pyinstaller --onefile --windowed --icon=OGS.ico game_time_limiter.py
```

### Configuration

I've made it so that you can configure the app before it is run. This is done by creating a `config.json` file in the base directory of the application. Just modify the values in the file to suit your needs.

**config.json**:

```json
{
    "limit_minutes": 120,
    "log_path": "C:/Users/clamy/AppData/Roaming/GameTimeLog.json",
    "apps_list": "C:/Users/clamy/Documents/apps_list.txt",
    "password": "mysecurepassword"
}
```

## Additional tools

I've provided additional scripts to help with finding what Steam and Epic Games are installed on the system, along with another to display the currently running executables.

```zsh
> python find_games.py

[Steam]
LockdownProtocol.exe
Myst.exe
HogwartsLegacy.exe
ClearThirdParty.exe
StillWakesTheDeep.exe
Warhammer 40,000 Boltgun.exe
Wuthering Waves.exe
Riven.exe

[EpicGames]
InfinityNikki.exe
```

and

```zsh
> python active_processes.py

[Processes]
ASUS_FRQ_Control.exe
AacAmbientLighting.exe
AcPowerNotification.exe
AcrobatNotificationClient.exe
AdobeCollabSync.exe
AggregatorHost.exe
AppVShNotify.exe
AppleMobileDeviceService.exe
ApplicationFrameHost.exe
ArmouryCrate.Service.exe
ArmouryCrate.UserSessionHelper.exe
ArmouryCrate.exe
ArmouryHtmlDebugServer.exe
ArmourySocketServer.exe
ArmourySwAgent.exe
...
```

These will make it easy to populate the `apps_list.txt` file.

**apps_list.txt**:

```txt
javaw.exe
InfinityNikki.exe
Minecraft.Windows.exe
MinecraftDungeons.exe
RobloxPlayerBeta.exe
steam.exe
```

## Auto Starting the Application

So that the application starts automatically when the user logs in we will add a new Task to the Task Scheduler.

### Start Task Scheduler

1. Win+R: taskschd.msc
2. Click: OK

### Adding New Task

1. Select Task Scheduler (Local)
2. From menu: Action > Create Task...
3. Type: Game Time Limiter
4. Under Security options: Select Run when user is logged on
5. Select Triggers
6. Click on New...
7. Begin the task: At log on
8. Settings: Any user
9. Advanced settings: Enabled
10. Click: OK
11. Select Actions
12. Click on New...
13. Actions: Start a program
14. Settings > Program/script: Browse to location of game_time_limiter.exe
15. Start in (optional): Enter the path to base directory of executable
16. Click: OK
17. Click: OK

## Contributing

Contributions are welcomed.
Tests can be run with with `pytest -v`, please ensure that all tests are passing and that you've checked your code with the following packages before submitting a pull request:

* black
* flake8
* isort
* mypy
* pytest-cov

I am not adhering to them strictly, but try to clean up what's reasonable.

## License

Distributed under the terms of the [MIT](https://opensource.org/licenses/MIT) license, "game_time_limiter" is free and open source software.

## Issues

If you encounter any problems, please [file an issue](https://github.com/clamytoe/toepack/issues) along with a detailed description.

## Changelog

* **v0.1.1** Modified badge url for license file from master to main branch.
* **v0.1.0** Initial commit.

[python-version]:https://img.shields.io/badge/python-3.13.3-brightgreen.svg
[latest-version]:https://img.shields.io/badge/version-0.1.1-blue.svg
[issues-image]:https://img.shields.io/github/issues/clamytoe/game_time_limiter.svg
[issues-url]:https://github.com/clamytoe/game_time_limiter/issues
[fork-image]:https://img.shields.io/github/forks/clamytoe/game_time_limiter.svg
[fork-url]:https://github.com/clamytoe/game_time_limiter/network
[stars-image]:https://img.shields.io/github/stars/clamytoe/game_time_limiter.svg
[stars-url]:https://github.com/clamytoe/game_time_limiter/stargazers
[license-image]:https://img.shields.io/github/license/clamytoe/game_time_limiter.svg
[license-url]:https://github.com/clamytoe/game_time_limiter/blob/main/LICENSE
