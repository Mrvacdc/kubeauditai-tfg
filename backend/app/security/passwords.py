from passlib.context import CryptContext


MIN_PASSWORD_LENGTH = 15
MAX_PASSWORD_LENGTH = 128


class PasswordPolicyError(ValueError):
    """
    Error controlado para incumplimientos de política de contraseñas.
    No incluye la contraseña recibida ni fragmentos de ella.
    """
    pass


def validate_password_policy(plain_password: str) -> None:
    """
    Valida la política declarada por KubeAuditAI.

    Reglas aplicadas:
    - mínimo 15 caracteres;
    - permite frases de contraseña;
    - admite longitudes de al menos 64 caracteres;
    - no exige reglas rígidas de composición.
    """
    if plain_password is None:
        raise PasswordPolicyError("Password is required.")

    if not isinstance(plain_password, str):
        raise PasswordPolicyError("Password must be a string.")

    if len(plain_password) < MIN_PASSWORD_LENGTH:
        raise PasswordPolicyError(
            f"Password must contain at least {MIN_PASSWORD_LENGTH} characters."
        )

    if len(plain_password) > MAX_PASSWORD_LENGTH:
        raise PasswordPolicyError(
            f"Password must contain at most {MAX_PASSWORD_LENGTH} characters."
        )

pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
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
