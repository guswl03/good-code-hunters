# PRD.md — 착한코드검거단 MVP

> **프로젝트명:** 착한코드검거단 (Good Code Hunter)  
> **버전:** MVP v0.1  
> **공식 개발 기간:** 1주  
> **내부 목표:** 4일 안에 기능 완성 및 통합 가능 상태 달성  
> **팀 규모:** 4명  
> **개발 방식:** Harness Engineering + Codex 기반 병렬 개발  
> **MVP 대상:** Python 단일 소스 파일 (`.py`)  
> **사용자 인터페이스:** 데스크톱 GUI  
> **문서 역할:** 이 문서는 프로젝트의 “무엇을 만들 것인가”와 완료 조건을 정의하는 제품 요구사항의 단일 기준(Single Source of Truth)이다.

---

# 1. 제품 한 줄 정의

**착한코드검거단은 사용자가 GUI에서 Python 소스 파일 하나를 선택하면, 해당 코드를 실행하지 않고 정적으로 분석하여 보안적으로 권장할 만한 시큐어 코딩 패턴을 찾아 위치·근거 코드·설명과 함께 시각적으로 보여주는 데스크톱 프로그램이다.**

기존의 많은 보안 도구가 “위험한 코드”나 “악성 행위”를 찾는 데 집중한다면, 착한코드검거단은 반대로 코드 안에서 확인 가능한 **좋은 보안 습관(Positive Security Evidence)** 을 찾아 사용자가 이해하기 쉽게 보여주는 것을 핵심 콘셉트로 한다.

이 프로젝트는 ‘악성코드검거단’의 이름과 탐지 콘셉트에서 아이디어를 얻지만, 악성코드를 분석·차단하거나 실제 실행 중인 프로세스를 감시하는 프로그램을 구현하는 것은 아니다.

---

# 2. 우리가 해결하려는 문제

일반적인 SAST, 린터, 보안 점검 도구는 대부분 다음과 같은 방식으로 동작한다.

- 위험한 함수 사용 탐지
- 취약한 설정 탐지
- 보안 규칙 위반 탐지
- 취약점 후보 경고

하지만 교육, 코드 리뷰, 시큐어 코딩 학습 상황에서는 반대 방향의 피드백도 가치가 있다.

예를 들어 개발자는 다음을 알고 싶을 수 있다.

- 내가 작성한 코드에서 보안적으로 잘한 부분은 무엇인가?
- 어떤 시큐어 코딩 원칙이 실제 코드에 적용되어 있는가?
- 단순히 “취약점이 안 보인다”가 아니라, 좋은 보안 패턴이 있다는 근거를 확인할 수 있는가?
- 보안 관점에서 칭찬할 수 있는 코드가 어디에 있는가?

착한코드검거단은 이 질문에 답한다.

중요한 점은 **코드 전체가 안전하다고 인증하는 것이 아니라**, 정적 분석으로 확실하게 확인할 수 있는 긍정적인 보안 패턴을 찾아 보여주는 것이다.

---

# 3. MVP의 핵심 사용자 경험

사용자가 프로그램을 실행하면 복잡한 설정 없이 다음 흐름으로 사용할 수 있어야 한다.

```text
프로그램 실행
    ↓
[Python 파일 선택]
    ↓
분석할 .py 파일 선택
    ↓
[착한코드 검거 시작]
    ↓
AST 기반 정적 분석
    ↓
착한코드 탐지 결과 표시
    ↓
결과 항목 선택
    ↓
라인 / 근거 코드 / 왜 좋은 코드인지 상세 설명 확인
    ↓
필요하면 결과를 JSON 파일로 저장
```

사용자는 터미널 명령어를 몰라도 프로그램의 모든 핵심 기능을 사용할 수 있어야 한다.

---

# 4. MVP 목표

4일 안에 다음 기능을 완성하는 것을 목표로 한다.

## 4.1 필수 기능

1. GUI 프로그램이 실행된다.
2. 사용자가 파일 선택 창에서 `.py` 파일 하나를 선택할 수 있다.
3. 선택한 파일의 경로와 파일명이 GUI에 표시된다.
4. 사용자가 `착한코드 검거 시작` 버튼을 누를 수 있다.
5. 프로그램은 대상 Python 코드를 **절대 실행하지 않고** 읽기와 AST 분석만 수행한다.
6. 미리 정의한 시큐어 코딩 탐지 규칙을 적용한다.
7. 발견된 착한코드 목록을 GUI에 표시한다.
8. 각 탐지 결과의 다음 정보를 확인할 수 있다.
   - Rule ID
   - 규칙 이름
   - 카테고리
   - 라인 번호
   - 근거 코드
   - 왜 좋은 코드인지에 대한 설명
9. 탐지 결과 개수를 요약해서 보여준다.
10. 분석 결과가 없을 때도 오류가 아니라 정상 상태로 안내한다.
11. 문법 오류나 잘못된 파일을 사용자 친화적인 GUI 메시지로 처리한다.
12. 결과를 JSON 파일로 저장할 수 있다.
13. 모든 핵심 기능에 자동 테스트가 존재한다.
14. 프로그램을 빌드하여 다른 사람이 실행할 수 있는 배포 산출물을 만든다.

---

# 5. MVP 성공 기준

다음 조건을 모두 만족하면 MVP가 성공한 것으로 본다.

