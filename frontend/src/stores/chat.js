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
    avatarUrl: '/images/character_xiyang.png',
    voice: 'onyx',  // OpenAI深沉男声，成熟稳重 - 儿子
    voice_speed: 1.0
  },
  {
    id: 'meiyang',
    characterId: 'meiyang',
    name: '美羊羊',
    role: '女儿',
    personality: '温柔、细心、贴心、善解人意，是父母的贴心小棉袄',
    avatarUrl: '/images/character_meiyang.png',
    voice: 'nova',  // OpenAI优雅女声，清晰温暖 - 女儿
    voice_speed: 0.9
  },
  {
    id: 'lanyang',
    characterId: 'lanyang',
    name: '懒羊羊',
    role: '孙子',
    personality: '天真烂漫、活泼可爱、爱撒娇、充满童趣，是爷爷奶奶的开心果',
    avatarUrl: '/images/character_lanyang.png',
    voice: 'fable',  // OpenAI英国口音，年轻活泼 - 孙子
    voice_speed: 1.1
  }
]
    
    try {
      const apiCharacters = await chatService.getCharacters()
      if (apiCharacters.length > 0) {
        // 处理API角色数据，确保兼容性
        characters.value = apiCharacters.map(char => ({
          ...char,
          id: char.characterId || char.id,  // 确保有id字段
          characterId: char.characterId || char.id,  // 确保有characterId字段
          // 保证音色配置存在
          voice: char.voice || (char.id === 'xiyang' ? 'onyx' : char.id === 'meiyang' ? 'shimmer' : 'fable'),
          voice_speed: char.voice_speed || 1.0
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
    console.log('🎭 开始选择角色:', character.name, '角色数据:', character)
    
    selectedCharacter.value = character
    
    // 强制清空当前对话和缓存
    messages.value = []
    console.log('🗨️ 已清空消息列表')
    
    // 清除相关缓存（防止干扰）
    localStorage.removeItem('conversationHistory')
    localStorage.removeItem('welcomeMessageSent')
    localStorage.setItem('selectedCharacter', JSON.stringify(character))
    console.log('🧽 已清除相关缓存')
    
    console.log('✅ 已选择角色:', character.name)
    
    // 强制发送欢迎消息（不管以前是否发过）
    console.log('🚀 开始发送欢迎消息...')
    await sendWelcomeMessage(character)
  }
  
  const sendWelcomeMessage = async (character) => {
    try {
      isLoading.value = true
      
      console.log('🎆 强制发送欢迎消息给:', character.name, '角色ID:', character.id)
      
      // 使用默认欢迎消息，让AI主动关怀用户
      const welcomeMessage = getDefaultWelcomeMessage(character)
      console.log('📝 欢迎消息内容:', welcomeMessage.substring(0, 50) + '...')
      
      const aiMessage = {
        id: `welcome-${Date.now()}`,
        content: welcomeMessage,
        sender: 'ai',
        timestamp: new Date().toISOString(),
        avatar: character.avatarUrl,
        characterName: character.name,
        isWelcome: true
      }
      
      // 生成欢迎消息的TTS音频
      try {
        console.log('🎵 为欢迎消息生成TTS音频...', character.name)
        
        // 获取角色的音色配置（确保有默认值）
        const voiceConfig = {
          voice: character.voice || (character.id === 'xiyang' ? 'onyx' : character.id === 'meiyang' ? 'shimmer' : 'fable'),
          speed: character.voice_speed || 1.0
        }
        console.log('🎵 音色配置:', voiceConfig)
        
        // 调用AI Agent生成TTS音频
        const ttsResponse = await chatService.generateWelcomeTTS(
          currentUser.value.id,
          character.characterId || character.id,
          welcomeMessage,
          voiceConfig
        )
        
        if (ttsResponse && (ttsResponse.audioBase64 || ttsResponse.audioUrl)) {
          aiMessage.audioBase64 = ttsResponse.audioBase64
          aiMessage.audioUrl = ttsResponse.audioUrl
          console.log('✅ 欢迎消息 TTS 生成成功')
        }
      } catch (ttsError) {
        console.warn('⚠️ 欢迎消息 TTS 生成失败:', ttsError)
        // TTS失败不影响欢迎消息发送
      }
      
      messages.value.push(aiMessage)
      
      console.log('✅ AI欢迎消息已添加到消息列表:', aiMessage.content.substring(0, 30) + '...')
      console.log('📊 当前消息数量:', messages.value.length)
      
      // 如果有音频数据，尝试播放
      if (aiMessage.audioBase64 || aiMessage.audioUrl) {
        console.log('🎶 欢迎消息包含音频，将自动播放')
      } else {
        console.log('⚠️ 欢迎消息没有音频数据（TTS可能失败）')
      }
      
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
  
  const sendMessage = async (content, audioData = null, forceWebSearch = false) => {
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
      
      // 获取角色的音色配置
      const voiceConfig = {
        voice: selectedCharacter.value.voice,  // 传递角色音色
        speed: selectedCharacter.value.voice_speed || 1.0
      }
      
      console.log('🎵 传递音色配置:', voiceConfig)
      
      const response = await chatService.sendTextMessage(
        currentUser.value.id,
        characterId,
        content,
        voiceConfig,  // 添加音色配置参数
        forceWebSearch  // 添加联网搜索参数
      )
      
      // 添加AI回复
      console.log('🤖 AI回复数据:', response)
      
      // 🐞 调试: 检查store接收的图片数据
      console.log('🖼️ Store接收到的图片数据:', {
        imageUrl: !!response.imageUrl,
        imageBase64: !!response.imageBase64,
        imageDescription: response.imageDescription,
        imageUrl_value: response.imageUrl ? response.imageUrl.substring(0, 50) + '...' : '无',
        imageBase64_length: response.imageBase64 ? response.imageBase64.length : 0
      })
      const aiMessage = {
        id: `ai-${Date.now()}`,
        content: response.aiResponseText || response.response || response.message || '系统繁忙，请稍后重试',
        sender: 'ai',
        timestamp: new Date().toISOString(),
        avatar: selectedCharacter.value.avatarUrl,
        characterName: response.characterName || selectedCharacter.value.name,
        audioUrl: response.aiAudioUrl,
        audioBase64: response.audioBase64,  // 添加audioBase64数据
        // 图片相关字段 - 处理字段名不匹配的问题
        imageUrl: response.imageUrl || response.image_url,
        imageBase64: response.imageBase64 || response.image_base64,
        imageDescription: response.imageDescription || response.image_description,
        enhancedPrompt: response.enhancedPrompt || response.enhanced_prompt
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
