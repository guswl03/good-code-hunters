# plan.md — 착한코드검거단 MVP 실행 계획

> **프로젝트:** 착한코드검거단 (Good Code Hunter) MVP v0.1  
> **팀 규모:** 4명  
> **공식 기간:** 1주  
> **내부 개발 목표:** Day 4 안에 기능 구현·통합·Windows 빌드 완료  
> **개발 방식:** Harness Engineering + Codex 기반 병렬 개발  
> **기준 문서:** `PRD.md` → `AGENTS.md` → `plan.md`

---

# 0. 이 문서의 역할

이 문서는 **누가 무엇을, 어떤 파일에서, 어떤 순서로, 언제까지 구현할지**를 정의한다.

세 문서의 역할은 다음과 같다.

```text
PRD.md
→ 무엇을 만들 것인가

AGENTS.md
→ Codex가 어떤 규칙을 지켜야 하는가

plan.md
→ 4명이 실제로 어떻게 나누어 구현하고 합칠 것인가
```

모든 팀원과 Codex Agent는 작업 전에 세 문서를 모두 읽는다.

이 문서에서 가장 중요한 목표는 단순 분업이 아니다.

```text
공통 Contract를 먼저 고정
        ↓
4명이 서로 다른 영역을 독립적으로 구현
        ↓
각자 자기 영역을 테스트
        ↓
작은 PR 단위로 main에 통합
        ↓
전체 회귀 테스트
        ↓
Windows GUI 프로그램으로 빌드
```

즉, 다른 팀원의 구현이 끝날 때까지 기다리지 않고 **각 Agent가 자기 영역 안에서 최대한 독립적으로 완주할 수 있는 구조**를 만든다.

---

# 1. MVP 최종 목표

Day 4 종료 시 다음 사용자 흐름이 실제로 동작해야 한다.

```text
GoodCodeHunter 실행
        ↓
GUI에서 Python .py 파일 선택
        ↓
[착한코드 검거 시작]
        ↓
파일을 실행하지 않고 AST 기반 정적 분석
        ↓
GOOD001 ~ GOOD006 규칙 적용
        ↓
발견된 착한코드 목록 표시
        ↓
항목 선택
        ↓
Rule / Line / Evidence / 설명 확인
        ↓
JSON 결과 저장
```

최종 MVP에서 반드시 구현되어야 하는 P0 Rule은 다음 6개다.

| Rule ID | 이름 | 담당 |
|---|---|---|
| GOOD001 | Parameterized SQL Query | 팀원 C |
| GOOD002 | Cryptographically Secure Randomness | 팀원 C |
| GOOD003 | Password Hashing / KDF | 팀원 C |
| GOOD004 | Constant-Time Secret Comparison | 팀원 D |
| GOOD005 | Safer Subprocess Invocation | 팀원 D |
| GOOD006 | Safe YAML Deserialization | 팀원 D |

P1인 `GOOD007`, `GOOD008`은 **Day 4 P0 완료 후 시간이 남는 경우에만** 구현한다.

---

# 2. 4명 최종 역할 배정

이번 MVP는 다음 네 역할로 나눈다.

```text
팀원 A — GUI / UX
팀원 B — Core / Shared Contract / AST Infrastructure
팀원 C — Rule Pack A (GOOD001 ~ GOOD003)
팀원 D — Rule Pack B (GOOD004 ~ GOOD006) + Export / Integration / Build
```

역할 관계는 다음과 같다.

```text
                         [Shared Contract]
                  Finding / ScanResult / Rule API
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        [A. GUI]          [B. Core]        [C/D. Rules]
             │                │                │
             │                └──── Rule Engine┘
             │                       │
             └──── scan_file() ◀────┘
                     │
                     ▼
                 ScanResult
                     │
              ┌──────┴──────┐
              ▼             ▼
             GUI        JSON Export
                             │
                             ▼
                     [D. Integration]
                             │
                             ▼
                       PyInstaller Build
```

---

# 3. Branch 전략

각 팀원은 다음 브랜치를 사용한다.

```text
팀원 A: feat/gui
팀원 B: feat/core
팀원 C: feat/rules-a
팀원 D: feat/rules-b-integration
```

공통 기반 계약을 고정하기 위한 최초 1회 브랜치:

```text
chore/foundation-contract
```

이 브랜치는 **팀원 B가 작성하되, 네 명이 함께 내용 확인 후 main에 먼저 merge**한다.

그 후 네 명 모두 동일한 main을 기준으로 자신의 feature branch를 만든다.

```bash
git switch main
git pull
git switch -c feat/gui
```

각자 자신의 브랜치 이름에 맞게 생성한다.

---

# 4. Day 1 첫 작업 — Foundation Contract Freeze

병렬 개발을 시작하기 전에 약 1~2시간만 공통 기반을 고정한다.

이 작업이 끝나기 전에는 각자 기능 구현을 크게 시작하지 않는다.

## 4.1 담당

```text
작성: 팀원 B
검토: 팀원 A, C, D 전원
브랜치: chore/foundation-contract
```

## 4.2 반드시 먼저 고정할 것

### Finding

최소 의미:

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

### ScanResult

최소 의미:

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

### Public Core API

```python
scan_file(file_path) -> ScanResult
```

권장 위치:

```text
goodcode/core/service.py
```

