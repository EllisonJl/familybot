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
          @keyup.enter="handleEnterKey"
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
          
          <!-- 文件上传按钮 -->
          <el-tooltip content="上传文档到当前角色知识库" placement="top">
            <div 
              class="file-upload-toggle" 
              @click="showFileUpload = true"
            >
              <el-icon><Document /></el-icon>
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
    
    <!-- 文件上传对话框 -->
    <el-dialog
      v-model="showFileUpload"
      title="上传文档到角色知识库"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="file-upload-dialog">
        <div class="current-character-info">
          <el-avatar :src="chatStore.selectedCharacter?.avatarUrl" :size="40" />
          <span>为 {{ chatStore.selectedCharacter?.name }} 上传文档</span>
        </div>
        
        <el-upload
          ref="uploadRef"
          :action="`http://localhost:8001/upload-document`"
          :data="{ 
            character_id: chatStore.selectedCharacter?.characterId || chatStore.selectedCharacter?.id,
            user_id: chatStore.currentUser.id 
          }"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          :show-file-list="true"
          :auto-upload="false"
          accept=".pdf,.doc,.docx,.txt,.md"
          drag
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 PDF、Word、TXT、Markdown 格式文件，大小不超过 10MB
            </div>
          </template>
        </el-upload>
        
        <div class="upload-actions">
          <el-button @click="showFileUpload = false">取消</el-button>
          <el-button type="primary" @click="submitUpload" :loading="uploadLoading">
            开始上传
          </el-button>
        </div>
        
        <!-- 角色文档列表 -->
        <div class="character-documents" v-if="characterDocuments.length > 0">
          <h4>{{ chatStore.selectedCharacter?.name }} 的文档库</h4>
          <div class="document-list">
            <div 
              v-for="doc in characterDocuments" 
              :key="doc.file_id"
              class="document-item"
            >
              <div class="document-info">
                <el-icon class="document-icon">
                  <Document v-if="doc.file_type === '.pdf'" />
                  <DocumentCopy v-else />
                </el-icon>
                <div class="document-details">
                  <div class="document-name">{{ doc.filename }}</div>
                  <div class="document-meta">
                    {{ formatFileSize(doc.file_size) }} • 
                    {{ formatDate(doc.upload_time) }}
                    <span v-if="doc.page_count > 0">• {{ doc.page_count }} 页</span>
                  </div>
                  <div class="document-summary" v-if="doc.summary">{{ doc.summary }}</div>
                </div>
              </div>
              <el-button 
                type="danger" 
                size="small" 
                :icon="Delete"
                @click="deleteDocument(doc.file_id)"
                circle
              />
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Avatar, 
  UserFilled, 
  ChatLineRound, 
  Microphone, 
  VideoPause, 
  Promotion,
  VideoPlay,
  Document,
  UploadFilled,
  DocumentCopy,
  Delete
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
const showFileUpload = ref(false)
const messageListRef = ref(null)
const isListening = ref(false)
const recognition = ref(null)
const voiceEnabled = ref(false)
const ttsEnabled = ref(true)
const isSpeaking = ref(false)
const voiceRetryCount = ref(0)
const maxRetries = 3
const sidebarCollapsed = ref(false)
const uploadRef = ref(null)
const uploadLoading = ref(false)
const characterDocuments = ref([])

