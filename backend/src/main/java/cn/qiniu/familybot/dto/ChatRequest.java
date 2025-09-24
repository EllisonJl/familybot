package cn.qiniu.familybot.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.util.Map;

/**
 * 聊天请求DTO
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ChatRequest {
    
    /**
     * 用户输入消息
     */
    private String message;
    
    /**
     * 用户ID
     */
    private String userId;
    
    /**
     * 角色ID
     */
    private String characterId;
    
    /**
     * 会话ID（可选）
     */
    private String sessionId;
    
    /**
     * 上下文信息
     */
    private Map<String, Object> context;
    
    /**
     * 对话类型 (TEXT/VOICE)
     */
    private String conversationType = "TEXT";
}
