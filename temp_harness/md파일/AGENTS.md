# AGENTS.md — 착한코드검거단 개발 규칙

> **프로젝트:** 착한코드검거단 (Good Code Hunter) MVP v0.1  
> **대상:** 이 저장소에서 작업하는 모든 Codex Agent  
> **목적:** 4명의 팀원이 서로 다른 브랜치에서 병렬 개발하더라도 동일한 제품 계약과 품질 기준을 유지하기 위한 공통 작업 규칙

---

# 0. 이 문서의 역할

이 저장소에는 세 개의 핵심 문서가 있다.

```text
PRD.md
→ 무엇을 만들 것인가

AGENTS.md
→ Codex가 어떤 규칙으로 작업할 것인가

plan.md
→ 누가 무엇을 어떤 순서와 범위로 구현할 것인가
```

모든 Agent는 코드를 수정하기 전에 반드시 위 세 파일을 읽는다.

문서 간 충돌이 있을 경우 우선순위는 다음과 같다.

```text
1. PRD.md
2. AGENTS.md
3. plan.md
4. 개별 프롬프트의 구현 세부사항
```

단, 팀원이 명시적으로 새로운 결정을 내려 문서를 수정한 경우 최신 문서를 따른다.

Agent는 문서에 없는 기능을 임의로 확장하지 않는다.

---

# 1. 프로젝트 한 줄 이해

착한코드검거단은 사용자가 GUI에서 Python `.py` 파일 하나를 선택하면, 해당 파일을 **절대 실행하지 않고** AST 기반으로 정적 분석하여 보안적으로 권장할 만한 시큐어 코딩 패턴을 찾아 보여주는 Windows 데스크톱 프로그램이다.

이 도구는 다음을 하지 않는다.

- 악성코드 탐지
- 취약점 공격
- 대상 코드 실행
- SAFE / UNSAFE 판정
- 전체 보안 점수 계산
- LLM 기반 보안 판정
- Python 프로젝트 전체 분석

MVP 성공의 핵심은 기능 수가 아니라 다음이다.

```text
정확한 Positive Evidence
+ No Execution
+ 설명 가능한 Finding
+ 결정적인 결과
+ GUI에서 쉬운 사용
+ 4명 병렬 개발 후 안정적인 통합
```

---

# 2. 작업 시작 전 필수 절차

모든 Agent는 작업을 시작할 때 다음 순서를 따른다.

```text
1. PRD.md 읽기
2. AGENTS.md 읽기
3. plan.md 읽기
4. 자신의 담당 영역 확인
5. 현재 브랜치 확인
6. git status 확인
7. 관련 기존 코드와 테스트 확인
8. 구현
9. 관련 테스트 실행
10. 전체 테스트 실행
11. lint 실행
12. 변경 파일 확인
13. 담당 범위를 침범하지 않았는지 확인
14. commit / PR 준비
```

처음부터 코드를 작성하지 말고 먼저 현재 저장소 구조와 기존 구현을 확인한다.

---

# 3. 가장 중요한 원칙: 담당 영역만 수정한다

`plan.md`에서 자신에게 배정된 영역 밖의 코드는 원칙적으로 수정하지 않는다.

예를 들어 GUI 담당 Agent가 다음 영역을 배정받았다면:

```text
goodcode/gui/**
app.py
```

다음 파일을 임의로 수정하면 안 된다.

```text
goodcode/core/**
goodcode/rules/**
```

다른 영역의 변경이 필요해 보이면 직접 고치지 말고 다음 중 하나를 선택한다.

1. 이미 정의된 public contract를 사용한다.
2. Mock / fixture를 사용해 자신의 작업을 계속한다.
3. 자신의 PR 설명에 필요한 변경사항을 명시한다.
4. 정말 공통 계약 수정이 필요하면 팀 합의 후 문서와 계약을 먼저 수정한다.

병렬 개발 중 편의를 위해 다른 담당자의 코드를 임시로 고치는 행동은 금지한다.

---

# 4. 공통 Contract는 마음대로 변경하지 않는다

다음 요소는 4명의 작업을 연결하는 **공용 계약**이다.

```text
Finding
ScanResult
scan_file(...)
Rule interface
JSON schema
```

Agent는 자신의 구현이 불편하다는 이유로 이 계약을 임의로 변경하면 안 된다.

공통 계약을 변경해야 하는 경우:

