<template>
  <div class="page">
    <!-- 动态视频背景 -->
    <video 
      class="background-video" 
      autoplay 
      muted 
      loop 
      playsinline
    >
      <source src="/website background.mp4" type="video/mp4">
      您的浏览器不支持视频播放
    </video>
    
    <!-- 背景图片层 -->
    <div class="background-image"></div>
    
    <!-- 自然渐变遮罩 -->
    <div class="natural-overlay"></div>

    <!-- Meela风格导航栏 -->
    <nav class="meela-navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <span class="brand-name">FamilyBot</span>
          <span class="brand-icon">🎵</span>
        </div>
        <div class="nav-menu">
          <span class="nav-item">功能介绍</span>
          <span class="nav-item">使用指南</span>
          <span class="nav-item">常见问题</span>
          <span class="nav-item">关于我们</span>
          <button class="get-started-btn" @click="goToChat">开始聊天</button>
        </div>
      </div>
    </nav>

    <!-- 动态粒子背景 -->
    <div class="particles-container">
      <div class="particle" v-for="i in 50" :key="i" :style="getParticleStyle(i)"></div>
    </div>

    <!-- 主要内容区域 -->
    <main class="hero-section">
      <!-- 特色标签 -->
      <div class="feature-badge">
        <span>🎵 Featured on China Daily</span>
        <div class="badge-arrow">></div>
      </div>

      <!-- 主标题区域 -->
      <div class="hero-content">
        <h1 class="hero-title">
          温暖的AI陪伴<br>
          为您的黄金岁月
        </h1>
        <p class="hero-subtitle">
          FamilyBot 是一个个性化的AI语音助手，专门为老年朋友设计，<br>
          通过定期的语音通话提供情感陪伴和贴心关怀。
        </p>
        
        
        <!-- 行动按钮 -->
        <div class="hero-actions">
          <button class="secondary-btn glass-btn" @mouseenter="playSecondaryButtonEffect">
            <span class="btn-icon">🔊</span>
            <span class="btn-text">听听 FamilyBot</span>
            <div class="btn-shine"></div>
          </button>
          <button class="primary-btn advanced-btn" @click="goToChat" @mouseenter="playButtonEffect">
            <span class="btn-text">开始体验 FamilyBot</span>
            <div class="btn-glow"></div>
            <div class="btn-ripple"></div>
          </button>
        </div>
      </div>
    </main>

  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()


const goToChat = () => {
  router.push('/chat')
}

// 粒子样式生成
const getParticleStyle = (index) => {
  const size = Math.random() * 4 + 2
  const animationDuration = Math.random() * 20 + 10
  const delay = Math.random() * 5
  const left = Math.random() * 100
  
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDuration: `${animationDuration}s`,
    animationDelay: `${delay}s`
  }
}

// 高级按钮效果
const playButtonEffect = (event) => {
  const button = event.currentTarget
  const ripple = button.querySelector('.btn-ripple')
  const glow = button.querySelector('.btn-glow')
  
  // 添加涟漪效果
  ripple.style.animation = 'rippleEffect 0.6s ease-out'
  glow.style.animation = 'glowPulse 0.8s ease-out'
  
  setTimeout(() => {
    ripple.style.animation = ''
    glow.style.animation = ''
  }, 800)
}

const playSecondaryButtonEffect = (event) => {
  const button = event.currentTarget
  const shine = button.querySelector('.btn-shine')
  
  shine.style.animation = 'shineEffect 1s ease-out'
  
  setTimeout(() => {
    shine.style.animation = ''
  }, 1000)
}

</script>

<style scoped>
/* 全局样式 */
* {
  box-sizing: border-box;
}

.page {
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  position: relative;
  overflow-x: hidden;
}

/* 动态视频背景 */
.background-video {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 1;
  opacity: 0.6;
  filter: blur(2px) brightness(0.7);
}

/* 背景图片层 */
.background-image {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 2;
  background-image: url('/background photo.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0.3;
  mix-blend-mode: overlay;
}

/* 自然渐变遮罩 */
.natural-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 3;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.1) 0%,
    rgba(255, 250, 245, 0.05) 30%,
    rgba(255, 245, 238, 0.03) 60%,
    rgba(255, 240, 230, 0.02) 100%
  );
  pointer-events: none;
}

