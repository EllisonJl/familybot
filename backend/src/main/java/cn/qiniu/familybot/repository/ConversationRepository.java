package cn.qiniu.familybot.repository;

import cn.qiniu.familybot.model.Conversation;
import cn.qiniu.familybot.model.User;
import cn.qiniu.familybot.model.Character;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 对话记录数据访问层
 */
@Repository
public interface ConversationRepository extends JpaRepository<Conversation, Long> {
    
    /**
     * 根据用户和角色查找对话记录（分页）
     */
    Page<Conversation> findByUserAndCharacterOrderByCreatedAtDesc(
        User user, 
        Character character, 
        Pageable pageable
    );
    
    /**
     * 根据用户查找对话记录（分页）
     */
    Page<Conversation> findByUserOrderByCreatedAtDesc(User user, Pageable pageable);
    
    /**
     * 根据角色查找对话记录（分页）
     */
    Page<Conversation> findByCharacterOrderByCreatedAtDesc(Character character, Pageable pageable);
    
    /**
     * 根据会话ID查找对话记录
     */
    List<Conversation> findBySessionIdOrderByCreatedAtAsc(String sessionId);
    
    /**
     * 查找用户与特定角色的最近对话
     */
    @Query("SELECT c FROM Conversation c WHERE c.user = :user AND c.character = :character " +
           "ORDER BY c.createdAt DESC")
    List<Conversation> findRecentConversations(
        @Param("user") User user, 
        @Param("character") Character character, 
        Pageable pageable
    );
    
    /**
     * 统计用户与角色的对话总数
     */
    @Query("SELECT COUNT(c) FROM Conversation c WHERE c.user = :user AND c.character = :character")
    Long countByUserAndCharacter(@Param("user") User user, @Param("character") Character character);
    
    /**
     * 统计用户的对话总数
     */
    Long countByUser(User user);
    
    /**
     * 统计角色的对话总数
     */
    Long countByCharacter(Character character);
    
    /**
     * 查找指定时间范围内的对话
     */
    @Query("SELECT c FROM Conversation c WHERE c.createdAt BETWEEN :startTime AND :endTime " +
           "ORDER BY c.createdAt DESC")
    List<Conversation> findByTimeRange(
        @Param("startTime") LocalDateTime startTime, 
        @Param("endTime") LocalDateTime endTime
    );
    
    /**
     * 查找用户在指定时间范围内的对话
     */
    @Query("SELECT c FROM Conversation c WHERE c.user = :user " +
           "AND c.createdAt BETWEEN :startTime AND :endTime ORDER BY c.createdAt DESC")
    List<Conversation> findByUserAndTimeRange(
        @Param("user") User user,
        @Param("startTime") LocalDateTime startTime, 
        @Param("endTime") LocalDateTime endTime
    );
    
    /**
     * 根据对话类型查找对话
     */
    List<Conversation> findByConversationType(Conversation.ConversationType type);
    
    /**
     * 查找重要对话
     */
    @Query("SELECT c FROM Conversation c WHERE c.isImportant = true ORDER BY c.createdAt DESC")
    List<Conversation> findImportantConversations();
    
    /**
     * 根据情绪状态查找对话
     */
    List<Conversation> findByEmotion(String emotion);
    
    /**
     * 根据意图查找对话
     */
    List<Conversation> findByIntent(String intent);
    
    /**
     * 查找有满意度评分的对话
     */
    @Query("SELECT c FROM Conversation c WHERE c.satisfactionScore IS NOT NULL " +
           "ORDER BY c.createdAt DESC")
    List<Conversation> findConversationsWithSatisfactionScore();
    
    /**
     * 统计平均满意度评分
     */
    @Query("SELECT AVG(c.satisfactionScore) FROM Conversation c WHERE c.satisfactionScore IS NOT NULL")
    Double getAverageSatisfactionScore();
    
    /**
     * 统计用户的平均满意度评分
     */
    @Query("SELECT AVG(c.satisfactionScore) FROM Conversation c " +
           "WHERE c.user = :user AND c.satisfactionScore IS NOT NULL")
    Double getAverageSatisfactionScoreByUser(@Param("user") User user);
    
    /**
     * 统计角色的平均满意度评分
     */
    @Query("SELECT AVG(c.satisfactionScore) FROM Conversation c " +
           "WHERE c.character = :character AND c.satisfactionScore IS NOT NULL")
    Double getAverageSatisfactionScoreByCharacter(@Param("character") Character character);
    
    /**
     * 删除指定时间之前的对话记录
     */
    @Query("DELETE FROM Conversation c WHERE c.createdAt < :cutoffTime")
    void deleteOldConversations(@Param("cutoffTime") LocalDateTime cutoffTime);
}