// 方法
const handleSend = async (inputText = null) => {
  // 确保inputText是字符串，如果是事件对象则忽略
  let message
  if (typeof inputText === 'string') {
    message = inputText.trim()
  } else {
    message = currentMessage.value.trim()
  }
  
  if (!message) return
  if (!chatStore.selectedCharacter) {
    ElMessage.warning('请先选择当前角色')
    showCharacterSelector.value = true
    return
  }

  // 只有在没有传入文本时才清空输入框
  if (typeof inputText !== 'string') {
    currentMessage.value = ''
  }

  try {
    const aiMessage = await chatStore.sendMessage(message)
    scrollToBottom()
    
    // 如果启用了TTS，播放AI回复
    if (aiMessage && aiMessage.content && ttsEnabled.value) {
      // 稍微延迟播放，确保消息已经显示
      setTimeout(() => {
        playAIAudio(aiMessage)
      }, 500)
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    // 显示真实的错误信息
    ElMessage.error(`消息发送失败: ${error.message || '网络连接错误'}`)
  }
}

const handleEnterKey = (e) => {
  if (!e.shiftKey) {
    e.preventDefault()
    handleSend()
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
  try {
    console.log('开始初始化语音识别...')
    
    // 检查浏览器支持
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      console.error('❌ 浏览器不支持语音识别')
      ElMessage.error('您的浏览器不支持语音识别，请使用Chrome、Edge或Safari')
      return false
    }
    console.log('✅ 浏览器支持语音识别:', SpeechRecognition.name)
    
    // 检查是否已经初始化过
    if (recognition.value) {
      console.log('语音识别已经初始化，尝试重新启动...')
      try {
        recognition.value.stop()
      } catch (e) {
        console.log('停止现有语音识别:', e)
      }
      recognition.value = null
    }
    
    // 检查麦克风权限
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('浏览器不支持麦克风访问')
    }
    
    console.log('🔐 请求麦克风权限...')
    let stream
    try {
      stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      })
      console.log('✅ 麦克风权限获取成功')
    } catch (permissionError) {
      console.error('❌ 麦克风权限被拒绝:', permissionError.name, permissionError.message)
      if (permissionError.name === 'NotAllowedError') {
        ElMessage.error('请允许使用麦克风，然后刷新页面重试')
      } else if (permissionError.name === 'NotFoundError') {
        ElMessage.error('未检测到麦克风设备，请检查设备连接')
      } else {
        ElMessage.error(`麦克风访问失败: ${permissionError.message}`)
      }
      return false
    }
    
    const tracks = stream.getAudioTracks()
    if (!tracks || tracks.length === 0) {
      throw new Error('未检测到麦克风设备')
    }
    
    console.log('麦克风权限已获取:', {
      tracks: tracks.length,
      label: tracks[0].label,
      enabled: tracks[0].enabled
    })
    
    // 保持音频流活跃
    if (window.audioStream) {
      window.audioStream.getTracks().forEach(track => track.stop())
    }
    window.audioStream = stream

    // 创建语音识别实例
    console.log('创建语音识别实例...')
    recognition.value = new SpeechRecognition()
    console.log('✅ 语音识别实例创建成功')
    
    // 配置语音识别
    recognition.value.continuous = true
    recognition.value.interimResults = true
    recognition.value.lang = 'zh-CN'
    recognition.value.maxAlternatives = 3
    
    console.log('语音识别配置完成:', {
      continuous: recognition.value.continuous,
      interimResults: recognition.value.interimResults,
      lang: recognition.value.lang,
      maxAlternatives: recognition.value.maxAlternatives
    })
    
    // 设置音频上下文
    console.log('设置音频上下文...')
    let audioContext
    try {
      audioContext = new (window.AudioContext || window.webkitAudioContext)()
      console.log('音频上下文创建成功')
    } catch (error) {
      console.error('创建音频上下文失败:', error)
      throw new Error('无法创建音频上下文')
    }
    
    try {
      const source = audioContext.createMediaStreamSource(stream)
      console.log('音频源创建成功')
      
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 1024  // 增加FFT大小以提高精度
      analyser.smoothingTimeConstant = 0.8  // 平滑处理
      analyser.minDecibels = -90
      analyser.maxDecibels = -10
      
      source.connect(analyser)
      console.log('音频分析器配置完成:', {
        fftSize: analyser.fftSize,
        frequencyBinCount: analyser.frequencyBinCount,
        minDecibels: analyser.minDecibels,
        maxDecibels: analyser.maxDecibels
      })
      
      // 保存到全局以便后续使用
      window.audioContext = audioContext
      window.analyser = analyser
    } catch (error) {
      console.error('音频分析器配置失败:', error)
      throw new Error('无法配置音频分析器')
    }
    
    // 音量监测
