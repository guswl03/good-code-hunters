# GOOD004 — Constant-Time Secret Comparison

`hmac.compare_digest()` 또는 `secrets.compare_digest()` 사용을 확인하여 비밀값 비교에서 timing 차이를 줄이려는 긍정적인 보안 패턴을 보여준다.

탐지:

```python
import hmac
hmac.compare_digest(expected, actual)
```

공통 Alias Resolver가 해석하는 module alias와 from-import alias도 지원한다. 일반 `==` 비교는 탐지하지 않는다.

category: `side-channel-defense`
confidence: `HIGH`
