import pymysql

conn = pymysql.connect(
    host='192.168.140.139', port=3306, user='root', password='123',
    database='medicine', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

# 角色
print("正在插入角色...")
roles = [
    ("admin", "超级管理员", "拥有所有权限", 1),
    ("operator", "运营人员", "商品、订单、用户管理", 1),
    ("viewer", "只读用户", "仅查看数据", 1),
]
for code, name, remark, status in roles:
    cur.execute("SELECT id FROM role WHERE role_code=%s", (code,))
    if cur.fetchone():
        print(f"  角色 {name} 已存在，跳过")
        continue
    cur.execute(
        "INSERT INTO role (role_code, role_name, remark, status, create_time, update_time) "
        "VALUES (%s, %s, %s, %s, NOW(), NOW())",
        (code, name, remark, status)
    )
    print(f"  插入角色: {name}")
conn.commit()

# 权限
print("\n正在插入权限...")
cur.execute("SELECT COUNT(*) as cnt FROM permission")
if cur.fetchone()["cnt"] == 0:
    permissions = [
        (0, "dashboard", "数据概览", 1),
        (0, "mall", "商城管理", 2),
        (0, "system", "系统管理", 3),
        (0, "ai", "AI智能", 4),
    ]
    for parent_id, code, name, sort_order in permissions:
        cur.execute(
            "INSERT INTO permission (parent_id, permission_code, permission_name, sort_order, status, create_time, update_time) "
            "VALUES (%s, %s, %s, %s, 1, NOW(), NOW())",
            (parent_id, code, name, sort_order)
        )
        print(f"  插入权限: {name}")
    conn.commit()
else:
    print("  权限数据已存在，跳过")

# 分类
print("\n正在插入分类...")
cur.execute("SELECT COUNT(*) as cnt FROM mall_category")
if cur.fetchone()["cnt"] == 0:
    categories = [
        (None, "中药饮片", "中药材和中药饮片", 1),
        (None, "西药", "化学药品和生物制品", 2),
        (None, "中成药", "中成药制剂", 3),
        (None, "医疗器械", "医疗设备和器械", 4),
        (None, "保健品", "保健食品和营养品", 5),
    ]
    for parent_id, name, desc, sort in categories:
        cur.execute(
            "INSERT INTO mall_category (parent_id, name, description, sort, status, create_time, update_time) "
            "VALUES (%s, %s, %s, %s, 0, NOW(), NOW())",
            (parent_id, name, desc, sort)
        )
        print(f"  插入分类: {name}")
    conn.commit()
else:
    print("  分类数据已存在，跳过")

# 优惠券
print("\n正在插入优惠券...")
cur.execute("SELECT COUNT(*) as cnt FROM coupon_template")
if cur.fetchone()["cnt"] == 0:
    coupons = [
        ("FULL_REDUCTION", "满100减20", 100.00, 20.00, "PUBLISHED"),
        ("FULL_REDUCTION", "满200减50", 200.00, 50.00, "PUBLISHED"),
        ("CASH", "新人10元券", 0.00, 10.00, "PUBLISHED"),
        ("DISCOUNT", "9折优惠券", 50.00, 0.90, "PUBLISHED"),
        ("FULL_REDUCTION", "满500减100", 500.00, 100.00, "PUBLISHED"),
    ]
    for ctype, name, threshold, face, status in coupons:
        cur.execute(
            "INSERT INTO coupon_template (coupon_type, name, threshold_amount, face_amount, "
            "continue_use_enabled, stackable_enabled, status, version, create_time, update_time, is_deleted) "
            "VALUES (%s, %s, %s, %s, 0, 0, %s, 1, NOW(), NOW(), 0)",
            (ctype, name, threshold, face, status)
        )
        print(f"  插入优惠券: {name}")
    conn.commit()
else:
    print("  优惠券数据已存在，跳过")

# 用户
print("\n正在插入用户...")
cur.execute("SELECT COUNT(*) as cnt FROM user WHERE id > 1")
if cur.fetchone()["cnt"] == 0:
    users = [
        ("user_zhang", "张三", "13800001111", "zhang@example.com", "2025-09-01 10:00:00"),
        ("user_li", "李四", "13800002222", "li@example.com", "2025-09-05 14:00:00"),
        ("user_wang", "王五", "13800003333", "wang@example.com", "2025-09-10 09:00:00"),
        ("user_zhao", "赵六", "13800004444", "zhao@example.com", "2025-09-15 16:00:00"),
        ("user_sun", "孙七", "13800005555", "sun@example.com", "2025-09-20 11:00:00"),
        ("user_zhou", "周八", "13800006666", "zhou@example.com", "2025-10-01 08:00:00"),
        ("user_wu", "吴九", "13800007777", "wu@example.com", "2025-10-10 13:00:00"),
        ("user_zheng", "郑十", "13800008888", "zheng@example.com", "2025-10-15 15:00:00"),
    ]
    for username, nickname, phone, email, t in users:
        cur.execute(
            "INSERT INTO user (username, password, nickname, phone_number, email, status, create_time, update_time) "
            "VALUES (%s, '$2a$10$M/wHbN5ENWNUqAj.URs.GOQjmM6I/9pzbZL4zpUm8MQ21AI.5/lgC', %s, %s, %s, '0', %s, %s)",
            (username, nickname, phone, email, t, t)
        )
        print(f"  插入用户: {nickname}")
    conn.commit()
else:
    print("  用户数据已存在，跳过")

# 商品
print("\n正在插入商品...")
cur.execute("SELECT COUNT(*) as cnt FROM mall_product")
if cur.fetchone()["cnt"] == 0:
    products = [
        ("阿莫西林胶囊", 2, "盒", 25.00, 200, "2025-09-01 10:00:00"),
        ("布洛芬缓释胶囊", 2, "盒", 18.50, 150, "2025-09-02 10:00:00"),
        ("维生素C片", 3, "瓶", 35.00, 300, "2025-09-03 10:00:00"),
        ("板蓝根颗粒", 1, "袋", 12.00, 500, "2025-09-04 10:00:00"),
        ("电子血压计", 4, "台", 299.00, 80, "2025-09-05 10:00:00"),
        ("一次性医用口罩", 4, "盒", 15.00, 1000, "2025-09-06 10:00:00"),
        ("葡萄糖酸钙口服液", 3, "盒", 42.00, 120, "2025-09-07 10:00:00"),
        ("连花清瘟胶囊", 3, "盒", 22.00, 180, "2025-09-08 10:00:00"),
        ("鱼油软胶囊", 5, "瓶", 88.00, 90, "2025-09-09 10:00:00"),
        ("创可贴", 4, "盒", 8.00, 600, "2025-09-10 10:00:00"),
        ("复方丹参滴丸", 3, "盒", 32.00, 160, "2025-09-11 10:00:00"),
        ("医用酒精棉片", 4, "盒", 6.00, 800, "2025-09-12 10:00:00"),
        ("钙尔奇D片", 5, "瓶", 68.00, 100, "2025-09-13 10:00:00"),
        ("小柴胡颗粒", 1, "盒", 16.00, 250, "2025-09-14 10:00:00"),
        ("血糖仪", 4, "台", 158.00, 60, "2025-09-15 10:00:00"),
    ]
    product_ids = []
    for name, cat_id, unit, price, stock, t in products:
        cur.execute(
            "INSERT INTO mall_product (name, category_id, unit, price, stock, status, create_time, update_time, create_by, update_by) "
            "VALUES (%s, %s, %s, %s, %s, 1, %s, %s, 'admin', 'admin')",
            (name, cat_id, unit, price, stock, t, t)
        )
        product_ids.append(cur.lastrowid)
        print(f"  插入商品: {name}")
    conn.commit()
    print(f"  共插入 {len(product_ids)} 个商品")

    # 商品分类关联
    print("\n正在插入商品分类关联...")
    for pid, (name, cat_id, *_) in zip(product_ids, products):
        cur.execute(
            "INSERT INTO mall_product_category_rel (product_id, category_id, create_time, update_time) "
            "VALUES (%s, %s, NOW(), NOW())",
            (pid, cat_id)
        )
    conn.commit()
    print("  商品分类关联完成")
else:
    print("  商品数据已存在，跳过")

# 订单
print("\n正在插入订单...")
cur.execute("SELECT COUNT(*) as cnt FROM mall_order")
if cur.fetchone()["cnt"] == 0:
    import random
    all_statuses = [
        "PENDING_PAYMENT", "PENDING_SHIPMENT", "SHIPPED", "COMPLETED",
        "CANCELLED", "AFTER_SALE",
    ]
    # 生成最近12个月的订单
    months = [
        "2025-09", "2025-10", "2025-11", "2025-12",
        "2026-01", "2026-02", "2026-03", "2026-04",
        "2026-05", "2026-06", "2026-07", "2026-08",
    ]
    order_count = 0
    for month_idx, month in enumerate(months):
        # 每个月 5-15 个订单
        orders_in_month = random.randint(5, 15)
        for i in range(orders_in_month):
            day = random.randint(1, 28)
            hour = random.randint(8, 22)
            minute = random.randint(0, 59)
            order_time = f"{month}-{day:02d} {hour:02d}:{minute:02d}:00"

            user_id = random.randint(2, 9)
            total = round(random.uniform(20, 300), 2)
            status = random.choices(
                all_statuses,
                weights=[0.5, 1, 0.8, 3, 0.3, 0.2],
                k=1,
            )[0]
            paid = 1 if status not in ("PENDING_PAYMENT", "CANCELLED") else 0
            pay_time = order_time if paid else None

            order_no = f"SD{month.replace('-', '')}{day:02d}{hour:02d}{minute:02d}{i:04d}"

            cur.execute(
                "INSERT INTO mall_order (order_no, user_id, total_amount, pay_amount, freight_amount, "
                "order_status, paid, pay_time, items_amount, create_time, update_time, is_deleted) "
                "VALUES (%s, %s, %s, %s, 0.00, %s, %s, %s, %s, %s, %s, 0)",
                (order_no, user_id, total, total, status, paid, pay_time, total, order_time, order_time)
            )
            order_id = cur.lastrowid

            # 每个订单 1-3 个商品
            items_count = random.randint(1, 3)
            for j in range(items_count):
                pid = random.choice(product_ids) if product_ids else 1
                qty = random.randint(1, 5)
                price = round(random.uniform(8, 200), 2)
                item_total = round(price * qty, 2)
                cur.execute(
                    "INSERT INTO mall_order_item (order_id, product_id, product_name, quantity, "
                    "price, total_price, create_time, update_time) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (order_id, pid, f"商品{pid}", qty, price, item_total, order_time, order_time)
                )
            order_count += 1
    conn.commit()
    print(f"  共插入 {order_count} 个订单")
else:
    print("  订单数据已存在，跳过")

print("\n完成！")
conn.close()