import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

import Home from '../views/Home.vue'
import P1Basics from '../views/knowledge/P1Basics.vue'
import M1DataLab from '../views/practice/M1DataLab.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/knowledge/p1_basics', name: 'P1Basics', component: P1Basics },
  { path: '/practice/m1_data_lab', name: 'M1DataLab', component: M1DataLab },
  // 默认章节路由（后续动态注册更多）
  { path: '/knowledge/:phaseId', name: 'KnowledgePhase', component: P1Basics },
  { path: '/practice/:labId', name: 'PracticeLab', component: M1DataLab },
]

const router = new VueRouter({
  mode: 'hash',
  routes,
})

export default router
