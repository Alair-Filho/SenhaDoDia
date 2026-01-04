import os
from cryptography.fernet import Fernet
from tkinter import messagebox

# Caminhos antigos e novos
pasta_antiga = "C:\\"
pasta_nova = "C:\\App Senha"
chave_antiga = os.path.join(pasta_antiga, "chave.key")
dados_antigo = os.path.join(pasta_antiga, "dados_usuario.txt")
chave_nova = os.path.join(pasta_nova, "chave.key")
dados_novo = os.path.join(pasta_nova, "dados_usuario.txt")

# Cria pasta nova se necessário
if not os.path.exists(pasta_nova):
    os.makedirs(pasta_nova)

# Migra arquivos antigos para a nova pasta
if os.path.exists(chave_antiga) and not os.path.exists(chave_nova):
    os.rename(chave_antiga, chave_nova)

if os.path.exists(dados_antigo) and not os.path.exists(dados_novo):
    os.rename(dados_antigo, dados_novo)

# Gera chave se não existir
if not os.path.exists(chave_nova):
    with open(chave_nova, "wb") as chave_file:
        chave_file.write(Fernet.generate_key())

with open(chave_nova, "rb") as chave_file:
    chave = chave_file.read()

fernet = Fernet(chave)

def salvar_dados(usuario, senha, ultima_senha_capturada=None):
    dados = f"{usuario}\n{senha}\n{ultima_senha_capturada if ultima_senha_capturada else ''}"
    dados_criptografados = fernet.encrypt(dados.encode())

    with open(dados_novo, "wb") as arquivo:
        arquivo.write(dados_criptografados)

def carregar_dados():
    if os.path.exists(dados_novo):
        with open(dados_novo, "rb") as arquivo:
            dados_criptografados = arquivo.read()
            try:
                dados = fernet.decrypt(dados_criptografados).decode()
                linhas = dados.split("\n")

                usuario = linhas[0].strip()
                senha = linhas[1].strip()
                ultima = linhas[2].strip() if len(linhas) > 2 else None

                return usuario, senha, ultima

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar os dados: {e}")

    return None, None, None
