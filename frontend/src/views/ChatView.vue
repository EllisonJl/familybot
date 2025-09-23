<template>
  <div class="chat-container">
    <!-- 顶部角色信息 -->
    <div class="character-header">
      <div class="character-info">
        <img 
          :src="currentCharacter.avatarUrl || getDefaultAvatar(currentCharacter.characterId)" 
          :alt="currentCharacter.name"
          class="character-avatar"
        >
        <div class="character-details">
          <h2 class="character-name">{{ currentCharacter.name }}</h2>
          <p class="character-role">{{ currentCharacter.familyRole }}</p>
        </div>
      </div>
      
      <div class="header-actions">
        <button @click="showCharacterSelector = true" class="change-character-btn">
          切换角色
        </button>
        <button @click="clearChat" class="clear-chat-btn">
          清空聊天
        </button>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-area" ref="chatArea">
      <div class="chat-messages">
        <!-- 欢迎消息 -->
        <div v-if="messages.length === 0" class="welcome-message">
          <div class="message character-message">
            <div class="message-avatar">
              <img :src="getDefaultAvatar(currentCharacter.characterId)" :alt="currentCharacter.name">
            </div>
            <div class="message-content">
              <p>{{ currentCharacter.greeting || '你好！很高兴和你聊天！' }}</p>
            </div>
          </div>
        </div>

        <!-- 对话消息 -->
        <div v-for="(message, index) in messages" :key="index" class="message-wrapper">
          <!-- 用户消息 -->
          <div class="message user-message">
            <div class="message-content">
              <p>{{ message.userMessage }}</p>
            </div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>

          <!-- AI回复 -->
          <div class="message character-message">
            <div class="message-avatar">
              <img :src="getDefaultAvatar(currentCharacter.characterId)" :alt="currentCharacter.name">
            </div>
            <div class="message-content">
              <p>{{ message.assistantResponse }}</p>
              <div class="message-actions">
                <button @click="playAudio(message)" class="play-btn" :disabled="isPlaying">
                  <i class="icon-play"></i> 播放语音
                </button>
                <span class="emotion-indicator" :class="`emotion-${message.emotion}`">
                  {{ getEmotionText(message.emotion) }}
                </span>
              </div>
            </div>
            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
          </div>
        </div>

        <!-- 加载指示器 -->
        <div v-if="isLoading" class="message character-message">
          <div class="message-avatar">
            <img :src="getDefaultAvatar(currentCharacter.characterId)" :alt="currentCharacter.name">
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-container">
        <div class="input-box">
          <input 
            v-model="inputMessage" 
            @keydown.enter="sendMessage"
            :disabled="isLoading"
            placeholder="输入你想说的话..."
            class="message-input"
          >
          <button @click="toggleVoiceInput" class="voice-btn" :class="{ active: isRecording }">
            <i class="icon-mic"></i>
          </button>
          <button @click="sendMessage" :disabled="isLoading || !inputMessage.trim()" class="send-btn">
            <i class="icon-send"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 角色选择器模态框 -->
    <div v-if="showCharacterSelector" class="modal-overlay" @click="showCharacterSelector = false">
      <div class="character-selector" @click.stop>
        <h3>选择陪伴角色</h3>
        <div class="character-grid">
          <div 
            v-for="character in characters" 
            :key="character.characterId"
            @click="selectCharacter(character)"
            class="character-card"
            :class="{ active: character.characterId === currentCharacter.characterId }"
          >
            <img :src="getDefaultAvatar(character.characterId)" :alt="character.name" class="character-image">
            <div class="character-info">
              <h4>{{ character.name }}</h4>
              <p>{{ character.familyRole }}</p>
              <small>{{ character.personality.substring(0, 50) }}...</small>
            </div>
          </div>
        </div>
        <button @click="showCharacterSelector = false" class="close-btn">关闭</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { chatService } from '@/services/chatService'

