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
        
        <!-- 图片显示 -->
        <div v-if="message.imageUrl || message.imageBase64" class="message-image">
          <!-- 调试信息 -->
          <div v-if="showDebugInfo" class="debug-info">
            <small style="color: #999;">
              调试: imageUrl={{ !!message.imageUrl }}, imageBase64={{ !!message.imageBase64 }}, 
              imageSource={{ imageSource ? '有' : '无' }}
            </small>
          </div>
          
          <el-image
            v-if="imageSource"
            :src="imageSource"
            :preview-src-list="[imageSource]"
            fit="cover"
            loading="lazy"
            class="generated-image"
            :alt="message.imageDescription || '生成的图片'"
            @error="onImageError"
          >
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
                <span>图片加载失败</span>
                <div style="margin-top: 8px;">
                  <el-button size="small" @click="openImageLink">
                    打开原始链接
                  </el-button>
                </div>
              </div>
            </template>
          </el-image>
          
          <!-- 如果没有图片源但有URL，显示链接 -->
          <div v-else-if="message.imageUrl" class="image-fallback">
            <el-icon><Picture /></el-icon>
            <span>图片处理中...</span>
            <el-button size="small" type="primary" @click="openImageLink">
              查看图片
            </el-button>
          </div>
          <div v-if="message.imageDescription" class="image-description">
            <el-icon><View /></el-icon>
            <span>{{ message.imageDescription }}</span>
          </div>
          <!-- 图片链接按钮 -->
          <div v-if="message.imageUrl && !imageSource" class="image-link-section">
            <el-button 
              type="primary" 
              size="small" 
              :icon="Picture"
              @click="openImageLink"
            >
              查看图片链接
            </el-button>
            <div class="image-url-display">
              <el-text class="image-url-text" size="small">
                {{ message.imageUrl }}
              </el-text>
            </div>
          </div>
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
import { User, Avatar, VideoPlay, VideoPause, Picture, View } from '@element-plus/icons-vue'
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
const showDebugInfo = ref(true) // 临时启用调试信息

// 计算属性
const isUser = computed(() => props.message.sender === 'user')
const formattedTime = computed(() => {
  return moment(props.message.timestamp).format('HH:mm')
})

const imageSource = computed(() => {
  // 🐞 调试: 检查消息中的图片数据
  console.log('🖼️ ChatMessage组件接收到的图片数据:', {
    messageId: props.message.id,
    hasImageUrl: !!props.message.imageUrl,
    hasImageBase64: !!props.message.imageBase64,
    imageDescription: props.message.imageDescription,
    imageUrl_preview: props.message.imageUrl ? props.message.imageUrl.substring(0, 50) + '...' : '无'
  })
  
  // 优先使用imageUrl，如果没有则使用base64
  if (props.message.imageUrl) {
    console.log('✅ 使用imageUrl作为图片源')
    return props.message.imageUrl
  } else if (props.message.imageBase64) {
    console.log('✅ 使用imageBase64作为图片源')
    return `data:image/png;base64,${props.message.imageBase64}`
  }
  console.log('❌ 没有可用的图片源')
  return null
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

const openImageLink = () => {
  if (props.message.imageUrl) {
    window.open(props.message.imageUrl, '_blank')
  }
}

const onImageError = (error) => {
  console.error('图片加载失败:', {
    error,
    imageUrl: props.message.imageUrl,
    imageBase64: !!props.message.imageBase64,
    imageSource: imageSource.value
  })
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

/* 图片相关样式 */
.message-image {
  margin-top: 12px;
  max-width: 100%;
}

.generated-image {
  max-width: 300px;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s ease;
}

.generated-image:hover {
  transform: scale(1.02);
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  color: #909399;
  min-height: 100px;
}

.image-error .el-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.image-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 8px;
  border: 1px solid #b3d8ff;
  color: #1890ff;
  min-height: 100px;
  gap: 12px;
}

.image-fallback .el-icon {
  font-size: 32px;
}

.image-description {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 6px 10px;
  background: #f0f9ff;
  border-radius: 6px;
  font-size: 12px;
  color: #1890ff;
  border: 1px solid #b3d8ff;
}

.image-description .el-icon {
  font-size: 14px;
}

.image-link-section {
  margin-top: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.image-url-display {
  margin-top: 8px;
}

.image-url-text {
  word-break: break-all;
  color: #666;
  font-family: monospace;
  font-size: 11px;
  line-height: 1.4;
  padding: 4px 8px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #ddd;
  display: block;
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
