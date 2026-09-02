package com.medicine.controller;

import com.medicine.common.Result;
import com.medicine.entity.User;
import com.medicine.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @GetMapping
    public Result<List<User>> search(@RequestParam(defaultValue = "") String keyword) {
        return Result.ok(userService.search(keyword));
    }

    @GetMapping("/{id}")
    public Result<User> detail(@PathVariable Long id) {
        return Result.ok(userService.getById(id));
    }
}