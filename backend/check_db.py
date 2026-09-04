import pymysql

conn = pymysql.connect(
    host='192.168.140.139', port=3306, user='root', password='123',
    database='medicine', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

# Check mall_order structure
cur.execute("DESCRIBE mall_order")
print("=== mall_order ===")
for row in cur.fetchall():
    print(row)

# Check mall_category status values
cur.execute("SELECT DISTINCT status FROM mall_category")
print("\n=== mall_category status values ===")
for row in cur.fetchall():
    print(row)

# Check mall_category count
cur.execute("SELECT COUNT(*) as cnt FROM mall_category")
print(f"\nmall_category total: {cur.fetchone()['cnt']}")

# Check mall_product
cur.execute("SELECT COUNT(*) as cnt FROM mall_product WHERE is_deleted=0")
print(f"mall_product: {cur.fetchone()['cnt']}")

# Check mall_order
cur.execute("SELECT COUNT(*) as cnt FROM mall_order WHERE is_deleted=0")
print(f"mall_order: {cur.fetchone()['cnt']}")

conn.close()