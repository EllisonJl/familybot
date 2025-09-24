package cn.qiniu.familybot.service;

import cn.qiniu.familybot.dto.ChatRequest;
import cn.qiniu.familybot.dto.ChatResponse;
import cn.qiniu.familybot.dto.CharacterDTO;
import cn.qiniu.familybot.dto.UserDTO;
import cn.qiniu.familybot.model.Character;
import cn.qiniu.familybot.model.Conversation;
import cn.qiniu.familybot.model.User;
import cn.qiniu.familybot.repository.CharacterRepository;
import cn.qiniu.familybot.repository.ConversationRepository;
import cn.qiniu.familybot.repository.UserRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class FamilyBotService {

    private final UserRepository userRepository;
    private final CharacterRepository characterRepository;
    private final ConversationRepository conversationRepository;
    private final WebClient webClient;

    @Value("${familybot.ai-agent.base-url:http://localhost:8001}")
    private String aiAgentBaseUrl;

    public FamilyBotService(UserRepository userRepository, CharacterRepository characterRepository,
                            ConversationRepository conversationRepository, WebClient.Builder webClientBuilder,
                            AIAgentService aiAgentService) {
        this.userRepository = userRepository;
        this.characterRepository = characterRepository;
        this.conversationRepository = conversationRepository;
        this.webClient = webClientBuilder.baseUrl("http://localhost:8001").build();
        this.aiAgentService = aiAgentService;
    }

    // --- User Management ---
    public UserDTO createUser(UserDTO userDTO) {
        User user = new User();
        user.setUsername(userDTO.getUsername());
        user.setNickname(userDTO.getNickname());
        user.setAvatarUrl(userDTO.getAvatarUrl());
        user.setPasswordHash("dummy_hash");
        User savedUser = userRepository.save(user);
        return convertToUserDTO(savedUser);
    }

    public Optional<UserDTO> getUserById(Long id) {
        return userRepository.findById(id).map(this::convertToUserDTO);
    }

    public List<UserDTO> getAllUsers() {
        return userRepository.findAll().stream()
                .map(this::convertToUserDTO)
                .collect(Collectors.toList());
    }

    // --- Character Management ---
    public CharacterDTO createCharacter(CharacterDTO characterDTO) {
        Character character = new Character();
        character.setName(characterDTO.getName());
        character.setFamilyRole(characterDTO.getFamilyRole());
        character.setPersonality(characterDTO.getPersonality());
        character.setVoiceConfig(characterDTO.getVoiceConfig().toString());
        character.setAvatarUrl(characterDTO.getAvatarUrl());
        Character savedCharacter = characterRepository.save(character);
        return convertToCharacterDTO(savedCharacter);
    }

    public Optional<CharacterDTO> getCharacterById(Long id) {
        return characterRepository.findById(id).map(this::convertToCharacterDTO);
    }

    public List<CharacterDTO> getAllCharacters() {
        return characterRepository.findAll().stream()
                .map(this::convertToCharacterDTO)
                .collect(Collectors.toList());
    }

    // --- Chat Functionality ---
    private final AIAgentService aiAgentService;

    public ChatResponse processChat(ChatRequest chatRequest) {
        Optional<User> userOptional = userRepository.findByUserId(chatRequest.getUserId());
        Optional<Character> characterOptional = characterRepository.findByCharacterId(chatRequest.getCharacterId());

        if (userOptional.isEmpty() || characterOptional.isEmpty()) {
            throw new IllegalArgumentException("User or Character not found.");
        }

        User user = userOptional.get();
        Character character = characterOptional.get();
        String characterMappedId = mapCharacterName(character.getName());

        try {
            // 调用AI Agent服务
            AIAgentService.AIAgentResponse aiResponse;
            
            if (chatRequest.getMessage() != null && !chatRequest.getMessage().isEmpty()) {
                // 文本消息
                aiResponse = aiAgentService.sendTextMessage(
                    user.getId().toString(), 
                    characterMappedId, 
                    chatRequest.getMessage()
                ).block();
            } else if (chatRequest.getAudioBase64() != null && !chatRequest.getAudioBase64().isEmpty()) {
                // 语音消息
                aiResponse = aiAgentService.sendAudioMessage(
                    user.getId().toString(), 
                    characterMappedId, 
                    chatRequest.getAudioBase64()
                ).block();
            } else {
                throw new IllegalArgumentException("Either message or audioBase64 must be provided.");
            }

            if (aiResponse != null) {
                // 构建响应
                ChatResponse response = new ChatResponse();
                response.setAiResponseText(aiResponse.getResponse());
                response.setCharacterName(aiResponse.getCharacterName());
                response.setEmotion(aiResponse.getEmotion());
                response.setIntent(aiResponse.getIntent());
                response.setAiAudioUrl(aiResponse.getAudioUrl());
                response.setAudioBase64(aiResponse.getAudioBase64());
                
                // 设置增强功能标识
                response.setRagEnhanced(aiResponse.isRagEnhanced());
                response.setCotEnhanced(aiResponse.isCotEnhanced());
                response.setCotStepsCount(aiResponse.getCotStepsCount());
                response.setCotAnalysis(aiResponse.getCotAnalysis());
                
                // 设置路由和语音配置
                response.setRouterInfo(aiResponse.getRouterInfo());
                response.setVoiceConfig(aiResponse.getVoiceConfig());

                // 保存对话历史
                Conversation conversation = new Conversation();
                conversation.setUser(user);
                conversation.setCharacter(character);
                conversation.setUserMessage(chatRequest.getMessage() != null ? chatRequest.getMessage() : "[Audio Input]");
                conversation.setAssistantResponse(response.getAiResponseText());
                conversation = conversationRepository.save(conversation);

                response.setConversationId(conversation.getId());
                return response;
            } else {
                throw new RuntimeException("No response from AI Agent");
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to get response from AI Agent: " + e.getMessage(), e);
        }
    }
    
    /**
     * 映射角色名称到AI Agent使用的ID
     */
    private String mapCharacterName(String characterName) {
        switch (characterName) {
            case "喜羊羊":
                return "xiyang";
            case "美羊羊":
                return "meiyang";
            case "懒羊羊":
                return "lanyang";
            default:
                return "xiyang"; // 默认
        }
    }

    // --- Conversation History ---
    public List<Conversation> getConversationHistory(Long userId, Long characterId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));
        Character character = characterRepository.findById(characterId)
                .orElseThrow(() -> new IllegalArgumentException("Character not found"));
        return conversationRepository.findByUserAndCharacterOrderByCreatedAtAsc(user, character);
    }

    // --- Helper methods for DTO conversion ---
    private UserDTO convertToUserDTO(User user) {
        UserDTO dto = new UserDTO();
        dto.setUserId(user.getUserId());
        dto.setUsername(user.getUsername());
        dto.setNickname(user.getNickname());
        dto.setAge(user.getAge());
        dto.setGender(user.getGender());
        dto.setPhone(user.getPhone());
        dto.setAddress(user.getAddress());
        dto.setHealthStatus(user.getHealthStatus());
        dto.setInterests(user.getInterests());
        dto.setDefaultCharacter(user.getDefaultCharacter());
        dto.setStatus(user.getStatus().toString());
        dto.setLastActiveTime(user.getLastActiveTime());
        dto.setCreatedAt(user.getCreatedAt());
        return dto;
    }

    private CharacterDTO convertToCharacterDTO(Character character) {
        CharacterDTO dto = new CharacterDTO();
        dto.setCharacterId(character.getCharacterId());
        dto.setName(character.getName());
        dto.setFamilyRole(character.getFamilyRole());
        dto.setPersonality(character.getPersonality());
        dto.setVoiceConfig(java.util.Map.of("config", character.getVoiceConfig()));
        dto.setAvatarUrl(character.getAvatarUrl());
        dto.setGreeting(character.getGreeting());
        dto.setBackgroundUrl(character.getBackgroundUrl());
        dto.setIsDefault(character.getIsDefault());
        dto.setStatus(character.getStatus().toString());
        dto.setSortOrder(character.getSortOrder());
        dto.setCreatedAt(character.getCreatedAt());
        return dto;
    }
    
    // --- Additional Methods ---
    
    /**
     * 获取角色问候语
     */
    public String getCharacterGreeting(String characterId) {
        Optional<Character> character = characterRepository.findByCharacterId(characterId);
        return character.map(Character::getGreeting)
                .orElse("你好！我是你的AI家庭成员，很高兴见到你！");
    }
    
    /**
     * 切换角色
     */
    public String switchCharacter(String userId, String newCharacterId) {
        try {
            Optional<User> userOpt = userRepository.findByUserId(userId);
            if (userOpt.isPresent()) {
                User user = userOpt.get();
                user.setDefaultCharacter(newCharacterId);
                userRepository.save(user);
                return "角色切换成功！";
            }
            return "用户不存在";
        } catch (Exception e) {
            return "角色切换失败：" + e.getMessage();
        }
    }
    
    /**
     * 获取用户统计信息
     */
    public Map<String, Object> getUserStats(String userId) {
        Map<String, Object> stats = new HashMap<>();
        try {
            Optional<User> userOpt = userRepository.findByUserId(userId);
            if (userOpt.isPresent()) {
                User user = userOpt.get();
                stats.put("totalConversations", conversationRepository.countByUser(user));
                stats.put("joinDate", user.getCreatedAt());
                stats.put("lastActive", user.getLastActiveTime());
                stats.put("defaultCharacter", user.getDefaultCharacter());
            }
        } catch (Exception e) {
            stats.put("error", e.getMessage());
        }
        return stats;
    }
    
    /**
     * 获取对话历史（重载方法，支持分页）
     */
    public List<Conversation> getConversationHistory(String userId, String characterId, int page, int size) {
        try {
            Optional<User> userOpt = userRepository.findByUserId(userId);
            Optional<Character> characterOpt = characterRepository.findByCharacterId(characterId);
            
            if (userOpt.isPresent() && characterOpt.isPresent()) {
                return conversationRepository.findByUserAndCharacterOrderByCreatedAtAsc(userOpt.get(), characterOpt.get());
            }
            return new ArrayList<>();
        } catch (Exception e) {
            return new ArrayList<>();
        }
    }
}