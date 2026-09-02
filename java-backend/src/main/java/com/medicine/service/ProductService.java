package com.medicine.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.medicine.entity.Product;
import com.medicine.mapper.ProductMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ProductService {
    private final ProductMapper productMapper;

    public List<Product> search(String keyword) {
        LambdaQueryWrapper<Product> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Product::getIsDeleted, 0)
               .eq(Product::getStatus, 1)
               .like(Product::getName, keyword)
               .orderByDesc(Product::getCreateTime)
               .last("LIMIT 10");
        return productMapper.selectList(wrapper);
    }

    public Product getById(Long id) {
        return productMapper.selectById(id);
    }
}