package com.medicine.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.medicine.entity.Order;
import com.medicine.entity.Product;
import com.medicine.entity.User;
import com.medicine.mapper.OrderMapper;
import com.medicine.mapper.ProductMapper;
import com.medicine.mapper.UserMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class AnalyticsService {
    private final OrderMapper orderMapper;
    private final ProductMapper productMapper;
    private final UserMapper userMapper;

    public Map<String, Object> summary() {
        Map<String, Object> data = new HashMap<>();

        long userCount = userMapper.selectCount(new LambdaQueryWrapper<User>().eq(User::getIsDelete, 0));
        data.put("userCount", userCount);

        long productCount = productMapper.selectCount(
            new LambdaQueryWrapper<Product>().eq(Product::getIsDeleted, 0).eq(Product::getStatus, 1));
        data.put("productCount", productCount);

        long orderCount = orderMapper.selectCount(
            new LambdaQueryWrapper<Order>().eq(Order::getIsDeleted, 0));
        data.put("orderCount", orderCount);

        var todayOrders = orderMapper.selectList(
            new LambdaQueryWrapper<Order>()
                .eq(Order::getIsDeleted, 0)
                .apply("DATE(create_time) = CURDATE()"));
        BigDecimal todayAmount = todayOrders.stream()
            .map(Order::getPayAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        data.put("todayAmount", todayAmount);
        data.put("todayOrderCount", todayOrders.size());

        return data;
    }
}