# 착한코드검거단 협업·통합 가이드

이 문서는 네 명이 각자 담당 기능을 개발한 뒤 실제로 함께 동작하는지 검증하고, 검증된 결과만 `main`에 반영하는 절차를 정의한다.

## 핵심 원칙

```text
개인 브랜치에서 개발·단위 테스트
→ Pull Request 생성
→ integration/mvp에서 순차 통합
→ 전체 자동 테스트·GUI·빌드 확인
→ integration/mvp를 main으로 Pull Request
→ 팀원 검토 후 병합
```

`main`은 시험장이 아니다. 전체 검증이 끝난 안정적인 상태만 보관한다.

## 브랜치 구성

| 브랜치 | 담당 | 목적 |
|---|---|---|
| `main` | 전원 | 검증된 기준 버전 |
| `chore/foundation-contract` | 팀원 B, 전원 검토 | 공통 모델과 인터페이스 동결 |
| `feat/gui` | 팀원 A | GUI / UX |
| `feat/core` | 팀원 B | Core / AST / 공통 계약 |
| `feat/rules-a` | 팀원 C | GOOD001~GOOD003 |
| `feat/rules-b-integration` | 팀원 D | GOOD004~GOOD006 / Export / Build |
| `integration/mvp` | 팀원 D 주도, 전원 참여 | 네 작업의 통합 검증 |

## 1. 공통 기반 확정

팀원 B가 `chore/foundation-contract`에서 다음을 먼저 만든다.

- 프로젝트 기본 폴더 구조
- `Finding`
- `ScanResult`
- `scan_file(file_path) -> ScanResult`
- Rule interface
- 테스트 및 lint 기본 환경

네 명이 계약을 검토하고 테스트한 다음 이 PR만 먼저 `main`에 병합한다. 이후 모든 팀원은 같은 `main`에서 자신의 feature branch를 생성한다.

```powershell
git switch main
git pull origin main
git switch -c feat/gui
```

브랜치 이름은 각자의 담당 브랜치로 바꾼다.

## 2. 각자 개발하고 자기 영역에서 검증

모든 팀원은 담당 파일만 수정한다. 작업 전 `PRD.md`, `AGENTS.md`, `plan.md`를 읽고 공통 Contract를 임의로 변경하지 않는다.

### 팀원 A — GUI

Core가 완성되기 전에는 실제 `ScanResult`와 같은 구조의 Mock을 사용한다.

확인 항목:

- 창 실행
- `.py` 파일 선택 및 선택 파일 표시
- 분석 버튼
- Finding 목록 및 상세 화면
- Empty / Error 상태
- JSON 저장 UI
- Disclaimer

최종 통합에서는 Mock-only 경로를 제거하고 실제 `scan_file()`을 연결한다.

### 팀원 B — Core

GUI 없이 테스트한다.

- 파일 읽기와 AST 파싱
- Import / Alias Resolver
- Rule 실행과 Finding 취합
- 결정적 정렬
- 오류 상태
- 대상 코드가 실행되지 않는지

### 팀원 C — Rule Pack A

GOOD001~GOOD003 각각에 다음 세트를 만든다.

```text
Rule 구현 + Positive fixture + Negative fixture + Unit test + 규칙 설명
```

### 팀원 D — Rule Pack B / Export / Build

GOOD004~GOOD006에 동일한 Rule 완료 세트를 만들고 JSON Export, Golden JSON, No-Execution, 빌드를 준비한다.

각자 최소 검증:

```powershell
pytest -q
ruff check .
```

## 3. 개인 Pull Request 생성

개인 브랜치의 테스트가 통과하면 담당 파일만 명시적으로 stage하여 push한다.

```powershell
git add 담당파일
git commit -m "feat(core): implement AST scanner"
git push -u origin feat/core
```

PR에는 다음을 기록한다.

```text
담당 영역
구현 내용
수정 파일
Contract 변경 여부
실행한 테스트와 결과
수동 확인 방법
남은 문제
담당 외 영역을 변경하지 않았는지
```

개인 PR은 검토 자료이며, 네 기능을 모두 검증하기 전에 `main`으로 곧바로 병합하지 않는다.

## 4. 통합 브랜치 생성

Day 3에 팀원 D가 최신 `main`에서 통합 브랜치를 만든다.

```powershell
git switch main
git pull origin main
git switch -c integration/mvp
git push -u origin integration/mvp
```

## 5. 하나씩 통합하고 매번 검사

권장 순서는 다음과 같다.

```text
feat/core
→ feat/rules-a
→ feat/rules-b-integration
→ feat/gui
```

한꺼번에 네 브랜치를 합치지 않는다. 하나를 합칠 때마다 테스트하여 실패 원인을 좁힌다.

```powershell
git switch integration/mvp
git merge origin/feat/core
pytest -q
ruff check .
```

통과한 경우에만 다음 브랜치를 병합하고 같은 검사를 반복한다.

## 6. 통합 실패 처리

실패하면 다음 중 무엇인지 먼저 분류한다.

- Contract 불일치
- 담당 기능의 실제 버그
- 테스트 기대값 오류
- Merge conflict
- 환경 또는 dependency 문제

통합 담당자가 다른 사람의 기능을 대신 대규모로 재작성하지 않는다. 원래 담당자가 자신의 feature branch에서 최소 수정하고 push한 뒤 통합 브랜치에 다시 반영한다.

공통 Contract 변경이 필요하면 네 명이 합의하고 관련 문서와 테스트를 먼저 수정한다.

## 7. 최종 통합 검증

### 자동 테스트

```powershell
pytest -q
ruff check .
```

필수 항목:

- 모든 Rule의 Positive / Negative Test
- No-Execution invariant
- Golden JSON
- Finding 결정적 정렬
- Import / Alias Resolver
- JSON serialization

### GUI Smoke Test

```powershell
python app.py
```

```text
앱 실행
→ .py 파일 선택
→ 분석
→ Finding 목록 및 상세 확인
→ JSON 저장
→ 다른 파일 재분석
→ Finding 없는 파일 확인
→ SyntaxError 파일 확인
```

### Windows 빌드 확인

```powershell
pyinstaller --noconfirm --windowed --onedir --name GoodCodeHunter app.py
```

`dist/GoodCodeHunter/GoodCodeHunter.exe`에서 GUI Smoke Test를 다시 수행한다.

## 8. main 반영

모든 검사가 통과한 경우에만 다음 최종 PR을 만든다.

```text
integration/mvp → main
```

최종 PR에 실제 결과를 기록한다.

```text
pytest -q: PASS
ruff check .: PASS
No-Execution: PASS
Golden JSON: PASS
GUI Smoke Test: PASS
PyInstaller Build: PASS
```

다른 팀원 최소 1명이 변경을 검토한 후 병합한다. 실패하거나 확인하지 않은 항목을 PASS로 적지 않는다.

## 매일 자정 현황 공유 형식

```text
담당 역할 / 브랜치
오늘 완료한 작업
변경 파일
실행한 테스트와 결과
현재 실제로 동작하는 범위
담당 외 영역 변경 여부
막힌 문제와 필요한 지원
내일 할 작업
```

## 최종 흐름

```text
main의 공통 계약
├─ feat/gui
├─ feat/core
├─ feat/rules-a
└─ feat/rules-b-integration
        ↓ 하나씩 병합·매번 테스트
integration/mvp
        ↓ 자동 테스트 + GUI Smoke Test + Windows 빌드
최종 Pull Request
        ↓ 팀원 검토·승인
main
```
