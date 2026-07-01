import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

import Home from '../views/Home.vue'
import P1Basics from '../views/knowledge/P1Basics.vue'
import M1DataLab from '../views/practice/M1DataLab.vue'
import Sandbox from '../views/practice/Sandbox.vue'
import ProgressDashboard from '../views/ProgressDashboard.vue'
import PsychologyCheck from '../views/PsychologyCheck.vue'
import TradingJournal from '../views/TradingJournal.vue'
import MarketOverview from '../views/MarketOverview.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/knowledge/p1_basics', name: 'P1Basics', component: P1Basics },
  { path: '/knowledge/:phaseId', name: 'KnowledgePhase', component: P1Basics },
  { path: '/practice/m1_data_lab', name: 'M1DataLab', component: M1DataLab },
  { path: '/practice/:labId', name: 'PracticeLab', component: M1DataLab },
  { path: '/sandbox', name: 'Sandbox', component: Sandbox },
  { path: '/progress', name: 'ProgressDashboard', component: ProgressDashboard },
  { path: '/psychology', name: 'PsychologyCheck', component: PsychologyCheck },
  { path: '/journal', name: 'TradingJournal', component: TradingJournal },
  { path: '/market-overview', name: 'MarketOverview', component: MarketOverview },
]

const router = new VueRouter({
  mode: 'hash',
  routes,
})

export default router
