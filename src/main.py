import tkinter as tk
from tkinter import messagebox
import threading
import pyperclip

# Módulos internos
from src import file_manager, email_services, shortcuts, themes, sound

CURRENT_VERSION = "v4.0.5"

# variaveis globais
senha_capturada = None
tema_escuro = False

# --- ESTILO ---
BG_COLOR = "#f4f6f8"
CARD_COLOR = "#ffffff"
TEXT_COLOR = "#111827"
MUTED = "#6b7280"
SUCCESS = "#16a34a"

DARK_DEFAULT = "#3f3f3f"  # cor padrão de botões no modo escuro

PALETAS = {
    "Roxo": "#4f46e5",
    "Azul": "#2563eb",
    "Vermelho": "#9B111E",
    "Verde": "#16a34a",
    "Laranja": "#f97316",
    "Rosa": "#db2777",
    "Cinza": "#6b7280"
}

PRIMARY_LIGHT = PALETAS["Roxo"]   # cor do modo claro (persistente)
PRIMARY_DARK = DARK_DEFAULT       # cor do modo escuro (por regra começa no padrão)
PRIMARY = PRIMARY_LIGHT           # cor atual usada nos botões principais
LAST_LIGHT_COLOR = PRIMARY_LIGHT

FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_SUB = ("Segoe UI", 10, "bold")
FONT_TEXT = ("Segoe UI", 9)
FONT_SMALL = ("Segoe UI", 8)
FONT_ICON = ("Segoe UI", 13)

PAD_Y = 2       # espacamento campo email e senha
PAD_BTN_Y = 8   # espaço vertical entre botões
PAD_BTN_X = 0   # se quiser espaço lateral extra


# ==========================
# Preferências de UI (visibilidade dos botões)
# ==========================
btn_visiveis = {
    "getcard": True,
    "fiserv": True,
    "senha_dia": True,
    "toggle": True,
    "atualizar": True,
    "abrir_farma": True,
    "abrir_fiscal": True,
    "copiar": True,
}

btn_grid_info = {}  # guarda o grid original de cada botão


def ui(callable_):
    """Executa algo com segurança no thread do Tk."""
    janela.after(0, callable_)


def run_bg(task_fn):
    """Executa uma função em background."""
    threading.Thread(target=task_fn, daemon=True).start()


def salvar_dados(usuario, senha, ultima_senha=None):
    # salva também o tema, cores e preferências de UI
    file_manager.salvar_dados(
        usuario,
        senha,
        ultima_senha,
        tema_escuro,
        PRIMARY_LIGHT,
        PRIMARY_DARK,
        btn_visiveis
    )


def carregar_dados():
    return file_manager.carregar_dados()


def atualizar_botao_tema(tema_escuro_local: bool):
    if tema_escuro_local:
        btn_tema.config(text="     ☀️", padx=6, pady=1)
    else:
        btn_tema.config(text="🌙", padx=6, pady=1)


def set_loading(
    button: tk.Button,
    loading: bool,
    text_loading: str = "Buscando...",
    text_normal: str | None = None
):
    if loading:
        button.config(text=text_loading, state="disabled")
    else:
        if text_normal is not None:
            button.config(text=text_normal)
        button.config(state="normal")


def capturar_senha():
    global senha_capturada
    usuario = entry_usuario.get().strip()
    senha = entry_senha.get().strip()

    if not usuario or not senha:
        messagebox.showwarning("Aviso", "Preencha e-mail e senha do app.")
        return

    def tarefa():
        ui(lambda: set_loading(btn_capturar, True, "Buscando...", "Buscar Senha do Dia"))

        senha_res, erro = email_services.buscar_senha_gmail(usuario, senha)

        def finish():
            set_loading(btn_capturar, False, text_normal="Buscar Senha do Dia")

            if erro:
                messagebox.showwarning("Aviso", erro)
                return
            if not senha_res:
                messagebox.showwarning("Aviso", "Senha não encontrada.")
                return

            global senha_capturada
            senha_capturada = senha_res
            lbl_senha_capturada.config(text=f"Senha Capturada: {senha_capturada}")
            messagebox.showinfo("Sucesso", f"Senha capturada: {senha_capturada}")
            salvar_dados(usuario, senha, senha_capturada)

        ui(finish)

    run_bg(tarefa)


def atualizar_atalho():
    if not senha_capturada:
        messagebox.showwarning("Aviso", "Nenhuma senha capturada.")
        return

    shortcuts.modificar_atalhos(
        senha_capturada,
        ["VetorFarma.lnk", "VetorFiscal.lnk"]
    )


