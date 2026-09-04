package com.medicine.agent;

public class ChatRequest {
    private String question;
    private String conversationUuid;

    public String getQuestion() { return question; }
    public void setQuestion(String question) { this.question = question; }
    public String getConversationUuid() { return conversationUuid; }
    public void setConversationUuid(String conversationUuid) { this.conversationUuid = conversationUuid; }
}