- Python `.py` 파일 하나를 GUI에서 선택해 분석할 수 있다.
- 최소 **6개의 핵심 시큐어 코딩 규칙**이 정상적으로 동작한다.
- 같은 입력 파일은 같은 탐지 결과를 만든다.
- 각 Finding은 실제 근거 코드와 라인 번호를 가진다.
- 분석 대상 Python 코드는 실행되지 않는다.
- 잘못된 입력에도 GUI가 종료되거나 traceback을 그대로 노출하지 않는다.
- 핵심 분석 엔진은 GUI와 독립적으로 자동 테스트할 수 있다.
- 최소 positive / negative fixture 테스트가 존재한다.
- 4명의 브랜치를 main에 병합한 상태에서 전체 테스트가 통과한다.
- Windows 환경에서 실행 가능한 MVP 빌드 결과를 만들 수 있다.

---

# 6. MVP에서 하지 않을 것

4일 완성을 위해 아래 기능은 **명시적으로 MVP 범위에서 제외한다.**

- Python 프로젝트 전체 디렉터리 분석
- 여러 파일 동시 분석
- Java / JavaScript / C / C++ 등 다른 언어 분석
- 악성코드 탐지
- 실행 중인 프로세스 감시
- 실시간 파일 감시
- 코드 실행 또는 샌드박스 실행
- 취약점 자동 공격
- 코드 자동 수정
- LLM을 이용한 보안 판정
- 보안 점수 0~100 계산
- SAFE / UNSAFE 인증
- GitHub 저장소 URL 직접 분석
- 웹 서비스 형태의 배포
- 사용자 계정 / 로그인
- 데이터베이스 저장
- 네트워크 서버 기능
- 복잡한 프로젝트 설정

다음 기능은 시간이 남을 경우에만 Stretch Goal로 고려한다.

- 드래그 앤 드롭 파일 입력
- 결과 필터링 / 검색
- 추가 탐지 규칙
- HTML/PDF 결과 보고서
- 여러 파일 일괄 분석
- 코드 편집기 형태의 시각화

---

# 7. 핵심 제품 원칙

## 7.1 Positive Evidence First

착한코드검거단은 다음처럼 판단해서는 안 된다.

```text
취약점이 발견되지 않았다 → 좋은 코드다
```

반드시 코드 내부에서 **실제로 확인 가능한 긍정적 보안 패턴**이 존재할 때만 착한코드로 탐지한다.

예를 들어 SQL 코드가 전혀 없는 파일에 대해 `SQL Injection 방어가 잘 되어 있습니다`라고 판정해서는 안 된다.

---

## 7.2 Precision over Recall

MVP는 많이 찾는 것보다 **틀리지 않게 찾는 것**을 우선한다.

확실하게 판단할 수 없는 코드라면 억지로 착한코드라고 판정하지 않는다.

즉,

```text
애매함 → 탐지하지 않음
명확한 근거 있음 → 탐지
```

을 기본 정책으로 한다.

---

## 7.3 No Execution

분석 대상 Python 소스는 어떤 경우에도 실행하지 않는다.

금지되는 동작:

- 대상 파일 `import`
- `exec()`
- `eval()`
- `subprocess`로 대상 파일 실행
- 대상 코드의 함수 호출
- 대상 코드의 클래스 생성
- import된 외부 패키지 실행을 통한 분석

허용되는 핵심 동작:

- 파일 읽기
- 문자열 처리
- `ast.parse()`
- AST 순회
- import/alias 정보의 정적 해석
- 근거 라인 추출

이 원칙은 보안성과 테스트 가능성을 동시에 위한 **MVP 최상위 불변조건(Invariant)** 이다.

---

## 7.4 Explainable Finding

모든 탐지 결과는 사용자가 “왜 이게 착한 코드인지” 이해할 수 있어야 한다.

각 Finding은 최소한 다음 질문에 답해야 한다.

```text
무엇을 발견했는가?
어디에서 발견했는가?
어떤 코드가 근거인가?
왜 보안적으로 좋은가?
```

---

## 7.5 Deterministic Analysis

같은 프로그램 버전에서 같은 파일을 분석하면 같은 결과가 나와야 한다.

Finding 기본 정렬 순서는 다음과 같다.

```text
line ASC
→ column ASC
→ rule_id ASC
```

LLM, 외부 API, 랜덤값 등 결과를 비결정적으로 만드는 요소는 MVP 분석 경로에 포함하지 않는다.

---

## 7.6 No False Security Guarantee

착한코드검거단은 코드 전체의 보안성을 인증하지 않는다.

GUI 결과 영역에는 다음 의미의 안내를 항상 제공한다.

> 이 결과는 코드에서 발견된 긍정적인 보안 패턴을 보여주는 것이며, 해당 파일 전체에 취약점이 없음을 보증하지 않습니다.

---

# 8. GUI 요구사항

MVP GUI는 화려한 디자인보다 **명확성, 안정성, 데모 가능성**을 우선한다.

기본 GUI 프레임워크는 **Python Tkinter + ttk**를 사용한다.

선정 이유:

