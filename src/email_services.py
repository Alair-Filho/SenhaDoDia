import imaplib
import email
import re
from datetime import datetime
from tkinter import messagebox
import threading
import time
import pyperclip

# -----------------------------
# BUSCAR SENHA DO DIA - VETOR
# -----------------------------
def buscar_senha_gmail(usuario, senha):
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(usuario, senha)
        mail.select('inbox')
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao servidor: {e}")
        return None

    data_atual = datetime.now().strftime("%d-%b-%Y")  
    filtro_data = f'(ON "{data_atual}")'

    try:
        status, mensagens = mail.search(None, filtro_data)
        if status != "OK" or not mensagens[0]:
            messagebox.showinfo("Aviso", "Nenhum e-mail encontrado na data de hoje.")
            return None
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao aplicar o filtro por data: {e}")
        return None

    remetente = "noreply@vetorsolucoes.com.br"

    for num in mensagens[0].split():
        try:
            status, dados = mail.fetch(num, '(RFC822)')
            if status != "OK":
                continue

            msg = email.message_from_bytes(dados[0][1])
            if msg.get("From") != remetente:
                continue

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        corpo = part.get_payload(decode=True).decode('utf-8')
                        break
            else:
                corpo = msg.get_payload(decode=True).decode('utf-8')

            senha = re.search(r'\bsua senha.*?:\s*([a-zA-Z0-9]+)', corpo, re.IGNORECASE)
            if senha:
                return senha.group(1)

        except Exception:
            continue

    messagebox.showinfo("Aviso", "Nenhum e-mail encontrado na data de hoje.")
    return None

# -----------------------------
# TOKEN GETCARD
# -----------------------------
def buscar_token_getcard(usuario, senha):
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(usuario, senha)
        mail.select('inbox')
    except Exception as e:
        return None, f"Erro ao conectar ao servidor: {e}"

    data_atual = datetime.now().strftime("%d-%b-%Y")
    remetente = "liberacaotef@getcard.com.br"

    try:
        status, mensagens = mail.search(None, f'(UNSEEN ON "{data_atual}")')
        if status != "OK" or not mensagens[0]:
            return None, "Nenhum e-mail não lido encontrado hoje."
    except Exception as e:
        return None, f"Erro ao buscar e-mails: {e}"

    for num in reversed(mensagens[0].split()):
        try:
            status, dados = mail.fetch(num, '(RFC822)')
            if status != "OK":
                continue

            msg = email.message_from_bytes(dados[0][1])
            if remetente not in msg.get("From"):
                continue

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        corpo = part.get_payload(decode=True).decode('utf-8')
                        break
            else:
                corpo = msg.get_payload(decode=True).decode('utf-8')

            token = re.search(r'Seu token para autenticar seu login:\s*(\d+)', corpo)
            if token:
                mail.store(num, '+FLAGS', '\\Seen')
                return token.group(1), None

        except Exception:
            continue

    return None, "Nenhum e-mail válido com token foi encontrado."

def capturar_token(usuario, senha):
    def tarefa():
        for tentativa in range(4):
            if tentativa > 0:
                time.sleep(5)

            token, erro = buscar_token_getcard(usuario, senha)
            if token:
                pyperclip.copy(token)
                messagebox.showinfo(
                    "Token Capturado",
                    f"{'✅ Token capturado e copiado para a área de transferência:':^50}\n\n"
                    f"{'* ' + token + ' *':^50}\n\n"
                )
                return

        messagebox.showwarning("Token não encontrado",
                               "Nenhum e-mail com o token foi encontrado após 4 tentativas.")

    threading.Thread(target=tarefa).start()

# -----------------------------
# TOKEN FISERV
# -----------------------------
def buscar_token_fiserv(usuario, senha):
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(usuario, senha)
        mail.select('inbox')
    except Exception as e:
        return None, f"Erro ao conectar ao servidor: {e}"

    data_atual = datetime.now().strftime("%d-%b-%Y")
    remetente = "noreply@fiserv.com"

    try:
        status, mensagens = mail.search(None, f'(UNSEEN ON "{data_atual}")')
        if status != "OK" or not mensagens[0]:
            return None, "Nenhum e-mail não lido encontrado hoje."
    except Exception as e:
        return None, f"Erro ao buscar e-mails: {e}"

    for num in reversed(mensagens[0].split()):
        try:
            status, dados = mail.fetch(num, '(RFC822)')
            if status != "OK":
                continue

            msg = email.message_from_bytes(dados[0][1])
            if remetente not in msg.get("From"):
                continue

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        corpo = part.get_payload(decode=True).decode('utf-8')
                        break
            else:
                corpo = msg.get_payload(decode=True).decode('utf-8')

            token = re.search(r'Código:\s*(\d+)', corpo)
            if token:
                mail.store(num, '+FLAGS', '\\Seen')
                return token.group(1), None

        except Exception:
            continue

    return None, "Nenhum e-mail válido com token foi encontrado."

def capturar_token_fiserv(usuario, senha):
    def tarefa():
        for tentativa in range(4):
            if tentativa > 0:
                time.sleep(5)

            token, erro = buscar_token_fiserv(usuario, senha)

            if token:
                pyperclip.copy(token)
                messagebox.showinfo(
                    "Token Capturado",
                    f"{'✅ Token Fiserv capturado e copiado para a área de transferência:':^50}\n\n"
                    f"{'* ' + token + ' *':^50}\n\n"
                )
                return

        messagebox.showwarning(
            "Token não encontrado",
            "Nenhum e-mail com o token Fiserv foi encontrado após 4 tentativas."
        )

    threading.Thread(target=tarefa).start()