### Rule Contract

개별 Rule은 개념적으로 다음 입력을 받아야 한다.

```text
AST
source text
정적 import / alias context
```

그리고 다음만 반환한다.

```text
list[Finding]
```

## 4.3 Foundation에서 만들 파일

최소:

```text
good-code-hunter/
├── PRD.md
├── AGENTS.md
├── plan.md
├── pyproject.toml
│
├── goodcode/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── service.py
│   │
│   └── rules/
│       ├── __init__.py
│       └── base.py
│
├── tests/
│   └── __init__.py
│
└── docs/
```

`service.py`는 이 시점에 완전한 Scanner가 없어도 된다.

단, public signature가 고정되어 있어야 한다.

## 4.4 Contract Freeze Gate

네 명이 아래를 확인하면 Foundation을 main에 merge한다.

```text
[ ] Finding 필드 합의
[ ] ScanResult 필드 합의
[ ] status 값 합의
[ ] scan_file() signature 합의
[ ] Rule input/output 방향 합의
[ ] Python 버전 합의
[ ] pytest / ruff 실행 방식 합의
[ ] GUI는 Core internals를 직접 호출하지 않는다는 점 합의
[ ] 분석 대상 코드를 절대 실행하지 않는다는 점 합의
```

**이 Gate 이후 공통 Contract를 각 Agent가 임의로 변경하면 안 된다.**

---

# 5. 파일 소유권

병렬 개발 충돌을 줄이기 위해 담당 파일을 명확하게 나눈다.

## 5.1 팀원 A — GUI

주 소유 영역:

```text
app.py
goodcode/gui/**
tests/gui/**        # 필요한 범위만
```

수정 금지 원칙:

```text
goodcode/core/**
goodcode/rules/**
goodcode/exporters/**
```

GUI에서 Core 변경이 필요해 보여도 먼저 기존 Contract로 해결한다.

---

## 5.2 팀원 B — Core

주 소유 영역:

```text
goodcode/core/**
tests/core/**
```

Foundation 이후 공통 Contract 파일을 관리하는 1차 책임자다.

주요 파일 예시:

```text
goodcode/core/models.py
goodcode/core/scanner.py
goodcode/core/import_resolver.py
goodcode/core/service.py
```

수정 금지 원칙:

```text
goodcode/gui/**
개별 GOOD00X Rule 구현 파일
```

---

## 5.3 팀원 C — Rule Pack A

주 소유 영역:

```text
goodcode/rules/sql.py
goodcode/rules/secure_random.py
goodcode/rules/password_hashing.py

tests/rules/test_good001.py
tests/rules/test_good002.py
tests/rules/test_good003.py

tests/fixtures/good001/**
tests/fixtures/good002/**
tests/fixtures/good003/**

docs/rules/GOOD001.md
docs/rules/GOOD002.md
docs/rules/GOOD003.md
```

담당 규칙:

```text
GOOD001
GOOD002
GOOD003
```

---

## 5.4 팀원 D — Rule Pack B + Integration

주 소유 영역:

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

