package cn.qiniu.familybot.repository;

import cn.qiniu.familybot.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.List;

/**
 * 用户数据访问层
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    /**
     * 根据用户ID查找用户
     */
    Optional<User> findByUserId(String userId);
    
    /**
     * 根据用户名查找用户
     */
    Optional<User> findByUsername(String username);
    
    /**
     * 根据手机号查找用户
     */
    Optional<User> findByPhone(String phone);
    
    /**
     * 根据状态查找用户
     */
    List<User> findByStatus(User.UserStatus status);
    
    /**
     * 查找活跃用户（指定时间后有活动）
     */
    @Query("SELECT u FROM User u WHERE u.lastActiveTime > :since")
    List<User> findActiveUsersSince(@Param("since") LocalDateTime since);
    
    /**
     * 根据年龄范围查找用户
     */
    @Query("SELECT u FROM User u WHERE u.age BETWEEN :minAge AND :maxAge")
    List<User> findByAgeRange(@Param("minAge") Integer minAge, @Param("maxAge") Integer maxAge);
    
    /**
     * 统计用户总数
     */
    @Query("SELECT COUNT(u) FROM User u WHERE u.status = :status")
    Long countByStatus(@Param("status") User.UserStatus status);
    
    /**
     * 查找近期注册的用户
     */
    @Query("SELECT u FROM User u WHERE u.createdAt > :since ORDER BY u.createdAt DESC")
    List<User> findRecentUsers(@Param("since") LocalDateTime since);
    
    /**
     * 检查用户ID是否存在
     */
    boolean existsByUserId(String userId);
    
    /**
     * 检查用户名是否存在
     */
    boolean existsByUsername(String username);
    
    /**
     * 检查手机号是否存在
     */
    boolean existsByPhone(String phone);
}
