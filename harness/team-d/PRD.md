# 팀원 D 하네스 PRD

> 프로젝트: 착한코드검거단 MVP v0.1  
> 역할: Rule Pack B + JSON Export + Integration + Build  
> 기준 문서: 저장소 루트의 `PRD.md`, `AGENTS.md`, `plan.md`

## 1. 목적

팀원 D는 다음 결과를 완성한다.

```text
GOOD004~GOOD006 정적 분석 규칙
+ JSON Exporter
+ 통합 회귀 테스트
+ No-Execution / Golden JSON 검증
+ Windows PyInstaller 빌드
```

이 문서는 팀원 D의 범위를 좁혀 Codex가 담당 영역 밖의 기능을 임의로 구현하지 않게 하는 역할별 하네스다. 공통 문서와 충돌하면 루트 `PRD.md → AGENTS.md → plan.md` 순서로 따른다.

## 2. 전제 조건

다음 공통 Contract가 `main`에 존재해야 한다.

- `Finding`
- `ScanResult`
- `scan_file(file_path) -> ScanResult`
- `Rule.check(tree, source, imports) -> list[Finding]`
- `ImportAliasContext`
- `SourceHelper`

팀원 D는 이 Contract를 재정의하지 않고 그대로 사용한다.

## 3. 담당 범위

### GOOD004 — Constant-Time Secret Comparison

명확한 Positive Evidence만 탐지한다.

```python
import hmac

hmac.compare_digest(expected, actual)
```

지원 대상:

- `hmac.compare_digest(...)`
- `import hmac as hm` 이후 `hm.compare_digest(...)`
- `from hmac import compare_digest`와 alias

탐지하지 않는 예:

```python
expected == actual
```

권장 category: `cryptography`

### GOOD005 — Safer Subprocess Invocation

명령과 인자를 리스트 또는 튜플로 전달하고 shell 실행을 사용하지 않는 명확한 호출만 탐지한다.

```python
import subprocess

subprocess.run(["git", "status"], check=True)
```

지원 대상:

- `subprocess.run`
- `subprocess.Popen`
- `subprocess.check_call`
- `subprocess.check_output`
- 공통 Alias Resolver가 해석할 수 있는 alias

탐지 조건:

- 첫 번째 인자가 list 또는 tuple AST
- `shell=True`가 아님
- `shell` 인자가 없으면 기본값 `False`로 취급 가능

탐지하지 않는 예:

```python
subprocess.run("git status", shell=True)
```

권장 category: `process-security`

### GOOD006 — Safe YAML Deserialization

```python
import yaml

data = yaml.safe_load(text)
```

지원 대상:

- `yaml.safe_load(...)`
- 공통 Alias Resolver가 해석할 수 있는 module/symbol alias
- 구현 난이도가 낮고 안전성이 명확한 범위의 SafeLoader 사용

탐지하지 않는 예:

```python
yaml.load(text)
```

분석기에서 실제 `yaml` 패키지를 import하거나 실행하지 않는다.

권장 category: `deserialization`

## 4. Rule 완료 계약

각 Rule은 반드시 다음 세트를 제공한다.

```text
Rule 구현
+ Positive fixture
+ Negative fixture
+ Unit test
+ docs/rules.md 설명
```

Finding은 공통 모델의 필드를 모두 채운다.

```text
rule_id, name, category, confidence, file,
line, column, evidence, message
```

MVP Finding의 confidence는 명확한 탐지만 생성하므로 기본적으로 `HIGH`다.

## 5. JSON Export

Exporter는 `ScanResult`를 입력받아 UTF-8 JSON으로 저장한다.

필수 출력:

- `schema_version`
- `tool_version`
- `target`
- `status`
- `summary.findings`
- `summary.categories`
- 결정적으로 정렬된 `findings`
- `warnings`

Exporter는 AST 분석, Rule 실행, GUI widget 접근을 하지 않는다. `ScanResult`의 의미를 별도 모델로 재정의하지 않는다.

## 6. 통합 검증

팀원 D는 다음 검증을 주도한다.

- 모든 P0 Rule의 Positive / Negative Test
- No-Execution invariant
- Golden JSON
- Finding 정렬
- Import / Alias Resolver 회귀 테스트
- JSON serialization
- GUI Smoke Test
- PyInstaller onedir 빌드 및 배포본 Smoke Test

## 7. 비범위

다음은 구현하지 않는다.

- GOOD001~GOOD003 재작성
- GUI 디자인 또는 위젯 구현
- Core Contract 임의 변경
- 대상 Python 실행·import
- LLM 판정
- 보안 점수 또는 SAFE / UNSAFE 판정
- P0 완료 전 GOOD007~GOOD008
- 멀티파일 또는 폴더 분석
- 자동 수정 기능

## 8. 완료 조건

- [ ] GOOD004~GOOD006 각각 Rule/Positive/Negative/Test/문서 완료
- [ ] alias 형태를 공통 Resolver 범위에서 처리
- [ ] 모호한 패턴을 Positive로 오탐하지 않음
- [ ] JSON Export 결과가 공통 schema와 일치
- [ ] No-Execution 테스트 통과
- [ ] Golden JSON 테스트 통과
- [ ] `pytest -q` 통과
- [ ] `ruff check .` 통과
- [ ] GUI Smoke Test 통과
- [ ] PyInstaller onedir 빌드 성공
- [ ] 배포본에서 `.py` 분석과 JSON 저장 성공