/* 动态粒子背景 */
.particles-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 4;
  pointer-events: none;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.2) 70%, transparent 100%);
  border-radius: 50%;
  animation: particleFloat linear infinite;
  filter: blur(0.5px);
}

@keyframes particleFloat {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) rotate(360deg);
    opacity: 0;
  }
}

/* Meela风格导航栏 */
.meela-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 20;
  padding: 20px 0;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(30px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-name {
  font-size: 28px;
  font-weight: 400;
  color: #2c3e50;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.brand-icon {
  font-size: 20px;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 32px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px);
  padding: 14px 28px;
  border-radius: 50px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
}

.nav-item {
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: color 0.3s ease;
}

.nav-item:hover {
  color: #2c3e50;
}

.get-started-btn {
  background: #2c3e50;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 30px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(44, 62, 80, 0.3);
}

.get-started-btn:hover {
  background: #34495e;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(44, 62, 80, 0.4);
}

/* 主要内容区域 */
.hero-section {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 120px 40px 60px;
  position: relative;
  z-index: 15;
}

/* 特色标签 */
.feature-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(25px);
  padding: 14px 28px;
  border-radius: 50px;
  margin-bottom: 48px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.feature-badge:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  background: rgba(255, 255, 255, 0.95);
}

.feature-badge span {
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

.badge-arrow {
  color: #999;
  font-size: 16px;
}

/* 主标题区域 */
.hero-content {
  max-width: 800px;
}

.hero-title {
  font-size: clamp(48px, 7vw, 78px);
  font-weight: 300;
  line-height: 1.1;
  color: #2c3e50;
  margin-bottom: 36px;
  letter-spacing: -0.02em;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}


.hero-subtitle {
  font-size: 19px;
  line-height: 1.55;
  margin-bottom: 48px;
  max-width: 650px;
  margin-left: auto;
  margin-right: auto;
  color: #4a5568;
  font-weight: 400;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 行动按钮 */
.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.primary-btn {
  background: #2c3e50;
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(44, 62, 80, 0.3);
}

.primary-btn:hover {
  background: #34495e;
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(44, 62, 80, 0.4);
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.8);
  color: #2c3e50;
  border: 1px solid rgba(255, 255, 255, 0.4);
  padding: 16px 32px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.secondary-btn:hover {
  background: rgba(255, 255, 255, 1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.btn-icon {
  font-size: 18px;
}


/* 高级按钮效果 */
.advanced-btn {
  position: relative;
  overflow: hidden;
  background: #2c3e50;
  border: none;
  box-shadow: 0 6px 20px rgba(44, 62, 80, 0.25);
  border-radius: 50px;
  padding: 16px 36px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.advanced-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(44, 62, 80, 0.35);
  background: #34495e;
}

.btn-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  border-radius: inherit;
  opacity: 0;
}

.btn-ripple {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.6) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.glass-btn {
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  color: #2c3e50;
  border-radius: 50px;
  padding: 16px 32px;
  font-size: 16px;
  font-weight: 500;
  backdrop-filter: blur(25px);
  transition: all 0.3s ease;
}

.glass-btn:hover {
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.12);
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.5s ease;
}

.btn-text {
  position: relative;
  z-index: 1;
}




@keyframes rippleEffect {
  0% {
    width: 0;
    height: 0;
    opacity: 1;
  }
  100% {
    width: 200px;
    height: 200px;
    opacity: 0;
  }
}

@keyframes glowPulse {
  0% { opacity: 0; }
  50% { opacity: 1; }
  100% { opacity: 0; }
}

@keyframes shineEffect {
  0% { left: -100%; }
  100% { left: 100%; }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 20px;
  }
  
  .nav-menu {
    display: none;
  }
  
  .get-started-btn {
    display: block;
  }
  
  .hero-section {
    padding: 100px 20px 40px;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .primary-btn,
  .secondary-btn {
    width: 100%;
    max-width: 300px;
    justify-content: center;
  }
  
  .feature-badge {
    flex-direction: column;
    gap: 4px;
    text-align: center;
  }
  
  .badge-arrow {
    transform: rotate(90deg);
  }
}

@media (max-width: 480px) {
  .nav-container {
    padding: 0 15px;
  }
  
  .brand-name {
    font-size: 20px;
  }
  
  .hero-section {
    padding: 80px 15px 30px;
  }
  
  .hero-subtitle {
    font-size: 16px;
  }
  
  .feature-badge span {
    font-size: 12px;
  }
}
</style>