```text
1. 왜 기존 계약으로 구현할 수 없는지 확인
2. 팀에 변경 필요성 공유
3. PRD.md / AGENTS.md / plan.md 중 필요한 문서 수정
4. 관련 테스트 수정
5. 영향받는 담당자 모두가 새 계약을 기준으로 작업
```

계약을 몰래 바꿔서 자신의 브랜치만 통과하게 만드는 것은 금지한다.

---

# 5. 고정 Core API

GUI, 테스트, Exporter가 Core 내부 구현을 알 필요가 없도록 MVP의 public entry point는 다음 개념을 유지한다.

```python
scan_file(file_path) -> ScanResult
```

권장 위치:

```text
goodcode/core/service.py
```

외부 모듈은 가능한 한 다음 방식으로만 분석을 요청한다.

```python
from goodcode.core.service import scan_file

result = scan_file(path)
```

GUI가 다음에 직접 의존하지 않도록 한다.

- `ast.NodeVisitor`
- Import Resolver 내부 구현
- 개별 Rule 클래스
- Scanner 내부 헬퍼

---

# 6. 고정 데이터 모델

MVP에서 `Finding`은 최소 다음 의미를 제공해야 한다.

```python
Finding(
    rule_id: str,
    name: str,
    category: str,
    confidence: str,
    file: str,
    line: int,
    column: int,
    evidence: str,
    message: str,
)
```

필드 의미:

```text
rule_id     GOOD001 같은 안정적인 규칙 ID
name        사람이 읽을 수 있는 규칙 이름
category    규칙 카테고리
confidence  MVP에서는 기본적으로 HIGH
file        분석 대상 파일 식별자
line        1-based line number
column      column position
evidence    실제 탐지 근거 코드
message     왜 좋은 보안 패턴인지 설명
```

실제 구현 필드명은 `file`을 사용한다.

`ScanResult`는 최소 다음 의미를 제공해야 한다.

```python
ScanResult(
    schema_version: str,
    tool_version: str,
    target: str,
    status: str,
    findings: list[Finding],
    warnings: list[str],
)
```

허용 status:

```text
GOOD_PATTERNS_FOUND
NO_GOOD_PATTERNS_FOUND
PARSE_ERROR
READ_ERROR
```

Summary 값은 가능한 한 `ScanResult`에서 계산한다.

```text
finding_count
category_count
```

같은 의미의 데이터를 GUI, Core, Exporter에서 각각 별도 형태로 재정의하지 않는다.

---

# 7. GUI Agent 규칙

GUI 담당자는 화면의 구체적인 디자인을 자유롭게 결정할 수 있다.

GUI 담당자가 소유하는 것은 `plan.md`의 최종 배정을 따르되 기본적으로 다음 영역을 예상한다.

```text
goodcode/gui/**
app.py
```

GUI 담당자는 다음을 자유롭게 결정할 수 있다.

- 위젯 배치
- 간격
- 크기
- 색상
- 폰트
- visual hierarchy
- 결과 테이블 배치
- 상세 패널 구조
- 버튼 위치
- 사용자 피드백 표현 방식

단, PRD에서 요구한 기능은 모두 제공해야 한다.

필수 UX:

```text
.py 파일 선택
→ 선택 파일 표시
→ 착한코드 검거 시작
→ 결과 요약
→ Finding 목록
→ Finding 상세 보기
→ Empty 상태
→ Error 상태
→ JSON 저장
→ 보안 보증이 아님을 알리는 Disclaimer
```

GUI 담당자는 Core 구현을 기다리지 않는다.

Core가 아직 완성되지 않았으면 `ScanResult` 계약과 동일한 Mock 객체를 만들어 UI를 먼저 완성한다.

예시:

```python
mock_result = ScanResult(
    schema_version="1.0",
    tool_version="0.1.0",
    target="sample.py",
    status="GOOD_PATTERNS_FOUND",
    findings=[...],
    warnings=[],
)
```

Mock은 개발 보조 수단이다.

최종 production 실행 경로에서는 반드시 실제 `scan_file()` 결과를 사용해야 한다.

GUI 담당자가 하면 안 되는 것:

- GUI 안에서 AST를 직접 분석하기
- GOOD001 같은 탐지 로직을 GUI에 구현하기
- Core가 불편하다는 이유로 Finding 필드를 바꾸기
- Rule 파일 수정하기
- 대상 Python 코드를 실행하기

