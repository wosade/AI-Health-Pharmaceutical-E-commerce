package com.medicine.controller;

import com.medicine.common.Result;
import com.medicine.entity.Product;
import com.medicine.service.ProductService;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/products")
public class ProductController {
    private final ProductService productService;

    public ProductController(ProductService productService) {
        this.productService = productService;
    }

    @GetMapping
    public Result<List<Product>> search(@RequestParam(defaultValue = "") String keyword) {
        return Result.ok(productService.search(keyword));
    }

    @GetMapping("/{id}")
    public Result<Product> detail(@PathVariable Long id) {
        return Result.ok(productService.getById(id));
    }
}