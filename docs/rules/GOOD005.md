# GOOD005 — Safer Subprocess Invocation

지원하는 `subprocess` API에서 명령과 인자를 list/tuple로 분리하고 shell을 사용하지 않는 호출을 찾는다.

탐지:

```python
import subprocess
subprocess.run(["git", "status"], check=True)
```

첫 인자가 문자열이거나 `shell=True`, `shell=변수`, `**kwargs`처럼 shell 미사용을 확정할 수 없는 경우는 탐지하지 않는다.

category: `process-security`
confidence: `HIGH`
