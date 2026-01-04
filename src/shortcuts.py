import os
from tkinter import messagebox
import win32com.client

def modificar_atalho(senha):
    nome_atalho = "VetorFarma.lnk"

    # Área de trabalho local
    caminho_area_trabalho = os.path.join(os.path.expanduser("~"), "Desktop")
    caminho_atalho = os.path.join(caminho_area_trabalho, nome_atalho)

    # Se não existir, tenta no OneDrive
    if not os.path.exists(caminho_atalho):
        caminho_onedrive = os.path.join(os.path.expanduser("~"), "OneDrive")
        caminho_area_trabalho_onedrive = os.path.join(caminho_onedrive, "Desktop")
        caminho_atalho = os.path.join(caminho_area_trabalho_onedrive, nome_atalho)

        if not os.path.exists(caminho_atalho):
            messagebox.showerror("Erro",
                                 f"Atalho '{nome_atalho}' não encontrado na área de trabalho ou no OneDrive.")
            return

    # Carregar atalho
    shell = win32com.client.Dispatch("WScript.Shell")
    atalho = shell.CreateShortcut(caminho_atalho)

    destino_atual = atalho.TargetPath
    if not destino_atual:
        messagebox.showerror("Erro",
                             f"Não foi possível obter o destino do atalho '{nome_atalho}'.")
        return

    # Garante que o caminho esteja entre aspas
    if not destino_atual.startswith('"') and not destino_atual.endswith('"'):
        destino_atual = f'"{destino_atual}"'

    atalho.Arguments = senha
    atalho.save()

    messagebox.showinfo("Sucesso",
                        f"A senha foi adicionada ao campo 'Destino' do atalho '{nome_atalho}'.")
