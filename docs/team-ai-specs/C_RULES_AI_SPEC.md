# 착한코드검거단 C 담당 AI 개발 명세서

## 담당 정보

- 담당자: 전상현
- GitHub: `gu1trh2ro`
- 담당 영역: GOOD001~003 Rule Pack A
- 작업 브랜치: `feat/rules-a`
- 현재 PR: https://github.com/guswl03/good-code-hunters/pull/11

## AI에게 그대로 전달할 명령

착한코드검거단 저장소의 `PRD.md`, `AGENTS.md`, `plan.md`와 PR #11을 먼저 확인해라. GOOD001~003을 새로 작성하지 말고 현재 구현의 통합 준비 상태를 검증한 뒤 실제 문제가 있는 부분만 최소 수정해라.

### 담당 규칙

- GOOD001: Parameterized SQL Query
- GOOD002: Secure Randomness
- GOOD003: Password Hashing

### 공통 개발 원칙

1. 대상 `.py` 파일은 읽기와 AST 분석만 하며 절대 실행하지 않는다.
2. 기존 Core 계약을 임의로 변경하지 않는다.
3. 탐지 범위를 PRD보다 과도하게 넓히지 않는다.
4. 기존 ZIP과 명세 파일을 변경하지 않는다.
5. `main`에 직접 push하거나 merge하지 않는다.
6. 새 주요 코드 블록에는 다음 형식의 주석을 작성한다.

```python
# ===
# 만든 이유: 이 코드가 필요한 이유
# 코드 설명: 이 코드가 수행하는 동작
# ===
```

### 현재 부족한 부분

GOOD001~003 단위 구현은 완료됐지만 B의 실제 `Finding.file` 전달 수정과 D의 Registry 연결을 포함한 전체 `scan_file()` 통합은 검증되지 않았다. 현재 PR의 통과 결과만으로 실제 GUI에서 세 규칙이 실행된다고 볼 수 없다.

### 필수 작업

- [ ] 각 규칙의 Positive Fixture에서 Finding이 생성되는지 확인한다.
- [ ] 각 규칙의 Negative Fixture에서 Finding이 생성되지 않는지 확인한다.
- [ ] 직접 import와 별칭 import 처리가 명세와 일치하는지 확인한다.
- [ ] 동일 코드에서 Finding이 불필요하게 중복 생성되지 않는지 확인한다.
- [ ] `line`, `column`, `evidence`, `message`가 실제 코드와 일치하는지 확인한다.
- [ ] Rule 문서와 실제 탐지 조건이 일치하는지 확인한다.
- [ ] B 수정 후 GOOD001~003의 `Finding.file`에 실제 경로가 들어가는지 확인한다.
- [ ] D가 Registry에 연결한 뒤 `scan_file()`에서 세 규칙이 실행되는지 확인한다.
- [ ] 통합 실패 원인이 Rule 구현일 때만 `feat/rules-a`를 수정한다.
- [ ] 문제가 없다면 불필요한 코드를 추가하지 말고 검증 결과만 보고한다.

### 수정 금지 영역

- Registry 기본 초기화
- Core Model과 Scanner
- GUI
- JSON Exporter
- GOOD004~006
- 명세에 없는 추가 Rule

### 완료 조건

- [ ] GOOD001~003 단위 테스트 통과
- [ ] C 담당 파일 ruff 통과
- [ ] D 통합 브랜치에서 세 Rule 호출 확인
- [ ] 문제가 있으면 최소 수정 커밋 생성
- [ ] 문제가 없으면 테스트 결과를 PR #11에 기록
- [ ] PR #11을 D 통합 전에 `main`에 직접 병합하지 않음

### 완료 보고 형식

```text
담당자: 전상현
브랜치: feat/rules-a
검증한 규칙: GOOD001, GOOD002, GOOD003
완료한 항목:
변경한 파일:
실행한 테스트:
테스트 결과:
통합 테스트 결과:
남은 작업:
발견한 문제:
커밋 SHA:
PR 주소: https://github.com/guswl03/good-code-hunters/pull/11
```