---

# 8. Core Agent 규칙

Core는 GUI와 독립적으로 동작해야 한다.

Core의 책임:

```text
파일 검증
파일 읽기
ast.parse()
Import / Alias Resolver
Rule 실행 orchestration
Finding 취합
결정적 정렬
ScanResult 생성
오류 상태 변환
```

Core가 하면 안 되는 것:

- Tkinter import
- GUI widget 조작
- messagebox 호출
- stdout 출력에 의존한 결과 전달
- 분석 대상 파일 import
- 분석 대상 코드 실행
- 개별 Rule의 모든 탐지 로직을 scanner.py에 몰아넣기

Core는 사용자의 코드를 **데이터**로만 취급한다.

---

# 9. Rule Agent 규칙

Rule 구현은 가능한 한 작고 독립적이어야 한다.

P0 규칙:

```text
GOOD001 Parameterized SQL Query
GOOD002 Cryptographically Secure Randomness
GOOD003 Password Hashing / KDF
GOOD004 Constant-Time Secret Comparison
GOOD005 Safer Subprocess Invocation
GOOD006 Safe YAML Deserialization
```

P1은 P0가 안정된 뒤에만 작업한다.

```text
GOOD007 Secure TLS Context
GOOD008 Secure Temporary File API
```

각 Rule은 반드시 다음 세트를 가진다.

```text
Rule 구현
+ Positive fixture
+ Negative fixture
+ Unit test
+ docs/rules.md 설명
```

Rule 구현 시 원칙:

```text
명확한 Positive Evidence만 탐지
애매하면 탐지하지 않음
문자열 단순 grep보다 AST 우선
alias resolver가 제공되면 사용
Finding 외의 방식으로 결과 전달 금지
화면 출력 금지
대상 코드 실행 금지
```

Rule은 취약점을 찾는 것이 아니라 **좋은 보안 패턴을 찾는다.**

예를 들어 `random` 사용을 발견했다고 해서 `GOOD002`를 만들면 안 된다.

---

# 10. Test / Export / Build / Integration Agent 규칙

통합 담당자는 다른 사람의 기능을 대신 구현하는 사람이 아니다.

주요 책임:

```text
공통 테스트 구조
Golden JSON
No-Execution invariant test
JSON Exporter
전체 regression test
PyInstaller build
최종 smoke test
통합 시 contract 검증
```

통합 과정에서 테스트가 실패했다고 다른 담당자의 구현을 대규모로 재작성하지 않는다.

먼저 실패 원인을 구분한다.

```text
Contract 불일치
실제 버그
Test 기대값 오류
Merge conflict
환경 문제
```

필요하면 해당 담당자에게 수정 요청을 남긴다.

---

# 11. Rule Interface 원칙

구체적인 내부 클래스 구조는 Core/Rule 담당자가 최소한으로 구현할 수 있지만, 다음 방향은 유지한다.

```text
입력:
- AST
- source text
- 필요한 정적 context / alias 정보

출력:
- list[Finding]
```

Rule이 다음을 반환하거나 수행해서는 안 된다.

```text
GUI widget
print 결과
JSON string 자체
Boolean 하나만 반환
대상 코드 실행 결과
```

Rule은 `Finding` 생성에 필요한 근거를 함께 제공한다.

---

# 12. No Execution은 최상위 불변조건이다

분석 대상 `.py` 파일을 어떤 경우에도 실행하지 않는다.

절대 금지:

```python
importlib.import_module(target)
exec(source)
eval(source)
subprocess.run(["python", target])
runpy.run_path(target)
```

또한 분석 대상에서 발견한 외부 패키지를 실제 import하여 확인하지 않는다.

예:

```python
import bcrypt
```

가 대상 파일에 존재하더라도 분석기는 `bcrypt`를 import할 필요가 없다.

AST 안의 이름과 호출 구조만 확인한다.

모든 변경은 다음 불변조건을 깨지 않아야 한다.

```text
scan(target.py)
→ target.py 내부 side effect가 발생하지 않는다.
```

---

# 13. 결정적 결과를 유지한다

같은 버전 + 같은 입력은 같은 의미의 결과를 생성해야 한다.

Finding 기본 정렬:

```text
line ASC
→ column ASC
→ rule_id ASC
```

다음 요소를 분석 결과 결정에 사용하지 않는다.

- LLM
- 외부 API
- 랜덤값
- 현재 시간
- 네트워크 상태

