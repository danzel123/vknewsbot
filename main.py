import tg
import sqlite3
import time





def update():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT tg_id FROM users')
    for tg_id in c.fetchall():
        tg.send_wall(tg_id[0])
    time.sleep(1)



if __name__ == '__main__':
    while True:
        try:
            update()
        except Exception as e:
            print(e)