def abrir_vetorfarma():
    shortcuts.abrir_vetorfarma("VetorFarma.lnk")


def abrir_vetorfiscal():
    shortcuts.abrir_vetorfarma("VetorFiscal.lnk")


def copiar_para_clipboard():
    if not senha_capturada:
        messagebox.showwarning("Aviso", "Nenhuma senha capturada.")
        return

    pyperclip.copy(senha_capturada)

    notificacao = tk.Toplevel(janela)
    notificacao.overrideredirect(True)
    notificacao.configure(bg=PRIMARY)

    x = janela.winfo_rootx() + 80
    y = janela.winfo_rooty() + 380
    notificacao.geometry(f"170x35+{x}+{y}")

    tk.Label(
        notificacao,
        text="Senha copiada!",
        bg=PRIMARY,
        fg="white",
        font=FONT_TEXT
    ).pack(fill="both", expand=True)

    janela.after(1500, notificacao.destroy)


def toggle_senha_capturada():
    if lbl_senha_capturada.winfo_ismapped():
        lbl_senha_capturada.grid_remove()
        btn_toggle.config(text="Mostrar Senha")
    else:
        lbl_senha_capturada.grid()
        btn_toggle.config(text="Ocultar Senha")


def _reaplicar_cor_botoes_principais():
    for btn in [
        btn_capturar_token,
        btn_capturar_token_fiserv,
        btn_capturar,
        btn_toggle,
        btn_atualizar,
        btn_abrir_vetor,
        btn_abrir_vetorfiscal,
        btn_copiar
    ]:
        btn.config(bg=PRIMARY, activebackground=PRIMARY)


def aplicar_cor_app(nova_cor: str):
    """
    - Se estiver no claro: altera PRIMARY_LIGHT e aplica.
    - Se estiver no escuro: altera PRIMARY_DARK e aplica.
    - Sempre salva.
    """
    global PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK, LAST_LIGHT_COLOR

    PRIMARY = nova_cor
    if tema_escuro:
        PRIMARY_DARK = nova_cor
    else:
        PRIMARY_LIGHT = nova_cor
        LAST_LIGHT_COLOR = nova_cor

    _reaplicar_cor_botoes_principais()
    salvar_dados(entry_usuario.get().strip(), entry_senha.get().strip(), senha_capturada)


