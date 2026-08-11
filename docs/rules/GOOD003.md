# GOOD003 — Password Hashing / KDF

## 목적

비밀번호 보호에 권장되는 Password Hash 또는 KDF 계열 API 사용을 명확한 Positive Security Evidence로 찾는다.

## 탐지하는 패턴

`ImportAliasContext`로 실제 import가 확인되는 다음 호출을 탐지한다.

- `hashlib.pbkdf2_hmac`
- `hashlib.scrypt`
- `bcrypt.hashpw`

```python
import hashlib as hl
import bcrypt

derived = hl.pbkdf2_hmac("sha256", password, salt, 200_000)
hashed = bcrypt.hashpw(password, salt)
```

Argon2는 직접 생성자 chain 또는 같은 module/function/class scope의 단순 이름 할당을 제한적으로 추적한다.

```python
from argon2 import PasswordHasher

hasher = PasswordHasher()
hashed = hasher.hash(password)
```

## 탐지하지 않는 패턴

일반-purpose hash와 이름만 같은 사용자 정의 함수 또는 object method는 탐지하지 않는다.

```python
import hashlib

digest = hashlib.sha256(password).digest()
```

## Precision-first 제한사항

Argon2 instance는 direct `PasswordHasher()` 할당만 추적한다. factory 반환값, attribute/subscript 할당, branch 안에서만 발생하는 할당, 함수 간 전달을 해석하는 범용 data-flow는 지원하지 않는다.

PBKDF2 iteration, scrypt cost, Argon2 memory cost, salt 길이 등 parameter strength는 MVP에서 평가하지 않는다. 따라서 이 Finding은 권장 계열 API 사용 근거이며 설정 강도나 파일 전체의 credential 보안을 보증하지 않는다.
