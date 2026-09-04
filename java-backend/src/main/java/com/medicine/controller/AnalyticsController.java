package com.medicine.controller;

import com.medicine.common.Result;
import com.medicine.service.AnalyticsService;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/analytics")
public class AnalyticsController {
    private final AnalyticsService analyticsService;

    public AnalyticsController(AnalyticsService analyticsService) {
        this.analyticsService = analyticsService;
    }

    @GetMapping("/summary")
    public Result<Map<String, Object>> summary() {
        return Result.ok(analyticsService.summary());
    }
}