<template>
  <el-dialog
    v-model="visible"
    title="选择家庭成员"
    width="600px"
    :before-close="handleClose"
    class="character-dialog"
  >
    <div class="character-grid">
      <div
        v-for="character in characters"
        :key="character.id"
        :class="['character-card', { 'selected': character.id === selectedCharacterId }]"
        @click="selectCharacter(character)"
      >
        <div class="character-avatar">
          <el-avatar :size="80" :src="character.avatarUrl">
            <el-icon size="40"><Avatar /></el-icon>
          </el-avatar>
        </div>
        
        <div class="character-info">
          <h3 class="character-name">{{ character.name }}</h3>
          <p class="character-role">{{ character.role }}</p>
          <p class="character-personality">{{ character.personality }}</p>
        </div>
        
        <!-- 选中标识 -->
        <div v-if="character.id === selectedCharacterId" class="selected-indicator">
          <el-icon><Check /></el-icon>
        </div>
      </div>
    </div>
    
    <!-- 底部操作按钮 -->
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          @click="confirmSelection"
          :disabled="!selectedCharacterId"
        >
          确定选择
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Avatar, Check } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  characters: {
    type: Array,
    default: () => []
  },
  currentCharacter: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'select'])

// 响应式数据
const visible = ref(props.modelValue)
const selectedCharacterId = ref(props.currentCharacter?.id || null)

// 监听props变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

watch(() => props.currentCharacter, (newCharacter) => {
  selectedCharacterId.value = newCharacter?.id || null
})

// 方法
const selectCharacter = (character) => {
  selectedCharacterId.value = character.id
}

const confirmSelection = () => {
  const selected = props.characters.find(c => c.id === selectedCharacterId.value)
  if (selected) {
    emit('select', selected)
  }
  handleClose()
}

const handleClose = () => {
  visible.value = false
  emit('update:modelValue', false)
}
</script>

<style scoped>
.character-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.character-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.character-card {
  position: relative;
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.character-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.character-card.selected {
  border-color: #409eff;
  background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.character-avatar {
  margin-bottom: 15px;
}

.character-info {
  text-align: center;
}

.character-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.character-role {
  font-size: 14px;
  color: #409eff;
  margin: 0 0 10px 0;
  font-weight: 500;
}

.character-personality {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
  margin: 0;
  text-align: left;
  background: #f5f7fa;
  padding: 8px;
  border-radius: 6px;
}

.selected-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 24px;
  height: 24px;
  background: #409eff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .character-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 20px auto;
  }
  
  .character-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .character-card {
    padding: 15px;
  }
  
  .character-name {
    font-size: 16px;
  }
  
  .character-personality {
    font-size: 11px;
  }
}
</style>
