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

    if atualizados and nao_encontrados or nao_encontrados:
        resp = messagebox.askyesno(
            "Atualização parcial",
            "Atualizei:\n- " + "\n- ".join(atualizados) +
            "\n\nNão encontrei:\n- " + "\n- ".join(nao_encontrados) +
            "\n\nDeseja criar os atalhos faltantes apontando para os executáveis do Vetor?"
        )
        if resp:
            shell = win32com.client.Dispatch("WScript.Shell")
            criados = []
            falhas = []
            desktops = _desktop_paths()
            destino_dir = desktops[0] if desktops else os.path.join(os.path.expanduser("~"), "Desktop")

            # tenta usar a variável de ambiente correta para Program Files (x86)
            program_files_x86 = os.environ.get("ProgramFiles(x86)") or os.environ.get("ProgramFiles") or r"C:\Program Files (x86)"
            vetor_dir = os.path.join(program_files_x86, "Vetor")

            for nome in nao_encontrados:
                caminho_novo = os.path.join(destino_dir, nome)
                try:
                    # determina o executável alvo conforme o nome do atalho
                    lower_nome = nome.lower()
                    if "vetorfarma" in lower_nome:
                        target_exe = os.path.join(vetor_dir, "VetorFarma.exe")
                    elif "vetorfiscal" in lower_nome:
                        target_exe = os.path.join(vetor_dir, "VetorFiscal.exe")
                    else:
                        target_exe = vetor_dir  # fallback para a pasta se não for possível mapear

                    sc = shell.CreateShortcut(caminho_novo)
                    sc.TargetPath = target_exe
                    sc.WorkingDirectory = vetor_dir
                    sc.Save()
                    criados.append(nome)
                except Exception as e:
                    falhas.append(f"{nome}: {e}")
            if criados:
                messagebox.showinfo("Atalhos criados", "Criei:\n- " + "\n- ".join(criados))
            if falhas:
                messagebox.showerror("Falha ao criar", "Falhas:\n- " + "\n- ".join(falhas))
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
