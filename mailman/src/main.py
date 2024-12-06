import subprocess
import json
from pathlib import Path

from mailman.src.parser.parser import *


home = Path.home()

temp_dir = "/tmp/mailman"

final_dir = f"{home}/.backup"

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
    subprocess.run(f"env > {temp_dir}/environment.env", shell=True, text=True, capture_output=True)


def os_package_manager_sources_report():
    Path(f"{temp_dir}/apt/sources").mkdir(parents=True, exist_ok=True)
    location = "/etc/apt/sources.list.d"
    subprocess.run(f"cp {location}/* {temp_dir}/apt/sources", shell=True, text=True, capture_output=True)


def dotfiles_backup():
    Path(f"{temp_dir}/dotfiles").mkdir(parents=True, exist_ok=True)
    subprocess.run(f"cp -r {home}/.dotfiles/* {temp_dir}/dotfiles", shell=True, text=True, capture_output=True)


def export_to_zip():
    import zipfile
    import time
    import os

    arquivo = f"os_config_backup_{time.time()}.zip"

    zip_file_path = f"{final_dir}/{arquivo}"
    folder_path = f"{temp_dir}"

    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Adiciona o arquivo ao ZIP com o caminho relativo
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)


# ---------------------------------------------------------------------------------------------------------- #


def __export(output_file: str):
    apps_report(output_file)
    environment_report()
    os_package_manager_sources_report()
    dotfiles_backup()
    export_to_zip()


def __import(source):
    pass


def centralize_dotfiles(file):
    Path(f"{home}/.dotfiles").mkdir(parents=True, exist_ok=True)
    slash_pos = file.find("/")
    if slash_pos == -1:
        slash_pos = 0
    subprocess.run(f"mv {file} {home}/.dotfiles", shell=True, text=True, capture_output=True)
    subprocess.run(f"ln -s {home}/.dotfiles/{file[slash_pos:]} {file}", shell=True, text=True, capture_output=True)
