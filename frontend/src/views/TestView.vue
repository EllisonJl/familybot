<template>
  <div class="test-page">
    <h1>🎉 Vue应用工作正常！</h1>
    <p>当前时间: {{ currentTime }}</p>
    <button @click="updateTime">更新时间</button>
    <p>点击次数: {{ clickCount }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentTime = ref('')
const clickCount = ref(0)

const updateTime = () => {
  currentTime.value = new Date().toLocaleString()
  clickCount.value++
}

onMounted(() => {
  updateTime()
})
</script>

<style scoped>
.test-page {
  padding: 50px;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  min-height: 100vh;
}

h1 {
  font-size: 2.5em;
  margin-bottom: 30px;
}

button {
  background: #fff;
  color: #333;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  margin: 20px;
  font-size: 16px;
}

button:hover {
  background: #f0f0f0;
}
</style>
