<template>
  <div class="chat-layout">
    <!-- 历史会话侧边栏 -->
    <ConversationSidebar 
      :collapsed="sidebarCollapsed"
      @toggle-collapse="sidebarCollapsed = !sidebarCollapsed"
    />
    
    <!-- 主聊天区域 -->
    <div class="chat-container">
    <!-- 顶部头部 -->
    <div class="chat-header">
      <div class="header-left">
        <el-avatar 
          :size="50" 
          :src="chatStore.selectedCharacter?.avatarUrl"
          class="character-avatar"
        >
          <el-icon><Avatar /></el-icon>
        </el-avatar>
        <div class="character-info">
          <h2 class="character-name">{{ chatStore.currentCharacterName }}</h2>
          <p class="character-role">当前角色</p>
        </div>
      </div>
      
      <div class="header-right">
        <el-button 
          type="primary" 
          :icon="UserFilled"
          @click="showCharacterSelector = true"
        >
          切换角色
        </el-button>
      </div>
    </div>

    <!-- 消息列表 -->
    <div class="message-list" ref="messageListRef">
      <div v-if="!chatStore.hasMessages" class="welcome-message">
        <el-icon size="60" class="welcome-icon"><ChatLineRound /></el-icon>
        <h3>开始和{{ chatStore.currentCharacterName }}聊天吧！</h3>
        <p>{{ chatStore.selectedCharacter?.personality || '请先选择当前角色开始对话' }}</p>
        <div v-if="voiceEnabled" class="voice-hint">
          <el-icon class="voice-hint-icon"><Microphone /></el-icon>
          <span v-if="isListening">正在听您说话，请直接开口...</span>
          <span v-else>语音识别已启用，点击麦克风可以关闭</span>
        </div>
      </div>
      
      <ChatMessage
        v-for="message in chatStore.messages"
        :key="message.id"
        :message="message"
      />
      
      <!-- 加载中指示器 -->
      <div v-if="chatStore.isLoading" class="loading-message">
        <el-avatar :size="40" :src="chatStore.selectedCharacter?.avatarUrl">
          <el-icon><Avatar /></el-icon>
        </el-avatar>
        <div class="typing-indicator">
          <span>{{ chatStore.currentCharacterName }}正在思考</span>
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <div class="input-container">
        <el-input
          v-model="currentMessage"
          type="textarea"
          :autosize="{ minRows: 1, maxRows: 4 }"
          placeholder="输入消息..."
          @keyup.enter.exact="handleSend"
          @keyup.enter.shift.exact="() => {}"
          :disabled="chatStore.isLoading || !chatStore.selectedCharacter"
          class="message-input"
        />
        
        <div class="input-actions">
          <!-- 语音控制按钮 -->
          <el-tooltip :content="voiceEnabled ? '点击关闭语音识别' : '点击启动语音识别'" placement="top">
            <div 
              class="voice-toggle" 
              :class="{ 'enabled': voiceEnabled, 'listening': isListening }"
              @click="toggleVoiceRecognition"
            >
              <el-icon><Microphone /></el-icon>
            </div>
          </el-tooltip>
          
          <!-- TTS控制按钮 -->
          <el-tooltip :content="ttsEnabled ? '点击关闭语音播放' : '点击启用语音播放'" placement="top">
            <div 
              class="tts-toggle" 
              :class="{ 'enabled': ttsEnabled, 'speaking': isSpeaking }"
              @click="toggleTTS"
            >
              <el-icon><VideoPlay /></el-icon>
            </div>
          </el-tooltip>
          
          <!-- 发送按钮 -->
          <el-button
            type="primary"
            :icon="Promotion"
            @click="handleSend"
            :disabled="!currentMessage.trim() || chatStore.isLoading || !chatStore.selectedCharacter"
            circle
            class="send-btn"
          />
        </div>
      </div>
    </div>

    <!-- 角色选择对话框 -->
    <CharacterSelector
      v-model="showCharacterSelector"
      :characters="chatStore.characters"
      :current-character="chatStore.selectedCharacter"
      @select="handleCharacterSelect"
    />
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Avatar, 
  UserFilled, 
  ChatLineRound, 
  Microphone, 
  VideoPause, 
  Promotion,
  VideoPlay
} from '@element-plus/icons-vue'

import { useChatStore } from '@/stores/chat'
import ChatMessage from '@/components/ChatMessage.vue'
import CharacterSelector from '@/components/CharacterSelector.vue'
import ConversationSidebar from '@/components/ConversationSidebar.vue'

// 状态管理
const chatStore = useChatStore()

// 响应式数据
const currentMessage = ref('')
const showCharacterSelector = ref(false)
const messageListRef = ref(null)
const isListening = ref(false)
const recognition = ref(null)
const voiceEnabled = ref(false)
const ttsEnabled = ref(true)
const isSpeaking = ref(false)
const sidebarCollapsed = ref(false)