const checkVolume = () => {
  if (!window.analyser) {
    console.warn('音频分析器未初始化')
    return
  }
  
  try {
    const dataArray = new Uint8Array(window.analyser.frequencyBinCount)
    window.analyser.getByteFrequencyData(dataArray)
    const volume = dataArray.reduce((a, b) => a + b) / dataArray.length
    
    // 更新音量显示
    if (volume > 0) {
      console.log('检测到声音，音量:', volume.toFixed(2))
      // 添加可视化反馈
      const voiceToggle = document.querySelector('.voice-toggle')
      if (voiceToggle) {
        voiceToggle.style.transform = `scale(${1 + (volume / 100)})`
        voiceToggle.style.backgroundColor = volume > 30 ? '#4CAF50' : '#f0f0f0'
      }
    }
    
    // 如果音量过低，可能是麦克风未正确工作
    if (isListening.value && volume < 1) {
      console.warn('警告：音量过低，可能麦克风未正确工作')
    }
    
    // 继续监测
    if (voiceEnabled.value) {
      requestAnimationFrame(checkVolume)
    }
  } catch (error) {
    console.error('音量监测错误:', error)
  }
}
    checkVolume()
    
    console.log('语音识别初始化成功')
  
    // 配置事件处理器
    recognition.value.onstart = () => {
      isListening.value = true
      voiceRetryCount.value = 0  // 成功启动时重置重试计数
      console.log('语音识别已启动')
    }
    
    recognition.value.onresult = (event) => {
      try {
        console.log('收到识别结果事件:', {
          resultIndex: event.resultIndex,
          resultsLength: event.results.length
        })
        
        let finalTranscript = ''
        let interimTranscript = ''
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i]
          const transcript = result[0].transcript.trim()
          
          if (result.isFinal) {
            finalTranscript += transcript
            console.log('最终识别结果:', {
              text: transcript,
              confidence: result[0].confidence
            })
          } else {
            interimTranscript += transcript
            console.log('临时识别结果:', {
              text: transcript,
              confidence: result[0].confidence
            })
          }
        }
        
        // 显示临时识别结果
        if (interimTranscript) {
          currentMessage.value = interimTranscript
        }
        
        // 处理最终识别结果
        if (finalTranscript.trim()) {
          const message = finalTranscript.trim()
          console.log('发送识别结果:', message)
          ElMessage.success('识别完成')
          currentMessage.value = ''
          handleSend(message)
        }
      } catch (error) {
        console.error('处理识别结果时出错:', error)
        ElMessage.error('语音识别出错，请重试')
      }
    }
    
    recognition.value.onerror = (event) => {
      console.error('语音识别错误:', {
        error: event.error,
        message: event.message,
        timestamp: new Date().toISOString()
      })
      
      isListening.value = false
      
      switch (event.error) {
        case 'not-allowed':
          ElMessage.error('请允许使用麦克风')
          voiceEnabled.value = false
          break
          
        case 'no-speech':
          console.log('未检测到语音...')
          // no-speech 错误不需要重启，这是正常的静音状态
          break
          
        case 'audio-capture':
          ElMessage.error('未检测到麦克风设备')
          voiceEnabled.value = false
          break
          
        case 'network':
          console.warn('网络连接不稳定')
          voiceRetryCount.value++
          if (voiceEnabled.value && voiceRetryCount.value < maxRetries) {
            setTimeout(() => {
              console.log(`尝试重新连接... (${voiceRetryCount.value}/${maxRetries})`)
              startSpeechRecognition()
            }, 2000)
          } else {
            console.error('网络重试次数已达上限，停止语音识别')
            voiceEnabled.value = false
            ElMessage.error('网络连接问题，请检查网络后手动重启语音')
          }
          break
          
        case 'aborted':
          console.log('语音识别已停止')
          break
          
        default:
          console.error('未知错误:', event.error)
          ElMessage.error('语音识别出错，请刷新页面重试')
          break
      }
    }
    
    recognition.value.onend = () => {
      console.log('语音识别结束')
      isListening.value = false
      
      // 只有在用户主动启用且没有错误的情况下才自动重启
      if (voiceEnabled.value && chatStore.selectedCharacter && voiceRetryCount.value < maxRetries) {
        console.log('准备重新启动语音识别...')
        setTimeout(() => {
          if (voiceEnabled.value && !isListening.value) {  // 确保当前没在运行
            console.log('重新启动语音识别...')
            startSpeechRecognition()
          }
        }, 500)  // 增加延迟避免过快重启
      } else if (voiceRetryCount.value >= maxRetries) {
        console.warn('语音识别重试次数已达上限，停止自动重启')
        voiceEnabled.value = false
        ElMessage.warning('语音识别遇到问题，请手动重新启动')
      }
    }
    
    // 初始化成功
    return true
  } catch (error) {
    console.error('语音识别初始化失败:', error)
    ElMessage.error('语音识别初始化失败，请刷新页面重试')
  }
}

