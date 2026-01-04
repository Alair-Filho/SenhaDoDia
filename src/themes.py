def alternar_tema(janela, container, card, widgets, entries, botoes, tema_escuro):
    tema_escuro = not tema_escuro

    if tema_escuro:
        bg_janela = "#1f2933"
        bg_card = "#2d2d2d"
        fg_texto = "white"
        fg_muted = "#9ca3af"
        fg_success = "#22c55e"
        bg_entry = "#444444"
        bg_btn = "#3f3f3f"
        fg_btn = "white"
    else:
        # 🔹 RESTAURA O LAYOUT ORIGINAL
        bg_janela = "#f4f6f8"
        bg_card = "#ffffff"
        fg_texto = "#111827"
        fg_muted = "#6b7280"
        fg_success = "#16a34a"
        bg_entry = "white"
        bg_btn = "#4f46e5"
        fg_btn = "white"

    # Janela
    janela.configure(bg=bg_janela)
    container.configure(bg=bg_janela)
    card.configure(bg=bg_card)

    # Labels (tratando tipos diferentes)
    for lbl in widgets:
        texto = lbl.cget("text")

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

    return tema_escuro
