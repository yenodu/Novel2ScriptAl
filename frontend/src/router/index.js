import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'

function getToken() {
  return localStorage.getItem('token')
}

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true },
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Auth guard
router.beforeEach((to, _from, next) => {
  const hasToken = !!getToken()

  if (to.meta.public) {
    if (hasToken && to.path === '/login') {
      return next('/')
    }
    return next()
  }

  if (!hasToken) {
    return next('/login')
  }

  next()
})

export default router
