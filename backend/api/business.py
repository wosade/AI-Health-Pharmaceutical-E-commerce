import os
import pymysql
import traceback
from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/api")


def _get_conn():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "192.168.140.139"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "123"),
        database=os.getenv("MYSQL_DATABASE", "medicine"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


# ==================== 商品 ====================

@router.get("/products")
def list_products(
    keyword: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    try:
        conn = _get_conn()
        try:
            with conn.cursor() as cur:
                if keyword:
                    cur.execute(
                        "SELECT COUNT(*) as cnt FROM mall_product WHERE is_deleted=0 AND name LIKE %s",
                        (f"%{keyword}%",),
                    )
                else:
                    cur.execute("SELECT COUNT(*) as cnt FROM mall_product WHERE is_deleted=0")
                total = cur.fetchone()["cnt"]

                offset = (page - 1) * page_size
                if keyword:
                    cur.execute(
                        "SELECT * FROM mall_product WHERE is_deleted=0 AND name LIKE %s "
                        "ORDER BY create_time DESC LIMIT %s OFFSET %s",
                        (f"%{keyword}%", page_size, offset),
                    )
                else:
                    cur.execute(
                        "SELECT * FROM mall_product WHERE is_deleted=0 "
                        "ORDER BY create_time DESC LIMIT %s OFFSET %s",
                        (page_size, offset),
                    )
                rows = cur.fetchall()

            for row in rows:
                row["createTime"] = row.pop("create_time", None)
                row["updateTime"] = row.pop("update_time", None)
                tag_ids = []
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT tag_id FROM mall_product_tag_rel WHERE product_id=%s",
                        (row["id"],),
                    )
                    tag_ids = [r["tag_id"] for r in cur.fetchall()]
                with conn.cursor() as cur:
                    images = []
                    cur.execute(
                        "SELECT image_url FROM mall_product_image WHERE product_id=%s AND is_deleted=0 ORDER BY sort",
                        (row["id"],),
                    )
                    images = [r["image_url"] for r in cur.fetchall()]
                with conn.cursor() as cur:
                    cat_ids = []
                    cur.execute(
                        "SELECT category_id FROM mall_product_category_rel WHERE product_id=%s AND is_deleted=0",
                        (row["id"],),
                    )
                    cat_ids = [r["category_id"] for r in cur.fetchall()]
                with conn.cursor() as cur:
                    category_names = []
                    if cat_ids:
                        placeholders = ",".join(["%s"] * len(cat_ids))
                        cur.execute(
                            f"SELECT name FROM mall_category WHERE id IN ({placeholders})",
                            cat_ids,
                        )
                        category_names = [r["name"] for r in cur.fetchall()]
                row["tagIds"] = tag_ids
                row["images"] = images
                row["categoryIds"] = cat_ids
                row["categoryNames"] = category_names

            return {"code": 200, "data": rows, "total": total, "page": page, "pageSize": page_size}
        finally:
            conn.close()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}")
def get_product(product_id: int):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM mall_product WHERE id=%s AND is_deleted=0", (product_id,))
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="商品不存在")
        row["createTime"] = row.pop("create_time", None)
        row["updateTime"] = row.pop("update_time", None)
        return {"code": 200, "data": row}
    finally:
        conn.close()


# ==================== 订单 ====================

@router.get("/orders")
def list_orders(
    user_id: int = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            if user_id:
                cur.execute("SELECT COUNT(*) as cnt FROM mall_order WHERE is_deleted=0 AND user_id=%s", (user_id,))
            else:
                cur.execute("SELECT COUNT(*) as cnt FROM mall_order WHERE is_deleted=0")
            total = cur.fetchone()["cnt"]

            offset = (page - 1) * page_size
            if user_id:
                cur.execute(
                    "SELECT * FROM mall_order WHERE is_deleted=0 AND user_id=%s "
                    "ORDER BY create_time DESC LIMIT %s OFFSET %s",
                    (user_id, page_size, offset),
                )
            else:
                cur.execute(
                    "SELECT * FROM mall_order WHERE is_deleted=0 "
                    "ORDER BY create_time DESC LIMIT %s OFFSET %s",
                    (page_size, offset),
                )
            rows = cur.fetchall()

        for row in rows:
            row["createTime"] = row.pop("create_time", None)
            row["updateTime"] = row.pop("update_time", None)
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM mall_order_item WHERE order_id=%s AND is_deleted=0",
                    (row["id"],),
                )
                items = cur.fetchall()
                for item in items:
                    item["createTime"] = item.pop("create_time", None)
            row["items"] = items
            if items:
                row["productInfo"] = {
                    "productName": items[0].get("product_name", ""),
                    "productImage": items[0].get("image_url", ""),
                    "quantity": sum(it.get("quantity", 0) for it in items),
                }

        return {"code": 200, "data": rows, "total": total, "page": page, "pageSize": page_size}
    finally:
        conn.close()


