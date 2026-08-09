# 팀원 D 실행 계획

> 기간: 9일~11일 개발, 12일 데모 영상  
> 브랜치: `feat/rules-b-integration`  
> 목표: P0 Rule B, JSON Export, 통합 검증, Windows 빌드 완성

## 0. 의존 관계

```text
팀원 B의 공통 Contract가 main에 병합
        ↓
GOOD004~006 및 Exporter 병렬 개발
        ↓
팀원 B Core 완성 + 팀원 C Rule A 완성
        ↓
integration/mvp 순차 통합
        ↓
GUI 실제 연결
        ↓
전체 회귀 테스트
        ↓
PyInstaller 빌드
```

개별 Rule과 Exporter는 공통 Contract가 확정되면 Core 전체 완성을 기다리지 않고 개발한다. 실제 E2E 검증과 빌드는 Core, P0 Rules, GUI가 연결된 뒤 진행한다.

## 1. 시작 준비

```powershell
git switch main
git pull origin main
git switch -c feat/rules-b-integration
```

확인할 공통 API:

- `Finding`
- `ScanResult`
- `Rule.check(...)`
- `ImportAliasContext.resolve_name(...)`
- `ImportAliasContext.resolve_attribute_chain(...)`
- `SourceHelper.line_text(...)`
- `SourceHelper.column_for_node(...)`
- `SourceHelper.snippet_for_node(...)`
- Rule registry 사용 방식

## 2. 9일 — Rule 기반 완성

### GOOD004

1. Positive/Negative fixture 작성
2. direct module import 탐지
3. module alias 탐지
4. from-import와 symbol alias 탐지
5. `==` 비교 Negative 확인
6. 단위 테스트 실행

### GOOD005

1. 지원할 subprocess API 목록 고정
2. list/tuple 첫 인자 탐지
3. `shell=True` 제외
4. 문자열 명령 Negative 확인
5. alias 탐지
6. 단위 테스트 실행

### GOOD006

1. `yaml.safe_load` 탐지
2. module/symbol alias 탐지
3. `yaml.load` Negative 확인
4. 실제 yaml import 없이 동작 확인
5. 단위 테스트 실행

### 9일 자정 Gate

- [ ] GOOD004~006 구현 파일 존재
- [ ] 각 Rule Positive/Negative fixture 존재
- [ ] 각 Rule 단위 테스트 존재
- [ ] 관련 테스트 통과
- [ ] 담당 외 Core/GUI 파일 수정 없음
- [ ] 개발 현황 공유

## 3. 10일 — Rule 완료 + JSON Export

### 오전

- alias/오탐 회귀 케이스 보강
- line, column, evidence 정확성 확인
- `docs/rules.md`에 GOOD004~006 설명 작성
- 전체 Rule 테스트 실행

### 오후

JSON Exporter 구현:

```text
ScanResult 입력
→ summary 계산
→ UTF-8 JSON 저장
→ stable machine artifact 생성
```

Exporter 테스트:

- Finding 존재 결과
- Finding 없는 결과
- Warning/Error 결과
- 한글 message
- 결정적 JSON 구조

Golden JSON 초안을 만든다. GUI 위젯과 연결하지 않고 `ScanResult`만 소비한다.

### 10일 자정 Gate

- [ ] GOOD004~006 Rule 완료 계약 충족
- [ ] JSON Exporter 및 단위 테스트 완료
- [ ] Golden JSON 초안 완료
- [ ] `pytest -q` 통과
- [ ] `ruff check .` 통과
- [ ] 개인 브랜치 push 및 PR 생성
- [ ] 개발 현황 공유

## 4. 11일 — 통합·회귀·빌드

### 통합 브랜치

최신 `main`에서 생성한다.

```powershell
git switch main
git pull origin main
git switch -c integration/mvp
git push -u origin integration/mvp
```

### 순차 통합

```text
1. feat/core
2. feat/rules-a
3. feat/rules-b-integration
4. feat/gui
```

각 병합 후:

```powershell
pytest -q
ruff check .
```

실패하면 실패한 단계, 명령, traceback, 예상/실제 결과를 기록하고 원래 담당자에게 수정 요청한다.

### 전체 회귀 테스트

- P0 Rule 6개 Positive/Negative
- Import/Alias Resolver
- Finding 정렬
- Parse/Read Error
- No-Execution
- Golden JSON
- JSON Export
- GUI와 실제 `scan_file()` 연결

### GUI Smoke Test

```text
앱 실행
→ demo_good.py 선택
→ 분석
→ Finding 목록과 상세 확인
→ demo_empty.py 확인
→ demo_syntax_error.py 확인
→ JSON 저장
→ 다른 파일 재분석
```

### PyInstaller 빌드

```powershell
pyinstaller --noconfirm --windowed --onedir --name GoodCodeHunter app.py
```

배포본에서 GUI Smoke Test를 다시 수행한다.

### 11일 자정 Final Gate

- [ ] `pytest -q` 전체 통과
- [ ] `ruff check .` 통과
- [ ] No-Execution 통과
- [ ] Golden JSON 통과
- [ ] GUI Smoke Test 통과
- [ ] PyInstaller onedir 빌드 성공
- [ ] exe에서 실제 `.py` 분석 성공
- [ ] exe에서 JSON 저장 성공
- [ ] `integration/mvp → main` PR 준비
- [ ] 실제 결과를 포함한 개발 현황 공유

## 5. 12일 — 데모 영상 지원

팀원 D는 확정된 배포본과 데모 파일을 제공한다.

데모 순서:

```text
GoodCodeHunter.exe 실행
→ demo_good.py 분석
→ GOOD004~006을 포함한 Finding 상세 확인
→ negative/empty 파일 비교
→ JSON 저장
→ No Execution과 결과 한계 설명
```

촬영 직전 기능을 추가하지 않고 11일에 검증된 빌드를 사용한다.

## 6. 개인 PR 체크리스트

- [ ] 담당 파일만 변경
- [ ] GOOD004~006 완료 계약 충족
- [ ] JSON Export 테스트 포함
- [ ] 공통 Contract 변경 없음
- [ ] 테스트 결과 기록
- [ ] lint 결과 기록
- [ ] 남은 문제 기록
- [ ] 다른 팀원이 재현할 실행 방법 기록

## 7. Codex 시작 프롬프트

```text
루트의 PRD.md, AGENTS.md, plan.md와 harness/team-d의 PRD.md, AGENTS.md, plan.md를 모두 읽어라.
너는 팀원 D이며 feat/rules-b-integration 브랜치에서 GOOD004~GOOD006, JSON Export, 통합 테스트, PyInstaller 빌드만 담당한다.
공통 Finding, ScanResult, Rule interface, Alias Resolver를 재정의하지 마라.
대상 Python 파일을 실행하거나 import하지 마라.
각 Rule에 Positive/Negative fixture와 테스트를 작성하고 관련 테스트, 전체 pytest, ruff를 실행하라.
담당 밖 파일 변경이 필요하면 임의로 수정하지 말고 변경 필요성과 Owner를 보고하라.
```
