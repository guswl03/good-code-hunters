def use_parameterized_queries(cursor, user_id, username, rows):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    cursor.executemany("INSERT INTO users(name) VALUES (%s)", rows)
    cursor.execute("UPDATE users SET name = :name", {"name": username})
