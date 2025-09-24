package cn.qiniu.familybot.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 角色实体类
 * 表示AI陪伴角色（喜羊羊、美羊羊、懒羊羊等）
 */
@Entity
@Table(name = "characters")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Character {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /**
     * 角色唯一标识
     */
    @Column(name = "character_id", unique = true, nullable = false)
    private String characterId;
    
    /**
     * 角色名称
     */
    @Column(name = "name", nullable = false)
    private String name;
    
    /**
     * 角色扮演的家庭关系
     */
    @Column(name = "family_role", nullable = false)
    private String familyRole;
    
    /**
     * 角色性格描述
     */
    @Column(name = "personality", columnDefinition = "TEXT")
    private String personality;
    
    /**
     * 语音配置
     */
    @Column(name = "voice_config", columnDefinition = "TEXT")
    private String voiceConfig;
    
    /**
     * 问候语
     */
    @Column(name = "greeting", columnDefinition = "TEXT")
    private String greeting;
    
    /**
     * 系统提示词
     */
    @Column(name = "system_prompt", columnDefinition = "TEXT")
    private String systemPrompt;
    
    /**
     * 角色头像URL
     */
    @Column(name = "avatar_url")
    private String avatarUrl;
    
    /**
     * 角色背景图URL
     */
    @Column(name = "background_url")
    private String backgroundUrl;
    
    /**
     * 角色状态
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private CharacterStatus status = CharacterStatus.ACTIVE;
    
    /**
     * 排序权重
     */
    @Column(name = "sort_order")
    private Integer sortOrder = 0;
    
    /**
     * 是否为默认角色
     */
    @Column(name = "is_default")
    private Boolean isDefault = false;
    
    /**
     * 角色配置（JSON格式，包含扩展配置）
     */
    @Column(name = "config", columnDefinition = "TEXT")
    private String config;
    
    /**
     * 创建时间
     */
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    /**
     * 更新时间
     */
    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;
    
    /**
     * 角色的对话记录
     */
    @OneToMany(mappedBy = "character", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Conversation> conversations;
    
    /**
     * 角色状态枚举
     */
    public enum CharacterStatus {
        ACTIVE,     // 活跃
        INACTIVE,   // 不活跃
        MAINTENANCE // 维护中
    }
}