const startSpeechRecognition = async () => {
  try {
    console.log('尝试启动语音识别...')
    
    // 检查状态
    const status = {
      hasRecognition: !!recognition.value,
      isListening: isListening.value,
      voiceEnabled: voiceEnabled.value,
      hasCharacter: !!chatStore.selectedCharacter
    }
    console.log('当前状态:', status)
    
    // 如果没有初始化或初始化失败，重新初始化
    if (!recognition.value) {
      console.log('需要初始化语音识别...')
      const success = await initSpeechRecognition()
      if (!success) {
        throw new Error('语音识别初始化失败')
      }
    }
    
    // 检查是否可以启动
    if (!recognition.value) {
      throw new Error('语音识别未初始化')
    }
    
    if (!voiceEnabled.value) {
      throw new Error('语音识别未启用')
    }
    
    if (!chatStore.selectedCharacter) {
      throw new Error('未选择对话角色')
    }
    
    if (isListening.value) {
      console.log('语音识别已在运行')
      return
    }
    
    // 启动语音识别
    console.log('开始语音识别...')
    recognition.value.start()
    console.log('语音识别启动成功')
    
  } catch (error) {
    console.error('启动语音识别失败:', error)
    
    if (error.message.includes('already started')) {
      console.log('语音识别已在运行，尝试重启...')
      try {
        recognition.value.stop()
        await new Promise(resolve => setTimeout(resolve, 100))
        recognition.value.start()
        console.log('语音识别重启成功')
      } catch (e) {
        console.error('重启语音识别失败:', e)
        ElMessage.error('语音识别出错，请刷新页面重试')
      }
    } else {
      ElMessage.error(error.message || '语音识别启动失败，请刷新页面重试')
    }
  }
}

const toggleVoiceRecognition = () => {
  console.log('切换语音识别状态...')
  console.log('之前状态:', voiceEnabled.value)
  
  voiceEnabled.value = !voiceEnabled.value
  console.log('新状态:', voiceEnabled.value)
  
  if (voiceEnabled.value) {
    console.log('启用语音识别...')
    voiceRetryCount.value = 0  // 重置重试计数
    startSpeechRecognition()
  } else {
    console.log('禁用语音识别...')
    voiceRetryCount.value = 0  // 重置重试计数
    stopSpeechRecognition()
  }
}

const stopSpeechRecognition = () => {
  console.log('尝试停止语音识别...')
  console.log('当前状态:', {
    hasRecognition: !!recognition.value,
    isListening: isListening.value
  })
  
  if (recognition.value && isListening.value) {
    try {
      recognition.value.stop()
      console.log('语音识别已停止')
    } catch (error) {
      console.error('停止语音识别失败:', error)
    }
    isListening.value = false
  } else {
    console.log('不满足停止条件，跳过停止')
  }
}

// 全局音频对象，用于管理播放状态
let currentAudio = null

// 停止当前音频播放
const stopCurrentAudio = () => {
  if (currentAudio) {
    console.log('🛑 停止当前音频播放')
    currentAudio.pause()
    currentAudio.currentTime = 0
    currentAudio = null
    isSpeaking.value = false
  }
}

// 只播放AI生成的音频，不使用浏览器TTS
const playAIAudio = (aiMessage) => {
  if (!ttsEnabled.value) return
  
  console.log('🎵 准备播放AI音频:', aiMessage)
  
  // 先停止当前音频
  stopCurrentAudio()
  
  // 优先使用audioBase64数据播放
  if (aiMessage.audioBase64) {
    console.log('✨ 使用audioBase64数据播放音频')
    playAudioFromBase64(aiMessage.audioBase64)
    return
  }
  
  // 如果有audioUrl，尝试使用完整URL播放
  if (aiMessage.audioUrl) {
    const fullAudioUrl = aiMessage.audioUrl.startsWith('http') 
      ? aiMessage.audioUrl 
      : `http://localhost:8001${aiMessage.audioUrl}`
    console.log('✨ 使用完整URL播放音频:', fullAudioUrl)
    playAudioFromUrl(fullAudioUrl)
    return
  }
  
  // 如果没有AI音频，不播放任何音频（不使用浏览器TTS）
  console.log('❌ 没有AI音频数据，跳过播放')
  ElMessage.warning('AI音频生成失败，请重试')
}

