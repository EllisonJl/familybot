package cn.qiniu.familybot.repository;

import cn.qiniu.familybot.model.Character;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.List;

/**
 * 角色数据访问层
 */
@Repository
public interface CharacterRepository extends JpaRepository<Character, Long> {
    
    /**
     * 根据角色ID查找角色
     */
    Optional<Character> findByCharacterId(String characterId);
    
    /**
     * 根据状态查找角色
     */
    List<Character> findByStatus(Character.CharacterStatus status);
    
    /**
     * 查找活跃角色并按排序权重排序
     */
    @Query("SELECT c FROM Character c WHERE c.status = :status ORDER BY c.sortOrder ASC, c.createdAt ASC")
    List<Character> findActiveCharactersSorted(@Param("status") Character.CharacterStatus status);
    
    /**
     * 查找默认角色
     */
    @Query("SELECT c FROM Character c WHERE c.isDefault = true AND c.status = :status")
    Optional<Character> findDefaultCharacter(@Param("status") Character.CharacterStatus status);
    
    /**
     * 根据家庭角色查找角色
     */
    List<Character> findByFamilyRole(String familyRole);
    
    /**
     * 根据角色名称查找角色
     */
    Optional<Character> findByName(String name);
    
    /**
     * 检查角色ID是否存在
     */
    boolean existsByCharacterId(String characterId);
    
    /**
     * 检查角色名称是否存在
     */
    boolean existsByName(String name);
    
    /**
     * 统计活跃角色数量
     */
    @Query("SELECT COUNT(c) FROM Character c WHERE c.status = :status")
    Long countByStatus(@Param("status") Character.CharacterStatus status);
}
