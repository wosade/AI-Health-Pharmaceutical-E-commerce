package com.medicine.agent;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Service
public class AgentService {

    private final ChatClient.Builder chatClientBuilder;
    private final ClientTools clientTools;
    private final AdminTools adminTools;
    private final RagService ragService;
    private final ObjectMapper objectMapper;
    private final ExecutorService executor = Executors.newCachedThreadPool();

    private static final String GATEWAY_PROMPT = """
            你是药智通客户端 AI 助手的意图路由节点。

            分析用户问题，判断属于哪种类型：
            - service_agent: 商品咨询、订单查询、售后服务、优惠券、购物车等电商问题
            - medical_agent: 症状描述、疾病咨询、用药建议、健康问题、身体不适等医疗问题

            输出格式：{"route_target": "service_agent"} 或 {"route_target": "medical_agent"}

            规则：
            - 商品/订单/售后/物流/优惠券 → service_agent
            - 症状/疾病/用药/健康/身体不适 → medical_agent
            - 模糊不清时，默认走 service_agent""";

    private static final String MEDICAL_PROMPT = """
            你是药智通 AI 问诊助手，帮助用户进行症状咨询、疾病判断和药品推荐。

            ## 可用工具
            - searchClientProducts: 搜索药品
            - sendQuestionnaireCard: 发送问诊问卷卡（补充症状信息时用）
            - sendPrescriptionCard: 发送药品推荐确认卡（诊断完成后推荐药品）
            - openUserPatientList: 打开就诊人列表

            ## 核心规则
            1. 红旗信号优先：呼吸困难、高热不退、精神差、症状急剧加重 → 建议立即就医
            2. 先拿就诊人资料，再问症状，再收敛诊断，再推荐药品
            3. 缺信息时用问诊卡追问，不要直接文字追问
            4. 每轮只做一个动作（不要同时发问诊卡和处方卡）
            5. 不凭经验编造药品信息，必须先搜索确认
            6. 用户拒绝推荐药品后，只给护理建议，不发商品卡""";

    private static final String SERVICE_PROMPT = """
            你是药智通客户端客服 AI，帮助用户处理商品咨询、订单查询、售后问题。

            ## 可用工具
            - searchClientProducts: 搜索商品
            - getClientOrder: 查询订单详情
            - openUserOrderList: 打开订单列表

            ## 核心原则
            1. 用户说症状/想买药时，主动搜索商品，不要反问用户"需要我帮您搜索吗"
            2. 找到商品后直接展示，附带价格、库存等信息
            3. 用亲切友好的语气回复
            4. 商品对比时，先搜索确认再对比""";

    private static final String ADMIN_PROMPT = """
            你是药智通管理后台的 AI 助手，帮助运营人员管理药品电商平台。

            ## 可用工具
            - searchOrders: 查询订单（支持按单号、状态、用户ID筛选）
            - searchProducts: 查询商品（支持按名称搜索）
            - searchUsers: 查询用户（支持按用户名、昵称、手机号搜索）
            - searchAfterSales: 查询售后单
            - getAnalytics: 查看运营数据概览

            ## 回复要求
            - 简洁专业，必要时用表格展示数据
            - 先分析用户意图，再调用合适的工具
            - 数据为空时如实说明，不要编造""";

    public AgentService(ChatClient.Builder chatClientBuilder,
                        ClientTools clientTools,
                        AdminTools adminTools,
                        RagService ragService,
                        ObjectMapper objectMapper) {
        this.chatClientBuilder = chatClientBuilder;
        this.clientTools = clientTools;
        this.adminTools = adminTools;
        this.ragService = ragService;
        this.objectMapper = objectMapper;
    }

    public String adminChat(String question) {
        return chatClientBuilder
                .defaultTools(adminTools)
                .build()
                .prompt()
                .system(ADMIN_PROMPT)
                .user(question)
                .call()
                .content();
    }

    public SseEmitter clientChatStream(String question, String conversationUuid) {
        String uuid = conversationUuid != null ? conversationUuid : UUID.randomUUID().toString();
        SseEmitter emitter = new SseEmitter(300000L);

        executor.execute(() -> {
            try {
                String route = routeGateway(question);
                String prompt = "medical_agent".equals(route) ? MEDICAL_PROMPT : SERVICE_PROMPT;

                String ragContext = ragService.searchAsContext(question, 3);
                if (!ragContext.isEmpty()) {
                    prompt = prompt + ragContext;
                }

                ChatClient client = chatClientBuilder
                        .defaultTools(clientTools)
                        .build();

                client.prompt()
                        .system(prompt)
                        .user(question)
                        .stream()
                        .content()
                        .doOnNext(content -> {
                            try {
                                sendSse(emitter, "answer", content);
                            } catch (IOException e) {
                                emitter.completeWithError(e);
                            }
                        })
                        .doOnError(error -> {
                            emitter.completeWithError(error);
                        })
                        .doOnComplete(() -> {
                            try {
                                Map<String, Object> done = Map.of(
                                        "type", "done",
                                        "conversation_uuid", uuid
                                );
                                emitter.send(SseEmitter.event().data(objectMapper.writeValueAsString(done)));
                                emitter.complete();
                            } catch (IOException e) {
                                emitter.completeWithError(e);
                            }
                        })
                        .subscribe();
            } catch (Exception e) {
                try {
                    sendSse(emitter, "error", e.getMessage());
                    emitter.complete();
                } catch (IOException ex) {
                    emitter.completeWithError(ex);
                }
            }
        });

        return emitter;
    }

    private String routeGateway(String question) {
        String response = chatClientBuilder.build()
                .prompt()
                .system(GATEWAY_PROMPT)
                .user(question)
                .call()
                .content();
        try {
            Map<String, String> map = objectMapper.readValue(response, Map.class);
            String route = map.getOrDefault("route_target", "service_agent");
            return "medical_agent".equals(route) ? "medical_agent" : "service_agent";
        } catch (Exception e) {
            return "service_agent";
        }
    }

    private void sendSse(SseEmitter emitter, String type, String content) throws IOException {
        if (content == null || content.isBlank()) {
            return;
        }
        Map<String, Object> event = Map.of("type", type, "content", content);
        emitter.send(SseEmitter.event().data(objectMapper.writeValueAsString(event)));
    }
}