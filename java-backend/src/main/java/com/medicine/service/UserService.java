package com.medicine.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.medicine.entity.User;
import com.medicine.mapper.UserMapper;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class UserService {
    private final UserMapper userMapper;

    public UserService(UserMapper userMapper) {
        this.userMapper = userMapper;
    }

    public List<User> search(String keyword) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getIsDelete, 0)
               .and(w -> w.like(User::getNickname, keyword)
                          .or().like(User::getPhoneNumber, keyword)
                          .or().like(User::getRealName, keyword))
               .last("LIMIT 10");
        return userMapper.selectList(wrapper);
    }

    public User getById(Long id) {
        return userMapper.selectById(id);
    }
}