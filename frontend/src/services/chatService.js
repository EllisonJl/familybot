/**
 * 聊天服务 - 封装与后端API的交互
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'

class ChatService {
  /**
   * 发送聊天消息
   */
  async sendMessage(data) {
    try {
      const response = await fetch(`${BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('发送消息失败:', error)
      throw error
    }
  }

  /**
   * 获取所有角色
   */
  async getCharacters() {
    try {
      const response = await fetch(`${BASE_URL}/characters`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('获取角色列表失败:', error)
      throw error
    }
  }

  /**
   * 切换角色
   */
  async switchCharacter(userId, characterId) {
    try {
      const response = await fetch(`${BASE_URL}/characters/${characterId}/switch?userId=${userId}`, {
        method: 'POST'
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('切换角色失败:', error)
      throw error
    }
  }

  /**
   * 获取角色问候语
   */
  async getCharacterGreeting(characterId) {
    try {
      const response = await fetch(`${BASE_URL}/characters/${characterId}/greeting`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('获取问候语失败:', error)
      throw error
    }
  }

  /**
   * 获取对话历史
   */
  async getConversationHistory(userId, characterId, page = 0, size = 20) {
    try {
      const params = new URLSearchParams({
        userId,
        characterId,
        page: page.toString(),
        size: size.toString()
      })

      const response = await fetch(`${BASE_URL}/conversations?${params}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('获取对话历史失败:', error)
      throw error
    }
  }

  /**
   * 获取用户统计信息
   */
  async getUserStats(userId) {
    try {
      const response = await fetch(`${BASE_URL}/users/${userId}/stats`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('获取用户统计失败:', error)
      throw error
    }
  }

  /**
   * 健康检查
   */
  async healthCheck() {
    try {
      const response = await fetch(`${BASE_URL}/health`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('健康检查失败:', error)
      throw error
    }
  }

  /**
   * 语音转文字
   */
  async speechToText(audioFile) {
    try {
      const formData = new FormData()
      formData.append('audio_file', audioFile)

      // 直接调用AI Agent的ASR接口
      const aiAgentUrl = import.meta.env.VITE_AI_AGENT_BASE_URL || 'http://localhost:8001'
      const response = await fetch(`${aiAgentUrl}/asr`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('语音识别失败:', error)
      throw error
    }
  }

  /**
   * 文字转语音
   */
  async textToSpeech(text, voice = 'Cherry', speed = 1.0) {
    try {
      const params = new URLSearchParams({
        text,
        voice,
        speed: speed.toString()
      })

      // 直接调用AI Agent的TTS接口
      const aiAgentUrl = import.meta.env.VITE_AI_AGENT_BASE_URL || 'http://localhost:8001'
      const response = await fetch(`${aiAgentUrl}/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: params
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('语音合成失败:', error)
      throw error
    }
  }
}

// 创建单例实例
export const chatService = new ChatService()
