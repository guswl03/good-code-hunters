"""GOOD001~GOOD006 발표용 정적 분석 입력 예제.

이 파일은 실행하지 않고 AST로만 읽는 데모 입력이다.
"""

import hashlib
import hmac
import secrets
import subprocess

import yaml


def demonstrate_good_patterns(cursor, user_id, password, yaml_text):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    token = secrets.token_urlsafe(32)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), b"demo-salt", 100_000
    )
    matches = hmac.compare_digest(token, "expected-token")
    status = subprocess.run(["git", "status"], shell=False, check=True)
    data = yaml.safe_load(yaml_text)
    return password_hash, matches, status, data
