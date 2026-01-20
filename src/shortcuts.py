import os
from tkinter import messagebox
import win32com.client


# =========================
# Localizar atalhos
# =========================
def _desktop_paths() -> list[str]:
    user = os.path.expanduser("~")
    paths = [
        os.path.join(user, "Desktop"),
        os.path.join(user, "OneDrive", "Desktop"),
    ]
    return [p for p in paths if os.path.isdir(p)]


def _find_shortcut(nome_atalho: str) -> str | None:
    for d in _desktop_paths():
        p = os.path.join(d, nome_atalho)
        if os.path.exists(p):
            return p
    return None


# =========================
# Atualizar argumentos (.lnk)
# =========================
def _set_shortcut_args(caminho_atalho: str, args: str) -> None:
    shell = win32com.client.Dispatch("WScript.Shell")
    sc = shell.CreateShortcut(caminho_atalho)

    if not sc.TargetPath:
        raise RuntimeError("Atalho sem destino (TargetPath).")

    sc.Arguments = args
    sc.Save()


def modificar_atalhos(senha: str, nomes_atalhos: list[str]) -> None:
    if not senha:
        messagebox.showwarning("Aviso", "Senha vazia. Capture a senha antes de atualizar.")
        return

    atualizados = []
    nao_encontrados = []

    for nome in nomes_atalhos:
        caminho = _find_shortcut(nome)
        if not caminho:
            nao_encontrados.append(nome)
            continue

        try:
            _set_shortcut_args(caminho, senha)
            atualizados.append(nome)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar '{nome}': {e}")
            return

    if atualizados and nao_encontrados:
        messagebox.showwarning(
            "Atualização parcial",
            "Atualizei:\n- " + "\n- ".join(atualizados) +
            "\n\nNão encontrei:\n- " + "\n- ".join(nao_encontrados)
        )
        return

    if atualizados:
        messagebox.showinfo(
            "Sucesso",
            "Senha aplicada nos atalhos:\n- " + "\n- ".join(atualizados)
        )
        return

    messagebox.showerror(
        "Erro",
        "Não encontrei nenhum dos atalhos informados no Desktop (local/OneDrive)."
    )


# =========================
# NOVO: abrir atalho VetorFarma
# =========================
def abrir_vetorfarma(nome_atalho: str = "VetorFarma.lnk") -> None:
    """
    Abre o atalho VetorFarma (equivalente a dar duplo clique).
    Procura no Desktop local e no OneDrive Desktop.
    """
    caminho = _find_shortcut(nome_atalho)

    if not caminho:
        messagebox.showerror(
            "Atalho não encontrado",
            f"Não encontrei '{nome_atalho}' no Desktop (local/OneDrive)."
        )
        return

    try:
        os.startfile(caminho)  # abre o .lnk como se fosse duplo clique
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao abrir '{nome_atalho}': {e}")
