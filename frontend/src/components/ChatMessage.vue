<template>
  <div class="message-wrapper" :class="{ 'user-message': isUser, 'ai-message': !isUser }">
    <!-- 用户消息 -->
    <div v-if="isUser" class="message-container user">
      <div class="message-content">
        <div class="message-text">{{ message.content }}</div>
        <div class="message-time">{{ formattedTime }}</div>
      </div>
      <el-avatar 
        :size="40" 
        :src="message.avatar" 
        class="message-avatar"
      >
        <el-icon><User /></el-icon>
      </el-avatar>
    </div>

    <!-- AI消息 -->
    <div v-else class="message-container ai">
      <el-avatar 
        :size="40" 
        :src="message.avatar" 
        class="message-avatar"
      >
        <el-icon><Avatar /></el-icon>
      </el-avatar>
      <div class="message-content">
        <div class="character-name">{{ message.characterName }}</div>
        <div class="message-text" :class="{ 'error-text': message.isError }">
          {{ message.content }}
        </div>
        <div class="message-actions">
          <div class="message-time">{{ formattedTime }}</div>
          <!-- 语音播放按钮 -->
          <el-button 
            v-if="message.audioUrl && !message.isError" 
            :icon="isPlaying ? 'VideoPause' : 'VideoPlay'"
            size="small" 
            type="text"
            @click="toggleAudio"
            class="audio-button"
          >
            {{ isPlaying ? '暂停' : '播放' }}
          </el-button>
          <!-- CoT推理标识 -->
          <el-tag 
            v-if="message.enhanced_by_cot" 
            type="success" 
            size="small"
            class="cot-tag"
          >
            深度思考
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 音频元素 -->
    <audio 
      v-if="message.audioUrl" 
      ref="audioElement" 
      @ended="onAudioEnded"
      @play="isPlaying = true"
      @pause="isPlaying = false"
    >
      <source :src="message.audioUrl" type="audio/wav">
    </audio>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { User, Avatar, VideoPlay, VideoPause } from '@element-plus/icons-vue'
import moment from 'moment'

// Props
const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

// 响应式数据
const audioElement = ref(null)
const isPlaying = ref(false)

// 计算属性
const isUser = computed(() => props.message.sender === 'user')
const formattedTime = computed(() => {
  return moment(props.message.timestamp).format('HH:mm')
})

// 方法
const toggleAudio = () => {
  if (!audioElement.value) return
  
  if (isPlaying.value) {
    audioElement.value.pause()
  } else {
    audioElement.value.play()
  }
}

const onAudioEnded = () => {
  isPlaying.value = false
}

// 组件卸载时停止音频
onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause()
  }
})
</script>

<style scoped>
.message-wrapper {
  margin-bottom: 20px;
  width: 100%;
}

.message-container {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 80%;
}

.message-container.user {
  flex-direction: row-reverse;
  margin-left: auto;
}

.message-container.ai {
  margin-right: auto;
}

.message-avatar {
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-content {
  background: white;
  border-radius: 16px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  word-wrap: break-word;
}

.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.user .message-content::before {
  content: '';
  position: absolute;
  top: 12px;
  right: -8px;
  width: 0;
  height: 0;
  border: 8px solid transparent;
  border-left-color: #667eea;
}

.ai .message-content::before {
  content: '';
  position: absolute;
  top: 12px;
  left: -8px;
  width: 0;
  height: 0;
  border: 8px solid transparent;
  border-right-color: white;
}

.character-name {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  font-weight: 500;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.error-text {
  color: #f56c6c;
  font-style: italic;
}

.message-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.message-time {
  font-size: 12px;
  color: #909399;
}

.user .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.audio-button {
  padding: 4px 8px;
  font-size: 12px;
}

.cot-tag {
  font-size: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-container {
    max-width: 95%;
  }
  
  .message-content {
    padding: 10px 12px;
  }
  
  .message-text {
    font-size: 13px;
  }
}
</style>
