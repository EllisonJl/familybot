<template>
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
          <p class="character-role">{{ chatStore.selectedCharacter?.role || '选择一个家庭成员' }}</p>
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
        <p>{{ chatStore.selectedCharacter?.personality || '请先选择一个家庭成员开始对话' }}</p>
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
          <!-- 语音输入按钮 -->
          <el-button
            :type="chatStore.isRecording ? 'danger' : 'info'"
            :icon="chatStore.isRecording ? 'VideoPause' : 'Microphone'"
            circle
            @click="toggleVoiceRecord"
            :disabled="chatStore.isLoading"
            class="voice-btn"
          />
          
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
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Avatar, 
  UserFilled, 
  ChatLineRound, 
  Microphone, 
  VideoPause, 
  Promotion 
} from '@element-plus/icons-vue'

import { useChatStore } from '@/stores/chat'
import ChatMessage from '@/components/ChatMessage.vue'
import CharacterSelector from '@/components/CharacterSelector.vue'

// 状态管理
const chatStore = useChatStore()

// 响应式数据
const currentMessage = ref('')
const showCharacterSelector = ref(false)
const messageListRef = ref(null)

// 方法
const handleSend = async () => {
  if (!currentMessage.value.trim()) return
  if (!chatStore.selectedCharacter) {
    ElMessage.warning('请先选择一个家庭成员')
    showCharacterSelector.value = true
    return
  }

  const message = currentMessage.value.trim()
  currentMessage.value = ''

  try {
    await chatStore.sendMessage(message)
    scrollToBottom()
  } catch (error) {
    ElMessage.error('发送消息失败，请重试')
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

const toggleVoiceRecord = () => {
  if (chatStore.isRecording) {
    stopVoiceRecord()
  } else {
    startVoiceRecord()
  }
}

const startVoiceRecord = () => {
  chatStore.setRecording(true)
  ElMessage.info('语音录制功能正在开发中...')
  // TODO: 实现语音录制
  setTimeout(() => {
    chatStore.setRecording(false)
  }, 2000)
}

const stopVoiceRecord = () => {
  chatStore.setRecording(false)
  // TODO: 处理录制结果
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
    if (chatStore.characters.length === 0) {
      ElMessage.warning('暂无可用角色，请联系管理员')
    } else if (!chatStore.selectedCharacter) {
      showCharacterSelector.value = true
    }
  } catch (error) {
    ElMessage.error('初始化失败，请刷新页面重试')
  }
})
</script>

<style scoped>
.chat-container {
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

.voice-btn, .send-btn {
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