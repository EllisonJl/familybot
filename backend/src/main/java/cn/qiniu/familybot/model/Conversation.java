package cn.qiniu.familybot.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * 对话记录实体类
 * 存储用户与AI角色的对话历史
 */
@Entity
@Table(name = "conversations", indexes = {
    @Index(name = "idx_user_character", columnList = "user_id, character_id"),
    @Index(name = "idx_created_at", columnList = "created_at")
})
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Conversation {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /**
     * 关联用户
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;
    
    /**
     * 关联角色
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "character_id", nullable = false)
    private Character character;
    
    /**
     * 用户输入消息
     */
    @Column(name = "user_message", columnDefinition = "TEXT", nullable = false)
    private String userMessage;
    
    /**
     * AI回复消息
     */
    @Column(name = "assistant_response", columnDefinition = "TEXT", nullable = false)
    private String assistantResponse;
    
    /**
     * 识别的用户意图
     */
    @Column(name = "intent")
    private String intent;
    
    /**
     * 情绪状态
     */
    @Column(name = "emotion")
    private String emotion;
    
    /**
     * 对话类型
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "conversation_type")
    private ConversationType conversationType = ConversationType.TEXT;
    
    /**
     * 会话ID（用于分组相关对话）
     */
    @Column(name = "session_id")
    private String sessionId;
    
    /**
     * 上下文信息（JSON格式）
     */
    @Column(name = "context", columnDefinition = "TEXT")
    private String context;
    
    /**
     * 音频文件路径（如果是语音对话）
     */
    @Column(name = "audio_file_path")
    private String audioFilePath;
    
    /**
     * 对话持续时间（毫秒）
     */
    @Column(name = "duration_ms")
    private Long durationMs;
    
    /**
     * 用户满意度评分 (1-5)
     */
    @Column(name = "satisfaction_score")
    private Integer satisfactionScore;
    
    /**
     * 是否标记为重要
     */
    @Column(name = "is_important")
    private Boolean isImportant = false;
    
    /**
     * 备注信息
     */
    @Column(name = "notes")
    private String notes;
    
    /**
     * 创建时间
     */
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    /**
     * 对话类型枚举
     */
    public enum ConversationType {
        TEXT,   // 文本对话
        VOICE,  // 语音对话
        VIDEO   // 视频对话（未来扩展）
    }
}
