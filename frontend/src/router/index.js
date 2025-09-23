import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '@/views/ChatView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    redirect: '/chat'
  },
  {
    path: '/chat',
    name: 'chat',
    component: ChatView,
    meta: {
      title: 'FamilyBot - AI陪伴聊天'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
})

export default router
