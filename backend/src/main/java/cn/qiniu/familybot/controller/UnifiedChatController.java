package cn.qiniu.familybot.controller;

import cn.qiniu.familybot.dto.ChatRequest;
import cn.qiniu.familybot.dto.ChatResponse;
import cn.qiniu.familybot.service.FamilyBotService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * 统一聊天控制器
 * 提供单一API端点，前端只需要与这个控制器交互
 */
@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "http://localhost:5173")
public class UnifiedChatController {

    private static final Logger logger = LoggerFactory.getLogger(UnifiedChatController.class);
    private final FamilyBotService familyBotService;

    public UnifiedChatController(FamilyBotService familyBotService) {
        this.familyBotService = familyBotService;
    }

    /**
     * 统一聊天接口 - 支持文本和语音
     * 前端只需要调用这一个接口
     */
    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest chatRequest) {
        logger.info("收到聊天请求: 用户ID={}, 角色ID={}, 消息类型={}", 
                   chatRequest.getUserId(), 
                   chatRequest.getCharacterId(),
                   (chatRequest.getMessage() != null ? "文本" : "语音"));

        try {
            // 参数验证
            if (chatRequest.getUserId() == null) {
                throw new IllegalArgumentException("用户ID不能为空");
            }
            if (chatRequest.getCharacterId() == null) {
                throw new IllegalArgumentException("角色ID不能为空");
            }
            if ((chatRequest.getMessage() == null || chatRequest.getMessage().trim().isEmpty()) && 
                (chatRequest.getAudioBase64() == null || chatRequest.getAudioBase64().trim().isEmpty())) {
                throw new IllegalArgumentException("消息内容或语音数据不能为空");
            }

            // 调用AI服务处理
            ChatResponse response = familyBotService.processChat(chatRequest);
            
            logger.info("聊天处理成功: 角色={}, 响应长度={}", 
                       response.getCharacterName(), 
                       response.getResponse() != null ? response.getResponse().length() : 0);

            return ResponseEntity.ok(response);

        } catch (IllegalArgumentException e) {
            logger.error("聊天请求参数错误: {}", e.getMessage());
            return ResponseEntity.badRequest()
                    .body(ChatResponse.builder()
                            .status("ERROR")
                            .error("请求参数无效: " + e.getMessage())
                            .build());
        } catch (Exception e) {
            logger.error("聊天处理失败", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(ChatResponse.builder()
                            .status("ERROR") 
                            .error("聊天服务暂时不可用，请稍后再试")
                            .build());
        }
    }

    /**
     * 健康检查接口
     */
    @GetMapping("/chat/health")
    public ResponseEntity<String> healthCheck() {
        // TODO: 检查AI Agent服务状态
        return ResponseEntity.ok("Chat service is running");
    }
}