def escolher_cor():
    popup = tk.Toplevel(janela)
    popup.title("Escolher cor")
    popup.resizable(False, False)
    popup.configure(bg=CARD_COLOR)

    popup.transient(janela)
    popup.grab_set()

    tk.Label(
        popup,
        text="Selecione uma cor:",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=FONT_SUB
    ).pack(padx=12, pady=(12, 8))

    frame = tk.Frame(popup, bg=CARD_COLOR)
    frame.pack(padx=12, pady=(0, 12))

    for nome, cor in PALETAS.items():
        def on_click(c=cor):
            aplicar_cor_app(c)
            popup.destroy()

        b = tk.Button(
            frame,
            text=nome,
            command=on_click,
            bg=cor,
            fg="white",
            relief="flat",
            width=16,
            height=1,
            cursor="hand2"
        )
        b.pack(pady=4)

    popup.update_idletasks()
    w = popup.winfo_width()
    h = popup.winfo_height()
    x_j = janela.winfo_rootx()
    y_j = janela.winfo_rooty()
    w_j = janela.winfo_width()
    h_j = janela.winfo_height()

    x = x_j + (w_j // 2) - (w // 2)
    y = y_j + (h_j // 2) - (h // 2)

    popup.geometry(f"+{x - 230}+{y}")


def centralizar_modal(modal, parent):
    modal.update_idletasks()

    w = modal.winfo_width()
    h = modal.winfo_height()

    x_parent = parent.winfo_rootx()
    y_parent = parent.winfo_rooty()
    w_parent = parent.winfo_width()
    h_parent = parent.winfo_height()

    x = x_parent + (w_parent // 2) - (w // 2)
    y = y_parent + (h_parent // 2) - (h // 2)

    modal.geometry(f"+{x}+{y}")


def ajustar_altura_janela():
    janela.update_idletasks()

    # mede o conteúdo REAL (card) e não o container
    h_card = card.winfo_reqheight()

    # folga para borda/título + paddings
    margem_extra = 80

    # ✅ permite encolher (altura mínima realista)
    ALTURA_MINIMA = 420
    ALTURA_MAXIMA = 640

    nova_altura = h_card + margem_extra
    nova_altura = max(ALTURA_MINIMA, nova_altura)
    nova_altura = min(ALTURA_MAXIMA, nova_altura)

    largura = janela.winfo_width() or 340
    x = janela.winfo_x()
    y = janela.winfo_y()

    janela.geometry(f"{largura}x{nova_altura}+{x}+{y}")


def alternar_tema_interface():
    global tema_escuro, PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK, LAST_LIGHT_COLOR

    if not tema_escuro:
        LAST_LIGHT_COLOR = PRIMARY_LIGHT

    novo_tema = themes.alternar_tema(
        janela, container, card,
        labels, entries, botoes,
        tema_escuro
    )

    if novo_tema:
        sound.tocar_som_tema_escuro_async()
        PRIMARY_DARK = DARK_DEFAULT
        PRIMARY = PRIMARY_DARK
    else:
        sound.tocar_som_tema_claro_async()

        if (PRIMARY_DARK or "").strip().lower() != DARK_DEFAULT.lower():
            PRIMARY_LIGHT = PRIMARY_DARK
        else:
            PRIMARY_LIGHT = LAST_LIGHT_COLOR

        PRIMARY = PRIMARY_LIGHT

    tema_escuro = novo_tema
    atualizar_botao_tema(tema_escuro)
    _reaplicar_cor_botoes_principais()

    salvar_dados(entry_usuario.get().strip(), entry_senha.get().strip(), senha_capturada)


def capturar_token_getcard():
    usuario = entry_usuario.get().strip()
    senha = entry_senha.get().strip()

    if not usuario or not senha:
        messagebox.showwarning("Aviso", "Preencha e-mail e senha do app.")
        return

    def tarefa():
        ui(lambda: set_loading(btn_capturar_token, True, "Buscando...", "Buscar Token GetCard"))

        try:
            token, erro = email_services.buscar_token_getcard(usuario, senha)
        except Exception as e:
            token, erro = None, f"Erro inesperado: {e}"

        def finish():
            set_loading(btn_capturar_token, False, text_normal="Buscar Token GetCard")

            if erro:
                messagebox.showwarning("Token não encontrado", erro)
                return

            pyperclip.copy(token)
            messagebox.showinfo(
                "Token Capturado",
                f"{'✅ Token capturado e copiado para a área de transferência:':^50}\n\n"
                f"{'* ' + token + ' *':^50}\n\n"
            )

        ui(finish)

    run_bg(tarefa)


def capturar_token_fiserv():
    usuario = entry_usuario.get().strip()
    senha = entry_senha.get().strip()

    if not usuario or not senha:
        messagebox.showwarning("Aviso", "Preencha e-mail e senha do app.")
        return

    def tarefa():
        ui(lambda: set_loading(btn_capturar_token_fiserv, True, "Buscando...", "Buscar Token Fiserv"))

        try:
            token, erro = email_services.buscar_token_fiserv(usuario, senha)
        except Exception as e:
            token, erro = None, f"Erro inesperado: {e}"

        def finish():
            set_loading(btn_capturar_token_fiserv, False, text_normal="Buscar Token Fiserv")

            if erro:
                messagebox.showwarning("Token não encontrado", erro)
                return

            pyperclip.copy(token)
            messagebox.showinfo(
                "Token Capturado",
                f"{'✅ Token Fiserv capturado e copiado para a área de transferência:':^50}\n\n"
                f"{'* ' + token + ' *':^50}\n\n"
            )

        ui(finish)

    run_bg(tarefa)


def aplicar_visibilidade_botoes():
    mapa = {
        "getcard": btn_capturar_token,
        "fiserv": btn_capturar_token_fiserv,
        "senha_dia": btn_capturar,
        "toggle": btn_toggle,
        "atualizar": btn_atualizar,
        "abrir_farma": btn_abrir_vetor,
        "abrir_fiscal": btn_abrir_vetorfiscal,
        "copiar": btn_copiar,
    }

    for chave, btn in mapa.items():
        if btn_visiveis.get(chave, True):
            info = btn_grid_info.get(btn)
            if info:
                btn.grid(**info)
            else:
                btn.grid()
        else:
            btn.grid_remove()

    # ajusta altura depois que o grid recalcular
    janela.after(50, ajustar_altura_janela)


def abrir_configuracoes():
    popup = tk.Toplevel(janela)
    popup.title("Configurações")
    popup.resizable(False, False)
    popup.configure(bg=CARD_COLOR)

    popup.transient(janela)
    popup.grab_set()

    tk.Label(
        popup,
        text="Escolha quais botões aparecem:",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        font=FONT_SUB
    ).pack(padx=12, pady=(12, 8), anchor="w")

    opcoes = [
        ("Buscar Token GetCard", "getcard"),
        ("Buscar Token Fiserv", "fiserv"),
        ("Buscar Senha do Dia", "senha_dia"),
        ("Ocultar/Mostrar Senha", "toggle"),
        ("Atualizar Atalho", "atualizar"),
        ("Abrir VetorFarma", "abrir_farma"),
        ("Abrir VetorFiscal", "abrir_fiscal"),
        ("Copiar Senha", "copiar"),
    ]

    vars_ = {}

    def on_change(chave):
        btn_visiveis[chave] = bool(vars_[chave].get())
        aplicar_visibilidade_botoes()
        salvar_dados(entry_usuario.get().strip(), entry_senha.get().strip(), senha_capturada)

    for texto, chave in opcoes:
        v = tk.BooleanVar(value=btn_visiveis.get(chave, True))
        vars_[chave] = v

        cb = tk.Checkbutton(
            popup,
            text=texto,
            variable=v,
            command=lambda c=chave: on_change(c),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            activebackground=CARD_COLOR,
            activeforeground=TEXT_COLOR,
            selectcolor=CARD_COLOR
        )
        cb.pack(padx=12, pady=4, anchor="w")

    tk.Button(
        popup,
        text="Fechar",
        command=popup.destroy,
        bg=PRIMARY,
        fg="white",
        relief="flat",
        cursor="hand2",
        width=14
    ).pack(padx=12, pady=(12, 12))

    centralizar_modal(popup, janela)


# --- JANELA ---
janela = tk.Tk()
janela.title("Gestão de Senha")
janela.configure(bg=BG_COLOR)

largura, altura = 340, 680
x = (janela.winfo_screenwidth() // 2) - (largura // 2)
y = (janela.winfo_screenheight() // 2) - (altura // 2)
janela.geometry(f"{largura}x{altura}+{x}+{y}")
janela.resizable(False, False)

container = tk.Frame(janela, bg=BG_COLOR)
container.pack(fill="both", expand=True)

card = tk.Frame(
    container,
    bg=CARD_COLOR,
    padx=20,
    pady=10,
    bd=0,
    relief="flat"
)
card.pack(padx=15, pady=15, fill="both", expand=True)

card.grid_columnconfigure(0, weight=1)
card.grid_columnconfigure(1, weight=1)

lbl_titulo = tk.Label(card, text="Gestão de Senha", font=FONT_TITLE, bg=CARD_COLOR, fg=TEXT_COLOR)
lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 10))

btn_tema = tk.Button(
    card,
    text="🌙",
    command=alternar_tema_interface,
    relief="flat",
    font=("Segoe UI Symbol", 12),
    bg=CARD_COLOR,
    width=1,
    height=1,
    padx=10,
    pady=10,
    anchor="center",
    cursor="hand2",
    activebackground=CARD_COLOR,
    highlightthickness=0,
    bd=0
)
btn_tema.place(x=-20, y=-8)

btn_cores = tk.Button(
    card,
    text="🎨",
    command=escolher_cor,
    relief="flat",
    font=("Segoe UI Symbol", 12),
    bg=CARD_COLOR,
    width=1,
    height=1,
    padx=6,
    pady=1,
    anchor="center",
    cursor="hand2",
    activebackground=CARD_COLOR,
    highlightthickness=0,
    bd=0
)
btn_cores.place(x=10, y=-8)

btn_config = tk.Button(
    card,
    text="⚙",
    command=abrir_configuracoes,
    relief="flat",
    font=("Segoe UI Symbol", 12),
    bg=CARD_COLOR,
    width=1,
    height=1,
    padx=6,
    pady=1,
    cursor="hand2",
    activebackground=CARD_COLOR,
    highlightthickness=0,
    bd=0
)
btn_config.place(relx=1.0, x=-8, y=-8, anchor="ne")


# label de E-mail e senha
lbl_usuario = tk.Label(card, text="E-mail", bg=CARD_COLOR, fg=MUTED, font=FONT_TEXT)
lbl_usuario.grid(row=1, column=0, columnspan=2, pady=(2, 0))

entry_usuario = tk.Entry(card, font=FONT_TEXT, width=38)
entry_usuario.grid(row=2, column=0, columnspan=2, pady=PAD_Y, padx=10)

lbl_senha = tk.Label(card, text="Senha do App", bg=CARD_COLOR, fg=MUTED, font=FONT_TEXT)
lbl_senha.grid(row=3, column=0, columnspan=2, pady=(5, 0))

entry_senha = tk.Entry(card, show="*", font=FONT_TEXT, width=38)
entry_senha.grid(row=4, column=0, columnspan=2, pady=PAD_Y, padx=10)


def criar_botao(texto, comando, linha):
    b = tk.Button(
        card,
        text=texto,
        command=comando,
        bg=PRIMARY,
        fg="white",
        relief="flat",
        height=2,
        cursor="hand2",
        width=28
    )
    b.grid(row=linha, column=0, columnspan=2, pady=(0, PAD_BTN_Y), padx=PAD_BTN_X)
    return b


btn_capturar_token = criar_botao("Buscar Token GetCard", capturar_token_getcard, 5)
btn_capturar_token.grid_configure(pady=(15, PAD_BTN_Y))

btn_capturar_token_fiserv = criar_botao("Buscar Token Fiserv", capturar_token_fiserv, 6)
btn_capturar = criar_botao("Buscar Senha do Dia", capturar_senha, 7)
btn_toggle = criar_botao("Ocultar Senha", toggle_senha_capturada, 8)
btn_atualizar = criar_botao("Atualizar Atalho", atualizar_atalho, 9)
btn_abrir_vetor = criar_botao("Abrir VetorFarma", abrir_vetorfarma, 10)
btn_abrir_vetorfiscal = criar_botao("Abrir VetorFiscal", abrir_vetorfiscal, 11)
btn_copiar = criar_botao("Copiar Senha", copiar_para_clipboard, 12)

# guarda grid original (pra poder esconder/mostrar sem bagunçar layout)
for b in [
    btn_capturar_token, btn_capturar_token_fiserv, btn_capturar, btn_toggle,
    btn_atualizar, btn_abrir_vetor, btn_abrir_vetorfiscal, btn_copiar
]:
    btn_grid_info[b] = b.grid_info()

lbl_senha_capturada = tk.Label(
    card,
    text="Senha Capturada: Nenhuma",
    fg=SUCCESS,
    bg=CARD_COLOR,
    font=FONT_SUB
)
lbl_senha_capturada.grid(row=13, column=0, columnspan=2, pady=5)

lbl_version = tk.Label(
    card,
    text=f"Versão {CURRENT_VERSION} - Áyron.ZettiTech | Alair Filho",
    bg=CARD_COLOR,
    fg=MUTED,
    font=FONT_SMALL
)
lbl_version.grid(row=14, column=0, columnspan=2, pady=(2, 0))

labels = [lbl_titulo, lbl_usuario, lbl_senha, lbl_senha_capturada, lbl_version]
entries = [entry_usuario, entry_senha]
botoes = [
    btn_capturar_token, btn_capturar_token_fiserv, btn_capturar,
    btn_atualizar, btn_abrir_vetor, btn_abrir_vetorfiscal, btn_copiar,
    btn_toggle, btn_tema, btn_cores, btn_config
]

# --- CARREGAR DADOS (1x só) ---
usuario_salvo, senha_salva, ultima_senha, tema_salvo, primary_light_salvo, primary_dark_salvo, ui_prefs_salvo = carregar_dados()

if usuario_salvo:
    entry_usuario.insert(0, usuario_salvo)

if senha_salva:
    entry_senha.insert(0, senha_salva)

if ultima_senha:
    senha_capturada = ultima_senha
    lbl_senha_capturada.config(text=f"Senha Capturada: {ultima_senha}")

# restaura cores salvas (se existirem)
if primary_light_salvo:
    PRIMARY_LIGHT = primary_light_salvo

if primary_dark_salvo:
    PRIMARY_DARK = primary_dark_salvo

# restaura preferências de UI (visibilidade)
if isinstance(ui_prefs_salvo, dict):
    btn_visiveis.update(ui_prefs_salvo)

# aplica tema salvo
tema_escuro = bool(tema_salvo)
themes.aplicar_tema(janela, container, card, labels, entries, botoes, tema_escuro)

# escolhe PRIMARY correto conforme tema inicial
PRIMARY = PRIMARY_DARK if tema_escuro else PRIMARY_LIGHT

# reaplica cor nos botões principais
_reaplicar_cor_botoes_principais()
atualizar_botao_tema(tema_escuro)

# aplica visibilidade escolhida
aplicar_visibilidade_botoes()

# ajusta após o primeiro desenho completo
janela.after(200, ajustar_altura_janela)

janela.mainloop()