- Python 표준 라이브러리에 포함되어 추가 설치 부담이 작다.
- 4일 MVP에서 환경 차이로 인한 문제를 줄일 수 있다.
- 파일 선택, 버튼, 테이블, 텍스트 영역 등 필요한 기능을 충분히 구현할 수 있다.
- PyInstaller를 이용한 Windows 빌드가 비교적 단순하다.
- GUI와 분석 엔진을 분리하면 향후 PySide/웹 GUI로 교체 가능하다.

---

# 9. GUI 화면 구성

MVP는 **하나의 메인 윈도우**에서 모든 핵심 기능을 처리한다.

복잡한 멀티 페이지 구조는 만들지 않는다.

## 9.1 화면 개념도

```text
┌──────────────────────────────────────────────────────────────┐
│  착한코드검거단                                              │
│  Python 코드 속 보안적으로 좋은 패턴을 찾아드립니다.         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  분석 파일                                                   │
│  [ C:\project\sample.py                         ] [파일 선택]│
│                                                              │
│                    [ 착한코드 검거 시작 ]                    │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  분석 결과                                                   │
│                                                              │
│  착한코드 3건 검거                                           │
│  발견 카테고리 3개                                           │
│                                                              │
│  ┌─────────┬────────────────────────┬─────────────┬──────┐   │
│  │ Rule ID │ 규칙                   │ Category    │ Line │   │
│  ├─────────┼────────────────────────┼─────────────┼──────┤   │
│  │ GOOD001 │ Parameterized SQL      │ Injection   │  12  │   │
│  │ GOOD002 │ Secure Random          │ Crypto      │  20  │   │
│  │ GOOD004 │ Constant-Time Compare  │ SideChannel │  35  │   │
│  └─────────┴────────────────────────┴─────────────┴──────┘   │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  상세 정보                                                   │
│                                                              │
│  GOOD002 — Cryptographically Secure Randomness               │
│  Line 20                                                     │
│                                                              │
│  token = secrets.token_urlsafe(32)                           │
│                                                              │
│  보안용 난수 생성에 적합한 secrets 모듈을 사용하고 있습니다.│
│                                                              │
│                                      [JSON 결과 저장]         │
├──────────────────────────────────────────────────────────────┤
│  ※ 발견되지 않은 취약점이 없음을 보증하는 도구가 아닙니다. │
└──────────────────────────────────────────────────────────────┘
```

위 디자인은 구조적 기준이며 픽셀 단위로 동일하게 만들 필요는 없다.

---

# 10. GUI 컴포넌트 요구사항

## 10.1 Header

표시 내용:

- `착한코드검거단`
- 한 줄 설명

예시:

```text
Python 코드 속 보안적으로 좋은 패턴을 찾아드립니다.
```

---

## 10.2 File Selection Area

필수 요소:

- 현재 선택한 파일 경로 표시
- `파일 선택` 버튼
- 선택 전 상태 안내

파일 선택 버튼 클릭 시 OS 기본 File Dialog를 띄운다.

허용 파일 필터:

```text
Python Files (*.py)
```

다른 확장자를 선택하거나 잘못된 경로가 전달되면 분석하지 않는다.

---

## 10.3 Scan Button

버튼 문구:

```text
착한코드 검거 시작
```

동작:

1. 입력 파일 검증
2. 파일 읽기
3. AST 파싱
4. Rule Engine 실행
5. 결과 정렬
6. GUI 결과 갱신

분석이 진행되는 동안 중복 실행 방지를 위해 버튼을 일시적으로 비활성화할 수 있다.

MVP에서는 단일 Python 파일 분석이 매우 빠르므로 복잡한 worker thread나 progress bar는 필수 요구사항으로 두지 않는다.

다만 GUI가 명백하게 멈추는 수준의 작업이 발생하면 이후 개선한다.

---

## 10.4 Summary Area

분석 완료 후 최소 다음 정보를 표시한다.

```text
착한코드 N건 검거
발견 카테고리 M개
```

예시:

```text
착한코드 5건 검거
발견 카테고리 4개
```

보안 점수는 표시하지 않는다.

---

## 10.5 Findings Table

탐지 결과는 표 형태로 표시한다.

필수 열:

- Rule ID
- Rule Name
- Category
- Line

예시:

```text
GOOD001 | Parameterized SQL Query | Injection Prevention | 12
GOOD002 | Secure Randomness       | Cryptography         | 20
```

사용자가 행 하나를 선택하면 해당 Finding의 상세 정보를 아래 Detail Area에 표시한다.

---

## 10.6 Finding Detail Area

선택한 Finding에 대해 다음 정보를 표시한다.

- Rule ID
- 규칙 이름
- 카테고리
- 파일명
- 라인 번호
- 근거 코드
- 설명

근거 코드는 일반 설명과 시각적으로 구분한다.

예시:

```python
token = secrets.token_urlsafe(32)
```

설명 예시:

```text
보안용 토큰 생성에 적합한 secrets 모듈을 사용하고 있습니다.
```

---

## 10.7 JSON Export Button

버튼 문구 예시:

```text
JSON 결과 저장
```

사용자가 저장 위치를 선택하면 현재 `ScanResult`를 JSON 파일로 저장한다.

분석 결과가 없는 상태에서는 버튼을 비활성화한다.

---

## 10.8 Disclaimer

메인 화면 하단 또는 결과 영역에 다음 의미의 안내를 항상 표시한다.

