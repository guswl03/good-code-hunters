# 착한코드검거단 D 담당 AI 개발 명세서

## 담당 정보

- 담당자: 이현지
- GitHub: `guswl03`
- 담당 영역: GOOD004~006 / JSON / Test / Build / Integration
- 기존 작업 브랜치: `feat/d-integration-export`
- 기존 PR: https://github.com/guswl03/good-code-hunters/pull/10
- 최종 통합 브랜치: `integration/mvp`

## AI에게 그대로 전달할 명령

착한코드검거단 저장소의 `PRD.md`, `AGENTS.md`, `plan.md`, 최신 `main`, PR #10, #11, #12와 B의 Core 수정 PR을 먼저 전부 확인해라. 각 PR을 `main`에 개별 병합하지 말고 `integration/mvp`에서 전체 MVP를 통합해라.

### 공통 개발 원칙

1. 대상 `.py` 파일은 읽기와 AST 분석만 하며 절대 실행하지 않는다.
2. 기존 ZIP과 명세 파일을 삭제·이동·변경하지 않는다.
3. 명세에 없는 기능을 추가하지 않는다.
4. 보안 점수, 티어, SAFE/UNSAFE 인증, 로그인, DB, 웹 기능을 최종 MVP에 포함하지 않는다.
5. 기존 `Finding`, `ScanResult`, `scan_file()` 계약을 유지한다.
6. 최종 검증 전에는 `main`에 병합하지 않는다.
7. 새 주요 코드 블록에는 다음 형식의 주석을 작성한다.

```python
# ===
# 만든 이유: 이 코드가 필요한 이유
# 코드 설명: 이 코드가 수행하는 동작
# ===
```

### 현재 부족한 부분

- Registry가 비어 있어 실제 `scan_file()`에서 GOOD001~006이 자동 실행되지 않는다.
- B의 실제 `Finding.file` 경로 전달 수정이 필요하다.
- GUI가 D Exporter 대신 직접 JSON을 생성하여 PRD JSON 계약과 다르다.
- PR #10과 #12가 `.gitignore`를 각각 수정한다.
- 전체 Ruff 오류가 남아 있다.
- setuptools가 여러 최상위 폴더를 패키지로 인식해 설치가 실패한다.
- PyInstaller Windows 빌드와 빌드 산출물 테스트가 완료되지 않았다.
- 각 PR 테스트는 통과했더라도 세 PR을 합친 실제 통합 테스트는 없다.

### 통합 순서

1. 최신 `main`에서 `integration/mvp` 브랜치를 만든다.
2. B의 Core 경로 수정 브랜치를 통합한다.
3. C의 `feat/rules-a`를 통합한다.
4. D의 `feat/d-integration-export`를 통합한다.
5. A의 `feat/gui`를 통합한다.
6. 충돌을 해결하고 전체 테스트를 실행한다.
7. Windows 빌드까지 성공한 후 `integration/mvp → main` Draft PR을 만든다.

### Rule Registry 작업

- [ ] GOOD001~006 구현 클래스 이름과 계약을 확인한다.
- [ ] 여섯 Rule을 기본 Registry에 등록한다.
- [ ] 초기화를 여러 번 호출해도 중복 등록되지 않게 한다.
- [ ] GUI가 별도 등록 작업을 하지 않아도 `scan_file()`에서 여섯 Rule이 실행되게 한다.
- [ ] Finding 정렬과 실제 파일 경로를 확인한다.

### JSON 통합 작업

- [ ] GUI의 직접 `json.dumps(result.to_dict())` 사용을 제거한다.
- [ ] GUI 저장 버튼을 `export_scan_result(result, output_path)`에 연결한다.
- [ ] JSON에 `schema_version`, `tool_version`, `target`, `status`, `summary`, `findings`, `warnings`가 포함되는지 확인한다.
- [ ] Golden JSON 계약과 실제 저장 결과가 일치하는지 확인한다.
- [ ] 동일 결과의 JSON이 결정적으로 생성되는지 확인한다.
- [ ] UTF-8 한글 저장을 확인한다.

### 충돌과 품질 작업

- [ ] #10과 #12의 `.gitignore`를 합집합 형태로 정리한다.
- [ ] D Fixture에 남은 Ruff 오류를 수정한다.
- [ ] 최종 GUI에서 랭킹과 티어가 노출되지 않는지 확인한다.
- [ ] `pyproject.toml`이 `goodcode` 패키지만 탐색하도록 설정한다.
- [ ] 개발 의존성 설치가 성공하는지 확인한다.
- [ ] 전체 `pytest`를 통과시킨다.
- [ ] 전체 `ruff check .`를 통과시킨다.

### 필수 실제 테스트

- [ ] GOOD001 각각 탐지
- [ ] GOOD002 각각 탐지
- [ ] GOOD003 각각 탐지
- [ ] GOOD004 각각 탐지
- [ ] GOOD005 각각 탐지
- [ ] GOOD006 각각 탐지
- [ ] GOOD001~006이 모두 포함된 파일 분석
- [ ] Finding이 없는 정상 파일
- [ ] 문법 오류 파일
- [ ] 존재하지 않는 파일
- [ ] `.py`가 아닌 파일
- [ ] 대상 파일 코드가 실행되지 않는지 확인
- [ ] GUI 파일 선택부터 Finding 상세 표시까지 확인
- [ ] GUI JSON 저장 후 Golden 계약 확인

### Windows 빌드 작업

- [ ] PyInstaller onedir 설정 작성
- [ ] `app.py`를 앱 진입점으로 사용
- [ ] 로고를 빌드 리소스에 포함
- [ ] `GoodCodeHunter.exe` 생성 확인
- [ ] 저장소 밖 `dist` 폴더에서 exe 실행 확인
- [ ] exe에서 파일 선택, 분석, 상세 결과, JSON 저장 확인
- [ ] README에 실행 및 빌드 방법 기록

### 완료 조건

- [ ] GOOD001~006 자동 실행
- [ ] 모든 Finding 실제 파일 경로 정상
- [ ] GUI 결과 목록과 상세 정상
- [ ] JSON Golden 계약 정상
- [ ] 전체 pytest 통과
- [ ] 전체 ruff 통과
- [ ] PyInstaller 빌드 성공
- [ ] 빌드 산출물 Smoke Test 성공
- [ ] `integration/mvp → main` Draft PR 생성
- [ ] A, B, C에게 최종 리뷰 요청

### 완료 보고 형식

```text
담당자: 이현지
브랜치: integration/mvp
통합한 브랜치와 PR:
완료한 항목:
해결한 충돌:
변경한 파일:
실행한 테스트:
pytest 결과:
ruff 결과:
GUI Smoke Test 결과:
PyInstaller 결과:
남은 작업:
발견한 문제:
커밋 SHA:
최종 PR 주소:
```
