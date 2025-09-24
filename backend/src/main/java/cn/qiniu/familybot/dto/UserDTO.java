package cn.qiniu.familybot.dto;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * 用户DTO
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserDTO {
    
    /**
     * 用户ID
     */
    private String userId;
    
    /**
     * 用户名
     */
    private String username;
    
    /**
     * 昵称
     */
    private String nickname;
    
    /**
     * 年龄
     */
    private Integer age;
    
    /**
     * 性别
     */
    private String gender;
    
    /**
     * 联系电话
     */
    private String phone;
    
    /**
     * 家庭住址
     */
    private String address;
    
    /**
     * 健康状况
     */
    private String healthStatus;
    
    /**
     * 兴趣爱好
     */
    private String interests;
    
    /**
     * 用户偏好
     */
    private Map<String, Object> preferences;
    
    /**
     * 默认角色
     */
    private String defaultCharacter;
    
    /**
     * 用户状态
     */
    private String status;
    
    /**
     * 最后活跃时间
     */
    private LocalDateTime lastActiveTime;
    
    /**
     * 创建时间
     */
    private LocalDateTime createdAt;
    
    /**
     * 统计信息
     */
    private Map<String, Object> stats;
}