```text
이 도구는 발견된 긍정적인 보안 패턴만 보여줍니다.
코드 전체에 취약점이 없음을 보증하지 않습니다.
```

---

# 11. GUI 상태 모델

GUI는 최소 다음 상태를 구분한다.

## EMPTY

아직 파일이 선택되지 않은 상태.

```text
Python 파일을 선택해주세요.
```

## READY

정상적인 `.py` 파일이 선택되어 분석할 준비가 된 상태.

## SCANNING

분석 수행 중인 상태.

## SUCCESS_WITH_FINDINGS

착한코드가 한 건 이상 탐지된 상태.

```text
착한코드 4건을 검거했습니다.
```

## SUCCESS_EMPTY

정상적으로 분석했지만 현재 규칙으로 찾은 착한코드가 없는 상태.

```text
현재 규칙으로 확인할 수 있는 착한코드를 찾지 못했습니다.
이 결과가 코드가 취약하다는 뜻은 아닙니다.
```

## ERROR

파일 오류, 인코딩 오류, SyntaxError 등으로 분석할 수 없는 상태.

오류는 traceback 대신 사용자 친화적인 메시지로 표시한다.

---

# 12. MVP 탐지 규칙

MVP는 모든 시큐어 코딩 원칙을 검사하려 하지 않는다.

다음 기준을 만족하는 규칙을 우선한다.

- AST 기반으로 비교적 확실히 판단할 수 있음
- 데모 시 이해하기 쉬움
- 보안적 의미가 분명함
- negative case와 구분 가능함
- 4일 안에 구현 및 테스트 가능함

---

# 13. P0 — 반드시 구현할 6개 규칙

## GOOD001 — Parameterized SQL Query

**목적:** SQL 문자열에 사용자 값을 직접 결합하지 않고 쿼리와 파라미터를 분리하여 전달하는 패턴을 탐지한다.

긍정 예시:

```python
cursor.execute(
    "SELECT * FROM users WHERE id = ?",
    (user_id,),
)
```

MVP 탐지 방향:

- `execute()` 또는 `executemany()` 호출
- SQL과 data argument가 분리되어 있음
- SQL 문자열에 placeholder가 존재함
- f-string이나 문자열 결합을 통한 SQL 조립은 좋은 패턴으로 인정하지 않음

카테고리:

```text
injection-prevention
```

---

## GOOD002 — Cryptographically Secure Randomness

**목적:** 보안용 난수 생성에 적합한 `secrets` API 사용을 탐지한다.

긍정 예시:

```python
import secrets

token = secrets.token_urlsafe(32)
```

MVP 주요 대상:

- `secrets.token_bytes`
- `secrets.token_hex`
- `secrets.token_urlsafe`
- `secrets.randbelow`
- `secrets.choice`
- `secrets.SystemRandom`

카테고리:

```text
cryptography
```

---

## GOOD003 — Password Hashing / Password KDF

**목적:** 비밀번호 처리에 적합한 Password Hashing 또는 KDF API 사용을 탐지한다.

MVP 주요 대상:

- `hashlib.pbkdf2_hmac`
- `hashlib.scrypt`
- `bcrypt.hashpw`
- Argon2 `PasswordHasher.hash`

예시:

```python
import hashlib

hashed = hashlib.pbkdf2_hmac(
    "sha256",
    password,
    salt,
    200_000,
)
```

MVP는 모든 알고리즘 파라미터의 강도를 완전히 평가하지 않는다.

확인 가능한 긍정 증거인 **권장 계열 Password Hash/KDF API 사용**에 집중한다.

카테고리:

```text
credential-protection
```

---

## GOOD004 — Constant-Time Secret Comparison

**목적:** 토큰, 서명값, MAC 등 비밀값 비교 시 constant-time 비교 API 사용을 탐지한다.

긍정 예시:

```python
import hmac

if hmac.compare_digest(received, expected):
    pass
```

주요 대상:

- `hmac.compare_digest`
- `secrets.compare_digest`

카테고리:

```text
side-channel-defense
```

---

## GOOD005 — Safer Subprocess Invocation

**목적:** shell command 문자열을 직접 실행하는 대신 argument list를 전달하는 비교적 안전한 subprocess 호출 패턴을 탐지한다.

긍정 예시:

```python
import subprocess

subprocess.run(
    ["git", "status"],
    shell=False,
    check=True,
)
```

MVP에서 긍정으로 인정할 조건:

- `subprocess.run()` 또는 `subprocess.Popen()`
- 첫 번째 명령 인자가 list/tuple 형태
- `shell=True`가 아님

카테고리:

```text
command-execution
```

---

## GOOD006 — Safe YAML Deserialization

**목적:** YAML 역직렬화 시 안전한 로딩 API 사용을 탐지한다.

긍정 예시:

```python
import yaml

data = yaml.safe_load(text)
```

주요 대상:

- `yaml.safe_load`
- 구현 난이도가 낮고 확실한 범위 내의 안전한 Loader 사용

카테고리:

```text
deserialization
```

---

# 14. P1 — 시간이 남으면 구현할 규칙

## GOOD007 — Secure TLS Context

긍정 예시:

```python
import ssl

context = ssl.create_default_context()
```

카테고리:

```text
transport-security
```

---

## GOOD008 — Secure Temporary File API

긍정 예시:

```python
import tempfile

with tempfile.NamedTemporaryFile() as fp:
    pass
```

