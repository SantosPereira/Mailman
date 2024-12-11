import subprocess
import json
from pathlib import Path

from mailman.src.parser.parser import *


home = Path.home()

temp_dir = "/tmp/mailman"

final_dir = f"{home}/.backup"

def apps_report(output_file):
    commands = [
        {"package-manager":"apt","command":"apt-mark showmanual", "parser": apt_out_parser, "importer": "apt update && apt install --fix-broken -y"},
        {"package-manager":"snap","command":"snap list", "parser": snap_out_parser, "importer": "snap install"},
        {"package-manager":"flatpak","command":"flatpak list --columns=name --columns=application", "parser": flatpak_out_parser, "importer": "flatpak install flathub"},
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
    import distro
    import json

    current_time = time.time()
    arquivo = f"{os.uname().nodename}_{distro.id()}_{distro.version()}_os_config_backup_{current_time}.zip"

    zip_file_path = f"{final_dir}/{arquivo}"
    folder_path = f"{temp_dir}"

    with open(f"{temp_dir}/manifest", "w") as foo:
        infos = {
            "hostname": os.uname().nodename,
            "os_name": distro.id(),
            "os_version": distro.version(),
            "export_creation_time": current_time
        }
        foo.write(json.dumps(infos))

    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)


def extract_backup(source):
    Path(f"{home}/.backup").mkdir(parents=True, exist_ok=True)
    import zipfile

    with zipfile.ZipFile(source, 'r') as zip_ref:
        zip_ref.extractall(f"{home}/.backup")


def load_env(path):
    with open(path+"/environment.env", "r") as foo:
        env_vars = foo.read()
    subprocess.run(f'echo "{env_vars}" >> /etc/environment', shell=True, text=True, capture_output=True)
    subprocess.run(f"sed 's/^/export /' /etc/environment > /tmp/env.sh && source /tmp/env.sh", shell=True, text=True, capture_output=True)


def load_apps(path):
    import json

    apps_list = json.load(open(path+'/apps.json', "r"))

    install_list = ""

    for i in apps_list:
        if i['package-manager'] == 'apt':
            for j in i['apps']:
                install_list += f"{j['name']} "
            
            subprocess.run(f'{i["importer"]} {install_list}', shell=True, text=True, capture_output=True)
            install_list = ""
        
        elif i['package-manager'] == 'flatpak':
            for k in i['apps']:
                install_list += f"{k['name']} "
            
            subprocess.run(f'{i["importer"]} {install_list}', shell=True, text=True, capture_output=True)
            install_list = ""
        
        elif i['package-manager'] == 'snap':
            for l in i['apps']:
                install_list += f"{l['name']} "
            
            subprocess.run(f'{i["importer"]} {install_list}', shell=True, text=True, capture_output=True)
            install_list = ""
    

def load_sources_apt(path):
    subprocess.run(f'mv {path}/apt/sources/* /etc/apt/sources.list.d', shell=True, text=True, capture_output=True)
    subprocess.run(f'apt update', shell=True, text=True, capture_output=True)


def restore_dotfiles(path):
    from pathlib import Path
    Path(f"{home}/.dotfiles").mkdir(parents=True, exist_ok=True)
    subprocess.run(f'mv {path}/dotfiles/* {home}/.dotfiles', shell=True, text=True, capture_output=True)


    pasta_dotfiles = Path(f'{home}/.dotfiles')

    dotfiles = [arquivo for arquivo in pasta_dotfiles.iterdir() if arquivo.is_file()]

    import re
    padrao = r'^/home/([a-zA-Z0-9_]+)'

    for i in range(len(dotfiles)):
        with open(f"{home}/dotfiles/manifest/{dotfiles[i].name}.path") as foo:
            destino = foo.read()
        
        match = re.match(padrao, destino)
        if match:
            destino = f"{home}{destino[match.end(1):]}"
        
        decentralize_dotfiles(dotfiles[i], destino)



# TODO ~~> Implementar meio de garantir que todas as pastas parent existam
def decentralize_dotfiles(file, destine):
    slash_pos = destine.rfind("/")
    destine_path = destine[:slash_pos]
    Path(f"{destine_path}").mkdir(parents=True, exist_ok=True)
    Path(f"{home}/.dotfiles/manifest/").mkdir(parents=True, exist_ok=True)
   
    subprocess.run(f"mv {file} {home}/.dotfiles", shell=True, text=True, capture_output=True)
    subprocess.run(f"ln -s {home}/.dotfiles {destine}", shell=True, text=True, capture_output=True)

    with open(f"{home}/.dotfiles/manifest/{file.name}.path", "w") as foo:
        foo.write(file)


# ---------------------------------------------------------------------------------------------------------- #


def __export(output_file: str):
    apps_report(output_file)
    environment_report()
    os_package_manager_sources_report()
    dotfiles_backup()
    export_to_zip()


def import_config(source):
    extract_backup(source)
    load_env(f'{home}/.backup')
    load_sources_apt(f'{home}/.backup')
    load_apps(f'{home}/.backup')
    restore_dotfiles(f'{home}/.backup')


def centralize_dotfiles(file):
    Path(f"{home}/.dotfiles/manifest").mkdir(parents=True, exist_ok=True)
    slash_pos = file.rfind("/")
    if slash_pos == -1:
        slash_pos = 0
    file_name = file[slash_pos+1:]
    subprocess.run(f"mv {file} {home}/.dotfiles", shell=True, text=True, capture_output=True)
    subprocess.run(f"ln -s {home}/.dotfiles/{file_name} {file}", shell=True, text=True, capture_output=True)

    with open(f"{home}/.dotfiles/manifest/{file_name}.path", "w") as foo:
        foo.write(file)


