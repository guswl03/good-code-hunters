# GOOD001 — Parameterized SQL Query

## 목적

SQL 문자열에 값을 직접 조립하지 않고 SQL과 parameter를 별도 인자로 전달하는 명확한 패턴을 찾는다. 이는 SQL injection을 예방하는 대표적인 코딩 방식이다.

## 탐지하는 패턴

- `execute()` 또는 `executemany()` method 호출
- 첫 번째 positional argument가 `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `REPLACE`, `WITH`로 시작하는 문자열 literal
- 두 번째 positional argument에 parameter 값 또는 collection 전달
- SQL literal 안에 `?`, `%s`, `:name` 중 하나의 지원 placeholder 존재

```python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
cursor.execute("UPDATE users SET name = :name", {"name": username})
```

## 탐지하지 않는 패턴

```python
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.execute("SELECT * FROM users WHERE id = " + str(user_id))
cursor.execute("SELECT * FROM users")
```

SQL이 아닌 문자열에 우연히 `?`가 있거나 placeholder가 SQL의 quoted literal/comment 안에만 있는 경우는 탐지하지 않는다. parameter argument가 `None` 또는 빈 literal collection인 경우도 탐지하지 않는다.

## Precision-first 제한사항

SQL query 변수의 값을 추적하지 않고 문자열 literal만 검사한다. keyword argument로만 전달한 query/parameter, driver별 추가 placeholder 문법, 동적으로 조립한 query는 MVP에서 지원하지 않는다.

이 규칙은 parameterized query 사용 근거만 보고하며 파일 전체가 SQL injection으로부터 안전하다고 보증하지 않는다.