// 使用Base64数据播放音频
const playAudioFromBase64 = async (audioBase64) => {
  try {
    console.log('📼 创建Base64音频Blob...')
    
    // 将Base64转换为Blob
    const binaryData = atob(audioBase64)
    const arrayBuffer = new ArrayBuffer(binaryData.length)
    const uint8Array = new Uint8Array(arrayBuffer)
    for (let i = 0; i < binaryData.length; i++) {
      uint8Array[i] = binaryData.charCodeAt(i)
    }
    
    const audioBlob = new Blob([arrayBuffer], { type: 'audio/wav' })
    const audioUrl = URL.createObjectURL(audioBlob)
    
    console.log('✅ Blob创建成功，大小:', audioBlob.size, '字节')
    
    const audio = new Audio()
    currentAudio = audio // 设置为当前音频
    
    // 处理音频播放事件
    audio.onloadstart = () => console.log('📼 开始加载Base64音频...')
    audio.onloadeddata = () => console.log('✅ Base64音频数据加载完成')
    audio.onplay = () => {
      console.log('🎵 开始播放Base64音频')
      isSpeaking.value = true
    }
    audio.onended = () => {
      console.log('✅ Base64音频播放结束')
      isSpeaking.value = false
      currentAudio = null
      URL.revokeObjectURL(audioUrl) // 清理URL
    }
    audio.onerror = (e) => {
      console.error('❌ Base64音频播放失败:', e)
      isSpeaking.value = false
      currentAudio = null
      URL.revokeObjectURL(audioUrl) // 清理URL
      ElMessage.warning('AI音频播放失败，使用系统TTS')
    }
    
    // 设置音频源并播放
    audio.src = audioUrl
    
    try {
      await audio.play()
      console.log('✅ 音频播放启动成功')
    } catch (playError) {
      console.error('❌ 音频play()失败:', playError)
      if (playError.name === 'AbortError') {
        console.log('⚠️ 音频播放被中断，可能是切换了新音频')
      } else {
        ElMessage.warning('AI音频播放失败')
      }
      currentAudio = null
      URL.revokeObjectURL(audioUrl)
    }
    
  } catch (error) {
    console.error('❌ Base64音频处理失败:', error)
    isSpeaking.value = false
    currentAudio = null
    ElMessage.warning('AI音频解析失败，使用系统TTS')
  }
}

// 播放音频URL的函数（备用）
const playAudioFromUrl = (audioUrl) => {
  try {
    const audio = new Audio()
    
    // 处理音频播放事件
    audio.onloadstart = () => console.log('📼 开始加载音频...')
    audio.onloadeddata = () => console.log('✅ 音频数据加载完成')
    audio.onplay = () => {
      console.log('🎵 开始播放音频')
      isSpeaking.value = true
    }
    audio.onended = () => {
      console.log('✅ 音频播放结束')
      isSpeaking.value = false
    }
    audio.onerror = (e) => {
      console.error('❌ 音频播放失败:', e)
      console.error('音频URL:', audioUrl)
      isSpeaking.value = false
      // 如果音频播放失败，使用TTS作为备选
      ElMessage.warning('音频播放失败，使用系统TTS')
    }
    
    // 设置音频源并播放
    audio.src = audioUrl
    audio.load()
    audio.play()
    
  } catch (error) {
    console.error('❌ 创建audio元素失败:', error)
    isSpeaking.value = false
  }
}

// 已删除浏览器TTS功能 - 只使用AI Agent生成的音频

