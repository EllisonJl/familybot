package cn.qiniu.familybot.controller;

import cn.qiniu.familybot.dto.*;
import cn.qiniu.familybot.model.Conversation;
import cn.qiniu.familybot.service.FamilyBotService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * FamilyBot主控制器
 * 提供聊天、角色管理、历史记录等API
 */
@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
@CrossOrigin(originPatterns = {"http://localhost:*", "http://127.0.0.1:*"}, allowCredentials = "true")
public class FamilyBotController {
    
    private final FamilyBotService familyBotService;
    
    /**
     * 文本聊天接口
     */
    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest request) {
        try {
            ChatResponse response = familyBotService.processChat(request);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ChatResponse errorResponse = ChatResponse.builder()
                .characterId(request.getCharacterId())
                .characterName("系统")
                .response("抱歉，服务暂时不可用，请稍后重试。")
                .emotion("error")
                .status("ERROR")
                .error(e.getMessage())
                .build();
            
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }
    
    /**
     * 获取所有可用角色
     */
    @GetMapping("/characters")
    public ResponseEntity<List<CharacterDTO>> getCharacters() {
        try {
            List<CharacterDTO> characters = familyBotService.getAllCharacters();
            return ResponseEntity.ok(characters);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 获取角色问候语
     */
    @GetMapping("/characters/{characterId}/greeting")
    public ResponseEntity<Map<String, String>> getCharacterGreeting(@PathVariable String characterId) {
        try {
            String greeting = familyBotService.getCharacterGreeting(characterId);
            return ResponseEntity.ok(Map.of(
                "characterId", characterId,
                "greeting", greeting
            ));
        } catch (Exception e) {
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 切换角色
     */
    @PostMapping("/characters/{characterId}/switch")
    public ResponseEntity<Map<String, Object>> switchCharacter(
        @PathVariable String characterId,
        @RequestParam String userId
    ) {
        try {
            String result = familyBotService.switchCharacter(userId, characterId);
            
            if (result.contains("成功")) {
                return ResponseEntity.ok(Map.of(
                    "success", true,
                    "message", result,
                    "characterId", characterId
                ));
            } else {
                return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "message", result
                ));
            }
        } catch (Exception e) {
            return ResponseEntity.internalServerError().body(Map.of(
                "success", false,
                "message", "角色切换失败: " + e.getMessage()
            ));
        }
    }
    
    /**
     * 获取对话历史
     */
    @GetMapping("/conversations")
    public ResponseEntity<List<Conversation>> getConversationHistory(
        @RequestParam String userId,
        @RequestParam String characterId,
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "20") int size
    ) {
        try {
            List<Conversation> conversations = familyBotService.getConversationHistory(
                userId, characterId, page, size
            );
            return ResponseEntity.ok(conversations);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 获取用户统计信息
     */
    @GetMapping("/users/{userId}/stats")
    public ResponseEntity<Map<String, Object>> getUserStats(@PathVariable String userId) {
        try {
            Map<String, Object> stats = familyBotService.getUserStats(userId);
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 获取所有用户
     */
    @GetMapping("/users")
    public ResponseEntity<List<Map<String, Object>>> getAllUsers() {
        try {
            // 返回简化的用户列表，实际项目中应该有专门的UserDTO
            List<Map<String, Object>> users = familyBotService.getAllUsers();
            return ResponseEntity.ok(users);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
    
    /**
     * 创建用户
     */
    @PostMapping("/users")
    public ResponseEntity<Map<String, Object>> createUser(@RequestBody Map<String, String> userRequest) {
        try {
            Map<String, Object> user = familyBotService.createUserSimple(userRequest);
            return ResponseEntity.ok(user);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }

    /**
     * 健康检查
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        return ResponseEntity.ok(Map.of(
            "status", "healthy",
            "service", "FamilyBot Backend",
            "timestamp", System.currentTimeMillis()
        ));
    }
    
    /**
     * 服务信息
     */
    @GetMapping("/info")
    public ResponseEntity<Map<String, Object>> getServiceInfo() {
        return ResponseEntity.ok(Map.of(
            "serviceName", "FamilyBot Backend",
            "version", "1.0.0",
            "description", "面向留守老人的AI陪伴系统后端服务",
            "features", List.of(
                "多角色AI对话",
                "语音交互支持", 
                "对话历史管理",
                "用户偏好学习",
                "情绪识别分析"
            )
        ));
    }
}
