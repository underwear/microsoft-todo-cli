import os
import yaml
import requests
import todocli
from datetime import datetime, timedelta

DATE_FORMAT = "%Y%m%d"
PYPI_PACKAGE = "microsoft-todo-cli"


def check():
    """Check for updates once per day, silently fail on errors."""
    config_dir = "{}/.config/tod0".format(os.path.expanduser("~"))
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)

    last_update_check = datetime(1990, 1, 1)
    file_path = os.path.join(config_dir, "data.yml")
    if os.path.isfile(file_path):
        try:
            with open(file_path, "r") as f:
                data = yaml.load(f, yaml.SafeLoader)
                if data and "last_update_check" in data:
                    last_update_check = datetime.strptime(
                        data["last_update_check"], DATE_FORMAT
                    )
        except (OSError, yaml.YAMLError, ValueError):
            pass

    # Check for updates if it has been a day since last check
    if last_update_check + timedelta(days=1) < datetime.now():
        try:
            response = requests.get(
                f"https://pypi.org/pypi/{PYPI_PACKAGE}/json",
                timeout=5,
            )
            if response.ok:
                data = response.json()
                latest_version = data.get("info", {}).get("version", "0.0.0")
                latest_tuple = tuple(map(int, latest_version.split(".")[:3]))
                current_tuple = tuple(map(int, todocli.__version__.split(".")[:3]))

                if latest_tuple > current_tuple:
                    print(
                        f"Update available: {todocli.__version__} -> {latest_version}. "
                        f'Run "pip install --upgrade {PYPI_PACKAGE}"'
                    )

            with open(file_path, "w") as f:
                yaml.dump(
                    {"last_update_check": datetime.now().strftime(DATE_FORMAT)}, f
                )
        except (requests.RequestException, ValueError, KeyError, OSError):
            # Silently ignore update check failures
            pass