@router.get("/orders/{order_no}")
def get_order(order_no: str):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM mall_order WHERE order_no=%s AND is_deleted=0", (order_no,))
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="订单不存在")
        row["createTime"] = row.pop("create_time", None)
        row["updateTime"] = row.pop("update_time", None)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM mall_order_item WHERE order_id=%s", (row["id"],))
            row["items"] = cur.fetchall()
        return {"code": 200, "data": row}
    finally:
        conn.close()


@router.get("/orders/status/{status}")
def list_orders_by_status(status: str):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM mall_order WHERE is_deleted=0 AND order_status=%s ORDER BY create_time DESC",
                (status,),
            )
            rows = cur.fetchall()
        for row in rows:
            row["createTime"] = row.pop("create_time", None)
            row["updateTime"] = row.pop("update_time", None)
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM mall_order_item WHERE order_id=%s", (row["id"],))
                items = cur.fetchall()
            if items:
                row["productInfo"] = {
                    "productName": items[0].get("product_name", ""),
                    "productImage": items[0].get("image_url", ""),
                    "quantity": sum(it.get("quantity", 0) for it in items),
                }
        return {"code": 200, "data": rows, "total": len(rows)}
    finally:
        conn.close()


# ==================== 用户 ====================

@router.get("/users")
def list_users(
    keyword: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            if keyword:
                cur.execute(
                    "SELECT COUNT(*) as cnt FROM user WHERE is_delete=0 AND "
                    "(username LIKE %s OR nickname LIKE %s OR phone_number LIKE %s)",
                    (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
                )
            else:
                cur.execute("SELECT COUNT(*) as cnt FROM user WHERE is_delete=0")
            total = cur.fetchone()["cnt"]

            offset = (page - 1) * page_size
            if keyword:
                cur.execute(
                    "SELECT id, username, nickname, avatar, email, phone_number, gender, "
                    "real_name, status, create_time FROM user WHERE is_delete=0 AND "
                    "(username LIKE %s OR nickname LIKE %s OR phone_number LIKE %s) "
                    "ORDER BY create_time DESC LIMIT %s OFFSET %s",
                    (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", page_size, offset),
                )
            else:
                cur.execute(
                    "SELECT id, username, nickname, avatar, email, phone_number, gender, "
                    "real_name, status, create_time FROM user WHERE is_delete=0 "
                    "ORDER BY create_time DESC LIMIT %s OFFSET %s",
                    (page_size, offset),
                )
            rows = cur.fetchall()

        for row in rows:
            row["createTime"] = row.pop("create_time", None)
            row["phoneNumber"] = row.pop("phone_number", None)
            row["realName"] = row.pop("real_name", None)
            with conn.cursor() as cur:
                cur.execute("SELECT role_id FROM user_role WHERE user_id=%s", (row["id"],))
                role_ids = [r["role_id"] for r in cur.fetchall()]
            with conn.cursor() as cur:
                role_names = []
                if role_ids:
                    placeholders = ",".join(["%s"] * len(role_ids))
                    cur.execute(
                        f"SELECT name FROM role WHERE id IN ({placeholders})",
                        role_ids,
                    )
                    role_names = [r["name"] for r in cur.fetchall()]
            row["roles"] = ",".join(role_names) if role_names else "user"

        return {"code": 200, "data": rows, "total": total, "page": page, "pageSize": page_size}
    finally:
        conn.close()


@router.get("/users/{user_id}")
def get_user(user_id: int):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, nickname, avatar, email, phone_number, gender, "
                "real_name, status, create_time FROM user WHERE id=%s AND is_delete=0",
                (user_id,),
            )
            row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="用户不存在")
        row["createTime"] = row.pop("create_time", None)
        row["phoneNumber"] = row.pop("phone_number", None)
        row["realName"] = row.pop("real_name", None)
        return {"code": 200, "data": row}
    finally:
        conn.close()


# ==================== 分类 ====================

@router.get("/categories")
def list_categories():
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM mall_category ORDER BY sort ASC")
            rows = cur.fetchall()
        for row in rows:
            row["createTime"] = row.pop("create_time", None)
            row["updateTime"] = row.pop("update_time", None)
        return {"code": 200, "data": rows}
    finally:
        conn.close()


# ==================== 数据概览 ====================

@router.get("/analytics/summary")
def analytics_summary():
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM user WHERE is_delete=0")
            user_count = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM mall_product WHERE is_deleted=0")
            product_count = cur.fetchone()["cnt"]
            cur.execute("SELECT COUNT(*) as cnt FROM mall_order WHERE is_deleted=0")
            order_count = cur.fetchone()["cnt"]
            cur.execute(
                "SELECT COALESCE(SUM(pay_amount), 0) as total FROM mall_order "
                "WHERE is_deleted=0 AND DATE(create_time)=CURDATE()"
            )
            today_sales = float(cur.fetchone()["total"])
            cur.execute(
                "SELECT COALESCE(SUM(pay_amount), 0) as total FROM mall_order "
                "WHERE is_deleted=0 AND order_status='PENDING_SHIPMENT'"
            )
            pending_ship = float(cur.fetchone()["total"])
            cur.execute(
                "SELECT COALESCE(SUM(pay_amount), 0) as total FROM mall_order "
                "WHERE is_deleted=0 AND order_status='AFTER_SALE'"
            )
            after_sale = float(cur.fetchone()["total"])
        return {
            "code": 200,
            "data": {
                "userCount": user_count,
                "productCount": product_count,
                "orderCount": order_count,
                "todaySales": round(today_sales, 2),
                "pendingShipmentOrders": pending_ship,
                "afterSaleOrders": after_sale,
            },
        }
    finally:
        conn.close()


@router.get("/analytics/charts")
def analytics_charts():
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT DATE_FORMAT(create_time, %s) as month, "
                "COUNT(*) as cnt, COALESCE(SUM(pay_amount), 0) as amount "
                "FROM mall_order WHERE is_deleted=0 "
                "AND create_time >= DATE_SUB(NOW(), INTERVAL 12 MONTH) "
                "GROUP BY month ORDER BY month",
                ("%Y-%m",)
            )
            sales_trend = [
                {"month": r["month"], "count": r["cnt"], "amount": float(r["amount"])}
                for r in cur.fetchall()
            ]

            cur.execute(
                "SELECT order_status, COUNT(*) as cnt "
                "FROM mall_order WHERE is_deleted=0 GROUP BY order_status"
            )
            order_status = [
                {"name": r["order_status"] or "UNKNOWN", "value": r["cnt"]}
                for r in cur.fetchall()
            ]

            cur.execute(
                "SELECT DATE(create_time) as date, COUNT(*) as cnt "
                "FROM mall_order WHERE is_deleted=0 "
                "AND create_time >= DATE_SUB(NOW(), INTERVAL 7 DAY) "
                "GROUP BY date ORDER BY date"
            )
            daily_orders = [
                {"date": r["date"], "count": r["cnt"]}
                for r in cur.fetchall()
            ]

            cur.execute(
                "SELECT c.name, COUNT(pcr.id) as cnt "
                "FROM mall_category c "
                "LEFT JOIN mall_product_category_rel pcr ON c.id = pcr.category_id AND pcr.is_deleted=0 "
                "GROUP BY c.id, c.name ORDER BY cnt DESC LIMIT 10"
            )
            category_dist = [
                {"name": r["name"], "value": r["cnt"]}
                for r in cur.fetchall()
            ]

        return {
            "code": 200,
            "data": {
                "salesTrend": sales_trend,
                "orderStatus": order_status,
                "dailyOrders": daily_orders,
                "categoryDistribution": category_dist,
            },
        }
    finally:
        conn.close()


