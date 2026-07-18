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
import SPASPrediction from '../views/SPASPrediction.vue'
import SPASSignal from '../views/SPASSignal.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/knowledge/p1_basics', name: 'P1Basics', component: P1Basics, props: { phaseId: 'p1_basics' } },
  { path: '/knowledge/:phaseId', name: 'KnowledgePhase', component: P1Basics, props: true },
  { path: '/practice/m1_data_lab', name: 'M1DataLab', component: M1DataLab, props: { labId: 'm1_data_lab' } },
  { path: '/practice/:labId', name: 'PracticeLab', component: M1DataLab, props: true },
  { path: '/sandbox', name: 'Sandbox', component: Sandbox },
  { path: '/progress', name: 'ProgressDashboard', component: ProgressDashboard },
  { path: '/psychology', name: 'PsychologyCheck', component: PsychologyCheck },
  { path: '/journal', name: 'TradingJournal', component: TradingJournal },
  { path: '/market-overview', name: 'MarketOverview', component: MarketOverview },
  { path: '/spas', name: 'SPASSignal', component: SPASSignal },
  { path: '/manual-analysis', name: 'SPASPrediction', component: SPASPrediction },
]

const router = new VueRouter({
  mode: 'hash',
  routes,
})

export default router
