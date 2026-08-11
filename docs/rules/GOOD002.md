# GOOD002 — Cryptographically Secure Randomness

## 목적

보안용 token과 난수 생성에 적합한 Python `secrets` API 사용을 찾는다.

## 탐지하는 패턴

다음 API가 `import secrets`, module alias, `from secrets import ...`, symbol alias 중 하나로 실제 import된 것이 `ImportAliasContext`에서 확인될 때 탐지한다.

- `secrets.token_bytes`
- `secrets.token_hex`
- `secrets.token_urlsafe`
- `secrets.randbelow`
- `secrets.choice`
- `secrets.SystemRandom`

```python
import secrets as sec
from secrets import token_urlsafe as make_token

hex_token = sec.token_hex(32)
url_token = make_token(32)
```

## 탐지하지 않는 패턴

`random` module API와 이름만 같은 사용자 정의 함수는 탐지하지 않는다.

```python
import random

token = random.randint(0, 999999)

def token_hex(size):
    return "0" * size
```

## Precision-first 제한사항

지원 목록에 없는 `secrets` API나 `SystemRandom` instance method의 이후 사용은 추적하지 않는다. 난수의 사용 목적, token 길이, entropy 강도도 평가하지 않는다.

이 규칙은 확인된 `secrets` API 호출만 보고하며 애플리케이션 전체의 난수 사용이 안전하다고 보증하지 않는다.