주요 대상:

- `tempfile.NamedTemporaryFile`
- `tempfile.TemporaryDirectory`
- `tempfile.mkstemp`
- `tempfile.mkdtemp`

카테고리:

```text
file-security
```

P1 규칙은 P0 기능 안정화를 방해하지 않는 경우에만 추가한다.

---

# 15. 판정 정책

## 15.1 전체 파일을 SAFE / UNSAFE로 판정하지 않는다

다음 표현은 사용하지 않는다.

```text
안전도 95점
보안 점수 A+
이 파일은 안전합니다.
이 코드는 취약하지 않습니다.
```

착한코드검거단이 말할 수 있는 것은 다음뿐이다.

```text
현재 규칙으로 이 파일에서 긍정적인 보안 패턴 N건을 확인했습니다.
```

---

## 15.2 파일 단위 분석 상태

Core의 ScanResult 상태는 최소 다음을 사용한다.

```text
GOOD_PATTERNS_FOUND
NO_GOOD_PATTERNS_FOUND
PARSE_ERROR
READ_ERROR
```

GUI 표현은 사용자가 이해하기 쉽게 변환할 수 있다.

---

## 15.3 Confidence

향후 확장을 위해 Finding에 `confidence` 필드를 유지한다.

MVP에서는 기본적으로 `HIGH` confidence인 명확한 패턴만 Finding으로 생성한다.

---

# 16. 핵심 기술 설계

## 16.1 기술 스택

- Python 3.11+
- GUI: `tkinter`, `tkinter.ttk`
- AST: Python 표준 `ast`
- JSON: Python 표준 `json`
- Test: `pytest`
- Lint / Format: `ruff`
- Build: `PyInstaller`

분석 엔진에서는 가능한 한 표준 라이브러리를 우선한다.

외부 dependency는 규칙 분석을 위해 실제 패키지를 import하지 않는다.

예를 들어 분석 대상 코드에 `bcrypt`가 있더라도 착한코드검거단이 `bcrypt`를 실행하거나 import할 필요는 없다. AST에서 이름과 호출 구조만 분석한다.

---

# 17. 시스템 아키텍처

GUI와 분석 로직을 강하게 결합하지 않는다.

```text
┌──────────────────────┐
│      Desktop GUI     │
│ File / Scan / Result │
└──────────┬───────────┘
           │ ScanRequest
           ▼
┌──────────────────────┐
│  Application Service │
│    Scan Controller   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       Scanner        │
│ Read + ast.parse()   │
└──────────┬───────────┘
           │ AST + source
           ▼
┌──────────────────────┐
│     Rule Engine      │
│ GOOD001 ... GOOD00N  │
└──────────┬───────────┘
           │ Findings
           ▼
┌──────────────────────┐
│     ScanResult       │
│ deterministic model  │
└──────┬─────────┬─────┘
       │         │
       ▼         ▼
┌────────────┐ ┌────────────┐
│ GUI Render │ │ JSON Export│
└────────────┘ └────────────┘
```

핵심 원칙:

- GUI는 AST를 직접 분석하지 않는다.
- Rule은 GUI widget을 직접 조작하지 않는다.
- Rule은 문자열을 화면에 직접 출력하지 않는다.
- Scanner는 Tkinter에 의존하지 않는다.
- JSON Exporter는 GUI widget에 의존하지 않는다.
- GUI는 최종 `ScanResult`를 받아 화면에 그린다.

이 경계를 지켜야 4명의 Codex 작업을 병렬화하기 쉽다.

---

# 18. 공통 데이터 모델

4명이 각 브랜치에서 따로 구현해도 병합할 수 있도록 핵심 계약을 먼저 고정한다.

## 18.1 Finding

필수 필드:

```text
rule_id
name
description/category
confidence
file
line
column
evidence
message
```

권장 Python 모델 개념:

```python
Finding(
    rule_id="GOOD002",
    name="Cryptographically Secure Randomness",
    category="cryptography",
    confidence="HIGH",
    file="sample.py",
    line=20,
    column=8,
    evidence="token = secrets.token_urlsafe(32)",
    message="보안용 난수 생성에 적합한 secrets 모듈을 사용하고 있습니다.",
)
```

---

## 18.2 ScanResult

필수 필드:

```text
schema_version
tool_version
target
status
findings
warnings
```

Summary는 ScanResult로부터 계산 가능하게 한다.

예시:

```text
finding_count
category_count
```

---

# 19. Import / Alias Resolver 요구사항

단순 문자열 검색만으로는 다음과 같은 코드를 안정적으로 처리하기 어렵다.

```python
import secrets
secrets.token_hex(16)
```

```python
import secrets as sec
sec.token_hex(16)
```

```python
from secrets import token_hex

token_hex(16)
```

```python
from secrets import token_hex as make_token

make_token(16)
```

따라서 Core에는 최소한의 Import/Alias Resolver를 둔다.

MVP 지원 범위:

- `import module`
- `import module as alias`
- `from module import symbol`
- `from module import symbol as alias`

Python name binding 전체를 완벽하게 해결하려 하지 않는다.

확실하지 않은 경우 탐지하지 않는다.

---

# 20. JSON 결과 계약

JSON은 GUI의 부가 기능이지만, 테스트 및 향후 연동을 위한 **stable machine artifact**로 사용한다.