// 方法
const handleSend = async (inputText = null) => {
  const message = inputText || currentMessage.value.trim()
  if (!message) return
  if (!chatStore.selectedCharacter) {
    ElMessage.warning('请先选择当前角色')
    showCharacterSelector.value = true
    return
  }

  if (!inputText) {
    currentMessage.value = ''
  }

  try {
    const aiMessage = await chatStore.sendMessage(message)
    scrollToBottom()
    
    // 如果启用了TTS，播放AI回复
    if (aiMessage && aiMessage.content && ttsEnabled.value) {
      // 稍微延迟播放，确保消息已经显示
      setTimeout(() => {
        speakText(aiMessage.content)
      }, 500)
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    // 由于chat.js中已有fallback机制，这里的错误通常不会出现
    // 如果出现，说明是其他问题
    ElMessage.warning('正在使用离线模式，AI回复可能较为简单')
  }
}

const handleCharacterSelect = async (character) => {
  try {
    await chatStore.selectCharacter(character)
    ElMessage.success(`已切换到${character.name}`)
    scrollToBottom()
  } catch (error) {
    ElMessage.error('切换角色失败')
  }
}

// 初始化语音识别
const initSpeechRecognition = async () => {
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    ElMessage.warning('您的浏览器不支持语音识别功能，请使用Chrome或Safari浏览器')
    return
  }

  // 先请求麦克风权限
  try {
    await navigator.mediaDevices.getUserMedia({ audio: true })
    console.log('麦克风权限已获取')
  } catch (error) {
    console.error('无法获取麦克风权限:', error)
    ElMessage.error('请允许使用麦克风，然后刷新页面重试')
    return
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  recognition.value = new SpeechRecognition()
  
  recognition.value.continuous = true
  recognition.value.interimResults = true  // 恢复临时结果，提高识别率
  recognition.value.lang = 'zh-CN'
  recognition.value.maxAlternatives = 3  // 增加候选结果
  recognition.value.grammars = null  // 不限制语法
  
  recognition.value.onstart = () => {
    isListening.value = true
    console.log('语音识别已启动')
  }
  
  recognition.value.onresult = (event) => {
    let finalTranscript = ''
    let interimTranscript = ''
    
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript.trim()
      if (event.results[i].isFinal) {
        finalTranscript += transcript
      } else {
        interimTranscript += transcript
      }
    }
    
    // 显示临时识别结果
    if (interimTranscript) {
      currentMessage.value = interimTranscript
      console.log('临时识别:', interimTranscript)
    }
    
    // 处理最终识别结果
    if (finalTranscript.trim()) {
      console.log('最终识别完成:', finalTranscript.trim())
      // 显示识别成功提示
      ElMessage.success(`识别完成: "${finalTranscript.trim()}"`)
      // 清空输入框
      currentMessage.value = ''
      // 直接发送语音识别结果
      handleSend(finalTranscript.trim())
    }
  }
  
  recognition.value.onerror = (event) => {
    console.error('语音识别错误:', event.error)
    isListening.value = false
    
    switch (event.error) {
      case 'not-allowed':
        ElMessage.error('麦克风权限被拒绝，请在浏览器设置中允许使用麦克风')
        break
      case 'no-speech':
        console.log('没有检测到语音，继续监听...')
        // 没有语音时不显示错误，自动重启
        setTimeout(() => startSpeechRecognition(), 1000)
        break
      case 'audio-capture':
        ElMessage.error('无法捕获音频，请检查麦克风连接')
        break
      case 'network':
        ElMessage.warning('网络错误，语音识别可能不稳定')
        setTimeout(() => startSpeechRecognition(), 2000)
        break
      case 'aborted':
        console.log('语音识别被中止')
        break
      default:
        console.log('语音识别错误:', event.error, '自动重试中...')
        setTimeout(() => startSpeechRecognition(), 1000)
        break
    }
  }
  
  recognition.value.onend = () => {
    isListening.value = false
    // 只有在语音功能启用时才自动重启
    if (voiceEnabled.value && chatStore.selectedCharacter) {
      setTimeout(() => startSpeechRecognition(), 1000)
    }
  }
}

const startSpeechRecognition = () => {
  if (recognition.value && !isListening.value && voiceEnabled.value) {
    try {
      recognition.value.start()
    } catch (error) {
      console.log('语音识别已在运行')
    }
  }
}

const toggleVoiceRecognition = () => {
  voiceEnabled.value = !voiceEnabled.value
  if (voiceEnabled.value) {
    startSpeechRecognition()
  } else {
    stopSpeechRecognition()
  }
}

const stopSpeechRecognition = () => {
  if (recognition.value && isListening.value) {
    recognition.value.stop()
    isListening.value = false
  }
}

