package com.medicine.agent;

import com.medicine.entity.Order;
import com.medicine.entity.Product;
import com.medicine.service.OrderService;
import com.medicine.service.ProductService;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
public class ClientTools {

    private final ProductService productService;
    private final OrderService orderService;

    public ClientTools(ProductService productService, OrderService orderService) {
        this.productService = productService;
        this.orderService = orderService;
    }

    @Tool(description = "搜索客户端商品。用户想找药、按症状/用途选商品时调用。")
    public List<Product> searchClientProducts(
            @ToolParam(description = "搜索关键词") String keyword) {
        return productService.search(keyword != null ? keyword : "");
    }

    @Tool(description = "查询客户端用户的订单详情。")
    public Order getClientOrder(
            @ToolParam(description = "订单编号") String orderNo) {
        return orderService.getByOrderNo(orderNo);
    }

    @Tool(description = "发送问诊问卷卡，当需要补充症状信息时调用。返回卡片数据让前端渲染。")
    public Map<String, Object> sendQuestionnaireCard(
            @ToolParam(description = "追问问题列表，最多5个") List<String> questions,
            @ToolParam(description = "问诊卡标题") String title) {
        Map<String, Object> card = new HashMap<>();
        card.put("card_type", "questionnaire");
        card.put("title", title != null ? title : "补充问诊信息");
        List<String> qs = questions.size() > 5 ? questions.subList(0, 5) : questions;
        card.put("questions", qs);
        card.put("message", "请用户填写以下问诊信息");
        return card;
    }

    @Tool(description = "发送药品推荐确认卡，当诊断完成需要推荐药品时调用。")
    public Map<String, Object> sendPrescriptionCard(
            @ToolParam(description = "推荐药品名称") String drugName,
            @ToolParam(description = "推荐理由") String reason,
            @ToolParam(description = "参考价格") Double price) {
        Map<String, Object> card = new HashMap<>();
        card.put("card_type", "prescription");
        card.put("drug_name", drugName);
        card.put("reason", reason);
        card.put("price", price != null ? price : 0);
        card.put("message", "推荐药品：" + drugName + "，" + reason);
        return card;
    }

    @Tool(description = "打开就诊人列表，让用户选择就诊人。")
    public Map<String, Object> openUserPatientList() {
        Map<String, Object> card = new HashMap<>();
        card.put("card_type", "patient_list");
        card.put("message", "请选择就诊人");
        return card;
    }

    @Tool(description = "打开用户订单列表，让用户选择订单。")
    public Map<String, Object> openUserOrderList() {
        Map<String, Object> card = new HashMap<>();
        card.put("card_type", "order_list");
        card.put("message", "请选择订单");
        return card;
    }
}