# ==================== 售后 ====================

@router.get("/after-sales")
def list_after_sales(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM mall_after_sale WHERE is_deleted=0")
            total = cur.fetchone()["cnt"]
            offset = (page - 1) * page_size
            cur.execute(
                "SELECT * FROM mall_after_sale WHERE is_deleted=0 "
                "ORDER BY create_time DESC LIMIT %s OFFSET %s",
                (page_size, offset),
            )
            rows = cur.fetchall()
        for row in rows:
            row["createTime"] = row.pop("create_time", None)
            row["updateTime"] = row.pop("update_time", None)
            row["afterSaleNo"] = row.pop("after_sale_no", None)
            row["afterSaleType"] = row.pop("after_sale_type", None)
            row["afterSaleStatus"] = row.pop("after_sale_status", None)
            row["refundAmount"] = float(row.pop("refund_amount", 0))
            row["applyReason"] = row.pop("apply_reason", None)
            row["applyDescription"] = row.pop("apply_description", None)
            row["applyTime"] = row.pop("apply_time", None)
            row["auditTime"] = row.pop("audit_time", None)
        return {"code": 200, "data": rows, "total": total, "page": page, "pageSize": page_size}
    finally:
        conn.close()


@router.put("/after-sales/{sale_id}/approve")
def approve_after_sale(sale_id: int):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE mall_after_sale SET after_sale_status='APPROVED', audit_time=NOW(), update_time=NOW() WHERE id=%s",
                (sale_id,))
            conn.commit()
            return {"code": 200}
    finally:
        conn.close()


