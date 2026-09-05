package com.medicine.agent;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.poi.hwpf.HWPFDocument;
import org.apache.poi.hwpf.extractor.WordExtractor;
import org.apache.poi.xwpf.extractor.XWPFWordExtractor;
import org.apache.poi.xwpf.usermodel.XWPFDocument;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;

@Service
public class DocumentReaderService {

    private static final Logger log = LoggerFactory.getLogger(DocumentReaderService.class);

    public String read(MultipartFile file) throws IOException {
        String filename = file.getOriginalFilename();
        if (filename == null) {
            throw new IllegalArgumentException("文件名为空");
        }

        String lower = filename.toLowerCase();
        if (lower.endsWith(".pdf")) {
            return readPdf(file.getInputStream());
        } else if (lower.endsWith(".docx")) {
            return readDocx(file.getInputStream());
        } else if (lower.endsWith(".doc")) {
            return readDoc(file.getInputStream());
        } else {
            throw new IllegalArgumentException("不支持的文件格式: " + filename + "，仅支持 pdf/doc/docx");
        }
    }

    private String readPdf(InputStream inputStream) throws IOException {
        try (PDDocument document = Loader.loadPDF(inputStream.readAllBytes())) {
            PDFTextStripper stripper = new PDFTextStripper();
            stripper.setSortByPosition(true);
            String text = stripper.getText(document);
            log.info("PDF 解析完成，提取 {} 字符", text.length());
            return text;
        }
    }

    private String readDocx(InputStream inputStream) throws IOException {
        try (XWPFDocument document = new XWPFDocument(inputStream);
             XWPFWordExtractor extractor = new XWPFWordExtractor(document)) {
            String text = extractor.getText();
            log.info("DOCX 解析完成，提取 {} 字符", text.length());
            return text;
        }
    }

    private String readDoc(InputStream inputStream) throws IOException {
        try (HWPFDocument document = new HWPFDocument(inputStream);
             WordExtractor extractor = new WordExtractor(document)) {
            String text = extractor.getText();
            log.info("DOC 解析完成，提取 {} 字符", text.length());
            return text;
        }
    }
}