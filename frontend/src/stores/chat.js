import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import chatService from '@/services/chatService'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const currentUser = ref(null)
  const selectedCharacter = ref(null)
  const characters = ref([])
  const messages = ref([])
  const isLoading = ref(false)
  const isRecording = ref(false)
  
  // 计算属性
  const hasMessages = computed(() => messages.value.length > 0)
  const currentCharacterName = computed(() => 
    selectedCharacter.value ? selectedCharacter.value.name : '当前角色'
  )
  
  // 方法
  const initializeUser = async () => {
    try {
      // 获取或创建默认用户
      let users = await chatService.getAllUsers()
      if (users.length === 0) {
        currentUser.value = await chatService.createUser({
          username: '爷爷奶奶',
          nickname: '测试用户',
          avatarUrl: '/images/user_default.png'
        })
      } else {
        currentUser.value = users[0]
      }
    } catch (error) {
      console.error('初始化用户失败:', error)
    }
  }
  
  const loadCharacters = async () => {
    try {
      characters.value = await chatService.getCharacters()
      if (characters.value.length > 0 && !selectedCharacter.value) {
        selectedCharacter.value = characters.value[0]
      }
    } catch (error) {
      console.error('加载角色失败:', error)
    }
  }
  
  const selectCharacter = async (character) => {
    selectedCharacter.value = character
    await loadConversationHistory()
  }
  
  const loadConversationHistory = async () => {
    if (!currentUser.value || !selectedCharacter.value) return
    
    try {
      const history = await chatService.getConversationHistory(
        currentUser.value.id, 
        selectedCharacter.value.id
      )
      
      messages.value = history.flatMap(conv => [
        {
          id: `${conv.id}-user`,
          content: conv.userMessage,
          sender: 'user',
          timestamp: conv.timestamp,
          avatar: currentUser.value.avatarUrl
        },
        {
          id: `${conv.id}-ai`,
          content: conv.aiResponse,
          sender: 'ai',
          timestamp: conv.timestamp,
          avatar: selectedCharacter.value.avatarUrl,
          characterName: selectedCharacter.value.name
        }
      ])
    } catch (error) {
      console.error('加载对话历史失败:', error)
    }
  }
  
  const sendMessage = async (content, audioData = null) => {
    if (!currentUser.value || !selectedCharacter.value) {
      throw new Error('请先选择用户和角色')
    }
    
    // 添加用户消息
    const userMessage = {
      id: `user-${Date.now()}`,
      content,
      sender: 'user',
      timestamp: new Date().toISOString(),
      avatar: currentUser.value.avatarUrl
    }
    
    messages.value.push(userMessage)
    isLoading.value = true
    
    try {
      const response = await chatService.sendTextMessage(
        currentUser.value.id,
        selectedCharacter.value.id,
        content
      )
      
      // 添加AI回复
      const aiMessage = {
        id: `ai-${Date.now()}`,
        content: response.aiResponseText,
        sender: 'ai',
        timestamp: new Date().toISOString(),
        avatar: selectedCharacter.value.avatarUrl,
        characterName: response.characterName,
        audioUrl: response.aiAudioUrl
      }
      
      messages.value.push(aiMessage)
      return aiMessage
      
    } catch (error) {
      console.error('发送消息失败:', error)
      
      // 添加错误消息
      const errorMessage = {
        id: `error-${Date.now()}`,
        content: '抱歉，我现在有点累了，请稍后再试。',
        sender: 'ai',
        timestamp: new Date().toISOString(),
        avatar: selectedCharacter.value.avatarUrl,
        characterName: selectedCharacter.value.name,
        isError: true
      }
      
      messages.value.push(errorMessage)
      throw error
      
    } finally {
      isLoading.value = false
    }
  }
  
  const clearMessages = () => {
    messages.value = []
  }
  
  const setRecording = (recording) => {
    isRecording.value = recording
  }
  
  // 初始化
  const initialize = async () => {
    await initializeUser()
    await loadCharacters()
    if (selectedCharacter.value) {
      await loadConversationHistory()
    }
  }
  
  return {
    // 状态
    currentUser,
    selectedCharacter,
    characters,
    messages,
    isLoading,
    isRecording,
    
    // 计算属性
    hasMessages,
    currentCharacterName,
    
    // 方法
    initialize,
    selectCharacter,
    sendMessage,
    clearMessages,
    setRecording,
    loadConversationHistory
  }
})
