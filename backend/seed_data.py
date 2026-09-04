import pymysql
import datetime
import random

conn = pymysql.connect(
    host='192.168.140.139', port=3306, user='root', password='123',
    database='medicine', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

print("正在插入用户数据...")

# 插入用户
users = [
    ("张三", "zhangsan@test.com", "13800000001", 1, "张三", "zhangsan"),
    ("李四", "lisi@test.com", "13800000002", 2, "李四", "lisi"),
    ("王五", "wangwu@test.com", "13800000003", 1, "王五", "wangwu"),
    ("赵六", "zhaoliu@test.com", "13800000004", 0, "赵六", "zhaoliu"),
    ("孙七", "sunqi@test.com", "13800000005", 2, "孙七", "sunqi"),
    ("周八", "zhouba@test.com", "13800000006", 1, "周八", "zhouba"),
    ("吴九", "wujiu@test.com", "13800000007", 0, "吴九", "wujiu"),
    ("郑十", "zhengshi@test.com", "13800000008", 2, "郑十", "zhengshi"),
]
for nickname, email, phone, gender, real_name, username in users:
    cur.execute(
        "SELECT id FROM user WHERE username=%s", (username,)
    )
    if cur.fetchone():
        print(f"  用户 {username} 已存在，跳过")
        continue
    cur.execute(
        "INSERT INTO user (nickname, avatar, email, phone_number, gender, username, password, real_name, status, create_time, update_time, is_delete) "
        "VALUES (%s, '', %s, %s, %s, %s, '$2a$10$M/wHbN5ENWNUqAj.URs.GOQjmM6I/9pzbZL4zpUm8MQ21AI.5/lgC', %s, '0', NOW(), NOW(), 0)",
        (nickname, email, phone, gender, username, real_name)
    )
    print(f"  插入用户: {nickname}")

conn.commit()

# 获取用户ID列表
cur.execute("SELECT id FROM user WHERE is_delete=0")
user_ids = [r["id"] for r in cur.fetchall()]
print(f"共 {len(user_ids)} 个用户")

# 插入用户地址
print("\n正在插入用户地址...")
cur.execute("SELECT id, nickname, phone_number FROM user WHERE is_delete=0")
all_users = cur.fetchall()
addresses_data = [
    "北京市朝阳区建国路88号",
    "上海市浦东新区陆家嘴金融中心",
    "广州市天河区天河路100号",
    "深圳市南山区科技园1号",
    "杭州市西湖区文三路200号",
    "成都市武侯区天府大道500号",
    "武汉市洪山区珞喻路300号",
    "南京市鼓楼区新街口1号",
    "西安市雁塔区科技路88号",
]
for i, u in enumerate(all_users):
    if i >= len(addresses_data):
        break
    cur.execute("SELECT id FROM user_address WHERE user_id=%s", (u["id"],))
    if cur.fetchone():
        print(f"  用户 {u['nickname']} 地址已存在，跳过")
        continue
    cur.execute(
        "INSERT INTO user_address (user_id, receiver_name, receiver_phone, address, detail_address, is_default, create_time, update_time) "
        "VALUES (%s, %s, %s, %s, %s, 1, NOW(), NOW())",
        (u["id"], u["nickname"], u["phone_number"], addresses_data[i][:4] + "市", addresses_data[i])
    )
    print(f"  插入地址: {u['nickname']} - {addresses_data[i]}")

conn.commit()

# 插入钱包
print("\n正在插入钱包...")
for uid in user_ids:
    cur.execute("SELECT id FROM user_wallet WHERE user_id=%s", (uid,))
    if cur.fetchone():
        print(f"  用户 {uid} 钱包已存在，跳过")
        continue
    import uuid
    wallet_no = "W" + str(uuid.uuid4()).replace("-", "")[:16].upper()
    balance = round(random.uniform(100, 5000), 2)
    cur.execute(
        "INSERT INTO user_wallet (user_id, wallet_no, balance, frozen_balance, total_income, total_expend, status, is_deleted) "
        "VALUES (%s, %s, %s, 0, %s, 0, 0, 0)",
        (uid, wallet_no, balance, balance + random.randint(0, 500))
    )
    print(f"  插入钱包: user_id={uid}, balance={balance}")

conn.commit()

# 获取分类
print("\n正在处理商品...")
cur.execute("SELECT id, name FROM mall_category LIMIT 20")
categories = cur.fetchall()
print(f"共 {len(categories)} 个分类")

# 插入商品
products = [
    ("阿莫西林胶囊", 1, 28.50, 500, "用于敏感菌所致的呼吸道感染、泌尿生殖道感染等", "处方药", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("布洛芬缓释胶囊", 1, 18.80, 800, "用于缓解轻至中度疼痛，如头痛、关节痛、偏头痛等", "OTC", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("连花清瘟胶囊", 2, 15.00, 1000, "清瘟解毒，宣肺泄热。用于流行性感冒", "中成药", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("板蓝根颗粒", 2, 12.00, 1200, "清热解毒，凉血利咽。用于肺胃热盛所致的咽喉肿痛", "中成药", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("维生素C片", 3, 35.00, 600, "用于预防和治疗坏血病以及各种急慢性感染", "保健品", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("蒙脱石散", 4, 22.00, 400, "用于成人及儿童急、慢性腹泻", "OTC", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("氯雷他定片", 5, 16.50, 350, "用于缓解过敏性鼻炎有关症状", "OTC", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("奥美拉唑肠溶胶囊", 4, 45.00, 300, "用于胃酸过多引起的烧心和反酸症状", "处方药", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("云南白药气雾剂", 6, 38.00, 250, "活血散瘀，消肿止痛。用于跌打损伤", "中成药", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("葡萄糖酸钙口服液", 3, 55.00, 200, "用于预防和治疗钙缺乏症", "保健品", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("999感冒灵颗粒", 2, 13.50, 900, "解热镇痛。用于感冒引起的头痛、发热、鼻塞等", "OTC", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("达克宁乳膏", 6, 25.00, 450, "用于体癣、股癣、手癣、足癣等", "OTC", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("复方丹参滴丸", 7, 32.00, 380, "活血化瘀，理气止痛。用于气滞血瘀所致的胸痹", "中成药", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("阿奇霉素片", 1, 42.00, 280, "用于敏感细菌所引起的感染", "处方药", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("健胃消食片", 8, 9.80, 1500, "健胃消食。用于脾胃虚弱，消化不良", "中成药", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("红霉素软膏", 6, 8.50, 600, "用于脓疱疮等化脓性皮肤病及小面积烧伤", "OTC", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("胰岛素注射液", 9, 68.00, 150, "用于1型糖尿病和2型糖尿病", "处方药", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("小儿氨酚黄那敏颗粒", 10, 11.00, 700, "用于缓解儿童普通感冒及流行性感冒引起的发热", "OTC", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("六味地黄丸", 7, 28.00, 500, "滋阴补肾。用于肾阴亏损，头晕耳鸣，腰膝酸软", "中成药", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
    ("钙尔奇D片", 3, 88.00, 180, "用于妊娠和哺乳期妇女、更年期妇女、老年人等的钙补充", "保健品", "https://img.zcool.cn/community/01e5f45e5a0b1fa801216a945e5ec1.png"),
]

product_ids = []
for name, cat_id, price, stock, desc, tag, img in products:
    cur.execute("SELECT id FROM mall_product WHERE name=%s AND is_deleted=0", (name,))
    existing = cur.fetchone()
    if existing:
        print(f"  商品 {name} 已存在，跳过")
        product_ids.append(existing["id"])
        continue
    cur.execute(
        "INSERT INTO mall_product (name, category_id, price, stock, sort, status, delivery_type, version, create_time, update_time, is_deleted, coupon_enabled) "
        "VALUES (%s, %s, %s, %s, 0, 1, 0, 0, NOW(), NOW(), 0, 1)",
        (name, cat_id, price, stock)
    )
    pid = cur.lastrowid
    product_ids.append(pid)
    print(f"  插入商品[{pid}]: {name} ¥{price}")

    # 插入商品图片
    cur.execute(
        "INSERT INTO mall_product_image (product_id, image_url, sort, create_time, is_deleted) "
        "VALUES (%s, %s, 0, NOW(), 0)",
        (pid, img)
    )

    # 插入分类关联
    cur.execute(
        "INSERT INTO mall_product_category_rel (product_id, category_id, is_deleted) "
        "VALUES (%s, %s, 0)",
        (pid, cat_id)
    )

conn.commit()
print(f"共 {len(product_ids)} 个商品")

# 插入订单
print("\n正在插入订单...")
order_statuses = ["PENDING_PAYMENT", "PENDING_SHIPMENT", "PENDING_RECEIPT", "COMPLETED", "COMPLETED", "COMPLETED", "REFUNDED", "AFTER_SALE"]
pay_types = ["WALLET", "WALLET", "WALLET", "WALLET", "WALLET"]

import uuid as uuid_mod

for i in range(50):
    order_no = "ORD" + datetime.datetime.now().strftime("%Y%m%d") + str(i + 1).zfill(4)
    cur.execute("SELECT id FROM mall_order WHERE order_no=%s", (order_no,))
    if cur.fetchone():
        print(f"  订单 {order_no} 已存在，跳过")
        continue

    uid = random.choice(user_ids)
    pid = random.choice(product_ids)
    cur.execute("SELECT name, price, stock FROM mall_product WHERE id=%s", (pid,))
    product = cur.fetchone()
    quantity = random.randint(1, 5)
    pay_amount = round(product["price"] * quantity, 2)

    # 获取地址
    cur.execute("SELECT id, receiver_name, receiver_phone, address, detail_address FROM user_address WHERE user_id=%s LIMIT 1", (uid,))
    addr = cur.fetchone()
    if not addr:
        continue

    status = random.choice(order_statuses)
    pay_type = random.choice(pay_types)

    cur.execute(
        "INSERT INTO mall_order (order_no, user_id, total_amount, pay_amount, freight_amount, pay_type, "
        "order_status, delivery_type, address_id, receiver_name, receiver_phone, "
        "receiver_detail, create_time, update_time, is_deleted, items_amount) "
        "VALUES (%s, %s, %s, %s, 0, %s, %s, 'EXPRESS', %s, %s, %s, %s, "
        "DATE_SUB(NOW(), INTERVAL %s DAY), NOW(), 0, %s)",
        (order_no, uid, pay_amount, pay_amount, pay_type, status,
         addr["id"], addr["receiver_name"], addr["receiver_phone"],
         addr["detail_address"], random.randint(0, 30), pay_amount)
    )
    order_id = cur.lastrowid

    # 插入订单项
    cur.execute(
        "INSERT INTO mall_order_item (order_id, product_id, product_name, quantity, price, "
        "total_price, image_url, create_time, update_time, is_deleted, coupon_deduct_amount, payable_amount) "
        "VALUES (%s, %s, %s, %s, %s, %s, '', NOW(), NOW(), 0, 0, %s)",
        (order_id, pid, product["name"], quantity, product["price"], pay_amount, pay_amount)
    )
    print(f"  插入订单: {order_no} | {product['name']} x{quantity} | ¥{pay_amount} | {status}")

conn.commit()

# 插入售后单
print("\n正在插入售后单...")
cur.execute("SELECT id, order_no, user_id FROM mall_order WHERE order_status='AFTER_SALE' AND is_deleted=0 LIMIT 5")
refund_orders = cur.fetchall()
for ro in refund_orders:
    cur.execute("SELECT id FROM mall_after_sale WHERE order_no=%s", (ro["order_no"],))
    if cur.fetchone():
        continue
    cur.execute(
        "INSERT INTO mall_after_sale (order_no, user_id, order_id, order_item_id, after_sale_no, after_sale_status, "
        "after_sale_type, refund_amount, apply_reason, apply_time, create_time, update_time, is_deleted) "
        "VALUES (%s, %s, %s, 1, %s, 'PENDING', 'REFUND', 0, '商品质量问题', NOW(), NOW(), NOW(), 0)",
        (ro["order_no"], ro["user_id"], ro["id"],
         "AS" + datetime.datetime.now().strftime("%Y%m%d") + str(random.randint(1000, 9999)))
    )
    print(f"  插入售后单: {ro['order_no']}")

conn.commit()

# ==================== 角色数据 ====================
print("\n正在插入角色数据...")
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

# ==================== 权限数据 ====================
print("\n正在插入权限数据...")
cur.execute("SELECT COUNT(*) as cnt FROM permission")
if cur.fetchone()["cnt"] == 0:
    permissions = [
        (0, "dashboard", "数据概览", 1, "菜单"),
        (0, "mall", "商城管理", 2, "菜单"),
        (0, "system", "系统管理", 3, "菜单"),
        (0, "ai", "AI智能", 4, "菜单"),
    ]
    for parent_id, code, name, sort_order, remark in permissions:
        cur.execute(
            "INSERT INTO permission (parent_id, permission_code, permission_name, sort_order, status, remark, create_time, update_time) "
            "VALUES (%s, %s, %s, %s, 1, %s, NOW(), NOW())",
            (parent_id, code, name, sort_order, remark)
        )
        print(f"  插入权限: {name}")
    conn.commit()
else:
    print("  权限数据已存在，跳过")

# ==================== 分类数据 ====================
print("\n正在插入分类数据...")
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

# ==================== 优惠券数据 ====================
print("\n正在插入优惠券数据...")
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

print("\n数据插入完成！")
conn.close()