JSON key ordering 자체보다 **semantic contract 안정성**을 우선한다.

---

# 14. 오류 처리 규칙

Core는 GUI 문구를 직접 출력하지 않는다.

Core는 가능한 한 안정적인 상태와 warning을 반환한다.

GUI가 사용자 친화적인 문구로 변환한다.

예:

```text
Core:
PARSE_ERROR

GUI:
Python 문법 오류로 분석할 수 없습니다.
Line 17: invalid syntax
```

예상 가능한 사용자 입력 오류 때문에 앱 전체를 crash시키지 않는다.

traceback을 GUI 사용자에게 그대로 노출하지 않는다.

---

# 15. Dependency 규칙

MVP는 4일 안에 완성해야 한다.

새 dependency는 비용이다.

기본 기술 스택:

```text
Python 3.11+
tkinter / ttk
ast
json
pytest
ruff
PyInstaller
```

새 외부 dependency를 추가하기 전에 반드시 다음을 확인한다.

```text
표준 라이브러리로 해결할 수 없는가?
정말 MVP 필수인가?
Windows build를 어렵게 만들지 않는가?
다른 팀원의 환경에도 설치가 필요한가?
```

단순 편의를 위한 새 프레임워크 추가는 피한다.

특히 GUI를 임의로 PyQt/PySide/Web UI로 변경하지 않는다.

---

# 16. 코드 품질 규칙

다음 원칙을 따른다.

- 읽기 쉬운 이름을 사용한다.
- 함수 하나에 너무 많은 책임을 넣지 않는다.
- 필요 없는 abstraction을 만들지 않는다.
- 4일 MVP에 필요 없는 확장 포인트를 과도하게 설계하지 않는다.
- dead code를 남기지 않는다.
- 주석은 코드가 무엇을 하는지 반복하기보다 **왜 필요한지** 설명한다.
- 테스트를 통과시키기 위한 하드코딩을 하지 않는다.
- broad `except Exception:`로 모든 오류를 숨기지 않는다.
- public contract에는 가능하면 type hint를 사용한다.

Harness Engineering의 목적은 코드량을 늘리는 것이 아니라 Agent가 좁은 범위에서 안정적으로 작업하고 스스로 검증할 수 있게 하는 것이다.

---

# 17. 테스트 규칙

기능 변경에는 관련 테스트가 따라야 한다.

최소 검증 명령:

```bash
pytest
ruff check .
```

가능한 경우 자신의 변경과 직접 관련된 테스트를 먼저 실행한다.

예:

```bash
pytest tests/test_good002.py -q
```

그 후 전체 테스트를 실행한다.

```bash
pytest -q
ruff check .
```

Rule은 Positive test만으로 완료되지 않는다.

최소:

```text
Positive
Negative
```

둘 다 필요하다.

핵심 regression:

```text
No-Execution Test
Golden JSON Test
Sorting Test
Import/Alias Resolver Test
```

테스트가 실패한 상태에서 완료되었다고 보고하지 않는다.

---

# 18. 테스트를 약화시키지 않는다

Agent는 자신의 구현을 통과시키기 위해 기존 테스트를 삭제하거나 의미를 약화시키면 안 된다.

금지 예:

```text
assert expected == actual
```

가 실패한다고 해서:

```text
assert actual is not None
```

수준으로 테스트를 약화시키는 것.

기존 테스트가 실제로 잘못되었다면 이유를 설명하고 기대 계약과 함께 수정한다.

---

# 19. Mock 사용 규칙

Mock은 병렬 개발을 가능하게 하기 위한 도구다.

허용:

```text
GUI 개발 중 Mock ScanResult
Exporter 단위 테스트용 ScanResult fixture
Core 없는 상태에서 화면 동작 검증
```

금지:

```text
production scan 버튼이 항상 Mock 결과 반환
실제 Rule 대신 하드코딩된 Finding 반환
Golden test를 통과하기 위한 고정 JSON 반환
```

통합 시 모든 Mock-only 실행 경로가 실제 Core와 교체되었는지 확인한다.

---

# 20. Git / Branch 작업 규칙

각 팀원은 자신의 feature branch에서 작업한다.

예시:

```text
feat/gui
feat/core
feat/rules
feat/integration
```

실제 branch 이름은 `plan.md`에서 확정한다.

작업 시작 시:

```bash
git branch --show-current
git status
```

