package com.medicine.controller;

import com.medicine.common.Result;
import com.medicine.entity.Order;
import com.medicine.service.OrderService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {
    private final OrderService orderService;

    @GetMapping
    public Result<List<Order>> list(@RequestParam Long userId) {
        return Result.ok(orderService.listByUser(userId));
    }

    @GetMapping("/{orderNo}")
    public Result<Order> detail(@PathVariable String orderNo) {
        return Result.ok(orderService.getByOrderNo(orderNo));
    }

    @GetMapping("/status/{status}")
    public Result<List<Order>> listByStatus(@PathVariable String status) {
        return Result.ok(orderService.listByStatus(status));
    }
}