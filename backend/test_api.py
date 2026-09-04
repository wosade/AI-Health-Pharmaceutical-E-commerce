import pymysql

conn = pymysql.connect(
    host='192.168.140.139', port=3306, user='root', password='123',
    database='medicine', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

for t in ['mall_product_tag_rel', 'mall_product_category_rel', 'mall_product_image']:
    try:
        cur.execute(f"SELECT * FROM {t} WHERE is_deleted=0 LIMIT 1")
        print(f"{t}: is_deleted EXISTS")
    except Exception as e:
        print(f"{t}: {e}")

conn.close()