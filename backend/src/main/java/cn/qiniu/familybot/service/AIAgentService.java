package cn.qiniu.familybot.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

/**
 * AI Agent 服务集成
 * 负责与Python AI Agent通信
 */
@Service
public class AIAgentService {

    private final WebClient webClient;
    private final ObjectMapper objectMapper;

    @Value("${familybot.ai-agent.base-url:http://localhost:8001}")
    private String aiAgentBaseUrl;

    public AIAgentService(WebClient.Builder webClientBuilder, ObjectMapper objectMapper) {
        this.webClient = webClientBuilder
                .baseUrl("http://localhost:8001")
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(10 * 1024 * 1024))
                .build();
        this.objectMapper = objectMapper;
    }

    /**
     * 发送文本消息到AI Agent
     */
    public Mono<AIAgentResponse> sendTextMessage(String userId, String characterId, String message) {
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("user_id", userId);
        requestBody.put("character_id", characterId);
        requestBody.put("message", message);
        requestBody.put("use_agent", true);
        requestBody.put("role", "elderly");
        requestBody.put("thread_id", userId + "_" + characterId);  // 使用固定的thread_id以保持对话连续性

        return webClient.post()
                .uri("/chat")
                .bodyValue(requestBody)
                .retrieve()
                .bodyToMono(JsonNode.class)
                .timeout(Duration.ofSeconds(60))
                .map(this::parseAIResponse)
                .onErrorMap(ex -> new RuntimeException("AI Agent调用失败: " + ex.getMessage(), ex));
    }

    /**
     * 发送语音消息到AI Agent
     */
    public Mono<AIAgentResponse> sendAudioMessage(String userId, String characterId, String audioBase64) {
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("user_id", userId);
        requestBody.put("character_id", characterId);
        requestBody.put("audio_base64", audioBase64);
        requestBody.put("use_agent", true);
        requestBody.put("role", "elderly");
        requestBody.put("thread_id", userId + "_" + characterId);  // 使用固定的thread_id以保持对话连续性

        return webClient.post()
                .uri("/chat/audio")
                .bodyValue(requestBody)
                .retrieve()
                .bodyToMono(JsonNode.class)
                .timeout(Duration.ofSeconds(45))
                .map(this::parseAIResponse)
                .onErrorMap(ex -> new RuntimeException("AI Agent语音调用失败: " + ex.getMessage(), ex));
    }

    /**
     * 检查AI Agent健康状态
     */
    public Mono<Boolean> checkHealth() {
        return webClient.get()
                .uri("/")
                .retrieve()
                .bodyToMono(String.class)
                .timeout(Duration.ofSeconds(5))
                .map(response -> true)
                .onErrorReturn(false);
    }

    /**
     * 获取可用角色列表
     */
    public Mono<JsonNode> getAvailableCharacters() {
        return webClient.get()
                .uri("/characters")
                .retrieve()
                .bodyToMono(JsonNode.class)
                .timeout(Duration.ofSeconds(10))
                .onErrorMap(ex -> new RuntimeException("获取角色列表失败: " + ex.getMessage(), ex));
    }

    /**
     * 解析AI Agent响应
     */
    private AIAgentResponse parseAIResponse(JsonNode jsonNode) {
        try {
            AIAgentResponse response = new AIAgentResponse();
            response.setCharacterId(jsonNode.path("character_id").asText());
            response.setCharacterName(jsonNode.path("character_name").asText());
            response.setResponse(jsonNode.path("response").asText());
            response.setEmotion(jsonNode.path("emotion").asText());
            response.setIntent(jsonNode.path("intent").asText());
            
            // 语音配置
            JsonNode voiceConfig = jsonNode.path("voice_config");
            if (!voiceConfig.isMissingNode()) {
                Map<String, Object> voiceMap = objectMapper.convertValue(voiceConfig, Map.class);
                response.setVoiceConfig(voiceMap);
            }
            
            // 路由信息
            JsonNode routerInfo = jsonNode.path("router_info");
            if (!routerInfo.isMissingNode()) {
                Map<String, Object> routerMap = objectMapper.convertValue(routerInfo, Map.class);
                response.setRouterInfo(routerMap);
            }
            
            // RAG增强标识
            response.setRagEnhanced(jsonNode.path("rag_enhanced").asBoolean(false));
            
            // CoT推理标识
            JsonNode context = jsonNode.path("context");
            if (!context.isMissingNode() && context.has("cot_reasoning")) {
                response.setCotEnhanced(true);
                JsonNode cotInfo = context.path("cot_reasoning");
                response.setCotStepsCount(cotInfo.path("steps_count").asInt(0));
                response.setCotAnalysis(cotInfo.path("analysis").asText());
            }
            
            // 语音URL（如果有）
            response.setAudioUrl(jsonNode.path("audio_url").asText(null));
            response.setAudioBase64(jsonNode.path("audio_base64").asText(null));
            
            return response;
        } catch (Exception e) {
            throw new RuntimeException("解析AI Agent响应失败: " + e.getMessage(), e);
        }
    }

    /**
     * AI Agent响应数据类
     */
    public static class AIAgentResponse {
        private String characterId;
        private String characterName;
        private String response;
        private String emotion;
        private String intent;
        private Map<String, Object> voiceConfig;
        private Map<String, Object> routerInfo;
        private boolean ragEnhanced;
        private boolean cotEnhanced;
        private int cotStepsCount;
        private String cotAnalysis;
        private String audioUrl;
        private String audioBase64;

        // Getters and Setters
        public String getCharacterId() { return characterId; }
        public void setCharacterId(String characterId) { this.characterId = characterId; }

        public String getCharacterName() { return characterName; }
        public void setCharacterName(String characterName) { this.characterName = characterName; }

        public String getResponse() { return response; }
        public void setResponse(String response) { this.response = response; }

        public String getEmotion() { return emotion; }
        public void setEmotion(String emotion) { this.emotion = emotion; }

        public String getIntent() { return intent; }
        public void setIntent(String intent) { this.intent = intent; }

        public Map<String, Object> getVoiceConfig() { return voiceConfig; }
        public void setVoiceConfig(Map<String, Object> voiceConfig) { this.voiceConfig = voiceConfig; }

        public Map<String, Object> getRouterInfo() { return routerInfo; }
        public void setRouterInfo(Map<String, Object> routerInfo) { this.routerInfo = routerInfo; }

        public boolean isRagEnhanced() { return ragEnhanced; }
        public void setRagEnhanced(boolean ragEnhanced) { this.ragEnhanced = ragEnhanced; }

        public boolean isCotEnhanced() { return cotEnhanced; }
        public void setCotEnhanced(boolean cotEnhanced) { this.cotEnhanced = cotEnhanced; }

        public int getCotStepsCount() { return cotStepsCount; }
        public void setCotStepsCount(int cotStepsCount) { this.cotStepsCount = cotStepsCount; }

        public String getCotAnalysis() { return cotAnalysis; }
        public void setCotAnalysis(String cotAnalysis) { this.cotAnalysis = cotAnalysis; }

        public String getAudioUrl() { return audioUrl; }
        public void setAudioUrl(String audioUrl) { this.audioUrl = audioUrl; }

        public String getAudioBase64() { return audioBase64; }
        public void setAudioBase64(String audioBase64) { this.audioBase64 = audioBase64; }
    }
}