작업 종료 전:

```bash
git diff --check
git status
git diff
```

commit은 가능하면 하나의 논리적 변경 단위로 만든다.

좋은 예:

```text
feat(gui): add finding detail view
feat(core): add deterministic finding sort
feat(rule): implement GOOD002 secrets detection
test(core): add no-execution invariant test
```

피해야 할 예:

```text
update
fix stuff
final
```

---

# 21. 다른 Agent의 변경을 되돌리지 않는다

Merge 또는 rebase 과정에서 자신이 작성하지 않은 변경을 발견했을 때 이유 없이 삭제하거나 되돌리지 않는다.

특히 shared file에서 conflict가 발생하면:

```text
1. 두 변경의 의도를 확인
2. PRD / Contract 기준으로 판단
3. 둘 중 하나를 무조건 덮어쓰지 않음
4. 필요하면 최소 통합 변경만 수행
5. 전체 테스트 실행
```

---

# 22. Shared File 수정 규칙

다음 파일은 여러 Agent가 동시에 수정하면 conflict가 발생하기 쉽다.

```text
PRD.md
AGENTS.md
plan.md
pyproject.toml
README.md
app.py
common models
```

따라서 `plan.md`에서 명시적으로 맡지 않은 shared file은 불필요하게 수정하지 않는다.

formatting만 바꾸는 대규모 수정도 피한다.

---

# 23. 문서 변경 규칙

코드 동작이 제품 계약에 영향을 준다면 관련 문서도 함께 수정한다.

예:

```text
새 Rule 추가
→ docs/rules.md

JSON schema 변경
→ PRD.md + tests/golden

새 필수 dependency 추가
→ README / dependency file
```

단순 구현 세부사항까지 PRD에 과도하게 적지 않는다.

---

# 24. MVP 범위를 지킨다

Agent가 좋은 아이디어를 발견하더라도 P0를 방해하면 구현하지 않는다.

MVP에서 하지 않는 것:

```text
멀티파일 분석
폴더 재귀 스캔
GitHub URL 분석
LLM 판정
AI 자동 수정
HTML/PDF 리포트
실시간 감시
데이터베이스
웹 서버
로그인
코드 실행 샌드박스
보안 점수
SAFE 인증
```

추가 아이디어는 TODO나 PR 설명에 남길 수 있지만 P0와 섞지 않는다.

---

# 25. GUI와 Core 사이의 의존 방향

의존 방향은 다음을 유지한다.

```text
GUI
 ↓
Application Service
 ↓
Core / Scanner
 ↓
Rule Engine
 ↓
Finding / ScanResult
```

Exporter는 `ScanResult`를 소비한다.

```text
ScanResult
   ├──→ GUI
   └──→ JSON Exporter
```

반대 방향 의존은 만들지 않는다.

잘못된 예:

```text
Rule → GUI
Core → Tkinter
Exporter → Treeview
```

---

# 26. UI는 자유롭게, 기능 계약은 엄격하게

이 프로젝트는 GUI를 픽셀 단위로 통제하지 않는다.

UI 담당자는 더 나은 디자인이 있다면 자유롭게 구현한다.

단, 다음은 바꾸면 안 된다.

```text
사용자가 .py 파일 하나를 선택한다.
사용자가 명시적으로 분석을 시작한다.
Finding 목록을 볼 수 있다.
Finding의 근거와 설명을 볼 수 있다.
Empty / Error 상태가 구분된다.
JSON을 저장할 수 있다.
보안 보증이 아니라는 안내가 있다.
```

즉:

```text
PRD / AGENTS
= UI가 무엇을 해야 하는지 정의

GUI Agent
= 그것을 어떻게 보이게 만들지 결정
```

---

# 27. Agent가 막혔을 때의 행동

구현 중 문제가 생기면 임의로 전체 구조를 바꾸지 않는다.

다음 순서로 해결한다.

```text
1. 관련 PRD 요구사항 다시 확인
2. AGENTS의 contract 확인
3. plan.md의 담당 범위 확인
4. 기존 테스트 확인
5. 현재 public interface로 해결 가능한지 확인
6. 최소 변경으로 해결
```

다른 영역의 변경 없이는 해결할 수 없다면 그 사실을 명확하게 남긴다.

불확실한 계약을 마음대로 추측해서 새 표준을 만들지 않는다.

---

# 28. 작업 완료 조건

