package cn.qiniu.familybot.service;

import cn.qiniu.familybot.dto.*;
import cn.qiniu.familybot.model.*;
import cn.qiniu.familybot.repository.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * FamilyBot核心业务服务
 * 协调前端请求与AI Agent的交互
 */
@Service
@RequiredArgsConstructor
@Transactional
public class FamilyBotService {
    
    private final UserRepository userRepository;
    private final CharacterRepository characterRepository;
    private final ConversationRepository conversationRepository;
    private final ObjectMapper objectMapper;
    private final RestTemplate restTemplate;
    
    @Value("${familybot.ai-agent.base-url:http://localhost:8001}")
    private String aiAgentBaseUrl;
    
    /**
     * 处理聊天请求
     */
    public ChatResponse processChat(ChatRequest request) {
        try {
            // 获取或创建用户
            User user = getOrCreateUser(request.getUserId());
            
            // 获取角色
            Character character = getCharacter(request.getCharacterId());
            if (character == null) {
                character = getDefaultCharacter();
            }
            
            // 更新用户最后活跃时间
            user.setLastActiveTime(LocalDateTime.now());
            userRepository.save(user);
            
            // 调用AI Agent
            ChatResponse aiResponse = callAiAgent(request);
            
            // 保存对话记录
            Conversation conversation = saveConversation(user, character, request, aiResponse);
            
            // 构建响应
            aiResponse.setConversationId(conversation.getId());
            aiResponse.setTimestamp(conversation.getCreatedAt());
            
            return aiResponse;
            
        } catch (Exception e) {
            return ChatResponse.builder()
                .characterId(request.getCharacterId())
                .characterName("系统")
                .response("抱歉，我现在有些问题，请稍后再试。")
                .emotion("error")
                .timestamp(LocalDateTime.now())
                .status("ERROR")
                .error(e.getMessage())
                .build();
        }
    }
    
