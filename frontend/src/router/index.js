import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/chat'
  },
  {
    path: '/chat',
    name: 'Chat',
    component: ChatView,
    meta: {
      title: 'FamilyBot - AI家庭陪伴助手'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router