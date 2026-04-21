import sqlite3

conn = sqlite3.connect('chatbot.db')
cursor = conn.cursor()

print("=== conversation_history (last 10) ===")
cursor.execute('SELECT role, content, timestamp FROM conversation_history ORDER BY timestamp DESC LIMIT 10')
rows = cursor.fetchall()
if rows:
    for r in rows:
        print(f'[{r[2]}] {r[0]}: {r[1][:80]}')
else:
    print('No rows found - long term memory is NOT saving')

print("\n=== user_tokens ===")
cursor.execute('SELECT session_id, portal_id, created_at FROM user_tokens ORDER BY created_at DESC LIMIT 5')
rows = cursor.fetchall()
for r in rows:
    print(f'session: {r[0][:20]}... | portal: {r[1]} | created: {r[2]}')

print("\n=== user_preferences ===")
cursor.execute('SELECT * FROM user_preferences LIMIT 10')
rows = cursor.fetchall()
if rows:
    for r in rows:
        print(r)
else:
    print('No preferences saved yet')

conn.close()