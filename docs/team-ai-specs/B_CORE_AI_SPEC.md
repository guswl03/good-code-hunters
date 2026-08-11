# 착한코드검거단 B 담당 AI 개발 명세서

## 담당 정보

- 담당자: 박정빈
- GitHub: `jung213`
- 담당 영역: Core / Scanner / Model / Resolver
- 권장 브랜치: `fix/core-finding-file`

## AI에게 그대로 전달할 명령

착한코드검거단 저장소의 `PRD.md`, `AGENTS.md`, `plan.md`, 최신 `main`과 열린 PR #10, #11, #12를 먼저 확인해라. 기존 Core를 다시 만들지 말고 실제 분석 파일 경로 전달 문제를 최소 수정으로 해결해라.

### 공통 개발 원칙

1. 대상 `.py` 파일은 읽기와 AST 분석만 하며 절대 실행하지 않는다.
2. 기존 `Finding`, `ScanResult`, `scan_file()` 외부 계약을 변경하지 않는다.
3. 담당 영역 밖의 코드를 대규모로 수정하지 않는다.
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

Registry는 고정된 Rule 객체를 재사용하고 Rule 생성자의 `target_file` 기본값은 빈 문자열이다. Scanner는 실제 분석 경로를 알고 있지만 Rule 결과의 `Finding.file`에 해당 경로가 정확히 전달된다는 보장이 없다. 여러 파일을 연속 분석하면 빈 경로나 이전 경로가 남을 수 있다.

### 필수 작업

- [ ] `scan_file(path)`로 분석한 현재 경로가 모든 `Finding.file`에 들어가게 한다.
- [ ] Rule이 빈 경로나 다른 경로를 반환해도 최종 결과는 현재 분석 경로를 사용하게 한다.
- [ ] 권장 구현 위치는 모든 Rule 결과가 모이는 Core Scanner이다.
- [ ] frozen `Finding`을 직접 변경하지 말고 안전한 복사 방식을 사용한다.
- [ ] Finding 정렬 순서 `line → column → rule_id`를 유지한다.
- [ ] `GOOD_PATTERNS_FOUND`, `NO_GOOD_PATTERNS_FOUND`, `PARSE_ERROR`, `READ_ERROR` 계약을 유지한다.
- [ ] 실제 임시 `.py` 파일을 이용한 경로 전달 테스트를 추가한다.
- [ ] 서로 다른 파일 두 개를 연속 분석해도 경로가 섞이지 않는 테스트를 추가한다.
- [ ] Finding이 없는 파일, 문법 오류 파일, 읽을 수 없는 파일의 기존 동작을 확인한다.
- [ ] 대상 파일이 실행되지 않는 회귀 테스트를 유지한다.

### 수정 금지 영역

- GOOD001~006 탐지 기준
- GUI
- JSON Exporter
- Finding 또는 ScanResult 필드 삭제와 이름 변경
- Rule별 임시 전역 경로 저장

### 완료 조건

- [ ] 실제 파일 경로 테스트 통과
- [ ] 연속 파일 분석 테스트 통과
- [ ] 전체 pytest 통과
- [ ] Core 담당 파일 ruff 통과
- [ ] 별도 PR 생성
- [ ] D에게 브랜치명, PR 주소, 커밋 SHA 전달

### 완료 보고 형식

```text
담당자: 박정빈
브랜치: fix/core-finding-file
선택한 경로 전달 방식:
완료한 항목:
변경한 파일:
실행한 테스트:
테스트 결과:
계약 변경 여부: 없음
남은 작업:
발견한 문제:
커밋 SHA:
PR 주소:
```