tests/integration/**

docs/rules/GOOD004.md
docs/rules/GOOD005.md
docs/rules/GOOD006.md
docs/rules.md

build/**
*.spec
```

담당 규칙:

```text
GOOD004
GOOD005
GOOD006
```

그리고 Day 3~4부터 다음을 주도한다.

```text
Rule Registry 최종 연결
JSON Export
Golden JSON
No-Execution Regression
End-to-End Test
PyInstaller
Smoke Test
최종 Integration
```

---

# 6. Shared File 충돌 방지 규칙

다음 파일은 여러 명이 동시에 수정하면 conflict가 발생하기 쉽다.

```text
pyproject.toml
goodcode/rules/__init__.py
docs/rules.md
README.md
PRD.md
AGENTS.md
plan.md
```

따라서 소유권을 다음처럼 정한다.

```text
pyproject.toml              → 팀원 B, Day 4 필요 시 D와 합의
goodcode/rules/__init__.py  → 팀원 D가 Integration 시 최종 등록
docs/rules.md               → 팀원 D가 개별 Rule 문서를 취합
README.md                    → 팀원 D가 최종 사용법 작성, 각 팀원 내용 제공
PRD/AGENTS/plan             → 팀 합의 없는 개인 수정 금지
```

Rule 문서 충돌을 피하기 위해 C와 D는 먼저 다음처럼 **개별 Rule 문서**를 작성한다.

```text
docs/rules/GOOD001.md
...
docs/rules/GOOD006.md
```

D가 마지막에 `docs/rules.md`를 인덱스/요약 문서로 정리한다.

---

# 7. 팀원 A — GUI / UX 상세 계획

## 7.1 목표

Core와 Rule 구현을 기다리지 않고 **Mock/Fake ScanResult를 이용해 GUI를 독립적으로 완성**한다.

GUI의 세부 디자인은 A가 결정한다.

A는 다음을 자유롭게 선택할 수 있다.

```text
색상
폰트
간격
위젯 배치
결과 테이블 폭
상세 패널 구조
상태 메시지 위치
버튼 배치
```

단, PRD에 정의된 기능은 모두 보여야 한다.

## 7.2 필수 구현

```text
[ ] 메인 Window
[ ] Header / 프로그램 설명
[ ] .py File Picker
[ ] 선택 파일 경로 표시
[ ] 착한코드 검거 시작 버튼
[ ] 분석 상태 표시
[ ] Finding 개수 Summary
[ ] Category 개수 Summary
[ ] Findings Table
[ ] Table row 선택
[ ] Finding Detail Panel
[ ] Evidence 코드 표시
[ ] Empty State
[ ] Parse/Read Error State
[ ] Disclaimer
[ ] JSON 저장 버튼
[ ] 실제 scan_file() 연결 지점
```

## 7.3 Core를 기다리지 않는 방법

GUI는 개발/테스트 시 Fake 결과를 사용한다.

예:

```python
fake_result = ScanResult(
    schema_version="1.0",
    tool_version="0.1.0",
    target="sample.py",
    status="GOOD_PATTERNS_FOUND",
    findings=[...],
    warnings=[],
)
```

권장 방식은 GUI 코드 안에 영구 Mock 분기를 넣는 것이 아니라 **scan callable을 주입 가능하게 만드는 것**이다.

개념 예:

```python
MainWindow(scan_service=fake_scan_file)  # GUI 개발/테스트
MainWindow(scan_service=scan_file)       # 실제 app.py
```

정확한 구현은 A가 결정할 수 있다.

중요한 조건은 최종 `app.py`가 실제 `scan_file()`을 사용해야 한다는 것이다.

## 7.4 A의 Definition of Done

```text
[ ] Core가 없어도 Fake Result로 화면 데모 가능
[ ] 파일 선택 가능
[ ] GOOD_PATTERNS_FOUND 결과 표시 가능
[ ] NO_GOOD_PATTERNS_FOUND 표시 가능
[ ] PARSE_ERROR 표시 가능
[ ] READ_ERROR 표시 가능
[ ] Finding 하나를 클릭하면 상세 정보 표시
[ ] JSON 저장 기능을 호출할 UI 제공
[ ] Traceback을 사용자 화면에 그대로 노출하지 않음
[ ] GUI 안에 AST/Rule 로직 없음
[ ] production 경로에 하드코딩 Mock 없음
```

## 7.5 A의 권장 Commit 단위

```text
feat(gui): add main window and file picker
feat(gui): add findings table and detail panel
feat(gui): handle empty and error scan states
feat(gui): connect scan result and export actions
```

---

# 8. 팀원 B — Core / AST Infrastructure 상세 계획

## 8.1 목표

다른 세 담당자가 내부 구현을 몰라도 사용할 수 있는 안정적인 분석 기반을 만든다.

B의 핵심 결과물은 다음이다.

```text
scan_file(path) -> ScanResult
```

## 8.2 필수 구현

```text
[ ] Finding / ScanResult 모델
[ ] 입력 경로 검증
[ ] .py 파일 읽기
[ ] Encoding/Read error 처리
[ ] ast.parse()
[ ] SyntaxError → PARSE_ERROR 변환
[ ] source line 추출 기반
[ ] Import / Alias Resolver
[ ] Rule 실행 orchestration
[ ] Finding 취합
[ ] deterministic sorting
[ ] status 결정
[ ] scan_file() public API
```

## 8.3 Import / Alias Resolver 최소 범위

다음 정도의 정적 alias를 처리할 수 있게 한다.

```python
import secrets
secrets.token_hex(16)
```

```python
import secrets as s
s.token_hex(16)
```

```python
from secrets import token_hex
token_hex(16)
```

Rule마다 alias parsing을 중복 구현하지 않는 것이 목표다.

단, 4일 MVP이므로 Python의 모든 import semantics를 구현하지 않는다.

## 8.4 No Execution

B는 다음을 절대 사용하지 않는다.

```text
importlib로 target import
exec(target_source)
eval(target_source)
runpy
python target.py 실행
```

분석 대상 코드는 문자열/AST 데이터일 뿐이다.

## 8.5 Deterministic Sort

최종 Finding 기본 순서:

```text
line ASC
→ column ASC
→ rule_id ASC
```

## 8.6 B의 Definition of Done

```text
[ ] 정상 .py 파일을 ScanResult로 반환
[ ] 문법 오류 파일이 crash하지 않고 PARSE_ERROR
[ ] 읽기 오류가 READ_ERROR
[ ] 동일 입력 → 동일 의미의 결과
[ ] alias context를 Rule에 제공 가능
[ ] Rule 결과를 하나의 ScanResult로 합칠 수 있음
[ ] target code 실행 없이 분석
[ ] core tests 통과
[ ] GUI import 없음
```

## 8.7 B의 권장 Commit 단위

```text
feat(core): define scan result contract
feat(core): add safe python source parser
feat(core): add import alias resolver
feat(core): orchestrate rules and deterministic results
```

---

# 9. 팀원 C — Rule Pack A 상세 계획

## 9.1 담당

```text
GOOD001 — Parameterized SQL Query
GOOD002 — Cryptographically Secure Randomness
GOOD003 — Password Hashing / KDF
```

각 Rule은 독립적으로 구현하고 독립적으로 테스트할 수 있어야 한다.

---

## 9.2 GOOD001

탐지 목표:

```python
cursor.execute(
    "SELECT * FROM users WHERE id = ?",
    (user_id,),
)
```

최소 Positive 조건:

```text
execute / executemany 호출
SQL argument와 parameter argument가 분리됨
SQL 문자열에 placeholder가 존재
```

다음은 Positive로 인정하지 않는다.

```python
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

```python
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
```

---

## 9.3 GOOD002

주요 대상:

```text
secrets.token_bytes
secrets.token_hex
secrets.token_urlsafe
secrets.randbelow
secrets.choice
secrets.SystemRandom
```

Positive:

```python
import secrets

token = secrets.token_urlsafe(32)
```

Negative 예:

```python
import random

token = random.randint(0, 999999)
```

`random` 사용을 발견했다고 해서 Good Finding으로 만들지 않는다.

---

## 9.4 GOOD003

주요 대상:

```text
hashlib.pbkdf2_hmac
hashlib.scrypt
bcrypt.hashpw
Argon2 PasswordHasher.hash
```

MVP는 iteration 수 등 모든 보안 파라미터를 완전히 평가하지 않는다.

**확실하게 식별 가능한 Password Hash/KDF API 사용**을 Positive Evidence로 본다.

---

## 9.5 Rule별 필수 세트

C는 각 Rule마다 반드시 다음을 만든다.

```text
Rule implementation
Positive fixture
Negative fixture
Unit test
Rule document
```

예:

```text
goodcode/rules/secure_random.py

tests/fixtures/good002/positive.py
tests/fixtures/good002/negative.py

tests/rules/test_good002.py

docs/rules/GOOD002.md
```

## 9.6 C의 Definition of Done

```text
[ ] GOOD001 Positive 통과
[ ] GOOD001 Negative 오탐 없음
[ ] GOOD002 Positive 통과
[ ] GOOD002 Negative 오탐 없음
[ ] GOOD003 Positive 통과
[ ] GOOD003 Negative 오탐 없음
[ ] 각 Finding에 line / column / evidence / message 존재
[ ] 대상 코드 실행 없음
[ ] alias resolver contract 사용
[ ] 다른 Rule 담당 파일 수정 없음
[ ] pytest 관련 테스트 통과
```

## 9.7 C의 권장 Commit 단위

```text
feat(rule): implement GOOD001 parameterized sql detection
feat(rule): implement GOOD002 secure randomness detection
feat(rule): implement GOOD003 password hashing detection
```

---

# 10. 팀원 D — Rule Pack B / Export / Integration / Build 상세 계획

D는 기능을 대신 구현하는 사람이 아니라, **자신에게 배정된 기능 + 마지막 통합 흐름**을 담당한다.

## 10.1 Rule 담당

```text
GOOD004 — Constant-Time Secret Comparison
GOOD005 — Safer Subprocess Invocation
GOOD006 — Safe YAML Deserialization
```

---

## 10.2 GOOD004

주요 대상:

```text
hmac.compare_digest
secrets.compare_digest
```

Positive 예:

```python
import hmac

if hmac.compare_digest(received, expected):
    pass
```

일반 `==` 비교를 발견했다고 해서 취약점 Finding을 만들지는 않는다.

이 프로젝트는 Negative Security Scanner가 아니다.

---

## 10.3 GOOD005

최소 Positive 조건:

```text
subprocess.run 또는 subprocess.Popen
첫 명령 인자가 list/tuple
shell=True가 아님
```

Positive 예:

```python
subprocess.run(
    ["git", "status"],
    shell=False,
    check=True,
)
```

Negative 예:

```python
subprocess.run("git status", shell=True)
```

---

## 10.4 GOOD006

주요 대상:

```text
yaml.safe_load
```

Positive 예:

```python
import yaml

data = yaml.safe_load(text)
```

MVP에서는 PyYAML을 실제 import하거나 실행하지 않는다.

AST 안에서 호출 형태만 정적으로 판단한다.

---

## 10.5 JSON Export

D는 다음 의미를 만족하는 Exporter를 구현한다.

```text
ScanResult
    ↓
JSON serializable data
    ↓
사용자가 선택한 파일 경로에 저장
```

권장 위치:

```text
goodcode/exporters/json_exporter.py
```

Exporter가 GUI widget을 import하면 안 된다.

GUI는 저장 위치를 선택하고 Exporter를 호출한다.

---

## 10.6 Integration Regression

D는 main 통합 이후 최소 다음 회귀 테스트를 주도한다.

```text
[ ] GOOD001 ~ GOOD006 모두 동작
[ ] Finding sorting
[ ] Golden JSON
[ ] No-Execution invariant
[ ] Parse Error
[ ] Read Error
[ ] Empty Result
[ ] GUI → Core 연결
[ ] Core → Rules 연결
[ ] ScanResult → JSON Export 연결
```

---

## 10.7 No-Execution Invariant Test

테스트 대상 파일에 실행되면 side effect가 생기는 코드를 넣는다.

개념 예:

```python
from pathlib import Path

Path("SHOULD_NOT_EXIST.txt").write_text("executed")
```

Scanner로 해당 파일을 분석한 후 다음을 검증한다.

```text
SHOULD_NOT_EXIST.txt가 생성되지 않아야 한다.
```

이 테스트는 MVP의 가장 중요한 보안 불변조건 중 하나다.

---

## 10.8 Golden JSON Test

고정된 sample 파일을 분석한 결과가 예상 schema와 의미를 유지하는지 검증한다.

목적:

```text
Core 변경
Rule 변경
Exporter 변경
```

중 하나가 최종 출력 계약을 예상치 않게 깨뜨리는 것을 빠르게 발견한다.

---

## 10.9 PyInstaller

목표:

```text
Windows에서 더블 클릭으로 실행 가능한 GUI 프로그램
```

기본 빌드 방향:

```text
PyInstaller onedir
```

`onefile`은 시간이 남고 안정적일 때만 시도한다.

최종 산출물 예:

```text
dist/
└── GoodCodeHunter/
    └── GoodCodeHunter.exe
```

---

## 10.10 D의 Definition of Done

```text
[ ] GOOD004 ~ GOOD006 Positive/Negative 테스트
[ ] JSON Exporter 완료
[ ] Rule Registry에 P0 6개 연결
[ ] No-Execution test 통과
[ ] Golden JSON test 통과
[ ] 전체 pytest 통과
[ ] ruff check . 통과
[ ] Windows PyInstaller build 성공
[ ] EXE 실행 smoke test
[ ] README 실행 방법 정리
```

## 10.11 D의 권장 Commit 단위

```text
feat(rule): implement GOOD004 constant time comparison
feat(rule): implement GOOD005 safer subprocess detection
feat(rule): implement GOOD006 safe yaml detection
feat(export): add scan result json exporter
test(integration): add no-execution and golden result tests
build: add pyinstaller windows packaging
```

---

# 11. 4일 실행 일정

# Day 1 — Contract + Skeleton + 각자 독립 개발 시작

## 오전: 전원 공통

목표:

```text
PRD / AGENTS / plan 최종 확인
→ Foundation Contract Freeze
→ main merge
→ 각 feature branch 생성
```

완료 기준:

```text
[ ] 프로젝트 디렉터리 구조 존재
[ ] Finding 고정
[ ] ScanResult 고정
[ ] scan_file signature 고정
[ ] Rule interface 고정
[ ] pytest 실행 가능
[ ] ruff 실행 가능
```

## 오후: 병렬 작업

### A

```text
Main Window
File Picker
Fake ScanResult
Summary 영역
기본 상태 모델
```

### B

```text
Safe file read
ast.parse
Core error handling
Import/Alias Resolver 시작
```

### C

```text
GOOD001
GOOD002
각 Positive/Negative test
```

### D

```text
GOOD004
GOOD005
각 Positive/Negative test
JSON Exporter skeleton
```

### Day 1 Gate

```text
A: Fake data로 GUI 실행 가능
B: 한 .py 파일을 실행 없이 AST parsing 가능
C: GOOD001 또는 GOOD002 최소 1개 완성
D: GOOD004 또는 GOOD005 최소 1개 완성
```

---

# Day 2 — P0 Feature Complete

Day 2의 목표는 **모든 P0 기능을 각 브랜치 안에서 구현 완료**하는 것이다.

### A

```text
Findings Table
Detail View
Evidence 표시
Empty State
Error State
Disclaimer
JSON Export action 연결 구조
```

### B

```text
Import/Alias Resolver 완료
Rule orchestration 완료
Deterministic sorting
ScanResult status 결정
scan_file() 실제 동작 완료
Core tests
```

### C

```text
GOOD001 완료
GOOD002 완료
GOOD003 완료
각 fixture/test/doc 완료
```

### D

```text
GOOD004 완료
GOOD005 완료
GOOD006 완료
각 fixture/test/doc 완료
JSON Exporter 완료
```

### Day 2 Gate

다음이 만족되어야 Day 3 통합으로 넘어간다.

```text
[ ] A: Mock/Fake 기반 GUI 기능 전체 확인
[ ] B: scan_file() 단독 테스트 성공
[ ] C: GOOD001 ~ GOOD003 테스트 성공
[ ] D: GOOD004 ~ GOOD006 테스트 성공
[ ] 각자 pytest 관련 테스트 통과
[ ] 각자 ruff 관련 영역 문제 없음
```

P0가 미완성인데 P1 Rule을 만들지 않는다.

---

# Day 3 — Merge + Real Integration + Regression

Day 3부터는 기능 추가보다 **연결과 안정화**가 우선이다.

## 권장 merge 순서

```text
1. feat/core
2. feat/rules-a
3. feat/rules-b-integration
4. feat/gui
5. integration fixes
```

이 순서를 권장하는 이유:

```text
Core Contract/Engine
        ↓
Rule 구현 연결
        ↓
ScanResult 실제 생성
        ↓
GUI 실제 scan_file 연결
```

각 PR merge 직후 전체 테스트를 실행한다.

```bash
pytest -q
ruff check .
```

한꺼번에 4개 브랜치를 merge한 다음 문제를 찾지 않는다.

## A

```text
Fake → real scan_file 연결
실제 GOOD001~006 결과 화면 확인
GUI 오류 메시지 조정
```

## B

```text
Rule integration에서 발견된 Core contract bug 수정
Alias Resolver regression 수정
Core 안정화
```

## C

```text
통합 과정에서 발생한 GOOD001~003 실제 버그만 수정
오탐/미탐 fixture 추가
```

## D

```text
Rule Registry 최종 연결
GOOD004~006 통합 수정
Golden JSON
No-Execution
JSON E2E
전체 Integration 주도
```

### Day 3 Demo Gate

Day 3 종료 시 최소 다음 Demo가 가능해야 한다.

```text
1. app 실행
2. examples/demo_good.py 선택
3. 검거 시작
4. 여러 GOOD00X 결과 표시
5. 결과 하나 클릭
6. line/evidence/message 확인
7. JSON 저장
8. 저장 JSON 확인
```

이 Demo가 안 되면 Day 4에 P1을 하지 않는다.

---

# Day 4 — Freeze + Build + Demo 준비

Day 4부터는 **기능 동결(Feature Freeze)** 한다.

허용:

```text
버그 수정
오류 메시지 개선
UI 깨짐 수정
테스트 보강
빌드 수정
README 수정
Demo sample 보강
```

금지:

```text
새 대형 기능
새 GUI 프레임워크
프로젝트 디렉터리 분석
LLM 기능 추가
웹 기능 추가
새 언어 지원
대규모 refactor
```

## 오전

```text
전체 regression
No-Execution 확인
Golden JSON 확인
Demo sample 확정
GUI smoke test
```

## 오후

```text
PyInstaller build
실제 exe 실행
다른 팀원 PC에서 가능하면 실행 확인
README 사용법
발표 시연 순서 확정
```

### Day 4 Final Gate

```text
[ ] GUI 실행
[ ] .py 파일 선택
[ ] 실제 Core 분석
[ ] GOOD001 ~ GOOD006 모두 registry 등록
[ ] 결과 Table
[ ] Detail View
[ ] Empty 상태
[ ] Error 상태
[ ] JSON Export
[ ] No Execution
[ ] pytest -q PASS
[ ] ruff check . PASS
[ ] Windows build 성공
[ ] exe smoke test 성공
[ ] README에 실행 방법 존재
[ ] 데모 파일 존재
```

이 Gate를 통과하면 MVP v0.1 완료로 본다.

---

# 12. Day 5 ~ Day 7은 Buffer다

공식 기간은 1주지만 목표는 Day 4 완료다.

따라서 Day 5~7은 처음부터 기능 개발 일정으로 잡지 않는다.

사용 목적:

```text
예상치 못한 Windows build 문제
merge bug
GUI 환경 차이
Rule 오탐 수정
발표 자료
시연 리허설
README 보완
```

P0가 완벽하게 안정된 경우에만 P1을 고려한다.

```text
GOOD007 Secure TLS Context
GOOD008 Secure Temporary File API
```

P1 때문에 P0 안정성을 희생하면 안 된다.

---

# 13. Integration Contract

네 명의 결과물이 합쳐질 때 연결 지점은 최대한 적게 유지한다.

## GUI → Core

GUI는 분석을 다음 하나의 public API로 요청한다.

```python
result = scan_file(path)
```

GUI가 개별 Rule을 직접 호출하지 않는다.

---

## Core → Rules

Core는 등록된 Rule을 실행하고 `Finding`들을 취합한다.

개념:

```text
Parsed Source
     ↓
Static Context
     ↓
Registered Rules
     ↓
list[Finding]
     ↓
Sort
     ↓
ScanResult
```

---

## Core → GUI

GUI는 `ScanResult`만 해석한다.

```text
status
findings
warnings
target
```

GUI가 AST 객체를 전달받지 않는다.

---

## ScanResult → Exporter

Exporter는 `ScanResult`를 받아 JSON으로 직렬화한다.

Exporter가 Scanner를 다시 실행하지 않는다.

---

# 14. 실제 Demo용 파일 계획

통합 테스트와 발표를 위해 `examples/`를 준비한다.

권장:

```text
examples/
├── demo_good.py
├── demo_empty.py
└── demo_syntax_error.py
```

## demo_good.py

가능하면 GOOD001 ~ GOOD006이 모두 한 번 이상 탐지되도록 만든다.

주의:

이 파일은 Scanner가 **읽기만 해야 한다.**

실제 외부 패키지가 설치되어 있지 않아도 AST parsing 자체는 가능하도록 예제 코드를 작성한다.

## demo_empty.py

현재 P0 Rule과 관련 없는 정상 Python 코드.

목적:

```text
NO_GOOD_PATTERNS_FOUND GUI 검증
```

## demo_syntax_error.py

고의적인 Python Syntax Error.

목적:

```text
PARSE_ERROR GUI 검증
```

---

# 15. Pull Request 규칙

각 PR에는 최소 다음 내용을 적는다.

```text
## 담당 영역
예: GUI / GOOD001~003 / Core

## 구현 내용
- ...
- ...

## 수정 파일
- ...

## Contract 변경
없음 / 있음

## 테스트
pytest ...
ruff check .

## 남은 문제
없음 / ...
```

Contract 변경이 `있음`이면 바로 merge하지 않는다.

네 명이 영향 범위를 확인한다.

---

# 16. Merge 규칙

Merge 전:

```bash
git status
pytest -q
ruff check .
git diff --check
```

Merge 후 main에서도 다시:

```bash
pytest -q
ruff check .
```

원칙:

```text
branch PASS ≠ main PASS
```

각 브랜치에서 테스트가 성공해도 합친 뒤 깨질 수 있다.

따라서 **merge 후 검증이 반드시 필요하다.**

---

# 17. 충돌이 발생했을 때 담당

## GUI 관련

```text
1차 판단: A
```

## Core / Contract 관련

```text
1차 판단: B
```

## GOOD001 ~ GOOD003

```text
1차 판단: C
```

## GOOD004 ~ GOOD006 / Export / Build

```text
1차 판단: D
```

## 여러 영역을 동시에 건드리는 Integration 문제

```text
D가 원인을 분류
→ 해당 Owner와 함께 최소 수정
```

D가 다른 사람 코드를 마음대로 재작성하지 않는다.

---

# 18. 위험 요소와 대응

## 위험 1 — GUI 담당자가 Core 완료까지 대기

대응:

```text
Fixed ScanResult Contract
+ Fake ScanResult
+ scan callable injection
```

따라서 A는 Day 1부터 독립적으로 작업한다.

---

## 위험 2 — Rule Agent 둘이 같은 파일 수정

대응:

```text
C: GOOD001~003 전용 파일
D: GOOD004~006 전용 파일
Rule registry는 D가 통합 단계에서 한 번만 수정
```

---

## 위험 3 — 모든 Rule이 자기 방식으로 import alias를 처리

대응:

```text
Alias Resolver는 B가 Core 공통 기능으로 제공
Rule은 공통 context 사용
```

---

## 위험 4 — Agent가 범위를 확장

예:

```text
프로젝트 전체 scanning
LLM review
PySide 전환
웹 UI
보안 점수
취약점 탐지
```

대응:

```text
PRD의 Out-of-Scope 준수
Day 4 Feature Freeze
```

---

## 위험 5 — 분석 대상 Python이 실행됨

대응:

```text
No-Execution invariant
금지 API 명시
Side-effect fixture test
```

---

## 위험 6 — Build를 마지막 30분에 처음 시도

대응:

D는 가능하면 Day 3 후반에 PyInstaller smoke build를 한 번 수행한다.

Day 4는 처음 빌드하는 날이 아니라 **최종 빌드를 확정하는 날**로 만든다.

---

# 19. 각 팀원이 Codex에 처음 줄 작업 프롬프트

모든 팀원은 Codex에게 먼저 다음 공통 문장을 준다.

```text
저장소의 PRD.md, AGENTS.md, plan.md를 먼저 모두 읽어라.
이 세 문서를 프로젝트의 source of truth로 사용하라.
내 담당 영역 밖의 파일은 임의로 수정하지 마라.
구현 전에 현재 branch, git status, 저장소 구조, 관련 기존 코드를 확인하라.
구현 후 관련 테스트와 전체 테스트, lint를 실행하고 결과를 보고하라.
```

그 뒤 담당별 문장을 추가한다.

---

## A — GUI Agent Prompt

```text
너는 plan.md의 팀원 A, GUI/UX 담당이다.
feat/gui 브랜치에서 작업한다.

Core와 Rule을 구현하지 마라.
Finding/ScanResult Contract를 변경하지 마라.
Core가 아직 미완성이라면 Fake ScanResult 또는 주입 가능한 fake scan callable을 사용해 GUI를 독립적으로 완성하라.

PRD가 요구하는 GUI 기능을 모두 만족하되 구체적인 디자인, 레이아웃, 위젯 배치, 색상은 네 담당 범위 안에서 합리적으로 결정해라.
production app.py는 최종적으로 실제 scan_file()을 사용해야 한다.
```

---

## B — Core Agent Prompt

```text
너는 plan.md의 팀원 B, Core/AST Infrastructure 담당이다.
feat/core 브랜치에서 작업한다.

GUI와 개별 GOOD00X Rule을 구현하지 마라.
고정된 Finding, ScanResult, scan_file() Contract를 유지하라.
대상 Python 파일을 절대 실행하거나 import하지 마라.
파일 읽기, ast.parse, alias resolution, rule orchestration, deterministic sorting, error normalization을 구현하라.
Core는 GUI 없이 pytest로 검증 가능해야 한다.
```

---

## C — Rule Pack A Agent Prompt

```text
너는 plan.md의 팀원 C, Rule Pack A 담당이다.
feat/rules-a 브랜치에서 작업한다.

GOOD001, GOOD002, GOOD003만 구현하라.
GUI, Core, GOOD004~GOOD006을 수정하지 마라.
각 Rule마다 positive fixture, negative fixture, unit test, rule 문서를 만들어라.
명확한 Positive Security Evidence만 Finding으로 만들고 애매하면 탐지하지 마라.
대상 코드를 절대 실행하지 마라.
```

---

## D — Rule Pack B / Integration Agent Prompt

```text
너는 plan.md의 팀원 D, Rule Pack B + Export/Integration/Build 담당이다.
feat/rules-b-integration 브랜치에서 작업한다.

먼저 GOOD004, GOOD005, GOOD006과 각각의 positive/negative test를 완성하라.
그 후 JSON exporter를 구현하라.
Day 3부터 main 통합 상태를 기준으로 Rule registry, Golden JSON, No-Execution test, E2E regression, PyInstaller build를 담당하라.

다른 담당자의 기능을 대신 재작성하지 말고, integration 실패가 발생하면 원인을 분류해 해당 Owner의 최소 수정으로 해결하라.
```

---

# 20. Agent 작업 종료 보고 형식

Codex가 작업을 끝냈다고 할 때 최소 다음을 보고하게 한다.

```text
1. 구현한 기능
2. 변경한 파일
3. 변경하지 않은 담당 외 영역
4. 실행한 테스트 명령
5. 테스트 결과
6. lint 결과
7. 남은 TODO
8. Contract 변경 여부
9. merge 전에 확인해야 할 사항
```

예:

```text
Implemented:
- GOOD002 secrets detection
- alias cases
- positive/negative fixtures

Changed:
- goodcode/rules/secure_random.py
- tests/rules/test_good002.py
- tests/fixtures/good002/...

Tests:
pytest tests/rules/test_good002.py -q
→ 8 passed

Lint:
ruff check .
→ passed

Contract changes:
None
```

이 보고 형식은 사람이 Agent의 작업을 빠르게 검토하기 위한 Harness의 일부다.

---

# 21. 최종 저장소 목표 구조

MVP 종료 시 대략 다음 구조를 목표로 한다.

```text
good-code-hunter/
├── app.py
├── PRD.md
├── AGENTS.md
├── plan.md
├── README.md
├── pyproject.toml
│
├── goodcode/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── scanner.py
│   │   ├── import_resolver.py
│   │   └── service.py
│   │
│   ├── rules/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── sql.py
│   │   ├── secure_random.py
│   │   ├── password_hashing.py
│   │   ├── constant_time.py
│   │   ├── subprocess_rule.py
│   │   └── yaml_safe_load.py
│   │
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   └── result_view.py
│   │
│   └── exporters/
│       ├── __init__.py
│       └── json_exporter.py
│
├── tests/
│   ├── core/
│   ├── rules/
│   ├── gui/
│   ├── integration/
│   └── fixtures/
│
├── docs/
│   ├── rules.md
│   └── rules/
│       ├── GOOD001.md
│       ├── GOOD002.md
│       ├── GOOD003.md
│       ├── GOOD004.md
│       ├── GOOD005.md
│       └── GOOD006.md
│
├── examples/
│   ├── demo_good.py
│   ├── demo_empty.py
│   └── demo_syntax_error.py
│
└── build/
```

실제 구현 중 파일이 조금 달라지는 것은 허용한다.

단, 다음 경계는 유지한다.

```text
GUI ≠ Core
Core ≠ Rule implementation
Rule ≠ Exporter
분석 ≠ 실행
```

---

# 22. MVP Definition of Done

프로젝트 전체가 완료되었다고 말하려면 다음을 모두 만족해야 한다.

## Product

```text
[ ] Windows GUI 프로그램 실행 가능
[ ] GUI에서 .py 하나 선택 가능
[ ] 분석 시작 가능
[ ] Positive Security Finding 확인 가능
[ ] Finding 상세 정보 확인 가능
[ ] Empty Result 처리
[ ] Error 처리
[ ] JSON 저장
```

## Analysis

```text
[ ] GOOD001
[ ] GOOD002
[ ] GOOD003
[ ] GOOD004
[ ] GOOD005
[ ] GOOD006
[ ] deterministic sorting
[ ] alias handling 최소 범위
[ ] 설명 가능한 evidence
```

## Safety

```text
[ ] target import 없음
[ ] exec/eval 없음
[ ] target subprocess 실행 없음
[ ] No-Execution regression PASS
```

## Engineering

```text
[ ] PRD.md 공유
[ ] AGENTS.md 공유
[ ] plan.md 공유
[ ] 4개 역할별 branch 사용
[ ] 각 Agent 담당 영역 준수
[ ] pytest -q PASS
[ ] ruff check . PASS
[ ] main 통합 후 regression PASS
```

## Distribution

```text
[ ] PyInstaller build 성공
[ ] Windows 실행 확인
[ ] README 실행 방법 작성
[ ] demo sample 준비
```

---

# 23. 완료 후에만 고려할 Stretch Goal

아래는 모두 P0 이후다.

우선순위:

```text
1. GOOD007 Secure TLS Context
2. GOOD008 Secure Temporary File API
3. 결과 필터
4. Drag & Drop
5. HTML Report
```

다음은 1주 MVP에서는 계속 제외한다.

```text
LLM 판정
웹 서비스
다른 언어
전체 repository scan
취약점 공격
자동 코드 수정
실시간 프로세스 감시
```

---

# 24. 최종 개발 원칙 요약

이번 프로젝트에서 사람이 해야 할 가장 중요한 일은 Codex 대신 코드를 많이 작성하는 것이 아니다.

**Codex가 잘못된 방향으로 가지 않도록 작업 환경, 계약, 경계, 테스트, 완료 조건을 명확하게 만드는 것**이다.

따라서 네 명은 다음 흐름을 유지한다.

```text
문서로 목표를 고정한다.
        ↓
Contract를 먼저 고정한다.
        ↓
Agent마다 소유 영역을 제한한다.
        ↓
Mock/Fixture로 의존성을 제거한다.
        ↓
각 Agent가 자기 작업을 테스트한다.
        ↓
작은 PR로 합친다.
        ↓
merge마다 regression을 실행한다.
        ↓
최종 실행 프로그램으로 검증한다.
```

**기능을 많이 만드는 것보다 Day 4에 실제로 실행되고, 설명 가능하고, 테스트 가능하며, 네 명의 작업을 안정적으로 합칠 수 있는 MVP를 만드는 것을 최우선으로 한다.**
