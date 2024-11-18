import subprocess
import json

from src.parser.parser import *


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


with open("./apps.json", "w") as file:
    file.write(json.dumps(packages))


print(packages)