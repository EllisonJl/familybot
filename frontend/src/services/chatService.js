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
  sendTextMessage: async (userId, characterId, message) => {
    try {
      const requestData = {
        userId,
        characterId,
        message,
        useAgent: true,  // 强制使用AI Agent
        role: 'elderly'  // 指定角色为老人
      }
      console.log('发送文本消息:', requestData)
      console.log('请求URL:', '/chat')
      
      const response = await api.post('/chat', requestData)
      console.log('收到完整响应:', response)
      return response.data
    } catch (error) {
      console.error('发送文本消息失败:', error)
      console.error('错误详情:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: error.config
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