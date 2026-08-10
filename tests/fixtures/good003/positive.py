import hashlib as hl

import bcrypt
from argon2 import PasswordHasher as ArgonPasswordHasher
from bcrypt import hashpw as bcrypt_hashpw


def hash_password(password, salt):
    pbkdf = hl.pbkdf2_hmac("sha256", password, salt, 200_000)
    scrypt_hash = hl.scrypt(
        password,
        salt=salt,
        n=16_384,
        r=8,
        p=1,
    )
    bcrypt_hash = bcrypt.hashpw(password, salt)
    aliased_bcrypt_hash = bcrypt_hashpw(password, salt)
    hasher = ArgonPasswordHasher()
    argon_hash = hasher.hash(password)
    return pbkdf, scrypt_hash, bcrypt_hash, aliased_bcrypt_hash, argon_hash
