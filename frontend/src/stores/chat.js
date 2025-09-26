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
      id: 'default',
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
    characterId: 'xiyang',
    name: '喜羊羊',
    role: '儿子',
    personality: '聪明、勇敢、孝顺、责任心强，总是关心家人的安全和健康',
    avatarUrl: '/images/character_xiyang.png'
  },
  {
    id: 'meiyang',
    characterId: 'meiyang',
    name: '美羊羊',
    role: '女儿',
    personality: '温柔、细心、贴心、善解人意，是父母的贴心小棉袄',
    avatarUrl: '/images/character_meiyang.png'
  },
  {
    id: 'lanyang',
    characterId: 'lanyang',
    name: '懒羊羊',
    role: '孙子',
    personality: '天真烂漫、活泼可爱、爱撒娇、充满童趣，是爷爷奶奶的开心果',
    avatarUrl: '/images/character_lanyang.png'
  }
]
    
    try {
      const apiCharacters = await chatService.getCharacters()
      if (apiCharacters.length > 0) {
        // 处理API角色数据，确保兼容性
        characters.value = apiCharacters.map(char => ({
          ...char,
          id: char.characterId || char.id,  // 确保有id字段
          characterId: char.characterId || char.id  // 确保有characterId字段
        }))
        console.log('角色数据加载成功:', characters.value.length, '个角色')
        console.log('第一个角色数据:', characters.value[0])
      } else {
        characters.value = defaultCharacters
      }
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
    
    // 清空当前对话
    messages.value = []
    
    // 保存到本地存储
    localStorage.setItem('selectedCharacter', JSON.stringify(character))
    
    console.log('已选择角色:', character.name)
    
    // AI先发送欢迎消息
    await sendWelcomeMessage(character)
  }
  
  const sendWelcomeMessage = async (character) => {
    try {
      isLoading.value = true
      
      // 使用默认欢迎消息，让AI主动关怀用户
      const welcomeMessage = getDefaultWelcomeMessage(character)
      
      const aiMessage = {
        id: `welcome-${Date.now()}`,
        content: welcomeMessage,
        sender: 'ai',
        timestamp: new Date().toISOString(),
        avatar: character.avatarUrl,
        characterName: character.name,
        isWelcome: true
      }
      
      messages.value.push(aiMessage)
      
      console.log('AI欢迎消息已发送:', aiMessage.content)
      
    } catch (error) {
      console.error('发送欢迎消息失败:', error)
    } finally {
      isLoading.value = false
    }
  }
  
  const getDefaultWelcomeMessage = (character) => {
    const welcomeMessages = {
      'xiyang': '爸爸妈妈好！我是你们的儿子喜羊羊，好久没回家了，真的很想念你们！最近工作虽然忙，但我身体很好，你们身体还好吗？有没有按时吃药？记得要多注意保暖哦！',
      'meiyang': '爸爸妈妈，我是美羊羊！好想你们呀！你们最近身体怎么样？有没有好好照顾自己？妈妈的腰还疼吗？爸爸记得按时吃降压药哦！我虽然不在身边，但心里时时刻刻都牵挂着你们！',
      'lanyang': '爷爷奶奶！我是小懒羊羊，好开心见到你们呀！你们身体还好吗？我超级超级想你们的！爷爷的胡子又长长了呢！奶奶今天也很漂亮哦！我在学校学了好多新东西，想讲给你们听！'
    }
    
    return welcomeMessages[character.id] || `您好，我是${character.name}，很高兴和您聊天！`
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
      console.log('当前用户:', currentUser.value)
      console.log('选中角色:', selectedCharacter.value)
      
      if (!selectedCharacter.value || !selectedCharacter.value.id) {
        throw new Error('请先选择一个角色')
      }
      
      const characterId = selectedCharacter.value.characterId || selectedCharacter.value.id
      if (!characterId) {
        throw new Error('角色ID缺失，请重新选择角色')
      }
      
      console.log('发送消息参数:', {
        userId: currentUser.value.id,
        characterId: characterId,
        message: content
      })
      
      const response = await chatService.sendTextMessage(
        currentUser.value.id,
        characterId,
        content
      )
      
      // 添加AI回复
      console.log('🤖 AI回复数据:', response)
      const aiMessage = {
        id: `ai-${Date.now()}`,
        content: response.aiResponseText || response.response || response.message || '系统繁忙，请稍后重试',
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
      
      // 显示真实的错误信息，不使用fallback
      const errorMessage = {
        id: `error-${Date.now()}`,
        content: `❌ 发送失败: ${error.message || '网络连接错误'}`,
        sender: 'system',
        timestamp: new Date().toISOString(),
        avatar: '/images/error.png',
        characterName: '系统',
        isError: true
      }
      
      messages.value.push(errorMessage)
      
      // 重新抛出错误，让上层处理
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
    sendWelcomeMessage,
    getDefaultWelcomeMessage,
    
    // 会话管理方法
    createNewConversation,
    switchConversation,
    updateConversationTitle,
    deleteConversation,
    loadConversationsFromLocal
  }
})
