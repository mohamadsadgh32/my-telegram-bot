import sqlite3

def connect():
    return sqlite3.connect('bot.db')

def init_db():
    conn = connect()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_username TEXT UNIQUE,
            last_post_id INTEGER,
            auto_post BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_channel(username, auto_post=False):
    conn = connect()
    cur = conn.cursor()
    cur.execute('INSERT OR IGNORE INTO channels (channel_username, auto_post) VALUES (?, ?)', (username, auto_post))
    conn.commit()
    conn.close()

def update_last_post(username, post_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute('UPDATE channels SET last_post_id = ? WHERE channel_username = ?', (post_id, username))
    conn.commit()
    conn.close()

def get_channels():
    conn = connect()
    cur = conn.cursor()
    cur.execute('SELECT channel_username, last_post_id, auto_post FROM channels')
    result = cur.fetchall()
    conn.close()
    return result

def set_auto_post(username, auto_post):
    conn = connect()
    cur = conn.cursor()
    cur.execute('UPDATE channels SET auto_post = ? WHERE channel_username = ?', (auto_post, username))
    conn.commit()
    conn.close()
