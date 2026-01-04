import requests
import os
import sys
import re
from tkinter import messagebox
import subprocess

def get_latest_release():
    # Removido Token exposto. Use variáveis de ambiente ou acesso público.
    repo_url = "https://api.github.com/repos/AyronGPT/SenhaDoDia_4.0/releases/latest"
    try:
        response = requests.get(repo_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao verificar atualizações: {e}")
        return None

def version_to_tuple(version):
    match = re.match(r"v(\d+)\.(\d+)\.(\d+)", version)
    return tuple(map(int, match.groups())) if match else (0, 0, 0)

def download_file(asset_url, dest_path):
    try:
        # Para assets em repositórios públicos, o download direto do browser_download_url é mais simples
        response = requests.get(asset_url, stream=True, timeout=30)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Erro ao baixar: {e}")
        return False

def check_for_update(current_version):
    current_exe_name = "SenhaDoDia_4.0.exe"
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", current_exe_name)

    release_info = get_latest_release()
    if not release_info: return

    latest_version = release_info.get("tag_name", "v0.0.0")
    if version_to_tuple(latest_version) <= version_to_tuple(current_version):
        return

    for asset in release_info.get("assets", []):
        if asset["name"] == current_exe_name:
            if messagebox.askyesno("Atualização", f"Nova versão {latest_version} disponível. Baixar?"):
                # Usando browser_download_url para evitar problemas de autenticação com assets
                if download_file(asset["browser_download_url"], downloads_path):
                    messagebox.showinfo("Sucesso", "Download concluído na pasta Downloads.")
                    subprocess.Popen(f'explorer /select,"{downloads_path}"')
                    sys.exit(0)