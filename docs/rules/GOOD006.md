# GOOD006 — Safe YAML Deserialization

`yaml.safe_load()` 사용을 확인하여 임의 객체 생성을 피하는 YAML 역직렬화 패턴을 보여준다.

탐지:

```python
import yaml
data = yaml.safe_load(document)
```

공통 Alias Resolver가 해석하는 module alias와 from-import alias를 지원한다. `yaml.load()`는 탐지하지 않으며 분석기가 실제 yaml 패키지를 import하지 않는다.

category: `deserialization`
confidence: `HIGH`