export default {
  name: 'ChatView',
  setup() {
    // 响应式数据
    const currentCharacter = ref({
      characterId: 'xiyang',
      name: '喜羊羊',
      familyRole: '儿子',
      greeting: '爸爸妈妈好！我是你们的儿子喜羊羊，最近工作怎么样？身体还好吗？'
    })
    
    const characters = ref([])
    const messages = ref([])
    const inputMessage = ref('')
    const isLoading = ref(false)
    const isRecording = ref(false)
    const isPlaying = ref(false)
    const showCharacterSelector = ref(false)
    const chatArea = ref(null)
    
    const userId = 'user_' + Date.now() // 简单的用户ID生成

    // 获取默认头像
    const getDefaultAvatar = (characterId) => {
      const avatars = {
        xiyang: '/avatars/xiyang.png',
        meiyang: '/avatars/meiyang.png',
        lanyang: '/avatars/lanyang.png'
      }
      return avatars[characterId] || '/avatars/default.png'
    }

    // 格式化时间
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }

    // 获取情绪文本
    const getEmotionText = (emotion) => {
      const emotions = {
        happy: '😊',
        sad: '😢',
        angry: '😠',
        surprised: '😲',
        neutral: '😐',
        caring: '🥰',
        worried: '😟'
      }
      return emotions[emotion] || '😊'
    }

    // 滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (chatArea.value) {
          chatArea.value.scrollTop = chatArea.value.scrollHeight
        }
      })
    }

    // 发送消息
    const sendMessage = async () => {
      if (!inputMessage.value.trim() || isLoading.value) return

      const message = inputMessage.value.trim()
      inputMessage.value = ''
      isLoading.value = true

      try {
        const response = await chatService.sendMessage({
          message,
          userId,
          characterId: currentCharacter.value.characterId
        })

        messages.value.push({
          userMessage: message,
          assistantResponse: response.response,
          emotion: response.emotion,
          intent: response.intent,
          timestamp: response.timestamp || new Date().toISOString(),
          voiceConfig: response.voiceConfig
        })

        scrollToBottom()
      } catch (error) {
        console.error('发送消息失败:', error)
        // 显示错误消息
        messages.value.push({
          userMessage: message,
          assistantResponse: '抱歉，我现在有些问题，请稍后再试。',
          emotion: 'neutral',
          timestamp: new Date().toISOString(),
          error: true
        })
      } finally {
        isLoading.value = false
        scrollToBottom()
      }
    }

    // 语音输入切换
    const toggleVoiceInput = () => {
      if (isRecording.value) {
        stopRecording()
      } else {
        startRecording()
      }
    }

    // 开始录音
    const startRecording = () => {
      // TODO: 实现语音录制功能
      isRecording.value = true
      console.log('开始录音...')
    }

    // 停止录音
    const stopRecording = () => {
      // TODO: 实现语音录制功能
      isRecording.value = false
      console.log('停止录音...')
    }

    // 播放语音
    const playAudio = async (message) => {
      if (isPlaying.value) return

      try {
        isPlaying.value = true
        // TODO: 调用TTS API生成语音并播放
        console.log('播放语音:', message.assistantResponse)
        
        // 模拟播放时间
        setTimeout(() => {
          isPlaying.value = false
        }, 2000)
      } catch (error) {
        console.error('播放语音失败:', error)
        isPlaying.value = false
      }
    }

    // 选择角色
    const selectCharacter = async (character) => {
      try {
        await chatService.switchCharacter(userId, character.characterId)
        currentCharacter.value = character
        showCharacterSelector.value = false
        
        // 清空当前对话或显示新角色的问候语
        clearChat()
      } catch (error) {
        console.error('切换角色失败:', error)
      }
    }

    // 清空聊天
    const clearChat = () => {
      messages.value = []
    }

    // 加载角色列表
    const loadCharacters = async () => {
      try {
        const data = await chatService.getCharacters()
        characters.value = data
        
        // 设置默认角色
        if (data.length > 0) {
          const defaultChar = data.find(c => c.isDefault) || data[0]
          currentCharacter.value = defaultChar
        }
      } catch (error) {
        console.error('加载角色列表失败:', error)
      }
    }

    // 组件挂载时的初始化
    onMounted(() => {
      loadCharacters()
    })

    return {
      currentCharacter,
      characters,
      messages,
      inputMessage,
      isLoading,
      isRecording,
      isPlaying,
      showCharacterSelector,
      chatArea,
      getDefaultAvatar,
      formatTime,
      getEmotionText,
      sendMessage,
      toggleVoiceInput,
      playAudio,
      selectCharacter,
      clearChat
    }
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.character-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.character-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.character-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #4facfe;
}

.character-name {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
}

.character-role {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.change-character-btn, .clear-chat-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.change-character-btn {
  background: #4facfe;
  color: white;
}

.clear-chat-btn {
  background: #95a5a6;
  color: white;
}

.change-character-btn:hover, .clear-chat-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.chat-area {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.chat-messages {
  max-width: 800px;
  margin: 0 auto;
}

.welcome-message, .message-wrapper {
  margin-bottom: 1.5rem;
}

.message {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.user-message {
  justify-content: flex-end;
}

.user-message .message-content {
  background: #4facfe;
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 18px 18px 4px 18px;
  max-width: 70%;
  box-shadow: 0 2px 8px rgba(79, 172, 254, 0.3);
}

.character-message {
  justify-content: flex-start;
}

.character-message .message-content {
  background: white;
  color: #2c3e50;
  padding: 1rem 1.5rem;
  border-radius: 18px 18px 18px 4px;
  max-width: 70%;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.message-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.message-time {
  font-size: 0.75rem;
  color: rgba(255,255,255,0.7);
  margin-top: 0.5rem;
  text-align: center;
}

.message-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-top: 0.5rem;
}

.play-btn {
  background: none;
  border: 1px solid #4facfe;
  color: #4facfe;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.3s ease;
}

.play-btn:hover:not(:disabled) {
  background: #4facfe;
  color: white;
}

.play-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.emotion-indicator {
  font-size: 0.8rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  background: #ecf0f1;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #bdc3c7;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.input-area {
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.input-container {
  max-width: 800px;
  margin: 0 auto;
}

.input-box {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 1rem 1.5rem;
  border: 2px solid #ecf0f1;
  border-radius: 25px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.message-input:focus {
  border-color: #4facfe;
}

.voice-btn, .send-btn {
  width: 50px;
  height: 50px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.voice-btn {
  background: #95a5a6;
  color: white;
}

.voice-btn.active {
  background: #e74c3c;
  animation: pulse 1s infinite;
}

.send-btn {
  background: #4facfe;
  color: white;
}

.send-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.character-selector {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.character-selector h3 {
  margin: 0 0 1.5rem 0;
  text-align: center;
  color: #2c3e50;
}

.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.character-card {
  padding: 1rem;
  border: 2px solid #ecf0f1;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.character-card:hover {
  border-color: #4facfe;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.3);
}

.character-card.active {
  border-color: #4facfe;
  background: rgba(79, 172, 254, 0.1);
}

.character-image {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 1rem;
}

.character-card h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.character-card p {
  margin: 0 0 0.5rem 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.character-card small {
  color: #95a5a6;
  font-size: 0.8rem;
}

.close-btn {
  width: 100%;
  padding: 0.75rem;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
}

.close-btn:hover {
  background: #7f8c8d;
}

/* 图标样式 */
.icon-play::before { content: "▶"; }
.icon-mic::before { content: "🎤"; }
.icon-send::before { content: "➤"; }
</style>