예시:

```json
{
  "schema_version": "1.0",
  "tool_version": "0.1.0",
  "target": "sample.py",
  "status": "GOOD_PATTERNS_FOUND",
  "summary": {
    "findings": 2,
    "categories": 2
  },
  "findings": [
    {
      "rule_id": "GOOD001",
      "name": "Parameterized SQL Query",
      "category": "injection-prevention",
      "confidence": "HIGH",
      "line": 12,
      "column": 4,
      "evidence": "cursor.execute(\"SELECT * FROM users WHERE id = ?\", (user_id,))",
      "message": "SQL 문장과 데이터를 분리하여 전달하고 있습니다."
    }
  ],
  "warnings": []
}
```

JSON 요구사항:

- `schema_version` 포함
- 동일 입력에 동일한 의미의 필드 사용
- Finding은 결정적으로 정렬
- GUI 문구 변경이 JSON 구조를 불필요하게 변경시키지 않아야 함
- UTF-8로 저장

---

# 21. 오류 처리 요구사항

GUI 프로그램은 사용자에게 Python traceback을 그대로 보여주지 않는다.

## 21.1 파일 미선택

```text
분석할 Python 파일을 먼저 선택해주세요.
```

---

## 21.2 잘못된 확장자

```text
현재 MVP는 .py 파일만 분석할 수 있습니다.
```

---

## 21.3 존재하지 않는 파일

```text
선택한 파일을 찾을 수 없습니다.
```

---

## 21.4 파일 읽기 실패

```text
파일을 읽을 수 없습니다.
파일 권한 또는 인코딩을 확인해주세요.
```

---

## 21.5 SyntaxError

예시:

```text
Python 문법 오류로 분석할 수 없습니다.
Line 17: invalid syntax
```

GUI는 ERROR 상태가 되지만 프로그램 자체는 계속 사용할 수 있어야 한다.

사용자는 다시 다른 파일을 선택하여 분석할 수 있다.

---

# 22. 보안 불변조건 테스트

가장 중요한 자동 테스트 중 하나는 **분석 대상 코드가 절대 실행되지 않는다는 것**을 검증하는 것이다.

예를 들어 fixture 안에 다음 코드를 넣는다.

```python
from pathlib import Path

Path("SHOULD_NOT_EXIST.txt").write_text("executed")
```

이 파일을 착한코드검거단으로 분석한 뒤에도 해당 파일이 생성되지 않아야 한다.

즉,

```text
scan(target.py)
→ SHOULD_NOT_EXIST.txt가 존재하지 않음
```

을 자동 테스트로 고정한다.

이 테스트는 Harness Engineering 관점에서도 중요한 **기계적으로 검증 가능한 프로젝트 불변조건**이다.

---

# 23. Rule 완료 조건

새 Rule 하나는 코드만 작성했다고 완료된 것이 아니다.

각 Rule은 최소 다음 세트가 있어야 한다.

```text
1. Rule 구현
2. Positive fixture
3. Negative fixture
4. Unit test
5. Rule 설명 문서
```

예:

```text
GOOD002 구현
+ good_secrets.py
+ bad_random_for_token.py
+ test_good002.py
+ docs/rules.md 설명
```

이 조건을 만족하지 않으면 해당 Rule은 완료로 인정하지 않는다.

---

# 24. 테스트 전략

테스트는 GUI 테스트만으로 구성하지 않는다.

핵심 분석 엔진을 GUI 없이 테스트 가능하게 만든다.

## 24.1 Unit Test

대상:

- Import Resolver
- 각 Rule
- Finding 생성
- Sorting
- JSON serialization

---

## 24.2 Positive Fixture Test

착한코드가 있는 파일이 정확한 Rule로 탐지되는지 확인한다.

---

## 24.3 Negative Fixture Test

비슷해 보이지만 안전한 패턴이 아닌 코드를 잘못 탐지하지 않는지 확인한다.

예:

```python
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

이 코드를 `GOOD001`로 탐지해서는 안 된다.

---

## 24.4 No-Execution Test

대상 소스가 실행되지 않는지 검증한다.

---

## 24.5 Golden JSON Test

정해진 sample input의 JSON 결과를 golden file과 비교한다.

이를 통해 여러 Codex 작업 후에도 output contract가 무심코 깨지는 것을 방지한다.

---

## 24.6 GUI Smoke Test

GUI는 최소 다음을 사람이 직접 확인한다.

```text
앱 실행
→ 파일 선택
→ 분석 실행
→ 결과 표시
→ 결과 선택
→ 상세 보기
→ JSON 저장
→ 다른 파일 재분석
```

4일 MVP에서는 복잡한 GUI 자동화 프레임워크 도입을 필수 요구사항으로 두지 않는다.

---

# 25. UX 문구 원칙

프로그램 콘셉트는 재미있게 유지하되 보안 의미를 과장하지 않는다.

좋은 예:

```text
착한코드 4건 검거!

