package com.medicine.controller;

import com.medicine.common.Result;
import com.medicine.entity.Product;
import com.medicine.service.ProductService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/products")
@RequiredArgsConstructor
public class ProductController {
    private final ProductService productService;

    @GetMapping
    public Result<List<Product>> search(@RequestParam(defaultValue = "") String keyword) {
        return Result.ok(productService.search(keyword));
    }

    @GetMapping("/{id}")
    public Result<Product> detail(@PathVariable Long id) {
        return Result.ok(productService.getById(id));
    }
}