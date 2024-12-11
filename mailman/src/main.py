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


# def environment_report():
#     subprocess.run(f"cat > {temp_dir}/environment.env", shell=True, text=True, capture_output=True)


def os_package_manager_sources_report():
    Path(f"{temp_dir}/apt/sources").mkdir(parents=True, exist_ok=True)
    location = "/etc/apt/sources.list.d"
    command_executor(f"cp {location}/* {temp_dir}/apt/sources")


def dotfiles_backup():
    Path(f"{temp_dir}/dotfiles").mkdir(parents=True, exist_ok=True)
    command_executor(f"cp -r {home}/.dotfiles/. {temp_dir}/dotfiles")


def export_to_zip():
    import zipfile
    import time
    import os
    import distro
    import json

    current_time = time.time()
    file = f"{os.uname().nodename}_{distro.id()}_{distro.version()}_os_config_backup_{current_time}.zip"

    zip_file_path = f"{final_dir}/{file}"
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
    command_executor(f'rm -rf {folder_path}')


def extract_backup(source):
    Path(f"{home}/.backup").mkdir(parents=True, exist_ok=True)
    import zipfile

    with zipfile.ZipFile(source, 'r') as zip_ref:
        zip_ref.extractall(f"{home}/.backup")


def load_env(path):
    with open(path+"/dotfiles/.environment.env", "r") as foo:
        env_vars = foo.read()
    command_executor(f'echo "{env_vars}" >> /etc/environment')
    command_executor(f"sed 's/^/export /' /etc/environment > /tmp/env.sh && chmod +x /tmp/env.sh && /tmp/env.sh")

def command_executor(command):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  
        text=True,
        shell=True                
    )
    for line in process.stdout:
        print(line, end="")  
    process.wait()


def load_apps(path):
    import json

    apps_list = json.load(open(path+'/apps.json', "r"))
    install_list = ""

    for i in apps_list:
        if i['package-manager'] == 'apt':
            for j in i['apps']:
                install_list += f"{j['name']} "
            command_executor(f'{i["importer"]} {install_list}')
            install_list = ""
        
        elif i['package-manager'] == 'flatpak':
            for k in i['apps']:
                install_list += f"{k['name']} "
            command_executor(f'{i["importer"]} {install_list}')
            install_list = ""
        
        elif i['package-manager'] == 'snap':
            for l in i['apps']:
                install_list += f"{l['name']} "
            command_executor(f'{i["importer"]} {install_list}')
            install_list = ""
    

def load_sources_apt(path):
    command_executor(f'mv {path}/apt/sources/* /etc/apt/sources.list.d')
    command_executor(f'apt update')


def restore_dotfiles(path):
    from pathlib import Path
    Path(f"{home}/.dotfiles").mkdir(parents=True, exist_ok=True)
    command_executor(f'cp -r {path}/dotfiles/. {home}/.dotfiles')
    command_executor(f'rm -rf {path}/dotfiles')

    pasta_dotfiles = Path(f'{home}/.dotfiles')
    dotfiles = [file for file in pasta_dotfiles.iterdir() if file.is_file()]

    import re
    padrao = r'^/home/([a-zA-Z0-9_]+)'

    for i in range(len(dotfiles)):
        with open(f"{home}/.dotfiles/manifest/{dotfiles[i].name}.path") as foo:
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
    command_executor(f"ln -s {home}/.dotfiles {destine}")
    with open(f"{home}/.dotfiles/manifest/{file.name}.path", "w") as foo:
        foo.write(str(file))


# ---------------------------------------------------------------------------------------------------------- #


def __export(output_file: str):
    apps_report(output_file)
    # environment_report()
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

    command_executor(f"mv {file} {home}/.dotfiles")
    command_executor(f"ln -s {home}/.dotfiles/{file_name} {file}")

    with open(f"{home}/.dotfiles/manifest/{file_name}.path", "w") as foo:
        foo.write(file)