GOOD002 — 보안용 난수 사용
Line 20에서 secrets.token_urlsafe() 사용을 확인했습니다.
```

나쁜 예:

```text
완벽하게 안전한 코드입니다!
해킹 불가능!
보안 점수 100점!
```

---

# 26. 프로젝트 폴더 구조

권장 구조:

```text
good-code-hunter/
├── app.py
├── goodcode/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── scanner.py
│   │   ├── models.py
│   │   ├── import_resolver.py
│   │   └── service.py
│   │
│   ├── rules/
│   │   ├── base.py
│   │   ├── sql.py
│   │   ├── crypto.py
│   │   ├── subprocess_rule.py
│   │   ├── yaml_rule.py
│   │   ├── tls.py
│   │   └── tempfile_rule.py
│   │
│   ├── gui/
│   │   ├── main_window.py
│   │   ├── result_view.py
│   │   └── dialogs.py
│   │
│   └── exporters/
│       └── json_exporter.py
│
├── tests/
│   ├── fixtures/
│   │   ├── positive/
│   │   └── negative/
│   ├── golden/
│   └── test_*.py
│
├── examples/
├── docs/
│   └── rules.md
│
├── PRD.md
├── AGENTS.md
├── plan.md
├── pyproject.toml
├── requirements-dev.txt
└── README.md
```

실제 구현 과정에서 작은 파일을 합칠 수는 있다.

하지만 다음 모듈 경계는 유지한다.

```text
GUI
Application Service
Scanner/Core
Rules
Models
Exporter
Tests
```

---

# 27. Harness Engineering을 위한 제품 구조 원칙

이 프로젝트에서 Harness Engineering은 단순히 “4명이 Codex를 사용한다”는 뜻이 아니다.

Codex가 각자 독립적으로 작업해도 전체 프로젝트가 망가지지 않도록 **명확한 환경, 계약, 검증 수단을 저장소 안에 제공하는 것**이 핵심이다.

PRD 단계에서 다음 원칙을 고정한다.

## 27.1 문서가 기준이다

```text
PRD.md
→ 무엇을 만들 것인가

AGENTS.md
→ 에이전트가 어떤 규칙으로 작업할 것인가

plan.md
→ 누가 무엇을 어떤 순서로 구현할 것인가
```

Codex는 문서와 다른 방향으로 임의의 기능을 확장하지 않는다.

---

## 27.2 인터페이스를 먼저 고정한다

병렬 작업의 가장 큰 위험은 각자 다른 형태의 데이터를 만드는 것이다.

따라서 구현 초기에 다음을 고정한다.

```text
Finding
ScanResult
Rule interface
Scan service interface
JSON contract
```

---

## 27.3 기계가 확인할 수 있는 완료 조건을 만든다

사람이 “대충 되는 것 같다”고 판단하는 대신 다음 명령으로 상태를 확인할 수 있어야 한다.

예시:

```bash
pytest
ruff check .
```

빌드 단계에서는 PyInstaller build도 자동화 가능한 명령으로 고정한다.

---

## 27.4 Codex가 자신의 작업을 검증할 수 있어야 한다

각 작업은 가능하면 다음 루프를 따른다.

```text
문서 읽기
→ 담당 범위 확인
→ 코드 수정
→ 관련 테스트 작성
→ 테스트 실행
→ lint 실행
→ 실패 수정
→ 완료 조건 확인
→ commit / PR
```

세부 행동 규칙은 `AGENTS.md`에서 정의한다.

---

# 28. 병렬 개발을 고려한 경계

`plan.md`에서는 4명이 동시에 작업할 수 있도록 서로 겹치지 않는 작업 영역을 배정한다.

PRD에서는 이를 가능하게 하기 위해 다음 경계를 제공한다.

```text
영역 A: GUI
영역 B: Core / Scanner / Model / Resolver
영역 C: Security Rules
영역 D: Test / Export / Build / Integration
```

단, 실제 담당자는 `plan.md`에서 확정한다.

가장 먼저 Core contract를 고정한 뒤 각 영역을 병렬화한다.

---

# 29. Build / 배포 요구사항

MVP 최종 사용자는 개발 환경을 구성하지 않고도 프로그램을 실행할 수 있는 형태가 이상적이다.

기본 목표 플랫폼은 **Windows**로 한다.

PyInstaller를 사용하여 다음 형태의 빌드를 우선한다.

```text
dist/
└── GoodCodeHunter/
    └── GoodCodeHunter.exe
