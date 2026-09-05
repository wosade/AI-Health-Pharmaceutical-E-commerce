package com.medicine.agent;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.context.ApplicationContext;
import org.springframework.web.bind.annotation.*;

import java.lang.reflect.Method;
import java.lang.reflect.Parameter;
import java.util.*;

@RestController
@RequestMapping("/api/mcp")
public class McpController {

    private static final Logger log = LoggerFactory.getLogger(McpController.class);

    private final ApplicationContext context;
    private final ObjectMapper objectMapper;

    public McpController(ApplicationContext context, ObjectMapper objectMapper) {
        this.context = context;
        this.objectMapper = objectMapper;
    }

    @GetMapping("/tools")
    public List<Map<String, Object>> listTools() {
        List<Map<String, Object>> tools = new ArrayList<>();
        Map<String, Object> toolBeans = context.getBeansWithAnnotation(org.springframework.stereotype.Component.class);

        for (Map.Entry<String, Object> entry : toolBeans.entrySet()) {
            Object bean = entry.getValue();
            for (Method method : bean.getClass().getDeclaredMethods()) {
                Tool toolAnnotation = method.getAnnotation(Tool.class);
                if (toolAnnotation == null) continue;

                Map<String, Object> tool = new LinkedHashMap<>();
                tool.put("name", method.getName());
                tool.put("description", toolAnnotation.description());
                tool.put("inputSchema", buildInputSchema(method));
                tools.add(tool);
            }
        }
        return tools;
    }

    @PostMapping("/tools/{toolName}/call")
    public Object callTool(@PathVariable String toolName, @RequestBody Map<String, Object> params) {
        Map<String, Object> toolBeans = context.getBeansWithAnnotation(org.springframework.stereotype.Component.class);

        for (Object bean : toolBeans.values()) {
            for (Method method : bean.getClass().getDeclaredMethods()) {
                if (!method.getName().equals(toolName)) continue;
                Tool toolAnnotation = method.getAnnotation(Tool.class);
                if (toolAnnotation == null) continue;

                try {
                    Object[] args = resolveArgs(method, params);
                    return method.invoke(bean, args);
                } catch (Exception e) {
                    log.error("MCP 工具 {} 执行失败", toolName, e);
                    Map<String, String> error = new LinkedHashMap<>();
                    error.put("error", "工具执行失败: " + e.getMessage());
                    return error;
                }
            }
        }

        Map<String, String> error = new LinkedHashMap<>();
        error.put("error", "工具不存在: " + toolName);
        return error;
    }

    private Map<String, Object> buildInputSchema(Method method) {
        Map<String, Object> schema = new LinkedHashMap<>();
        schema.put("type", "object");
        Map<String, Object> properties = new LinkedHashMap<>();
        List<String> required = new ArrayList<>();

        for (Parameter param : method.getParameters()) {
            ToolParam toolParam = param.getAnnotation(ToolParam.class);
            if (toolParam == null) continue;
            Map<String, Object> prop = new LinkedHashMap<>();
            prop.put("type", mapJavaType(param.getType()));
            prop.put("description", toolParam.description());
            properties.put(param.getName(), prop);
            required.add(param.getName());
        }

        schema.put("properties", properties);
        if (!required.isEmpty()) schema.put("required", required);
        return schema;
    }

    private Object[] resolveArgs(Method method, Map<String, Object> params) {
        Object[] args = new Object[method.getParameterCount()];
        Parameter[] parameters = method.getParameters();
        for (int i = 0; i < parameters.length; i++) {
            Object value = params.get(parameters[i].getName());
            if (value != null) {
                args[i] = objectMapper.convertValue(value, parameters[i].getType());
            }
        }
        return args;
    }

    private String mapJavaType(Class<?> type) {
        if (type == String.class) return "string";
        if (type == Integer.class || type == int.class || type == Long.class || type == long.class) return "integer";
        if (type == Double.class || type == double.class || type == Float.class || type == float.class) return "number";
        if (type == Boolean.class || type == boolean.class) return "boolean";
        if (type == List.class) return "array";
        return "string";
    }
}