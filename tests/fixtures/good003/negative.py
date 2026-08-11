import hashlib


class FakePasswordHasher:
    def hash(self, password):
        return password


def scrypt(password):
    return password


def hash_password_insecurely(password):
    fake_hasher = FakePasswordHasher()
    return (
        hashlib.sha256(password).digest(),
        scrypt(password),
        fake_hasher.hash(password),
    )
