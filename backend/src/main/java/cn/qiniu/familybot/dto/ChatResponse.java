package cn.qiniu.familybot.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * 聊天响应DTO
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChatResponse {
    
    /**
     * 角色ID
     */
    private String characterId;
    
    /**
     * 角色名称
     */
    private String characterName;
    
    /**
     * AI回复内容
     */
    private String response;
    
    /**
     * 情绪状态
     */
    private String emotion;
    
    /**
     * 识别的意图
     */
    private String intent;
    
    /**
     * 会话ID
     */
    private String sessionId;
    
    /**
     * 语音配置（TTS参数）
     */
    private Map<String, Object> voiceConfig;
    
    /**
     * 音频URL（如果是语音回复）
     */
    private String audioUrl;
    
    /**
     * 响应时间戳
     */
    private LocalDateTime timestamp;
    
    /**
     * 对话ID
     */
    private Long conversationId;
    
    /**
     * 响应状态
     */
    private String status = "SUCCESS";
    
    /**
     * 错误信息（如果有）
     */
    private String error;
}
