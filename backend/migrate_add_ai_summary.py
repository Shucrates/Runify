import sqlite3

conn = sqlite3.connect('runify.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(runs)")
cols = [row[1] for row in cursor.fetchall()]

if 'ai_summary' not in cols:
    cursor.execute('ALTER TABLE runs ADD COLUMN ai_summary TEXT')
    conn.commit()
    print('SUCCESS: ai_summary column added to runs table')
else:
    print('OK: ai_summary column already exists')

conn.close()
