package com.medicine.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.medicine.entity.Order;
import com.medicine.mapper.OrderMapper;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class OrderService {
    private final OrderMapper orderMapper;

    public OrderService(OrderMapper orderMapper) {
        this.orderMapper = orderMapper;
    }

    public List<Order> listByUser(Long userId) {
        LambdaQueryWrapper<Order> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Order::getUserId, userId)
               .eq(Order::getIsDeleted, 0)
               .orderByDesc(Order::getCreateTime)
               .last("LIMIT 20");
        return orderMapper.selectList(wrapper);
    }

    public Order getByOrderNo(String orderNo) {
        LambdaQueryWrapper<Order> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Order::getOrderNo, orderNo)
               .eq(Order::getIsDeleted, 0);
        return orderMapper.selectOne(wrapper);
    }

    public List<Order> listByStatus(String status) {
        LambdaQueryWrapper<Order> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Order::getOrderStatus, status)
               .eq(Order::getIsDeleted, 0)
               .orderByDesc(Order::getCreateTime)
               .last("LIMIT 20");
        return orderMapper.selectList(wrapper);
    }
}