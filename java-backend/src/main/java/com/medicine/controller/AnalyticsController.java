package com.medicine.controller;

import com.medicine.common.Result;
import com.medicine.service.AnalyticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/analytics")
@RequiredArgsConstructor
public class AnalyticsController {
    private final AnalyticsService analyticsService;

    @GetMapping("/summary")
    public Result<Map<String, Object>> summary() {
        return Result.ok(analyticsService.summary());
    }
}