    /**
     * 调用AI Agent服务
     */
    private ChatResponse callAiAgent(ChatRequest request) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            // 构建请求体
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("message", request.getMessage());
            requestBody.put("user_id", request.getUserId());
            requestBody.put("character_id", request.getCharacterId());
            if (request.getContext() != null) {
                requestBody.put("context", request.getContext());
            }
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);
            
            // 发送请求
            ResponseEntity<Map> response = restTemplate.postForEntity(
                aiAgentBaseUrl + "/chat", 
                entity, 
                Map.class
            );
            
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> responseBody = response.getBody();
                
                return ChatResponse.builder()
                    .characterId((String) responseBody.get("character_id"))
                    .characterName((String) responseBody.get("character_name"))
                    .response((String) responseBody.get("response"))
                    .emotion((String) responseBody.get("emotion"))
                    .intent((String) responseBody.get("intent"))
                    .voiceConfig((Map<String, Object>) responseBody.get("voice_config"))
                    .sessionId(request.getSessionId())
                    .status("SUCCESS")
                    .build();
            } else {
                throw new RuntimeException("AI Agent调用失败");
            }
            
        } catch (Exception e) {
            throw new RuntimeException("AI Agent服务不可用: " + e.getMessage());
        }
    }
    
    /**
     * 获取或创建用户
     */
    private User getOrCreateUser(String userId) {
        return userRepository.findByUserId(userId)
            .orElseGet(() -> {
                User newUser = new User();
                newUser.setUserId(userId);
                newUser.setUsername("用户" + userId);
                newUser.setStatus(User.UserStatus.ACTIVE);
                newUser.setDefaultCharacter("xiyang");
                newUser.setLastActiveTime(LocalDateTime.now());
                return userRepository.save(newUser);
            });
    }
    
    /**
     * 获取角色
     */
    private Character getCharacter(String characterId) {
        if (characterId == null || characterId.trim().isEmpty()) {
            return null;
        }
        return characterRepository.findByCharacterId(characterId).orElse(null);
    }
    
    /**
     * 获取默认角色
     */
    private Character getDefaultCharacter() {
        return characterRepository.findDefaultCharacter(Character.CharacterStatus.ACTIVE)
            .orElseGet(() -> {
                // 如果没有默认角色，返回第一个活跃角色
                List<Character> activeCharacters = characterRepository.findByStatus(Character.CharacterStatus.ACTIVE);
                if (!activeCharacters.isEmpty()) {
                    return activeCharacters.get(0);
                }
                
                // 如果没有活跃角色，创建默认角色
                return createDefaultCharacter();
            });
    }
    
    /**
     * 创建默认角色
     */
    private Character createDefaultCharacter() {
        Character defaultChar = new Character();
        defaultChar.setCharacterId("xiyang");
        defaultChar.setName("喜羊羊");
        defaultChar.setFamilyRole("儿子");
        defaultChar.setPersonality("聪明、勇敢、孝顺，总是关心家人的安全和健康");
        defaultChar.setGreeting("爸爸妈妈好！我是你们的儿子喜羊羊，最近工作怎么样？身体还好吗？");
        defaultChar.setStatus(Character.CharacterStatus.ACTIVE);
        defaultChar.setIsDefault(true);
        defaultChar.setSortOrder(1);
        return characterRepository.save(defaultChar);
    }
    
    /**
     * 保存对话记录
     */
    private Conversation saveConversation(User user, Character character, ChatRequest request, ChatResponse response) {
        try {
            Conversation conversation = new Conversation();
            conversation.setUser(user);
            conversation.setCharacter(character);
            conversation.setUserMessage(request.getMessage());
            conversation.setAssistantResponse(response.getResponse());
            conversation.setIntent(response.getIntent());
            conversation.setEmotion(response.getEmotion());
            conversation.setSessionId(request.getSessionId());
            
            if ("VOICE".equals(request.getConversationType())) {
                conversation.setConversationType(Conversation.ConversationType.VOICE);
            } else {
                conversation.setConversationType(Conversation.ConversationType.TEXT);
            }
            
            // 保存上下文信息
            if (request.getContext() != null) {
                conversation.setContext(objectMapper.writeValueAsString(request.getContext()));
            }
            
            return conversationRepository.save(conversation);
            
        } catch (Exception e) {
            throw new RuntimeException("保存对话记录失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取所有角色
     */
    public List<CharacterDTO> getAllCharacters() {
        List<Character> characters = characterRepository.findActiveCharactersSorted(Character.CharacterStatus.ACTIVE);
        
        return characters.stream()
            .map(this::convertToCharacterDTO)
            .collect(Collectors.toList());
    }
    
    /**
     * 转换角色实体为DTO
     */
    private CharacterDTO convertToCharacterDTO(Character character) {
        try {
            Map<String, Object> voiceConfig = new HashMap<>();
            if (character.getVoiceConfig() != null) {
                voiceConfig = objectMapper.readValue(character.getVoiceConfig(), Map.class);
            }
            
            // 获取角色统计信息
            Long conversationCount = conversationRepository.countByCharacter(character);
            Double avgSatisfaction = conversationRepository.getAverageSatisfactionScoreByCharacter(character);
            
            Map<String, Object> stats = new HashMap<>();
            stats.put("conversationCount", conversationCount);
            stats.put("averageSatisfaction", avgSatisfaction);
            
            return CharacterDTO.builder()
                .characterId(character.getCharacterId())
                .name(character.getName())
                .familyRole(character.getFamilyRole())
                .personality(character.getPersonality())
                .voiceConfig(voiceConfig)
                .greeting(character.getGreeting())
                .avatarUrl(character.getAvatarUrl())
                .backgroundUrl(character.getBackgroundUrl())
                .isDefault(character.getIsDefault())
                .status(character.getStatus().name())
                .sortOrder(character.getSortOrder())
                .createdAt(character.getCreatedAt())
                .stats(stats)
                .build();
                
        } catch (Exception e) {
            throw new RuntimeException("转换角色DTO失败: " + e.getMessage());
        }
    }
    
    /**
     * 获取对话历史
     */
    public Page<Conversation> getConversationHistory(String userId, String characterId, int page, int size) {
        User user = userRepository.findByUserId(userId)
            .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        Character character = characterRepository.findByCharacterId(characterId)
            .orElseThrow(() -> new RuntimeException("角色不存在"));
        
        Pageable pageable = PageRequest.of(page, size);
        return conversationRepository.findByUserAndCharacterOrderByCreatedAtDesc(user, character, pageable);
    }
    
    /**
     * 获取用户统计信息
     */
    public Map<String, Object> getUserStats(String userId) {
        User user = userRepository.findByUserId(userId)
            .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        Long totalConversations = conversationRepository.countByUser(user);
        Double avgSatisfaction = conversationRepository.getAverageSatisfactionScoreByUser(user);
        
        // 获取最近7天的对话数
        LocalDateTime weekAgo = LocalDateTime.now().minusDays(7);
        List<Conversation> recentConversations = conversationRepository.findByUserAndTimeRange(
            user, weekAgo, LocalDateTime.now()
        );
        
        Map<String, Object> stats = new HashMap<>();
        stats.put("userId", userId);
        stats.put("totalConversations", totalConversations);
        stats.put("averageSatisfaction", avgSatisfaction);
        stats.put("recentConversations", recentConversations.size());
        stats.put("lastActiveTime", user.getLastActiveTime());
        
        return stats;
    }
    
    /**
     * 切换角色
     */
    public boolean switchCharacter(String userId, String characterId) {
        User user = userRepository.findByUserId(userId)
            .orElseThrow(() -> new RuntimeException("用户不存在"));
        
        Character character = characterRepository.findByCharacterId(characterId)
            .orElseThrow(() -> new RuntimeException("角色不存在"));
        
        if (character.getStatus() != Character.CharacterStatus.ACTIVE) {
            return false;
        }
        
        user.setDefaultCharacter(characterId);
        userRepository.save(user);
        
        return true;
    }
    
    /**
     * 获取角色问候语
     */
    public String getCharacterGreeting(String characterId) {
        Character character = characterRepository.findByCharacterId(characterId)
            .orElseThrow(() -> new RuntimeException("角色不存在"));
        
        return character.getGreeting();
    }
}
