package cn.qiniu.familybot.service;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

@SpringBootTest
public class AIAgentServiceTest {

    @Autowired
    private AIAgentService aiAgentService;

    @Test
    public void testSendTextMessage() {
        // 测试发送文本消息
        Mono<AIAgentService.AIAgentResponse> response = aiAgentService.sendTextMessage(
            "test_user",
            "xiyang",  // 测试喜羊羊角色
            "你好，最近过得怎么样？"
        );

        StepVerifier.create(response)
            .expectNextMatches(result -> {
                System.out.println("AI响应: " + result.getResponse());
                System.out.println("角色: " + result.getCharacterName());
                System.out.println("情感: " + result.getEmotion());
                System.out.println("意图: " + result.getIntent());
                System.out.println("路由信息: " + result.getRouterInfo());
                System.out.println("RAG增强: " + result.isRagEnhanced());
                System.out.println("CoT增强: " + result.isCotEnhanced());
                if (result.isCotEnhanced()) {
                    System.out.println("CoT步骤数: " + result.getCotStepsCount());
                    System.out.println("CoT分析: " + result.getCotAnalysis());
                }
                return true;
            })
            .verifyComplete();
    }

    @Test
    public void testSendTextMessageToMeiyang() {
        // 测试发送文本消息给美羊羊
        Mono<AIAgentService.AIAgentResponse> response = aiAgentService.sendTextMessage(
            "test_user",
            "meiyang",  // 测试美羊羊角色
            "女儿，我今天感觉有点不舒服。"
        );

        StepVerifier.create(response)
            .expectNextMatches(result -> {
                System.out.println("AI响应: " + result.getResponse());
                System.out.println("角色: " + result.getCharacterName());
                System.out.println("情感: " + result.getEmotion());
                System.out.println("意图: " + result.getIntent());
                System.out.println("路由信息: " + result.getRouterInfo());
                return true;
            })
            .verifyComplete();
    }

    @Test
    public void testSendTextMessageToLanyang() {
        // 测试发送文本消息给懒羊羊
        Mono<AIAgentService.AIAgentResponse> response = aiAgentService.sendTextMessage(
            "test_user",
            "lanyang",  // 测试懒羊羊角色
            "孙子，你最近学习怎么样？"
        );

        StepVerifier.create(response)
            .expectNextMatches(result -> {
                System.out.println("AI响应: " + result.getResponse());
                System.out.println("角色: " + result.getCharacterName());
                System.out.println("情感: " + result.getEmotion());
                System.out.println("意图: " + result.getIntent());
                System.out.println("路由信息: " + result.getRouterInfo());
                return true;
            })
            .verifyComplete();
    }

    @Test
    public void testHealthCheck() {
        // 测试健康检查
        Mono<Boolean> healthStatus = aiAgentService.checkHealth();

        StepVerifier.create(healthStatus)
            .expectNext(true)
            .verifyComplete();
    }

    @Test
    public void testGetCharacters() {
        // 测试获取角色列表
        Mono<JsonNode> characters = aiAgentService.getAvailableCharacters();

        StepVerifier.create(characters)
            .expectNextMatches(result -> {
                System.out.println("可用角色: " + result);
                return true;
            })
            .verifyComplete();
    }
}
