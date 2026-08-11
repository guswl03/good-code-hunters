def use_unparameterized_queries(cursor, user_id):
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    cursor.execute("SELECT * FROM users WHERE id = " + str(user_id))
    cursor.execute("SELECT * FROM users")
    cursor.execute("audit event ?", (user_id,))
    cursor.execute("SELECT '?' AS marker", (user_id,))
    cursor.execute("SELECT 1 -- ? is only a comment", (user_id,))
