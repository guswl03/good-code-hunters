import secrets
import secrets as sec
from secrets import token_hex as make_token
from secrets import token_urlsafe


def generate_secure_values(items):
    return (
        secrets.token_bytes(32),
        sec.token_hex(32),
        token_urlsafe(32),
        make_token(32),
        secrets.randbelow(10),
        secrets.choice(items),
        secrets.SystemRandom(),
    )
