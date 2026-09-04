import pymysql
c = pymysql.connect(host='192.168.140.139', port=3306, user='root', password='123',
                    database='medicine', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
cur = c.cursor()
tables = ['role', 'role_permission']
for t in tables:
    print(f'\n=== {t} ===')
    cur.execute(f'DESC {t}')
    for r in cur.fetchall():
        print(f'  {r["Field"]:25s} {r["Type"]:20s} Null={r["Null"]:5s} Default={r["Default"]}')
c.close()