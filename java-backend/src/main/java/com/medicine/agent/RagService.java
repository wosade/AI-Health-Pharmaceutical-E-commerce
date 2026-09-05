package com.medicine.agent;

import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.document.Document;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class RagService {

    private static final Logger log = LoggerFactory.getLogger(RagService.class);

    private final EmbeddingModel embeddingModel;
    private VectorStore vectorStore;

    public RagService(EmbeddingModel embeddingModel) {
        this.embeddingModel = embeddingModel;
    }

    @PostConstruct
    public void init() {
        this.vectorStore = SimpleVectorStore.builder(embeddingModel).build();
        log.info("RAG 向量存储初始化完成");
    }

    public void addDocument(String content, Map<String, Object> metadata) {
        Document doc = new Document(content, metadata);
        vectorStore.add(List.of(doc));
        log.info("RAG 文档已入库: {}", metadata.getOrDefault("title", "无标题"));
    }

    public void addDocuments(List<Document> documents) {
        vectorStore.add(documents);
        log.info("RAG 批量入库 {} 条文档", documents.size());
    }

    public List<Document> search(String query, int topK) {
        return vectorStore.similaritySearch(
                SearchRequest.builder().query(query).topK(topK).build()
        );
    }

    public String searchAsContext(String query, int topK) {
        List<Document> docs = search(query, topK);
        if (docs.isEmpty()) {
            return "";
        }
        StringBuilder sb = new StringBuilder();
        sb.append("\n\n【知识库参考内容】\n");
        for (int i = 0; i < docs.size(); i++) {
            sb.append("--- 参考资料 ").append(i + 1).append(" ---\n");
            sb.append(docs.get(i).getText()).append("\n");
        }
        return sb.toString();
    }
}