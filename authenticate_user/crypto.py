from cryptography.fernet import Fernet
from decouple import config

# busca a chave criptográfica no .env
CHAVE = config('CHAVE_CRIPTOGRAFIA')
fernet = Fernet(CHAVE.encode())

def criptografar_dado(texto: str) -> str:
    """Recebe o texto puro (como a base32 do 2FA) e retorna cifrado em AES."""
    if not texto:
        return texto
    return fernet.encrypt(texto.encode()).decode()

def descriptografar_dado(texto_cifrado: str) -> str:
    """Recebe a sopa de letrinhas cifrada e devolve o texto original."""
    if not texto_cifrado:
        return texto_cifrado
    return fernet.decrypt(texto_cifrado.encode()).decode()