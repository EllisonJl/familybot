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
 * 用户实体类
 * 表示使用FamilyBot的老人用户
 */
@Entity
@Table(name = "users")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /**
     * 用户唯一标识（用于AI系统）
     */
    @Column(name = "user_id", unique = true, nullable = false)
    private String userId;
    
    /**
     * 用户姓名
     */
    @Column(name = "username", nullable = false)
    private String username;
    
    /**
     * 用户昵称
     */
    @Column(name = "nickname")
    private String nickname;
    
    /**
     * 用户年龄
     */
    @Column(name = "age")
    private Integer age;
    
    /**
     * 用户性别 (M/F)
     */
    @Column(name = "gender")
    private String gender;
    
    /**
     * 联系电话
     */
    @Column(name = "phone")
    private String phone;
    
    /**
     * 家庭住址
     */
    @Column(name = "address")
    private String address;
    
    /**
     * 健康状况描述
     */
    @Column(name = "health_status")
    private String healthStatus;
    
    /**
     * 兴趣爱好
     */
    @Column(name = "interests")
    private String interests;
    
    /**
     * 用户偏好设置（JSON格式）
     */
    @Column(name = "preferences", columnDefinition = "TEXT")
    private String preferences;
    
    /**
     * 默认交互角色ID
     */
    @Column(name = "default_character")
    private String defaultCharacter;
    
    /**
     * 用户状态 (ACTIVE/INACTIVE/SUSPENDED)
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private UserStatus status = UserStatus.ACTIVE;
    
    /**
     * 最后活跃时间
     */
    @Column(name = "last_active_time")
    private LocalDateTime lastActiveTime;
    
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
     * 用户的对话记录
     */
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Conversation> conversations;
    
    /**
     * 用户状态枚举
     */
    public enum UserStatus {
        ACTIVE,     // 活跃
        INACTIVE,   // 不活跃
        SUSPENDED   // 暂停
    }
}
