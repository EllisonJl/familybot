<template>
  <div class="conversation-sidebar" :class="{ 'collapsed': collapsed }">
    <!-- 侧边栏头部 -->
    <div class="sidebar-header">
      <div class="header-content">
        <h3 v-if="!collapsed">历史对话</h3>
        <el-button 
          @click="createNew" 
          type="primary" 
          size="small"
          :icon="Plus"
          :circle="collapsed"
        >
          <span v-if="!collapsed">新对话</span>
        </el-button>
      </div>
      <el-button 
        @click="toggleCollapse" 
        type="text" 
        size="small"
        :icon="collapsed ? ArrowRight : ArrowLeft"
        class="collapse-btn"
      />
    </div>

    <!-- 会话列表 -->
    <div class="conversation-list" v-if="!collapsed">
      <div 
        v-for="conversation in conversations"
        :key="conversation.id"
        class="conversation-item"
        :class="{ 'active': conversation.id === currentConversationId }"
        @click="switchTo(conversation.id)"
      >
        <div class="conversation-info">
          <div class="conversation-title">{{ conversation.title }}</div>
          <div class="conversation-meta">
            <span class="character-name">{{ conversation.characterName }}</span>
            <span class="message-count">{{ conversation.messageCount }}条消息</span>
          </div>
          <div class="conversation-time">{{ formatTime(conversation.updatedAt) }}</div>
        </div>
        <div class="conversation-actions">
          <el-button 
            @click.stop="deleteConv(conversation.id)"
            type="text" 
            size="small"
            :icon="Delete"
            class="delete-btn"
          />
        </div>
      </div>
    </div>

    <!-- 折叠状态下的简化显示 -->
    <div class="collapsed-list" v-else>
      <div 
        v-for="(conversation, index) in conversations.slice(0, 5)"
        :key="conversation.id"
        class="collapsed-item"
        :class="{ 'active': conversation.id === currentConversationId }"
        @click="switchTo(conversation.id)"
        :title="conversation.title"
      >
        {{ index + 1 }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowLeft, ArrowRight, Delete } from '@element-plus/icons-vue'
import { useChatStore } from '@/stores/chat'

// Props
const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['toggle-collapse'])

// Store
const chatStore = useChatStore()

// Computed
const conversations = computed(() => chatStore.conversations)
const currentConversationId = computed(() => chatStore.currentConversationId)

// Methods
const createNew = () => {
  chatStore.createNewConversation()
  ElMessage.success('已创建新对话')
}

const switchTo = (conversationId) => {
  chatStore.switchConversation(conversationId)
}

const deleteConv = async (conversationId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个对话吗？删除后无法恢复。',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    chatStore.deleteConversation(conversationId)
    ElMessage.success('对话已删除')
  } catch {
    // 用户取消删除
  }
}

const toggleCollapse = () => {
  emit('toggle-collapse')
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) { // 1分钟内
    return '刚刚'
  } else if (diff < 3600000) { // 1小时内
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) { // 24小时内
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleDateString()
  }
}
</script>

<style scoped>
.conversation-sidebar {
  width: 280px;
  height: 100vh;
  background: #f8f9fa;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.conversation-sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.header-content h3 {
  margin: 0;
  font-size: 16px;
  color: #374151;
}

.collapse-btn {
  padding: 4px;
  min-width: 24px;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-item {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border: 1px solid transparent;
}

.conversation-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.conversation-item.active {
  background: #eff6ff;
  border-color: #3b82f6;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-weight: 500;
  color: #374151;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
}

.character-name {
  background: #f0f9ff;
  color: #0369a1;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.message-count {
  color: #6b7280;
  font-size: 12px;
}

.conversation-time {
  color: #9ca3af;
  font-size: 11px;
}

.conversation-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.conversation-item:hover .conversation-actions {
  opacity: 1;
}

.delete-btn {
  color: #dc2626;
  padding: 4px;
  min-width: 24px;
}

.collapsed-list {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.collapsed-item {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #e5e7eb;
  color: #6b7280;
  font-weight: 500;
  font-size: 12px;
}

.collapsed-item:hover {
  background: #d1d5db;
}

.collapsed-item.active {
  background: #3b82f6;
  color: white;
}

/* 滚动条样式 */
.conversation-list::-webkit-scrollbar {
  width: 4px;
}

.conversation-list::-webkit-scrollbar-track {
  background: transparent;
}

.conversation-list::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 2px;
}

.conversation-list::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
