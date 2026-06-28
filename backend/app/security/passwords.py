from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(plain_password: str) -> str:
    """
    Genera un hash seguro de la contraseña usando bcrypt.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verifica una contraseña en texto plano contra su hash.
    """
    return pwd_context.verify(plain_password, password_hash)
