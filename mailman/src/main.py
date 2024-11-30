import subprocess
import json
from pathlib import Path

from mailman.src.parser.parser import *


home = Path.home()

def apps_report(output_file):
    commands = [
        {"package-manager":"apt","command":"apt-mark showmanual", "parser": apt_out_parser},
        {"package-manager":"snap","command":"snap list", "parser": snap_out_parser},
        {"package-manager":"flatpak","command":"flatpak list --columns=name --columns=application", "parser": flatpak_out_parser},
    ]

    packages = []
    for cmd in commands:
        resultado = subprocess.run(cmd["command"], shell=True, text=True, capture_output=True)
        cmd["apps"] = cmd["parser"](resultado.stdout)
        del cmd["parser"]
        packages.append(cmd)

    with open(output_file, "w") as file:
        file.write(json.dumps(packages))


def environment_report():
    subprocess.run(f"env > {home}/.backup/environment.env", shell=True, text=True, capture_output=True)


def os_package_manager_sources_report():
    Path(f"{home}/.backup/apt/sources").mkdir(parents=True, exist_ok=True)
    location = "/etc/apt/sources.list.d"
    subprocess.run(f"cp {location}/* {home}/.backup/apt/sources", shell=True, text=True, capture_output=True)


def dotfiles_backup():
    Path(f"{home}/.backup/dotfiles").mkdir(parents=True, exist_ok=True)
    subprocess.run(f"cp -r {home}/.dotfiles/* {home}/.backup/dotfiles", shell=True, text=True, capture_output=True)


# ---------------------------------------------------------------------------------------------------------- #


def export(output_file: str):
    apps_report(output_file)
    environment_report()
    os_package_manager_sources_report()
    dotfiles_backup()


def __import(source):
    pass


def save_dotfile(file):
    Path(f"{home}/.backup/dotfiles").mkdir(parents=True, exist_ok=True)
    slash_pos = file.find("/")
    if slash_pos == -1:
        slash_pos = 0
    subprocess.run(f"mv {file} {home}/.backup/dotfiles", shell=True, text=True, capture_output=True)
    subprocess.run(f"ln -s {home}/.backup/dotfiles/{file[slash_pos:]} {file}", shell=True, text=True, capture_output=True)