@router.put("/after-sales/{sale_id}/reject")
def reject_after_sale(sale_id: int):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE mall_after_sale SET after_sale_status='REJECTED', audit_time=NOW(), update_time=NOW() WHERE id=%s",
                (sale_id,))
            conn.commit()
            return {"code": 200}
    finally:
        conn.close()


# ==================== 角色 ====================

@router.get("/roles")
def list_roles(page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100)):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM role")
            total = cur.fetchone()["cnt"]
            offset = (page - 1) * page_size
            cur.execute("SELECT * FROM role ORDER BY create_time DESC LIMIT %s OFFSET %s", (page_size, offset))
            rows = cur.fetchall()
        for row in rows:
            row["createTime"] = row.pop("create_time", None)
            row["updateTime"] = row.pop("update_time", None)
            row["name"] = row.pop("role_name", None)
            row["code"] = row.pop("role_code", None)
            row["description"] = row.pop("remark", None)
        return {"code": 200, "data": rows, "total": total, "page": page, "pageSize": page_size}
    finally:
        conn.close()


@router.post("/roles/create")
def create_role(data: dict):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO role (role_code, role_name, remark, status, create_time, update_time) "
                "VALUES (%s, %s, %s, %s, NOW(), NOW())",
                (data.get("code", ""), data.get("name", ""), data.get("description", ""), data.get("status", 1))
            )
            conn.commit()
            return {"code": 200, "data": {"id": cur.lastrowid}}
    finally:
        conn.close()


@router.put("/roles/{role_id}")
def update_role(role_id: int, data: dict):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE role SET role_code=%s, role_name=%s, remark=%s, status=%s, update_time=NOW() WHERE id=%s",
                (data.get("code", ""), data.get("name", ""), data.get("description", ""), data.get("status", 1), role_id)
            )
            conn.commit()
            return {"code": 200}
    finally:
        conn.close()


@router.delete("/roles/{role_id}")
def delete_role(role_id: int):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM role WHERE id=%s", (role_id,))
            cur.execute("DELETE FROM role_permission WHERE role_id=%s", (role_id,))
            conn.commit()
            return {"code": 200}
    finally:
        conn.close()


@router.get("/roles/{role_id}/permissions")
def get_role_permissions(role_id: int):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT p.id, p.permission_name as name FROM permission p "
                "INNER JOIN role_permission rp ON p.id=rp.permission_id WHERE rp.role_id=%s",
                (role_id,))
            rows = cur.fetchall()
        return {"code": 200, "data": rows}
    finally:
        conn.close()


@router.put("/roles/{role_id}/permissions")
def update_role_permissions(role_id: int, data: dict):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM role_permission WHERE role_id=%s", (role_id,))
            for pid in data.get("permissionIds", []):
                cur.execute("INSERT INTO role_permission (role_id, permission_id, create_time) VALUES (%s, %s, NOW())", (role_id, pid))
            conn.commit()
            return {"code": 200}
    finally:
        conn.close()


# ==================== 权限 ====================

@router.get("/permissions/tree")
def get_permissions_tree():
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM permission ORDER BY sort_order ASC")
            rows = cur.fetchall()
        for row in rows:
            row["createTime"] = row.pop("create_time", None)
            row["name"] = row.pop("permission_name", None)
            row["code"] = row.pop("permission_code", None)
            row["sort"] = row.pop("sort_order", None)
            row["parentId"] = row.pop("parent_id", None)
        return {"code": 200, "data": rows}
    finally:
        conn.close()


@router.post("/permissions/create")
def create_permission(data: dict):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO permission (parent_id, permission_code, permission_name, sort_order, status, create_time, update_time) "
                "VALUES (%s, %s, %s, %s, 1, NOW(), NOW())",
                (data.get("parentId", 0), data.get("code", ""), data.get("name", ""), data.get("sort", 0))
            )
            conn.commit()
            return {"code": 200, "data": {"id": cur.lastrowid}}
    finally:
        conn.close()


