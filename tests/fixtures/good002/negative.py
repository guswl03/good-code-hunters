import random


class FakeSecrets:
    def token_urlsafe(self, size):
        return "0" * size


def token_hex(size):
    return "0" * size


def generate_insecure_values():
    secrets = FakeSecrets()
    return random.randint(0, 999_999), token_hex(32), secrets.token_urlsafe(32)
