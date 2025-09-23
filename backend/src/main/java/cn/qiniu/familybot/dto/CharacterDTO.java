package cn.qiniu.familybot.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * 角色DTO
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CharacterDTO {
    
    /**
     * 角色ID
     */
    private String characterId;
    
    /**
     * 角色名称
     */
    private String name;
    
    /**
     * 家庭角色
     */
    private String familyRole;
    
    /**
     * 性格描述
     */
    private String personality;
    
    /**
     * 语音配置
     */
    private Map<String, Object> voiceConfig;
    
    /**
     * 问候语
     */
    private String greeting;
    
    /**
     * 头像URL
     */
    private String avatarUrl;
    
    /**
     * 背景图URL
     */
    private String backgroundUrl;
    
    /**
     * 是否为默认角色
     */
    private Boolean isDefault;
    
    /**
     * 角色状态
     */
    private String status;
    
    /**
     * 排序权重
     */
    private Integer sortOrder;
    
    /**
     * 创建时间
     */
    private LocalDateTime createdAt;
    
    /**
     * 统计信息
     */
    private Map<String, Object> stats;
}
