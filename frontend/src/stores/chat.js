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
  const conversations = ref([])
  const currentConversationId = ref(null)
  
  // 计算属性
  const hasMessages = computed(() => messages.value.length > 0)
  const currentCharacterName = computed(() => 
    selectedCharacter.value ? selectedCharacter.value.name : '当前角色'
  )
  
  // 方法
  const initializeUser = async () => {
    // 首先设置默认用户数据，确保始终有可用用户
    const defaultUser = {
      id: 'default-user',
      username: '爷爷奶奶',
      nickname: '默认用户',
      avatarUrl: '/images/user_default.png'
    }
    
    try {
      // 尝试获取API用户数据
      let users = await chatService.getAllUsers()
      if (users.length === 0) {
        currentUser.value = await chatService.createUser(defaultUser)
      } else {
        currentUser.value = users[0]
      }
      console.log('用户数据加载成功:', currentUser.value.username)
    } catch (error) {
      console.error('初始化用户失败，使用默认用户:', error)
      // 使用默认用户数据
      currentUser.value = defaultUser
    }
  }
  
  const loadCharacters = async () => {
    // 首先设置默认角色数据，确保始终有可用角色
    const defaultCharacters = [
      {
        id: 'xiyang',
        name: '喜羊羊',
        role: '贴心的儿子',
        personality: '我是您的儿子喜羊羊，总是关心您的健康和心情，喜欢和您聊天谈心。虽然在外地工作，但时刻牵挂着家里。',
        avatarUrl: '/images/character_xiyang.png'
      },
      {
        id: 'meiyang',
        name: '美羊羊',
        role: '温柔的女儿',
        personality: '我是您的女儿美羊羊，细心体贴，喜欢和您分享生活中的点点滴滴。我最关心您的身体健康和心情。',
        avatarUrl: '/images/character_meiyang.png'
      },
      {
        id: 'lanyang',
        name: '懒羊羊',
        role: '活泼的孙子',
        personality: '我是您的孙子懒羊羊，虽然有时候比较懒，但我很爱您！总是有很多有趣的话题想要和您聊。',
        avatarUrl: '/images/character_lanyang.png'
      }
    ]
    
    try {
      const apiCharacters = await chatService.getCharacters()
      // 优先使用API数据，如果为空则使用默认数据
      characters.value = apiCharacters.length > 0 ? apiCharacters : defaultCharacters
      console.log('角色数据加载成功:', characters.value.length, '个角色')
    } catch (error) {
      console.error('加载角色失败，使用默认角色:', error)
      // 使用默认角色数据
      characters.value = defaultCharacters
    }
    
    // 确保总是有选中的角色
    if (!selectedCharacter.value && characters.value.length > 0) {
      selectedCharacter.value = characters.value[0]
      console.log('自动选择角色:', selectedCharacter.value.name)
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
        content: response.aiResponseText || response.message,
        sender: 'ai',
        timestamp: new Date().toISOString(),
        avatar: selectedCharacter.value.avatarUrl,
        characterName: response.characterName || selectedCharacter.value.name,
        audioUrl: response.aiAudioUrl
      }
      
      messages.value.push(aiMessage)
      return aiMessage
      
    } catch (error) {
      console.error('发送消息失败:', error)
      
      // Fallback: 提供简单的回复
      const fallbackReplies = [
        `您好，我是${selectedCharacter.value.name}。很高兴和您聊天！`,
        `谢谢您和我分享，我会认真听您说的每一句话。`,
        `您说得对，我们继续聊下去吧。`,
        `我理解您的想法，让我们一起聊聊这个话题。`,
        `您今天过得怎么样？我很关心您的近况。`
      ]
      
      const randomReply = fallbackReplies[Math.floor(Math.random() * fallbackReplies.length)]
      
      // 添加fallback回复
      const fallbackMessage = {
        id: `fallback-${Date.now()}`,
        content: randomReply,
        sender: 'ai',
        timestamp: new Date().toISOString(),
        avatar: selectedCharacter.value.avatarUrl,
        characterName: selectedCharacter.value.name,
        isFallback: true
      }
      
      messages.value.push(fallbackMessage)
      
      // 保存消息到当前会话
      if (currentConversationId.value) {
        localStorage.setItem(`conv-messages-${currentConversationId.value}`, JSON.stringify(messages.value))
        
        // 更新会话信息
        const conversation = conversations.value.find(c => c.id === currentConversationId.value)
        if (conversation) {
          conversation.messageCount = messages.value.length
          conversation.updatedAt = new Date().toISOString()
          // 如果是第一条消息，用消息内容作为标题
          if (conversation.messageCount === 2 && conversation.title === '新的对话') {
            conversation.title = content.slice(0, 20) + (content.length > 20 ? '...' : '')
          }
          saveConversationsToLocal()
        }
      }
      
      return fallbackMessage
      
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

  // 会话管理方法
  const createNewConversation = () => {
    const newConversation = {
      id: `conv-${Date.now()}`,
      title: '新的对话',
      characterId: selectedCharacter.value?.id,
      characterName: selectedCharacter.value?.name,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messageCount: 0
    }
    
    conversations.value.unshift(newConversation)
    currentConversationId.value = newConversation.id
    messages.value = []
    
    // 保存到localStorage
    saveConversationsToLocal()
    
    return newConversation
  }

  const switchConversation = (conversationId) => {
    const conversation = conversations.value.find(c => c.id === conversationId)
    if (conversation) {
      currentConversationId.value = conversationId
      // 这里可以加载该会话的历史消息
      loadConversationMessages(conversationId)
    }
  }

  const updateConversationTitle = (conversationId, title) => {
    const conversation = conversations.value.find(c => c.id === conversationId)
    if (conversation) {
      conversation.title = title
      conversation.updatedAt = new Date().toISOString()
      saveConversationsToLocal()
    }
  }

  const deleteConversation = (conversationId) => {
    const index = conversations.value.findIndex(c => c.id === conversationId)
    if (index > -1) {
      conversations.value.splice(index, 1)
      if (currentConversationId.value === conversationId) {
        if (conversations.value.length > 0) {
          switchConversation(conversations.value[0].id)
        } else {
          createNewConversation()
        }
      }
      saveConversationsToLocal()
    }
  }

  const loadConversationMessages = (conversationId) => {
    // 从localStorage加载该会话的消息
    const savedMessages = localStorage.getItem(`conv-messages-${conversationId}`)
    if (savedMessages) {
      messages.value = JSON.parse(savedMessages)
    } else {
      messages.value = []
    }
  }

  const saveConversationsToLocal = () => {
    localStorage.setItem('familybot-conversations', JSON.stringify(conversations.value))
  }

  const loadConversationsFromLocal = () => {
    const saved = localStorage.getItem('familybot-conversations')
    if (saved) {
      conversations.value = JSON.parse(saved)
      if (conversations.value.length > 0) {
        currentConversationId.value = conversations.value[0].id
      }
    }
    
    // 如果没有会话，创建一个新的
    if (conversations.value.length === 0) {
      createNewConversation()
    }
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
    conversations,
    currentConversationId,
    
    // 计算属性
    hasMessages,
    currentCharacterName,
    
    // 方法
    initialize,
    selectCharacter,
    sendMessage,
    clearMessages,
    setRecording,
    loadConversationHistory,
    
    // 会话管理方法
    createNewConversation,
    switchConversation,
    updateConversationTitle,
    deleteConversation,
    loadConversationsFromLocal
  }
})