@router.put("/permissions/{perm_id}")
def update_permission(perm_id: int, data: dict):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE permission SET parent_id=%s, permission_code=%s, permission_name=%s, sort_order=%s, "
                "update_time=NOW() WHERE id=%s",
                (data.get("parentId", 0), data.get("code", ""), data.get("name", ""), data.get("sort", 0), perm_id)
            )
            conn.commit()
            return {"code": 200}
    finally:
        conn.close()


@router.delete("/permissions/{perm_id}")
def delete_permission(perm_id: int):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM role_permission WHERE permission_id=%s", (perm_id,))
            cur.execute("DELETE FROM permission WHERE id=%s", (perm_id,))
            conn.commit()
            return {"code": 200}
    finally:
        conn.close()


# ==================== 分类 ====================

@router.get("/categories/tree")
def get_categories_tree():
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM mall_category ORDER BY sort ASC")
            rows = cur.fetchall()
        for row in rows:
            row["createTime"] = row.pop("create_time", None)
            row["updateTime"] = row.pop("update_time", None)
            row["parentId"] = row.pop("parent_id", None)
        return {"code": 200, "data": rows}
    finally:
        conn.close()


@router.post("/categories/create")
def create_category(data: dict):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO mall_category (parent_id, name, description, sort, status, create_time, update_time) "
                "VALUES (%s, %s, %s, %s, 0, NOW(), NOW())",
                (data.get("parentId"), data.get("name", ""), data.get("description", ""), data.get("sort", 0))
            )
            conn.commit()
            return {"code": 200, "data": {"id": cur.lastrowid}}
    finally:
        conn.close()


@router.put("/categories/{cat_id}")
def update_category(cat_id: int, data: dict):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE mall_category SET parent_id=%s, name=%s, description=%s, sort=%s, update_time=NOW() WHERE id=%s",
                (data.get("parentId"), data.get("name", ""), data.get("description", ""), data.get("sort", 0), cat_id)
            )
            conn.commit()
            return {"code": 200}
    finally:
        conn.close()


@router.delete("/categories/{cat_id}")
def delete_category(cat_id: int):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM mall_category WHERE id=%s", (cat_id,))
            conn.commit()
            return {"code": 200}
    finally:
        conn.close()


# ==================== 优惠券 ====================

@router.get("/coupons")
def list_coupons(page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100)):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM coupon_template WHERE is_deleted=0")
            total = cur.fetchone()["cnt"]
            offset = (page - 1) * page_size
            cur.execute("SELECT * FROM coupon_template WHERE is_deleted=0 ORDER BY create_time DESC LIMIT %s OFFSET %s", (page_size, offset))
            rows = cur.fetchall()
        for row in rows:
            row["createTime"] = row.pop("create_time", None)
            row["updateTime"] = row.pop("update_time", None)
            row["type"] = row.pop("coupon_type", None)
            row["value"] = float(row.pop("face_amount", 0))
            row["minAmount"] = float(row.pop("threshold_amount", 0))
            row["totalCount"] = 100
            row["usedCount"] = 0
        return {"code": 200, "data": rows, "total": total, "page": page, "pageSize": page_size}
    finally:
        conn.close()


@router.post("/coupons/create")
def create_coupon(data: dict):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO coupon_template (coupon_type, name, threshold_amount, face_amount, "
                "continue_use_enabled, stackable_enabled, status, version, create_time, update_time, is_deleted) "
                "VALUES (%s, %s, %s, %s, 0, 0, 'PUBLISHED', 1, NOW(), NOW(), 0)",
                (data.get("type", "FULL_REDUCTION"), data.get("name", ""),
                 data.get("minAmount", 0), data.get("value", 0))
            )
            conn.commit()
            return {"code": 200, "data": {"id": cur.lastrowid}}
    finally:
        conn.close()


@router.put("/coupons/{coupon_id}")
def update_coupon(coupon_id: int, data: dict):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE coupon_template SET coupon_type=%s, name=%s, threshold_amount=%s, face_amount=%s, "
                "update_time=NOW() WHERE id=%s",
                (data.get("type", "FULL_REDUCTION"), data.get("name", ""),
                 data.get("minAmount", 0), data.get("value", 0), coupon_id)
            )
            conn.commit()
            return {"code": 200}
    finally:
        conn.close()


@router.delete("/coupons/{coupon_id}")
def delete_coupon(coupon_id: int):
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE coupon_template SET is_deleted=1 WHERE id=%s", (coupon_id,))
            conn.commit()
            return {"code": 200}
    finally:
        conn.close()