```

MVP에서는 `--onefile`보다 문제가 발생할 가능성이 적은 **onedir 형태를 기본 빌드 목표**로 한다.

시간이 남고 안정적으로 동작하면 onefile 패키징을 추가할 수 있다.

빌드 후 반드시 다음 Smoke Test를 수행한다.

```text
배포 폴더의 exe 실행
→ Python 파일 선택
→ 분석
→ Finding 표시
→ JSON 저장
→ 앱 종료
```

---

# 30. README 최소 요구사항

최종 README에는 최소 다음 내용이 있어야 한다.

- 프로젝트 소개
- 스크린샷 또는 실행 GIF 1개 이상
- 주요 기능
- 탐지 규칙 목록
- 개발 환경에서 실행하는 방법
- 빌드 방법
- 결과 해석 방법
- 한계점
- 팀원 역할
- Harness Engineering 적용 방식 요약

README는 상세 개발 규칙을 저장하는 장소가 아니다.

상세 기준은 PRD / AGENTS / plan을 참조한다.

---

# 31. 4일 MVP 우선순위

## Day 1 종료 시 반드시 존재해야 하는 것

```text
프로젝트 skeleton
Finding / ScanResult 모델
Rule interface
Scanner 기본 구조
GUI 창 실행
파일 선택 기능
기본 테스트 환경
```

## Day 2 종료 목표

```text
P0 Rule 대부분 구현
Core scanner → Finding 반환 가능
GUI → Scan service 호출 가능
positive / negative fixture 증가
```

## Day 3 종료 목표

```text
GUI 결과 table
Finding detail view
오류 처리
JSON export
전체 P0 Rule 통합
Golden test
No-Execution test
```

## Day 4 종료 목표

```text
전체 통합
regression test
GUI smoke test
PyInstaller build
README
데모 sample
발표용 시나리오
```

세부 담당자와 병렬 작업 순서는 `plan.md`에서 확정한다.

---

# 32. MVP Demo Scenario

발표 시 아래 흐름이 1~2분 안에 자연스럽게 진행되어야 한다.

## Step 1 — 프로그램 실행

`착한코드검거단` GUI가 열린다.

## Step 2 — Python 파일 선택

시큐어 코딩 패턴이 여러 개 포함된 `demo_good.py`를 선택한다.

## Step 3 — 검거 시작

`착한코드 검거 시작` 버튼을 클릭한다.

## Step 4 — 결과 확인

예:

```text
착한코드 4건 검거
카테고리 4개
```

결과 테이블에 GOOD001, GOOD002 등이 나타난다.

## Step 5 — 상세 근거 확인

GOOD002 항목을 클릭한다.

화면에 다음이 표시된다.

```text
Line 20

token = secrets.token_urlsafe(32)

보안용 난수 생성에 적합한 secrets 모듈을 사용하고 있습니다.
```

## Step 6 — 잘못된 코드와 비교

`demo_negative.py`를 분석한다.

좋은 패턴으로 오탐하지 않는 모습을 보여준다.

## Step 7 — JSON 저장

탐지 결과를 JSON으로 저장한다.

## Step 8 — 프로젝트 메시지 전달

```text
“우리는 취약점이 없다는 것을 보증하는 도구를 만든 것이 아니라,
코드 안에서 확인 가능한 좋은 보안 습관을 찾아 설명하는 도구를 만들었습니다.”
```

---

# 33. 최종 Definition of Done

MVP는 다음 체크리스트를 전부 만족해야 한다.

## Product

- [ ] GUI가 정상 실행된다.
- [ ] `.py` 파일 하나를 선택할 수 있다.
- [ ] 버튼 한 번으로 분석할 수 있다.
- [ ] 대상 코드를 실행하지 않는다.
- [ ] P0 Rule 6개가 구현되어 있다.
- [ ] Finding 목록이 GUI에 표시된다.
- [ ] Finding 선택 시 상세 근거가 표시된다.
- [ ] 결과 없음 상태가 정상 처리된다.
- [ ] SyntaxError가 GUI에서 정상 처리된다.
- [ ] JSON 결과 저장이 가능하다.
- [ ] 보안 보증이 아니라는 Disclaimer가 있다.

## Quality

- [ ] 각 Rule에 positive fixture가 있다.
- [ ] 각 Rule에 negative fixture가 있다.
- [ ] `pytest` 전체 통과
- [ ] `ruff check .` 통과
- [ ] No-Execution invariant test 통과
- [ ] Golden JSON test 통과
- [ ] 동일 입력 결과가 결정적이다.

## Integration

- [ ] 4명의 작업이 main 브랜치에 병합되어 있다.
- [ ] main에서 전체 regression test가 통과한다.
- [ ] GUI smoke test를 수행했다.

## Build / Delivery

- [ ] PyInstaller로 Windows 배포 빌드를 만들었다.
- [ ] 빌드 산출물에서 GUI가 실행된다.
- [ ] 배포 버전에서 실제 `.py` 분석이 된다.
- [ ] README가 작성되어 있다.
- [ ] demo sample 파일이 준비되어 있다.

---

# 34. 프로젝트의 핵심 메시지

착한코드검거단 MVP의 가치는 “수많은 보안 기능을 넣는 것”에 있지 않다.

핵심은 다음 네 가지다.

```text
1. Python 코드를 실행하지 않고 정적으로 분석한다.
2. 확실한 시큐어 코딩 패턴만 착한코드로 탐지한다.
3. 사용자가 GUI에서 근거와 이유를 바로 이해할 수 있다.
4. 4명의 Codex가 동일한 문서·계약·테스트를 기반으로 병렬 개발한다.
```

4일 안에 이 네 가지를 안정적으로 완성하는 것을 MVP 최우선 목표로 한다.

---

# 35. 다음 문서

이 PRD가 확정되면 다음 순서로 진행한다.

```text
1. PRD.md 확정
        ↓
2. AGENTS.md 작성
   - Codex 공통 행동 규칙
   - 수정 금지 영역
   - 테스트 의무
   - 작업 시작/종료 절차
   - Git/PR 규칙
        ↓
3. plan.md 작성
   - 4명 역할 분담
   - dependency 정의
   - Day 1~4 실행 순서
   - branch / integration 전략
        ↓
4. 구현
        ↓
5. 테스트
        ↓
6. 빌드 / 배포 / 데모
```

이 문서의 범위를 벗어나는 기능을 추가하려면 먼저 PRD 변경 여부를 팀에서 합의한다.
