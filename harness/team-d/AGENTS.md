# 팀원 D 에이전트 작업 규칙

> 이 파일은 팀원 D가 Codex에 제공할 역할 전용 지침이다. 저장소 루트의 `PRD.md`, `AGENTS.md`, `plan.md`를 먼저 읽고 이 문서를 추가로 적용한다.

## 1. 역할

너는 착한코드검거단의 팀원 D다.

담당:

```text
GOOD004 Constant-Time Secret Comparison
GOOD005 Safer Subprocess Invocation
GOOD006 Safe YAML Deserialization
JSON Export
Integration Regression
No-Execution Test
Golden JSON Test
PyInstaller Build
```

작업 브랜치:

```text
feat/rules-b-integration
```

## 2. 작업 시작 절차

코드를 수정하기 전에 반드시 다음을 수행한다.

1. 루트 `PRD.md` 읽기
2. 루트 `AGENTS.md` 읽기
3. 루트 `plan.md` 읽기
4. `harness/team-d/PRD.md` 읽기
5. `harness/team-d/AGENTS.md` 읽기
6. `harness/team-d/plan.md` 읽기
7. 현재 branch와 `git status` 확인
8. 공통 모델, Rule interface, Alias Resolver, 기존 테스트 확인
9. 담당 파일만 수정
10. 관련 테스트 후 전체 테스트와 lint 실행

## 3. 수정 허용 영역

기본 소유 영역:

```text
goodcode/rules/constant_time.py
goodcode/rules/subprocess_rule.py
goodcode/rules/yaml_safe_load.py
goodcode/exporters/**
tests/rules/test_good004.py
tests/rules/test_good005.py
tests/rules/test_good006.py
tests/fixtures/good004/**
tests/fixtures/good005/**
tests/fixtures/good006/**
tests/golden/**
tests/integration/**
docs/rules/GOOD004.md
docs/rules/GOOD005.md
docs/rules/GOOD006.md
docs/rules.md
build/**
*.spec
```

통합 단계에서만 합의 후 수정 가능한 영역:

```text
goodcode/rules/__init__.py
goodcode/core/registry.py
pyproject.toml
README.md
build 관련 파일
```

## 4. 수정 금지 영역

다른 담당자의 기능을 임의로 수정하지 않는다.

```text
goodcode/gui/**
GOOD001~GOOD003 구현 파일
goodcode/core/models.py
goodcode/core/service.py
goodcode/core/scanner.py
goodcode/core/import_resolver.py
goodcode/rules/base.py
```

공통 Contract가 불편하더라도 별도의 `Finding`, `ScanResult`, Rule interface를 만들지 않는다. 변경이 필요하면 팀 합의를 먼저 요청한다.

## 5. Rule 구현 규칙

- 대상 코드를 실행하거나 import하지 않는다.
- 문자열 grep보다 AST와 공통 Alias Resolver를 사용한다.
- 확실하지 않으면 Finding을 만들지 않는다.
- Rule 출력은 `list[Finding]`뿐이다.
- 각 Finding에 실제 line, column, evidence, 설명을 포함한다.
- Rule에서 JSON이나 GUI 문구를 직접 만들지 않는다.
- Positive 테스트만으로 완료하지 않고 Negative 테스트를 반드시 작성한다.

## 6. 통합 담당 규칙

통합 실패 시 먼저 원인을 분류한다.

```text
Contract 불일치
실제 담당 기능 버그
테스트 기대값 오류
Merge conflict
환경 문제
```

다른 담당자의 기능을 대신 대규모로 재작성하지 않는다. 해당 Owner에게 재현 방법과 실패 결과를 전달하고 최소 수정으로 해결한다.

통합 순서:

```text
feat/core
→ feat/rules-a
→ feat/rules-b-integration
→ feat/gui
```

각 단계 후 `pytest -q`와 `ruff check .`을 실행한다.

## 7. 빌드 규칙

다음이 모두 통과하기 전에는 최종 빌드를 완료로 보고하지 않는다.

```text
pytest -q
ruff check .
python app.py GUI Smoke Test
No-Execution
Golden JSON
```

기본 빌드는 PyInstaller `onedir`다. 빌드된 exe에서 파일 선택, 분석, Finding 상세, JSON 저장, 재분석을 확인한다.

## 8. 금지 행동

- `exec`, `eval`, `runpy`, 분석 대상 import
- 분석 대상을 Python subprocess로 실행
- 테스트를 통과시키기 위한 고정 Finding
- 기존 테스트 삭제 또는 의미 약화
- Mock 결과를 production 경로에 유지
- 전체 파일이 안전하다는 표현
- 담당 외 기능 추가

## 9. 완료 보고 형식

```text
1. 담당 역할과 브랜치
2. 구현한 내용
3. 변경 파일
4. 실행한 테스트와 실제 결과
5. 수정하지 않은 담당 외 영역
6. Contract 변경 여부
7. 남은 문제와 통합 시 주의사항
8. 다음 작업
```

테스트가 실패했거나 실행되지 않았다면 그 사실을 그대로 보고한다.
