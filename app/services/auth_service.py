import bcrypt

# bcrypt only accepts passwords up to 72 bytes (not chars: a <72-char
# non-ASCII password can still exceed 72 bytes once UTF-8 encoded).
MAX_PASSWORD_BYTES = 72


def _to_bytes(password: str) -> bytes:
    pwd_bytes = password.encode("utf-8")
    if len(pwd_bytes) > MAX_PASSWORD_BYTES:
        raise ValueError(
            f"Password must be at most {MAX_PASSWORD_BYTES} bytes long."
        )
    return pwd_bytes


def hash_password(password: str)->str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_to_bytes(password), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        # Overlong password (>72 bytes) can never match.
        return False
    