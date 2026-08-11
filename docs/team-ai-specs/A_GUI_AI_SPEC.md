# 착한코드검거단 A 담당 AI 개발 명세서

## 담당 정보

- 담당자: 차아미
- GitHub: `AmieCha`
- 담당 영역: GUI
- 작업 브랜치: `feat/gui`
- 현재 PR: https://github.com/guswl03/good-code-hunters/pull/12

## AI에게 그대로 전달할 명령

착한코드검거단 저장소의 `PRD.md`, `AGENTS.md`, `plan.md`와 PR #12를 먼저 전부 확인해라. 기존 GUI를 새로 만들지 말고 현재 구현에서 아래 부족한 부분만 수정해라.

### 공통 개발 원칙

1. 대상 `.py` 파일은 읽기와 AST 분석만 하며 절대 실행하지 않는다.
2. 기존 `Finding`, `ScanResult`, `scan_file()` 계약을 임의로 변경하지 않는다.
3. GUI는 `scan_file(path) -> ScanResult`만 사용한다.
4. GUI에서 개별 GOOD001~006 Rule을 직접 import하거나 실행하지 않는다.
5. 기존 ZIP, PRD, AGENTS, plan 파일을 삭제·이동·변경하지 않는다.
6. `main`에 직접 push하거나 merge하지 않는다.
7. 명세에 없는 보안 점수, SAFE/UNSAFE 인증, 로그인, DB, 웹 기능을 추가하지 않는다.
8. 새 주요 코드 블록에는 다음 형식의 주석을 작성한다.

```python
# ===
# 만든 이유: 이 코드가 필요한 이유
# 코드 설명: 이 코드가 수행하는 동작
# ===
```

### 현재 부족한 부분

- MVP 명세에 없는 랭킹, 티어, 가상 사용자 순위 기능이 포함되어 있다.
- 예상하지 못한 분석 예외가 발생하면 GUI가 종료될 가능성이 있다.
- 로고가 현재 작업 디렉터리에 의존하므로 exe 실행 환경에서 표시되지 않을 수 있다.
- GUI가 JSON을 직접 직렬화하여 D의 JSON Exporter와 계약이 달라질 수 있다.
- 현재 GUI 테스트는 가짜 ScanResult 중심이며 실제 전체 Rule 통합은 검증하지 않았다.

### 필수 작업

- [ ] `랭킹`, `티어`, 가상 사용자 순위 메뉴와 화면을 MVP에서 제거하거나 숨긴다.
- [ ] `.py 선택 → 분석 → 결과 목록 → 상세 확인 → JSON 저장` 흐름을 중심으로 유지한다.
- [ ] 분석 중 예상하지 못한 예외가 발생해도 창이 종료되지 않게 한다.
- [ ] Python traceback을 사용자 화면에 그대로 표시하지 않는다.
- [ ] 오류 후에도 새 파일을 선택하고 다시 분석할 수 있게 한다.
- [ ] Finding 목록에 Rule ID, 규칙 이름, Category, Line을 표시한다.
- [ ] Finding 상세에 파일명, 라인, 근거 코드, 설명을 표시한다.
- [ ] 결과 있음, 결과 없음, 문법 오류, 읽기 오류 상태를 구분한다.
- [ ] 분석 결과가 없으면 JSON 저장 버튼을 비활성화한다.
- [ ] 소스 실행과 PyInstaller 실행 모두에서 로고를 찾을 수 있도록 리소스 경로를 정리한다.
- [ ] 위 동작에 대한 GUI 테스트를 추가한다.

### JSON 작업 경계

JSON 계약과 실제 파일 저장은 D 담당이다. A 브랜치에서 D의 PR을 무리하게 병합하지 않는다. 저장 버튼과 저장 위치 선택 UI는 유지하되, 최종 통합 시 D가 `export_scan_result(result, path)`로 연결할 수 있도록 GUI 코드를 단순하게 유지한다.

### 수정 금지 영역

- Core Scanner와 Model
- Rule Registry
- GOOD001~006 탐지 로직
- JSON 계약 정의
- PyInstaller 최종 빌드 설정

### 완료 조건

- [ ] GUI 관련 pytest 통과
- [ ] A 담당 파일 ruff 통과
- [ ] 파일 선택과 상태별 화면 수동 확인
- [ ] 변경 파일과 테스트 결과를 PR #12 설명에 기록
- [ ] 완료 후 PR #12를 `Ready for review`로 변경

### 완료 보고 형식

```text
담당자: 차아미
브랜치: feat/gui
완료한 항목:
변경한 파일:
실행한 테스트:
테스트 결과:
남은 작업:
발견한 문제:
커밋 SHA:
PR 주소: https://github.com/guswl03/good-code-hunters/pull/12
```