// TTS 文本转语音功能
const speakText = (text) => {
  if (!ttsEnabled.value || !text.trim()) return
  
  // 停止当前播放
  speechSynthesis.cancel()
  
  // 创建语音合成实例
  const utterance = new SpeechSynthesisUtterance(text)
  
  // 设置语音参数
  utterance.lang = 'zh-CN'
  utterance.rate = 0.9  // 语速稍慢一些
  utterance.pitch = 1.1  // 音调稍高一些，更亲切
  utterance.volume = 0.8
  
  // 尝试使用中文语音
  const voices = speechSynthesis.getVoices()
  const chineseVoice = voices.find(voice => 
    voice.lang.includes('zh') || voice.name.includes('Chinese')
  )
  if (chineseVoice) {
    utterance.voice = chineseVoice
  }
  
  // 事件监听
  utterance.onstart = () => {
    isSpeaking.value = true
    console.log('开始语音播放:', text)
  }
  
  utterance.onend = () => {
    isSpeaking.value = false
    console.log('语音播放完成')
  }
  
  utterance.onerror = (event) => {
    isSpeaking.value = false
    console.error('语音播放错误:', event.error)
  }
  
  // 开始播放
  speechSynthesis.speak(utterance)
}

const toggleTTS = () => {
  ttsEnabled.value = !ttsEnabled.value
  if (!ttsEnabled.value) {
    speechSynthesis.cancel() // 关闭TTS时停止当前播放
    isSpeaking.value = false
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 生命周期
onMounted(async () => {
  try {
    await chatStore.initialize()
    
    // 加载会话历史
    chatStore.loadConversationsFromLocal()
    
    // 等待一小段时间确保fallback角色加载完成
    setTimeout(async () => {
      if (chatStore.characters.length === 0) {
        ElMessage.warning('正在初始化角色数据，请稍候...')
      } else if (!chatStore.selectedCharacter && chatStore.characters.length > 0) {
        showCharacterSelector.value = true
      }
      
      // 初始化语音识别
      await initSpeechRecognition()
      
      // 不自动启动语音识别，让用户手动控制
    }, 500)
    
  } catch (error) {
    console.error('初始化错误:', error)
    ElMessage.error('初始化失败，正在使用默认配置')
  }
})

// 监听角色变化
watch(() => chatStore.selectedCharacter, (newCharacter) => {
  if (!newCharacter) {
    stopSpeechRecognition()
    voiceEnabled.value = false
  }
  // 不自动启动语音识别，让用户手动控制
})
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  background: white;
}

.chat-container {
  flex: 1;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: white;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.character-avatar {
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.character-info h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.character-info p {
  margin: 4px 0 0 0;
  font-size: 14px;
  opacity: 0.9;
}

.header-right .el-button {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
}

.header-right .el-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  background: #f8fafc;
}

.welcome-message {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.welcome-icon {
  color: #c0c4cc;
  margin-bottom: 16px;
}

.welcome-message h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #606266;
}

.welcome-message p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
}

.voice-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 20px;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  animation: voicePulse 2s infinite;
}

.voice-hint-icon {
  animation: bounce 1s infinite;
}

@keyframes voicePulse {
  0%, 100% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.02); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.loading-message {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.typing-indicator {
  background: white;
  padding: 12px 16px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 8px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: #409eff;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.input-area {
  padding: 16px 24px;
  background: white;
  border-top: 1px solid #ebeef5;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  border-radius: 20px;
  border: 2px solid #e4e7ed;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.4;
}

.message-input :deep(.el-textarea__inner):focus {
  border-color: #409eff;
}

.input-actions {
  display: flex;
  gap: 8px;
}

.voice-toggle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border: 2px solid #e0e0e0;
  transition: all 0.3s ease;
  cursor: pointer;
}

.voice-toggle:hover {
  background: #e8e8e8;
  transform: scale(1.1);
}

.voice-toggle.enabled {
  background: #4CAF50;
  border-color: #45a049;
  color: white;
}

.voice-toggle.listening {
  animation: pulse 1.5s infinite;
}

.tts-toggle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border: 2px solid #e0e0e0;
  transition: all 0.3s ease;
  cursor: pointer;
  margin-left: 8px;
}

.tts-toggle:hover {
  background: #e8e8e8;
  transform: scale(1.1);
}

.tts-toggle.enabled {
  background: #2196F3;
  border-color: #1976D2;
  color: white;
}

.tts-toggle.speaking {
  animation: pulse 1.5s infinite;
  background: #FF9800;
  border-color: #F57C00;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.send-btn {
  width: 40px;
  height: 40px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-header {
    padding: 12px 16px;
  }
  
  .header-left {
    gap: 12px;
  }
  
  .character-info h2 {
    font-size: 18px;
  }
  
  .character-info p {
    font-size: 12px;
  }
  
  .message-list {
    padding: 16px;
  }
  
  .input-area {
    padding: 12px 16px;
  }
  
  .welcome-message {
    padding: 40px 16px;
  }
}
</style>