const toggleTTS = () => {
  ttsEnabled.value = !ttsEnabled.value
  if (!ttsEnabled.value) {
    stopCurrentAudio() // 关闭TTS时停止AI音频
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 文件上传相关方法
const beforeUpload = (file) => {
  const isValidType = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown'].includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('只支持 PDF、Word、TXT、Markdown 格式文件!')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

const submitUpload = () => {
  if (!uploadRef.value) return
  
  uploadLoading.value = true
  uploadRef.value.submit()
}

const handleUploadSuccess = (response, file) => {
  uploadLoading.value = false
  ElMessage.success(`文档 ${file.name} 上传成功！`)
  loadCharacterDocuments() // 重新加载文档列表
  uploadRef.value.clearFiles() // 清空文件列表
}

const handleUploadError = (error, file) => {
  uploadLoading.value = false
  console.error('文件上传失败:', error)
  ElMessage.error(`文档 ${file.name} 上传失败: ${error.message || '未知错误'}`)
}

const loadCharacterDocuments = async () => {
  if (!chatStore.selectedCharacter) return
  
  try {
    const characterId = chatStore.selectedCharacter.characterId || chatStore.selectedCharacter.id
    const response = await fetch(`http://localhost:8001/documents/${characterId}`)
    
    if (response.ok) {
      const data = await response.json()
      characterDocuments.value = data.files
      console.log('角色文档加载成功:', data.files.length, '个文档')
    } else {
      console.error('加载角色文档失败:', response.statusText)
    }
  } catch (error) {
    console.error('加载角色文档失败:', error)
  }
}

const deleteDocument = async (fileId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文档吗？删除后无法恢复。', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    
    const characterId = chatStore.selectedCharacter.characterId || chatStore.selectedCharacter.id
    const response = await fetch(`http://localhost:8001/documents/${characterId}/${fileId}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('文档删除成功')
      loadCharacterDocuments() // 重新加载文档列表
    } else {
      ElMessage.error('文档删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文档失败:', error)
      ElMessage.error('文档删除失败')
    }
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生命周期
onMounted(async () => {
  try {
    console.log('开始初始化聊天页面...')
    
    // 初始化聊天状态
    await chatStore.initialize()
    console.log('聊天状态初始化完成')
    
    // 加载会话历史
    chatStore.loadConversationsFromLocal()
    console.log('会话历史加载完成')
    
    // 等待角色数据加载
    await new Promise(resolve => setTimeout(resolve, 500))
    console.log('可用角色:', chatStore.characters)
    
    // 自动选择角色
    if (!chatStore.selectedCharacter) {
      // 默认选择喜羊羊（儿子）
      const defaultCharacter = chatStore.characters.find(c => c.id === 'xiyang')
      if (defaultCharacter) {
        console.log('选择默认角色:', defaultCharacter.name)
        await chatStore.selectCharacter(defaultCharacter)
      } else {
        console.log('未找到默认角色，显示角色选择器')
      showCharacterSelector.value = true
      }
    }
    
    // 初始化语音识别
    console.log('初始化语音识别...')
    const success = await initSpeechRecognition()
    if (success) {
      console.log('语音识别初始化成功，自动启动...')
      voiceEnabled.value = true
      await startSpeechRecognition()
    } else {
      console.error('语音识别初始化失败')
      ElMessage.error('语音识别初始化失败，请刷新页面重试')
    }
    
  } catch (error) {
    console.error('页面初始化错误:', error)
    ElMessage.error('初始化失败，请刷新页面重试')
  }
})

// 监听角色变化
watch(() => chatStore.selectedCharacter, (newCharacter) => {
  if (!newCharacter) {
    stopSpeechRecognition()
    voiceEnabled.value = false
    characterDocuments.value = []
  } else {
    // 加载新角色的文档
    loadCharacterDocuments()
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

/* 文件上传按钮样式 */
.file-upload-toggle {
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

.file-upload-toggle:hover {
  background: #e8e8e8;
  transform: scale(1.1);
  border-color: #409eff;
  color: #409eff;
}

/* 文件上传对话框样式 */
.file-upload-dialog {
  padding: 20px 0;
}

.current-character-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  font-weight: 500;
}

.upload-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* 文档列表样式 */
.character-documents {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.character-documents h4 {
  margin: 0 0 16px 0;
  color: #606266;
  font-size: 16px;
}

.document-list {
  max-height: 300px;
  overflow-y: auto;
}

.document-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 8px;
  background: white;
  transition: all 0.3s ease;
}

.document-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.document-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.document-icon {
  font-size: 24px;
  color: #409eff;
}

.document-details {
  flex: 1;
  min-width: 0;
}

.document-name {
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.document-meta {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.document-summary {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
  
  .file-upload-dialog {
    padding: 16px 0;
  }
  
  .document-item {
    padding: 8px;
  }
  
  .document-name {
    font-size: 14px;
  }
}
</style>