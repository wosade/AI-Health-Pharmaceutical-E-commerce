package com.medicine.agent;

import com.medicine.common.Result;
import org.springframework.ai.document.Document;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/rag")
public class RagController {

    private final RagService ragService;
    private final DocumentReaderService documentReaderService;

    public RagController(RagService ragService, DocumentReaderService documentReaderService) {
        this.ragService = ragService;
        this.documentReaderService = documentReaderService;
    }

    @PostMapping("/add")
    public Result<String> addDocument(@RequestBody Map<String, Object> body) {
        String content = (String) body.get("content");
        @SuppressWarnings("unchecked")
        Map<String, Object> metadata = (Map<String, Object>) body.getOrDefault("metadata", Map.of());
        ragService.addDocument(content, metadata);
        return Result.ok("文档已入库");
    }

    @PostMapping("/upload")
    public Result<String> uploadFile(@RequestParam("file") MultipartFile file) {
        try {
            String content = documentReaderService.read(file);
            String filename = file.getOriginalFilename();
            Map<String, Object> metadata = Map.of(
                    "title", filename != null ? filename : "未知文件",
                    "source", "upload"
            );
            ragService.addDocument(content, metadata);
            return Result.ok("文件 " + filename + " 解析入库成功");
        } catch (Exception e) {
            return Result.fail("文件解析失败: " + e.getMessage());
        }
    }

    @PostMapping("/search")
    public Result<List<Document>> search(@RequestBody Map<String, Object> body) {
        String query = (String) body.get("query");
        int topK = (int) body.getOrDefault("topK", 5);
        List<Document> docs = ragService.search(query, topK);
        return Result.ok(docs);
    }
}