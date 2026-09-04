package com.medicine.agent;

import com.medicine.common.Result;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/agent")
public class AgentController {

    private final AgentService agentService;

    public AgentController(AgentService agentService) {
        this.agentService = agentService;
    }

    @PostMapping("/admin/chat")
    public Result<Map<String, String>> adminChat(@RequestBody ChatRequest req) {
        String answer = agentService.adminChat(req.getQuestion());
        String uuid = req.getConversationUuid() != null
                ? req.getConversationUuid()
                : UUID.randomUUID().toString();
        return Result.ok(Map.of("answer", answer, "conversation_uuid", uuid));
    }

    @PostMapping("/client/chat")
    public SseEmitter clientChat(@RequestBody ChatRequest req) {
        return agentService.clientChatStream(req.getQuestion(), req.getConversationUuid());
    }
}