from cryptography.fernet import Fernet
import os

CHAVE = os.environ.get('TRONIX_CHAVE')

if not CHAVE:
    from dotenv import load_dotenv
    load_dotenv()
    CHAVE = os.environ.get('TRONIX_CHAVE')

if not CHAVE:
    raise ValueError("TRONIX_CHAVE não definida")

def criptografar(texto):
    f = Fernet(CHAVE.encode() if isinstance(CHAVE, str) else CHAVE)
    return f.encrypt(texto.encode()).decode()

def descriptografar(token):
    f = Fernet(CHAVE.encode() if isinstance(CHAVE, str) else CHAVE)
    return f.decrypt(token.encode()).decode()

if __name__ == "__main__":
    msg = "Mensagem secreta do Tronix"
    token = criptografar(msg)
    print(f"Original: {msg}")
    print(f"Criptografado: {token}")
    print(f"Descriptografado: {descriptografar(token)}")