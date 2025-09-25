<template>
  <div class="page">
    <!-- 高级背景网格 -->
    <div class="grid-background"></div>
    
    <!-- 主要内容容器 -->
    <div class="main-container">
      <!-- 导航栏 -->
      <nav class="navbar">
        <div class="nav-content">
          <div class="logo">
            <span class="logo-text">FamilyBot</span>
          </div>
          <div class="nav-menu">
            <span class="nav-item">产品介绍</span>
            <span class="nav-item">使用指南</span>
            <span class="nav-item">关于我们</span>
            <span class="nav-item">联系客服</span>
          </div>
          <button class="chat-btn" @click="goToChat">开始对话</button>
        </div>
      </nav>

      <!-- 主内容区域 -->
      <main class="main-content">
        <!-- 欢迎区域 -->
        <section class="welcome-section">
          <div class="welcome-content">
            <h1 class="main-title">
              <span class="title-word">您</span>
              <span class="title-word">贴心的</span>
              <span class="title-word">AI家人</span>
            </h1>
            <p class="main-subtitle">
              FamilyBot 是您身边最贴心的AI伙伴，专为老年朋友精心设计。我们用最自然的语音交流方式，就像真正的家人一样陪伴在您身边，关心您的日常生活，倾听您内心的想法，分享您的喜怒哀乐，让每一天都充满温暖的交流与关怀。
            </p>
            <button class="start-btn" @click="goToChat">
              <span class="btn-icon">💬</span>
              <span>开始聊天</span>
            </button>
          </div>
          <div class="welcome-image">
            <div class="family-photo" data-tilt data-tilt-max="5" data-tilt-scale="1.02">
              <img src="/website picture.png" alt="家庭温馨时刻" />
              <div class="photo-overlay"></div>
            </div>
          </div>
        </section>

        <!-- 特色功能 -->
        <section class="features-section">
          <h2 class="section-title">
            简单易用的贴心功能
          </h2>
          <div class="features-grid">
            <div class="feature-card" data-aos="fade-up" data-aos-delay="100">
              <div class="feature-icon-wrapper">
                <div class="feature-icon">🗣️</div>
                <div class="icon-glow"></div>
              </div>
              <h3>语音对话</h3>
              <p>直接说话就能聊天，不用打字，就像和家人通话一样自然</p>
            </div>
            <div class="feature-card" data-aos="fade-up" data-aos-delay="200">
              <div class="feature-icon-wrapper">
                <div class="feature-icon">❤️</div>
                <div class="icon-glow"></div>
              </div>
              <h3>情感陪伴</h3>
              <p>AI家人会关心您的心情，倾听您的烦恼，给您温暖的回应</p>
            </div>
            <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
              <div class="feature-icon-wrapper">
                <div class="feature-icon">🔒</div>
                <div class="icon-glow"></div>
              </div>
              <h3>隐私安全</h3>
              <p>您的谈话内容完全保密，只属于您和AI家人之间的秘密</p>
            </div>
          </div>
        </section>
      </main>

      <!-- 页脚 -->
      <footer class="footer">
      </footer>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const goToChat = () => {
  router.push('/chat')
}

// 视差滚动效果
const handleScroll = () => {
  const scrolled = window.pageYOffset
  const parallax = document.querySelector('.grid-background')
  if (parallax) {
    parallax.style.transform = `translateY(${scrolled * 0.5}px)`
  }
}

