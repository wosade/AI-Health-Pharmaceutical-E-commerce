package com.medicine.agent;

import com.medicine.entity.Order;
import com.medicine.entity.Product;
import com.medicine.entity.User;
import com.medicine.service.AnalyticsService;
import com.medicine.service.OrderService;
import com.medicine.service.ProductService;
import com.medicine.service.UserService;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
public class AdminTools {

    private final OrderService orderService;
    private final ProductService productService;
    private final UserService userService;
    private final AnalyticsService analyticsService;

    public AdminTools(OrderService orderService, ProductService productService,
                      UserService userService, AnalyticsService analyticsService) {
        this.orderService = orderService;
        this.productService = productService;
        this.userService = userService;
        this.analyticsService = analyticsService;
    }

    @Tool(description = "查询订单列表，按订单号、用户ID、状态筛选。")
    public Map<String, Object> searchOrders(
            @ToolParam(description = "订单号") String orderNo,
            @ToolParam(description = "用户ID") Long userId,
            @ToolParam(description = "订单状态") String orderStatus) {
        Map<String, Object> result = new HashMap<>();
        if (orderNo != null && !orderNo.isEmpty()) {
            Order order = orderService.getByOrderNo(orderNo);
            result.put("rows", order != null ? List.of(order) : List.of());
            result.put("total", order != null ? 1 : 0);
        } else if (orderStatus != null && !orderStatus.isEmpty()) {
            List<Order> rows = orderService.listByStatus(orderStatus);
            result.put("rows", rows);
            result.put("total", rows.size());
        } else if (userId != null) {
            List<Order> rows = orderService.listByUser(userId);
            result.put("rows", rows);
            result.put("total", rows.size());
        } else {
            result.put("rows", List.of());
            result.put("total", 0);
        }
        return result;
    }

    @Tool(description = "查询商品列表，按名称关键词搜索。")
    public List<Product> searchProducts(
            @ToolParam(description = "商品名称关键词") String name) {
        return productService.search(name != null ? name : "");
    }

    @Tool(description = "查询用户列表，按用户名/昵称/手机号搜索。")
    public List<User> searchUsers(
            @ToolParam(description = "用户名/昵称/手机号关键词") String keyword) {
        return userService.search(keyword != null ? keyword : "");
    }

    @Tool(description = "查询售后单列表。")
    public Map<String, Object> searchAfterSales(
            @ToolParam(description = "售后单号") String afterSaleNo,
            @ToolParam(description = "售后状态") String afterSaleStatus) {
        Map<String, Object> result = new HashMap<>();
        result.put("total", 0);
        result.put("rows", List.of());
        result.put("message", "售后功能需扩展，当前暂无数据");
        return result;
    }

    @Tool(description = "获取运营数据概览：用户数、商品数、订单数、今日销售额。")
    public Map<String, Object> getAnalytics() {
        return analyticsService.summary();
    }
}