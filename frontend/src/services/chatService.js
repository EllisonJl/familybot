import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('收到响应:', response.status, response.config.url, response.data)
    return response
  },
  error => {
    console.error('响应错误:', error.response?.status, error.message, error.response?.data)
    
    // 统一错误处理
    if (error.response?.status === 404) {
      console.error('API端点不存在:', error.config.url)
    } else if (error.response?.status >= 500) {
      console.error('服务器内部错误')
    }
    
    return Promise.reject(error)
  }
)

const chatService = {
  // 发送文本消息
  sendTextMessage: async (userId, characterId, message, voiceConfig = null, forceWebSearch = false) => {
    try {
      // 🔧 临时修复：直接调用AI Agent，绕过后端通信问题
      console.log('🔧 临时使用直接AI Agent调用')
      
      const aiAgentData = {
        user_id: userId,
        character_id: characterId,
        message: message,
        force_web_search: forceWebSearch,
        voice_config: voiceConfig
      }
      
      console.log('直接调用AI Agent:', aiAgentData)
      
      // 直接调用AI Agent
      const aiResponse = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(aiAgentData)
      })
      
      if (!aiResponse.ok) {
        throw new Error(`AI Agent请求失败: ${aiResponse.status}`)
      }
      
      const aiData = await aiResponse.json()
      console.log('AI Agent响应:', aiData)
      
      // 检查AI Agent响应是否有效
      if (!aiData.response || aiData.response.trim() === '') {
        console.error('❌ AI Agent返回空响应:', aiData)
        throw new Error('AI Agent返回了空响应，请稍后重试')
      }
      
      // 转换为前端期望的格式
      const frontendResponse = {
        characterId: aiData.character_id || characterId,
        characterName: aiData.character_name || '喜羊羊',
        response: aiData.response,
        emotion: aiData.emotion || 'neutral',
        timestamp: aiData.timestamp || new Date().toISOString(),
        audioUrl: aiData.audio_url,
        audioBase64: aiData.audio_base64,
        webSearchUsed: aiData.web_search_used || false,
        webSearchQuery: aiData.web_search_query,
        webSearchResultsCount: aiData.web_search_results_count || 0
      }
      
      console.log('转换后的前端响应:', frontendResponse)
      return frontendResponse
      
    } catch (error) {
      console.error('发送文本消息失败:', error)
      console.error('错误详情:', {
        message: error.message,
        stack: error.stack
      })
      throw error
    }
  },

  // 发送语音消息
  sendAudioMessage: async (userId, characterId, audioBase64) => {
    try {
      console.log('发送语音消息:', { userId, characterId })
      const response = await api.post('/chat', {
        userId,
        characterId,
        audioBase64,
        useAgent: true,  // 强制使用AI Agent
        role: 'elderly'  // 指定角色为老人
      })
      return response.data
    } catch (error) {
      console.error('发送语音消息失败:', error)
      throw error
    }
  },

  // 获取所有角色
  getCharacters: async () => {
    try {
      const response = await api.get('/characters')
      return response.data
    } catch (error) {
      console.error('获取角色列表失败:', error)
      throw error
    }
  },

  // 生成欢迎消息TTS音频
  generateWelcomeTTS: async (userId, characterId, message, voiceConfig) => {
    try {
      console.log('🎵 调用AI Agent生成欢迎消息TTS...', { characterId, voiceConfig })
      
      // 直接调用AI Agent的TTS接口 (使用query参数)
      const params = new URLSearchParams({
        text: message,
        voice: voiceConfig.voice,
        speed: voiceConfig.speed || 1.0,
        user_id: userId
      })
      const aiAgentResponse = await fetch(`http://localhost:8001/tts?${params}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (aiAgentResponse.ok) {
        const ttsData = await aiAgentResponse.json()
        console.log('✅ 欢迎消息TTS生成成功', ttsData)
        return {
          audioBase64: ttsData.audio_base64,
          audioUrl: ttsData.audio_url
        }
      } else {
        console.warn('⚠️ AI Agent TTS请求失败:', aiAgentResponse.status)
        return null
      }
      
    } catch (error) {
      console.error('❌ 欢迎消息TTS生成失败:', error)
      return null
    }
  },

  // 获取指定用户和角色的对话历史
  getConversationHistory: async (userId, characterId) => {
    try {
      const response = await api.get(`/conversations/${userId}/${characterId}`)
      return response.data
    } catch (error) {
      console.error('获取对话历史失败:', error)
      throw error
    }
  },

  // 获取所有用户
  getAllUsers: async () => {
    try {
      const response = await api.get('/users')
      return response.data
    } catch (error) {
      console.error('获取用户列表失败:', error)
      throw error
    }
  },

  // 创建用户
  createUser: async (userData) => {
    try {
      console.log('创建用户:', userData)
      const response = await api.post('/users', userData)
      return response.data
    } catch (error) {
      console.error('创建用户失败:', error)
      throw error
    }
  },

  // 获取用户信息
  getUserById: async (userId) => {
    try {
      const response = await api.get(`/users/${userId}`)
      return response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }
}

export default chatService