// 卡片3D倾斜效果
const initTiltEffect = () => {
  const cards = document.querySelectorAll('[data-tilt]')
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      
      const centerX = rect.width / 2
      const centerY = rect.height / 2
      
      const rotateX = (y - centerY) / 10
      const rotateY = (centerX - x) / 10
      
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`
    })
    
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)'
    })
  })
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  initTiltEffect()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})



</script>

<style scoped>
/* 全局样式 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.page {
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: linear-gradient(135deg, #faf7f2 0%, #f5f0e8 50%, #ede4d3 100%);
  position: relative;
  overflow-x: hidden;
}

/* 高级背景网格 */
.grid-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 120%;
  pointer-events: none;
  z-index: 1;
  background-image: 
    linear-gradient(rgba(214, 158, 46, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(214, 158, 46, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: gridFloat 20s ease-in-out infinite;
}

@keyframes gridFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}


.main-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 导航栏 */
.navbar {
  background: rgba(255, 250, 240, 0.85);
  backdrop-filter: blur(25px) saturate(200%);
  border-bottom: 1px solid rgba(214, 158, 46, 0.15);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.06),
    0 1px 0 rgba(255, 255, 255, 0.8) inset;
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  overflow: hidden;
}

.navbar::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(214, 158, 46, 0.6), rgba(255, 193, 7, 0.4), transparent);
  transition: left 3s ease-in-out;
  animation: shimmer 4s ease-in-out infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  50% { left: 100%; }
  100% { left: 100%; }
}

.navbar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%, rgba(214, 158, 46, 0.05) 100%);
  pointer-events: none;
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  position: relative;
  overflow: hidden;
}

.logo::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(214, 158, 46, 0.1), transparent);
  transition: left 0.6s ease;
}

.logo:hover::before {
  left: 100%;
}

.logo:hover {
  background: rgba(214, 158, 46, 0.08);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(214, 158, 46, 0.2);
}

.logo-text {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2d3748;
  background: linear-gradient(135deg, #2d3748 0%, #d69e2e 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
}

.logo:hover .logo-text {
  background: linear-gradient(135deg, #d69e2e 0%, #f6ad55 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  transform: scale(1.05);
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-item {
  font-size: 0.95rem;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  padding: 0.75rem 1.25rem;
  border-radius: 0.75rem;
  position: relative;
  overflow: hidden;
  font-weight: 500;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 0;
  height: 100%;
  background: linear-gradient(135deg, rgba(214, 158, 46, 0.15) 0%, rgba(246, 173, 85, 0.1) 100%);
  transition: width 0.4s ease;
  border-radius: 0.75rem;
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #d69e2e, #f6ad55);
  transition: all 0.3s ease;
  transform: translateX(-50%);
  border-radius: 1px;
}

.nav-item:hover {
  color: #d69e2e;
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 4px 15px rgba(214, 158, 46, 0.2);
}

.nav-item:hover::before {
  width: 100%;
}

.nav-item:hover::after {
  width: 70%;
}

.nav-item:active {
  transform: translateY(-1px) scale(0.98);
}

.chat-btn {
  background: linear-gradient(135deg, #d69e2e 0%, #f6ad55 100%);
  color: white;
  border: none;
  padding: 0.875rem 2rem;
  border-radius: 2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  font-size: 0.95rem;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(214, 158, 46, 0.3);
}

.chat-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s ease;
}

.chat-btn:hover {
  background: linear-gradient(135deg, #b7791f 0%, #d69e2e 100%);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 8px 25px rgba(214, 158, 46, 0.4);
}

.chat-btn:hover::before {
  left: 100%;
}

.chat-btn:active {
  transform: translateY(-1px) scale(1.02);
  box-shadow: 0 4px 15px rgba(214, 158, 46, 0.3);
}

/* 主内容区域 */
.main-content {
  flex: 1;
  padding: 2rem 0;
}

/* 欢迎区域 */
.welcome-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.welcome-content {
  text-align: left;
}

.main-title {
  font-size: 3rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 1.5rem;
  line-height: 1.2;
}

.title-word {
  display: inline-block;
  animation: titleFadeIn 1s ease-out forwards;
  opacity: 0;
  transform: translateY(20px);
}

.title-word:nth-child(1) { animation-delay: 0.2s; }
.title-word:nth-child(2) { animation-delay: 0.4s; }
.title-word:nth-child(3) { animation-delay: 0.6s; }

@keyframes titleFadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.main-subtitle {
  font-size: 1.2rem;
  color: #4a5568;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.start-btn {
  background: linear-gradient(135deg, #d69e2e 0%, #b7791f 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 3rem;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(214, 158, 46, 0.4);
  position: relative;
  overflow: hidden;
}

.start-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(214, 158, 46, 0.5);
}

.start-btn:hover::before {
  left: 100%;
}

.btn-icon {
  font-size: 1.2rem;
}

/* 家庭照片 */
.welcome-image {
  display: flex;
  justify-content: center;
  align-items: center;
}

.family-photo {
  width: 420px;
  height: 420px;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.2),
    inset 0 0 0 1px rgba(214, 158, 46, 0.1);
  transition: all 0.6s cubic-bezier(0.165, 0.84, 0.44, 1);
  position: relative;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.family-photo:hover {
  box-shadow: 
    0 30px 60px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.3),
    inset 0 0 0 1px rgba(214, 158, 46, 0.2);
}

.family-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition: transform 0.6s ease;
}

.family-photo:hover img {
  transform: scale(1.05);
}

.photo-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    135deg,
    rgba(214, 158, 46, 0.1) 0%,
    transparent 30%,
    transparent 70%,
    rgba(214, 158, 46, 0.05) 100%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.family-photo:hover .photo-overlay {
  opacity: 1;
}

/* 特色功能区域 */
.features-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 2rem;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 3rem;
  position: relative;
}

.title-decoration {
  display: inline-block;
  animation: sparkle 2s ease-in-out infinite;
  margin: 0 0.5rem;
}

@keyframes sparkle {
  0%, 100% {
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
  50% {
    transform: scale(1.2) rotate(180deg);
    opacity: 0.8;
  }
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.7);
  padding: 2rem;
  border-radius: 1.5rem;
  text-align: center;
  box-shadow: 
    0 8px 32px rgba(214, 158, 46, 0.08),
    0 1px 0 rgba(255, 255, 255, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  transition: all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  border: 1px solid rgba(214, 158, 46, 0.15);
  backdrop-filter: blur(20px) saturate(180%);
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(214, 158, 46, 0.1),
    transparent
  );
  transition: left 0.6s ease;
}

.feature-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 
    0 20px 60px rgba(214, 158, 46, 0.15),
    0 1px 0 rgba(255, 255, 255, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  border-color: rgba(214, 158, 46, 0.25);
  background: rgba(255, 255, 255, 0.85);
}

.feature-card:hover::before {
  left: 100%;
}

.feature-icon-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 1rem;
}

.feature-icon {
  font-size: 3rem;
  display: block;
  position: relative;
  z-index: 2;
  transition: transform 0.3s ease;
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(214, 158, 46, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: iconGlow 3s ease-in-out infinite;
  z-index: 1;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1) rotate(10deg);
}

@keyframes iconGlow {
  0%, 100% {
    opacity: 0.3;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.6;
    transform: translate(-50%, -50%) scale(1.1);
  }
}

.feature-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #4a5568;
  line-height: 1.6;
  font-size: 0.95rem;
}

/* 页脚 */
.footer {
  padding: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-content {
    padding: 1rem;
  }
  
  .logo-text {
    font-size: 1.2rem;
  }
  
  .nav-menu {
    display: none;
  }
  
  .welcome-section {
    grid-template-columns: 1fr;
    gap: 2rem;
    padding: 2rem 1rem;
    text-align: center;
  }
  
  .main-title {
    font-size: 2.2rem;
  }
  
  .main-subtitle {
    font-size: 1rem;
  }
  
  .family-photo {
    width: 320px;
    height: 320px;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .features-section {
    padding: 3rem 1rem;
  }
}

@media (max-width: 480px) {
  .main-title {
    font-size: 1.8rem;
  }
  
  .main-subtitle {
    font-size: 0.9rem;
  }
  
  .start-btn {
    font-size: 1rem;
    padding: 0.8rem 1.5rem;
  }
  
  .family-photo {
    width: 280px;
    height: 280px;
  }
  
  .section-title {
    font-size: 1.6rem;
  }
  
  .feature-card {
    padding: 1.5rem;
  }
}
</style>