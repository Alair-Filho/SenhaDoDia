# src/themes.py
from __future__ import annotations

# ==========================
# Fonte única de cores (Design Tokens)
# ==========================
THEME_LIGHT = {
    "bg_janela": "#f3f4f6",
    "bg_card": "#f3f4f6",
    "text": "#111827",
    "muted": "#6b7280",
    "success": "#16a34a",
    "entry_bg": "#f3f4f6",
    "btn_bg": "#4f46e5",
    "btn_fg": "white",
}

THEME_DARK = {
    "bg_janela": "#2d2d2d",
    "bg_card": "#2d2d2d",
    "text": "white",
    "muted": "#9ca3af",
    "success": "#22c55e",
    "entry_bg": "#444444",
    "btn_bg": "#3f3f3f",
    "btn_fg": "white",
}


def get_theme(tema_escuro: bool) -> dict:
    """Retorna o dicionário do tema atual (claro/escuro)."""
    return THEME_DARK if tema_escuro else THEME_LIGHT


def aplicar_tema(janela, container, card, widgets, entries, botoes, theme: dict):
    """
    Aplica um tema (dict) em toda a interface.

    - janela/container/card: frames principais
    - widgets: labels (lista)
    - entries: entradas (lista)
    - botoes: botões (lista)
    """
    bg_janela = theme["bg_janela"]
    bg_card = theme["bg_card"]
    fg_texto = theme["text"]
    fg_muted = theme["muted"]
    fg_success = theme["success"]
    bg_entry = theme["entry_bg"]
    bg_btn = theme["btn_bg"]
    fg_btn = theme["btn_fg"]

    # Janela / containers
    janela.configure(bg=bg_janela)
    container.configure(bg=bg_janela)
    card.configure(bg=bg_card)

    # Labels
    for lbl in widgets:
        texto = lbl.cget("text") or ""

        if "Versão" in texto:
            lbl.configure(bg=bg_card, fg=fg_muted)
        elif "Senha Capturada" in texto:
            lbl.configure(bg=bg_card, fg=fg_success)
        else:
            lbl.configure(bg=bg_card, fg=fg_texto)

    # Entradas
    for entry in entries:
        entry.configure(
            bg=bg_entry,
            fg=fg_texto,
            insertbackground=fg_texto
        )

    # Botões
    for btn in botoes:
        btn.configure(
            bg=bg_btn,
            fg=fg_btn,
            activebackground=bg_btn
        )


def alternar_tema(janela, container, card, widgets, entries, botoes, tema_escuro: bool) -> bool:
    """
    Alterna entre claro/escuro, aplica o novo tema e retorna o novo estado.
    """
    novo_tema_escuro = not tema_escuro
    aplicar_tema(janela, container, card, widgets, entries, botoes, get_theme(novo_tema_escuro))
    return novo_tema_escuro