Agent는 코드를 작성했다는 이유만으로 작업을 완료했다고 판단하지 않는다.

자신의 작업은 다음을 만족해야 한다.

```text
[ ] PRD 요구사항을 만족한다.
[ ] 담당 범위 밖 파일을 불필요하게 수정하지 않았다.
[ ] 공통 contract를 깨지 않았다.
[ ] 관련 테스트가 있다.
[ ] 관련 테스트가 통과한다.
[ ] 전체 pytest가 통과한다.
[ ] ruff check가 통과한다.
[ ] No-Execution 원칙을 위반하지 않는다.
[ ] debug code / temporary print가 없다.
[ ] production 경로에 Mock이 남지 않았다.
[ ] git diff를 확인했다.
[ ] PR에서 변경 내용과 검증 방법을 설명할 수 있다.
```

---

# 29. PR 작성 시 포함할 내용

각 PR에는 최소 다음을 작성한다.

```text
## What
무엇을 구현했는가

## Scope
어떤 파일/영역을 수정했는가

## Contract
공통 contract 변경 여부

## Test
실행한 테스트와 결과

## Manual Check
필요한 경우 직접 확인한 항목

## Remaining
남은 문제나 다른 담당자에게 필요한 작업
```

공통 contract 변경이 없다면 명시적으로 다음과 같이 적는다.

```text
Contract change: None
```

---

# 30. 최종 통합 시 확인사항

main 병합 후 최소 다음을 확인한다.

```text
1. 프로그램 실행
2. .py 파일 선택
3. 분석 시작
4. P0 Finding 탐지
5. 결과 목록 표시
6. 상세 정보 표시
7. Finding이 없는 파일 분석
8. SyntaxError 파일 분석
9. JSON 저장
10. 같은 파일 재분석 결과 일치
11. No-Execution test 통과
12. 전체 pytest 통과
13. ruff check 통과
14. PyInstaller build
15. 빌드된 exe smoke test
```

---

# 31. 이 프로젝트에서 좋은 Agent 작업의 기준

좋은 작업은 많은 코드를 만드는 것이 아니다.

좋은 작업은 다음과 같다.

```text
담당 범위가 작고 명확하다.
공통 contract를 지킨다.
다른 Agent의 작업을 기다리지 않고 Mock/fixture로 진행할 수 있다.
자동 테스트로 스스로 검증한다.
문서와 구현이 일치한다.
merge conflict를 최소화한다.
MVP 범위를 벗어나지 않는다.
```

4명의 Agent가 모두 이 규칙을 따르면 각자 독립적으로 작업해도 마지막에 하나의 제품으로 합쳐질 수 있어야 한다.

---

# 32. Agent용 작업 시작 템플릿

각 팀원은 Codex 세션을 시작할 때 다음과 같은 형태로 지시할 수 있다.

```text
이 저장소의 PRD.md, AGENTS.md, plan.md를 먼저 읽어라.

나는 plan.md에서 배정된 [담당 영역] 작업을 진행한다.
AGENTS.md의 ownership과 contract를 반드시 지켜라.
담당 영역 밖의 파일은 임의로 수정하지 마라.

먼저 현재 코드와 테스트 상태를 확인한 뒤,
plan.md에 정의된 내 작업만 구현하라.

구현 후 관련 테스트, 전체 pytest, ruff check를 실행하고
실패가 있으면 원인을 수정한 뒤 결과를 요약해라.
```

GUI 담당자는 다음 문장을 추가한다.

```text
Core 구현이 아직 없어도 기다리지 말고 AGENTS.md에 정의된 ScanResult contract와 Mock 데이터를 사용하여 UI를 완성하라.
GUI의 세부 디자인은 네가 자율적으로 결정하되 PRD의 필수 UX는 모두 만족하라.
```

---

# 33. 마지막 원칙

**문서가 경계를 만들고, Contract가 팀을 연결하며, 테스트가 Agent를 통제한다.**

모든 Agent는 자신의 코드를 많이 만드는 것보다 다음 질문을 우선한다.

```text
내 변경이 PRD를 만족하는가?
내 담당 범위 안에 있는가?
다른 Agent의 영역을 침범하지 않았는가?
공통 contract를 지키는가?
자동으로 검증 가능한가?
4일 MVP 완성에 실제로 필요한가?
```

위 질문들에 명확히 답할 수 없는 변경은 구현하지 않는다.
